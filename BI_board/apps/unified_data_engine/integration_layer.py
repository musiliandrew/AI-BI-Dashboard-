"""
Integration Layer for Unified Data Engine
Connects existing models with the new efficient processing engine
"""
import asyncio
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

from .core_engine import (
    UnifiedDataEngine, DataNode, ProcessingPriority, 
    DataFlowState, unified_data_engine
)
from ..data_pipeline.models import DataSource, DataPipeline
from ..social_intelligence.models import SocialMediaAccount, SocialMediaPost
from ..payments.models import PaymentTransaction, PaymentAccount
from ..website_intelligence.models import WebsiteProperty, WebsiteMetrics

logger = logging.getLogger(__name__)

class DataSourceAdapter:
    """Adapter to convert existing models to unified data nodes"""
    
    @staticmethod
    def from_social_media_post(post: SocialMediaPost, priority: ProcessingPriority = ProcessingPriority.MEDIUM) -> DataNode:
        """Convert social media post to data node"""
        node_id = f"social_{post.platform}_{post.id}"
        data_hash = f"{post.platform}_{post.post_id}_{post.created_at.timestamp()}"
        
        return DataNode(
            node_id=node_id,
            data_hash=data_hash,
            source_type=f"social_{post.platform}",
            timestamp=post.created_at.timestamp(),
            priority=priority,
            metadata={
                'post_id': str(post.id),
                'platform': post.platform,
                'account_id': str(post.account.id),
                'content_type': post.content_type,
                'engagement_metrics': {
                    'likes': post.likes_count,
                    'comments': post.comments_count,
                    'shares': post.shares_count
                }
            }
        )
    
    @staticmethod
    def from_payment_transaction(transaction: PaymentTransaction, priority: ProcessingPriority = ProcessingPriority.CRITICAL) -> DataNode:
        """Convert payment transaction to data node"""
        node_id = f"payment_{transaction.payment_account.provider.name}_{transaction.id}"
        data_hash = f"{transaction.transaction_id}_{transaction.created_at.timestamp()}"
        
        return DataNode(
            node_id=node_id,
            data_hash=data_hash,
            source_type=f"payment_{transaction.payment_account.provider.name}",
            timestamp=transaction.created_at.timestamp(),
            priority=priority,
            metadata={
                'transaction_id': transaction.transaction_id,
                'provider': transaction.payment_account.provider.name,
                'amount': float(transaction.amount),
                'currency': transaction.currency,
                'status': transaction.status,
                'payment_method': transaction.payment_method_type
            }
        )
    
    @staticmethod
    def from_website_metrics(metrics: WebsiteMetrics, priority: ProcessingPriority = ProcessingPriority.HIGH) -> DataNode:
        """Convert website metrics to data node"""
        node_id = f"website_{metrics.website.id}_{metrics.id}"
        data_hash = f"{metrics.website.domain}_{metrics.date}_{metrics.created_at.timestamp()}"
        
        return DataNode(
            node_id=node_id,
            data_hash=data_hash,
            source_type="website_analytics",
            timestamp=metrics.created_at.timestamp(),
            priority=priority,
            metadata={
                'website_id': str(metrics.website.id),
                'domain': metrics.website.domain,
                'date': metrics.date.isoformat(),
                'sessions': metrics.sessions,
                'users': metrics.users,
                'pageviews': metrics.pageviews,
                'bounce_rate': float(metrics.bounce_rate)
            }
        )
    
    @staticmethod
    def from_data_source(data_source: DataSource, raw_data: Any, priority: ProcessingPriority = ProcessingPriority.MEDIUM) -> DataNode:
        """Convert generic data source to data node"""
        node_id = f"datasource_{data_source.source_type}_{data_source.id}"
        data_hash = f"{data_source.name}_{time.time()}"
        
        return DataNode(
            node_id=node_id,
            data_hash=data_hash,
            source_type=data_source.source_type,
            timestamp=time.time(),
            priority=priority,
            metadata={
                'source_id': str(data_source.id),
                'source_name': data_source.name,
                'config': data_source.config,
                'raw_data_size': len(str(raw_data)) if raw_data else 0
            }
        )

class PipelineOrchestrator:
    """Orchestrates pipeline execution using the unified engine"""
    
    def __init__(self, engine: UnifiedDataEngine = None):
        self.engine = engine or unified_data_engine
        self.active_pipelines: Dict[str, PipelineRun] = {}
        
    async def execute_pipeline(self, pipeline: DataPipeline, input_data: Any = None) -> PipelineRun:
        """Execute a data pipeline using the unified engine"""
        # Create pipeline run record
        pipeline_run = PipelineRun.objects.create(
            pipeline=pipeline,
            status=ProcessingStatus.PROCESSING
        )
        
        self.active_pipelines[str(pipeline_run.id)] = pipeline_run
        
        try:
            # Convert input data to data nodes
            data_nodes = await self._create_pipeline_nodes(pipeline, input_data, pipeline_run)
            
            # Submit nodes to unified engine
            node_ids = []
            for node in data_nodes:
                node_id = await self.engine.submit_data_node(node)
                node_ids.append(node_id)
            
            # Process nodes in batches
            all_results = []
            while node_ids:
                # Process batch
                results = await self.engine.process_next_batch(batch_size=20)
                all_results.extend(results)
                
                # Remove completed nodes
                completed_ids = {r.node_id for r in results if r.success}
                node_ids = [nid for nid in node_ids if nid not in completed_ids]
                
                # Check for failures
                failed_results = [r for r in results if not r.success]
                if failed_results:
                    logger.warning(f"Pipeline {pipeline.id} has {len(failed_results)} failed nodes")
            
            # Update pipeline run with results
            await self._update_pipeline_run(pipeline_run, all_results)
            
            return pipeline_run
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            pipeline_run.status = ProcessingStatus.FAILED
            pipeline_run.error_log = str(e)
            pipeline_run.completed_at = datetime.now()
            pipeline_run.save()
            
            return pipeline_run
        finally:
            if str(pipeline_run.id) in self.active_pipelines:
                del self.active_pipelines[str(pipeline_run.id)]
    
    async def _create_pipeline_nodes(self, pipeline: DataPipeline, input_data: Any, pipeline_run: PipelineRun) -> List[DataNode]:
        """Create data nodes for pipeline processing"""
        nodes = []
        
        # Create ingestion node
        if input_data:
            ingestion_node = DataSourceAdapter.from_data_source(
                pipeline.data_source, 
                input_data, 
                ProcessingPriority.HIGH
            )
            nodes.append(ingestion_node)
            
            # Create transformation nodes
            for i, transform_rule in enumerate(pipeline.transformation_rules):
                transform_node = DataNode(
                    node_id=f"transform_{pipeline_run.id}_{i}",
                    data_hash=f"transform_{pipeline.id}_{i}_{time.time()}",
                    source_type="data_transformation",
                    timestamp=time.time(),
                    priority=ProcessingPriority.MEDIUM,
                    dependencies={ingestion_node.node_id} if i == 0 else {f"transform_{pipeline_run.id}_{i-1}"},
                    metadata={
                        'pipeline_id': str(pipeline.id),
                        'transform_rule': transform_rule,
                        'step_index': i
                    }
                )
                nodes.append(transform_node)
            
            # Create validation node
            if pipeline.validation_rules:
                validation_node = DataNode(
                    node_id=f"validate_{pipeline_run.id}",
                    data_hash=f"validate_{pipeline.id}_{time.time()}",
                    source_type="data_validation",
                    timestamp=time.time(),
                    priority=ProcessingPriority.HIGH,
                    dependencies={nodes[-1].node_id},  # Depends on last transformation
                    metadata={
                        'pipeline_id': str(pipeline.id),
                        'validation_rules': pipeline.validation_rules
                    }
                )
                nodes.append(validation_node)
        
        return nodes
    
    async def _update_pipeline_run(self, pipeline_run: PipelineRun, results: List[Any]):
        """Update pipeline run with processing results"""
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        # Update basic metrics
        pipeline_run.records_processed = len(results)
        pipeline_run.records_failed = len(failed_results)
        pipeline_run.completed_at = datetime.now()
        
        # Calculate processing time
        if results:
            total_time = sum(r.processing_time for r in results)
            pipeline_run.processing_time_seconds = total_time
        
        # Set status
        if failed_results:
            pipeline_run.status = ProcessingStatus.FAILED
            pipeline_run.error_log = "; ".join(r.error_message for r in failed_results if r.error_message)
        else:
            pipeline_run.status = ProcessingStatus.COMPLETED
        
        # Calculate data quality score
        if successful_results:
            quality_score = len(successful_results) / len(results)
            
            # Create quality report
            DataQualityReport.objects.create(
                pipeline_run=pipeline_run,
                completeness_score=quality_score * 100,
                consistency_score=95.0,  # Would be calculated from actual validation
                accuracy_score=90.0,     # Would be calculated from actual validation
                validity_score=quality_score * 100,
                overall_score=quality_score * 100,
                recommendations=self._generate_quality_recommendations(results)
            )
        
        pipeline_run.save()
    
    def _generate_quality_recommendations(self, results: List[Any]) -> List[str]:
        """Generate data quality recommendations"""
        recommendations = []
        
        failed_results = [r for r in results if not r.success]
        if failed_results:
            recommendations.append(f"Address {len(failed_results)} processing failures")
        
        # Add more sophisticated recommendations based on results
        if len(results) > 0:
            avg_time = sum(r.processing_time for r in results) / len(results)
            if avg_time > 5.0:  # 5 seconds
                recommendations.append("Consider optimizing processing performance")
        
        return recommendations

class RealTimeDataProcessor:
    """Handles real-time data processing for critical streams"""
    
    def __init__(self, engine: UnifiedDataEngine = None):
        self.engine = engine or unified_data_engine
        self.real_time_queue = asyncio.Queue(maxsize=10000)
        self.processing_task = None
        
    async def start_real_time_processing(self):
        """Start real-time processing loop"""
        if self.processing_task is None:
            self.processing_task = asyncio.create_task(self._process_real_time_loop())
    
    async def stop_real_time_processing(self):
        """Stop real-time processing loop"""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
            self.processing_task = None
    
    async def submit_real_time_data(self, data_node: DataNode):
        """Submit data for real-time processing"""
        try:
            await self.real_time_queue.put(data_node)
        except asyncio.QueueFull:
            logger.warning("Real-time queue is full, dropping data node")
    
    async def _process_real_time_loop(self):
        """Main real-time processing loop"""
        while True:
            try:
                # Get batch of nodes from queue
                batch = []
                try:
                    # Get first node (blocking)
                    node = await asyncio.wait_for(self.real_time_queue.get(), timeout=1.0)
                    batch.append(node)
                    
                    # Get additional nodes (non-blocking)
                    for _ in range(19):  # Max batch size of 20
                        try:
                            node = self.real_time_queue.get_nowait()
                            batch.append(node)
                        except asyncio.QueueEmpty:
                            break
                            
                except asyncio.TimeoutError:
                    continue  # No data available, continue loop
                
                # Submit batch to engine
                for node in batch:
                    await self.engine.submit_data_node(node)
                
                # Process batch
                await self.engine.process_next_batch(batch_size=len(batch))
                
            except Exception as e:
                logger.error(f"Real-time processing error: {e}")
                await asyncio.sleep(1)  # Brief pause on error

class DataFlowMonitor:
    """Monitors data flow performance and health"""
    
    def __init__(self, engine: UnifiedDataEngine = None):
        self.engine = engine or unified_data_engine
        
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        engine_metrics = self.engine.get_metrics()
        
        return {
            'processing_performance': {
                'total_processed': engine_metrics['total_processed'],
                'avg_processing_time': engine_metrics['avg_processing_time'],
                'error_rate': engine_metrics['error_rate'],
                'throughput_per_second': self._calculate_throughput()
            },
            'resource_utilization': {
                'active_nodes': engine_metrics['active_nodes'],
                'queue_size': engine_metrics['queue_size'],
                'cache_size': engine_metrics['cache_size'],
                'cache_hit_rate': self._calculate_cache_hit_rate(engine_metrics)
            },
            'data_quality': {
                'completed_nodes': engine_metrics['completed_nodes'],
                'failed_nodes': engine_metrics['failed_nodes'],
                'success_rate': self._calculate_success_rate(engine_metrics)
            }
        }
    
    def _calculate_throughput(self) -> float:
        """Calculate processing throughput"""
        metrics = self.engine.get_metrics()
        if metrics['avg_processing_time'] > 0:
            return 1.0 / metrics['avg_processing_time']
        return 0.0
    
    def _calculate_cache_hit_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate cache hit rate"""
        total_requests = metrics['cache_hits'] + metrics['cache_misses']
        if total_requests > 0:
            return metrics['cache_hits'] / total_requests
        return 0.0
    
    def _calculate_success_rate(self, metrics: Dict[str, Any]) -> float:
        """Calculate processing success rate"""
        total_nodes = metrics['completed_nodes'] + metrics['failed_nodes']
        if total_nodes > 0:
            return metrics['completed_nodes'] / total_nodes
        return 0.0

# Global instances
pipeline_orchestrator = PipelineOrchestrator()
real_time_processor = RealTimeDataProcessor()
data_flow_monitor = DataFlowMonitor()
