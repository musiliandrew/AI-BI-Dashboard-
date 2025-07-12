"""
Unified Data Processing Engine
Efficient, non-redundant data flow with optimal DSA implementation
"""
import asyncio
import heapq
import time
from collections import deque, defaultdict
from typing import Dict, List, Any, Optional, Tuple, Set, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import hashlib
import pickle
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class DataFlowState(Enum):
    """Data flow processing states"""
    PENDING = "pending"
    PROCESSING = "processing" 
    COMPLETED = "completed"
    FAILED = "failed"
    CACHED = "cached"

class ProcessingPriority(Enum):
    """Processing priority levels"""
    CRITICAL = 1    # Real-time data (payments, alerts)
    HIGH = 2        # User-facing analytics
    MEDIUM = 3      # Background processing
    LOW = 4         # Batch jobs, reports

@dataclass
class DataNode:
    """Efficient data node with minimal memory footprint"""
    node_id: str
    data_hash: str
    source_type: str
    timestamp: float
    priority: ProcessingPriority
    dependencies: Set[str] = field(default_factory=set)
    state: DataFlowState = DataFlowState.PENDING
    data_ref: Optional[str] = None  # Reference to data storage, not data itself
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __lt__(self, other):
        """For priority queue ordering"""
        return self.priority.value < other.priority.value

@dataclass
class ProcessingResult:
    """Lightweight processing result"""
    success: bool
    node_id: str
    processing_time: float
    output_hash: Optional[str] = None
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

class DataCache:
    """Efficient LRU cache with hash-based deduplication"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache: Dict[str, Any] = {}
        self.access_order = deque()  # For LRU
        self.hash_to_key: Dict[str, str] = {}  # Hash -> cache key mapping
        
    def get(self, key: str) -> Optional[Any]:
        """O(1) cache retrieval"""
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key: str, value: Any, data_hash: str) -> None:
        """O(1) cache insertion with deduplication"""
        # Check if we already have this data (by hash)
        if data_hash in self.hash_to_key:
            existing_key = self.hash_to_key[data_hash]
            if existing_key in self.cache:
                # Data already exists, just update access
                self.access_order.remove(existing_key)
                self.access_order.append(existing_key)
                return
        
        # Add new data
        if len(self.cache) >= self.max_size:
            # Remove LRU item
            lru_key = self.access_order.popleft()
            old_value = self.cache.pop(lru_key)
            # Remove hash mapping
            old_hash = self._compute_hash(old_value)
            if old_hash in self.hash_to_key:
                del self.hash_to_key[old_hash]
        
        self.cache[key] = value
        self.access_order.append(key)
        self.hash_to_key[data_hash] = key
    
    def _compute_hash(self, data: Any) -> str:
        """Compute hash for data deduplication"""
        return hashlib.sha256(pickle.dumps(data)).hexdigest()

class DependencyGraph:
    """Efficient DAG for processing dependencies"""
    
    def __init__(self):
        self.graph: Dict[str, Set[str]] = defaultdict(set)  # node -> dependencies
        self.reverse_graph: Dict[str, Set[str]] = defaultdict(set)  # node -> dependents
        self.in_degree: Dict[str, int] = defaultdict(int)
        
    def add_dependency(self, node: str, dependency: str) -> None:
        """Add dependency relationship - O(1)"""
        if dependency not in self.graph[node]:
            self.graph[node].add(dependency)
            self.reverse_graph[dependency].add(node)
            self.in_degree[node] += 1
            
    def remove_dependency(self, node: str, dependency: str) -> None:
        """Remove dependency relationship - O(1)"""
        if dependency in self.graph[node]:
            self.graph[node].remove(dependency)
            self.reverse_graph[dependency].remove(node)
            self.in_degree[node] -= 1
            
    def get_ready_nodes(self) -> List[str]:
        """Get nodes with no pending dependencies - O(n)"""
        return [node for node, degree in self.in_degree.items() if degree == 0]
    
    def mark_completed(self, node: str) -> List[str]:
        """Mark node as completed and return newly ready nodes - O(k) where k is dependents"""
        newly_ready = []
        for dependent in self.reverse_graph[node]:
            self.in_degree[dependent] -= 1
            if self.in_degree[dependent] == 0:
                newly_ready.append(dependent)
        return newly_ready

class ProcessorRegistry:
    """Registry for data processors with efficient lookup"""
    
    def __init__(self):
        self.processors: Dict[str, Callable] = {}
        self.processor_metadata: Dict[str, Dict[str, Any]] = {}
        
    def register(self, processor_type: str, processor_func: Callable, 
                metadata: Dict[str, Any] = None) -> None:
        """Register a processor - O(1)"""
        self.processors[processor_type] = processor_func
        self.processor_metadata[processor_type] = metadata or {}
        
    def get_processor(self, processor_type: str) -> Optional[Callable]:
        """Get processor by type - O(1)"""
        return self.processors.get(processor_type)
    
    def get_compatible_processors(self, source_type: str) -> List[str]:
        """Get processors compatible with source type - O(n)"""
        compatible = []
        for proc_type, metadata in self.processor_metadata.items():
            if source_type in metadata.get('compatible_sources', []):
                compatible.append(proc_type)
        return compatible

class UnifiedDataEngine:
    """
    Main unified data processing engine
    Eliminates redundancy between ingestion and pipeline processing
    """
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or mp.cpu_count()
        
        # Core data structures
        self.processing_queue = []  # Priority queue (heapq)
        self.dependency_graph = DependencyGraph()
        self.data_cache = DataCache(max_size=50000)
        self.processor_registry = ProcessorRegistry()
        
        # State tracking
        self.active_nodes: Dict[str, DataNode] = {}
        self.completed_nodes: Set[str] = set()
        self.failed_nodes: Set[str] = set()
        
        # Performance optimization
        self.thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = ProcessPoolExecutor(max_workers=self.max_workers // 2)
        
        # Metrics
        self.processing_metrics = {
            'total_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'avg_processing_time': 0.0,
            'error_rate': 0.0
        }
        
        # Register default processors
        self._register_default_processors()
        
    def _register_default_processors(self):
        """Register built-in processors"""
        # Social media processors
        self.processor_registry.register(
            'social_media_ingestion',
            self._process_social_media,
            {'compatible_sources': ['instagram', 'twitter', 'facebook', 'linkedin']}
        )
        
        # Payment processors
        self.processor_registry.register(
            'payment_ingestion', 
            self._process_payment_data,
            {'compatible_sources': ['stripe', 'paypal', 'square', 'flutterwave']}
        )
        
        # Website analytics processors
        self.processor_registry.register(
            'analytics_ingestion',
            self._process_analytics_data,
            {'compatible_sources': ['google_analytics', 'custom_tracking']}
        )
        
        # Transformation processors
        self.processor_registry.register(
            'data_transformation',
            self._transform_data,
            {'compatible_sources': ['any']}
        )
        
        # Validation processors
        self.processor_registry.register(
            'data_validation',
            self._validate_data,
            {'compatible_sources': ['any']}
        )
    
    async def submit_data_node(self, node: DataNode) -> str:
        """Submit data node for processing - O(log n) for priority queue"""
        # Check cache first
        cached_result = self.data_cache.get(node.data_hash)
        if cached_result:
            node.state = DataFlowState.CACHED
            self.processing_metrics['cache_hits'] += 1
            return node.node_id
        
        self.processing_metrics['cache_misses'] += 1
        
        # Add to processing structures
        self.active_nodes[node.node_id] = node
        
        # Add dependencies to graph
        for dep in node.dependencies:
            self.dependency_graph.add_dependency(node.node_id, dep)
        
        # Add to priority queue if ready
        if not node.dependencies:
            heapq.heappush(self.processing_queue, node)
            
        return node.node_id
    
    async def process_next_batch(self, batch_size: int = 10) -> List[ProcessingResult]:
        """Process next batch of ready nodes - O(k log n) where k is batch size"""
        results = []
        
        # Get ready nodes from queue
        batch_nodes = []
        for _ in range(min(batch_size, len(self.processing_queue))):
            if self.processing_queue:
                node = heapq.heappop(self.processing_queue)
                if node.node_id in self.active_nodes:  # Still active
                    batch_nodes.append(node)
        
        # Process batch concurrently
        if batch_nodes:
            tasks = [self._process_node(node) for node in batch_nodes]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle results and update dependencies
            for i, result in enumerate(results):
                if isinstance(result, ProcessingResult):
                    await self._handle_processing_result(batch_nodes[i], result)
                else:
                    # Handle exception
                    error_result = ProcessingResult(
                        success=False,
                        node_id=batch_nodes[i].node_id,
                        processing_time=0.0,
                        error_message=str(result)
                    )
                    await self._handle_processing_result(batch_nodes[i], error_result)
        
        return [r for r in results if isinstance(r, ProcessingResult)]
    
    async def _process_node(self, node: DataNode) -> ProcessingResult:
        """Process individual data node"""
        start_time = time.time()
        node.state = DataFlowState.PROCESSING
        
        try:
            # Get appropriate processor
            processor = self.processor_registry.get_processor(node.source_type)
            if not processor:
                # Try to find compatible processor
                compatible = self.processor_registry.get_compatible_processors(node.source_type)
                if compatible:
                    processor = self.processor_registry.get_processor(compatible[0])
            
            if not processor:
                raise ValueError(f"No processor found for source type: {node.source_type}")
            
            # Execute processor
            loop = asyncio.get_event_loop()
            if node.priority in [ProcessingPriority.CRITICAL, ProcessingPriority.HIGH]:
                # Use thread pool for high priority
                result_data = await loop.run_in_executor(self.thread_pool, processor, node)
            else:
                # Use process pool for lower priority
                result_data = await loop.run_in_executor(self.process_pool, processor, node)
            
            processing_time = time.time() - start_time
            
            # Cache result
            output_hash = self._compute_hash(result_data)
            self.data_cache.put(node.node_id, result_data, output_hash)
            
            return ProcessingResult(
                success=True,
                node_id=node.node_id,
                processing_time=processing_time,
                output_hash=output_hash,
                metrics={'data_size': len(str(result_data))}
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Processing failed for node {node.node_id}: {e}")
            
            return ProcessingResult(
                success=False,
                node_id=node.node_id,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    async def _handle_processing_result(self, node: DataNode, result: ProcessingResult):
        """Handle processing result and update dependencies"""
        if result.success:
            node.state = DataFlowState.COMPLETED
            self.completed_nodes.add(node.node_id)
            
            # Update metrics
            self.processing_metrics['total_processed'] += 1
            self._update_avg_processing_time(result.processing_time)
            
            # Check for newly ready dependent nodes
            newly_ready = self.dependency_graph.mark_completed(node.node_id)
            for ready_node_id in newly_ready:
                if ready_node_id in self.active_nodes:
                    ready_node = self.active_nodes[ready_node_id]
                    heapq.heappush(self.processing_queue, ready_node)
        else:
            node.state = DataFlowState.FAILED
            self.failed_nodes.add(node.node_id)
            self._update_error_rate()
        
        # Clean up
        if node.node_id in self.active_nodes:
            del self.active_nodes[node.node_id]
    
    def _update_avg_processing_time(self, new_time: float):
        """Update average processing time efficiently"""
        total = self.processing_metrics['total_processed']
        current_avg = self.processing_metrics['avg_processing_time']
        self.processing_metrics['avg_processing_time'] = (
            (current_avg * (total - 1) + new_time) / total
        )
    
    def _update_error_rate(self):
        """Update error rate"""
        total = len(self.completed_nodes) + len(self.failed_nodes)
        if total > 0:
            self.processing_metrics['error_rate'] = len(self.failed_nodes) / total
    
    def _compute_hash(self, data: Any) -> str:
        """Compute hash for data deduplication"""
        return hashlib.sha256(str(data).encode()).hexdigest()
    
    # Default processor implementations
    def _process_social_media(self, node: DataNode) -> Dict[str, Any]:
        """Process social media data"""
        # Implementation would handle social media specific processing
        return {'processed': True, 'source': node.source_type, 'timestamp': node.timestamp}
    
    def _process_payment_data(self, node: DataNode) -> Dict[str, Any]:
        """Process payment data"""
        # Implementation would handle payment specific processing
        return {'processed': True, 'source': node.source_type, 'timestamp': node.timestamp}
    
    def _process_analytics_data(self, node: DataNode) -> Dict[str, Any]:
        """Process analytics data"""
        # Implementation would handle analytics specific processing
        return {'processed': True, 'source': node.source_type, 'timestamp': node.timestamp}
    
    def _transform_data(self, node: DataNode) -> Dict[str, Any]:
        """Transform data"""
        # Implementation would handle data transformation
        return {'transformed': True, 'source': node.source_type, 'timestamp': node.timestamp}
    
    def _validate_data(self, node: DataNode) -> Dict[str, Any]:
        """Validate data"""
        # Implementation would handle data validation
        return {'validated': True, 'source': node.source_type, 'timestamp': node.timestamp}
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics"""
        return {
            **self.processing_metrics,
            'active_nodes': len(self.active_nodes),
            'queue_size': len(self.processing_queue),
            'cache_size': len(self.data_cache.cache),
            'completed_nodes': len(self.completed_nodes),
            'failed_nodes': len(self.failed_nodes)
        }
    
    async def shutdown(self):
        """Graceful shutdown"""
        self.thread_pool.shutdown(wait=True)
        self.process_pool.shutdown(wait=True)

# Global unified engine instance
unified_data_engine = UnifiedDataEngine()
