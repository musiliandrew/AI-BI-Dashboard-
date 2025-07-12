"""
Enterprise Data Processing Engine
Core engine for data ingestion, transformation, validation, and publishing
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import asyncio
import json
import re
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from abc import ABC, abstractmethod

from .models import DataSource, DataPipeline, PipelineExecution, DataQualityRule, DataQualityCheck

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result from data processing operation"""
    success: bool
    records_processed: int
    records_successful: int
    records_failed: int
    data_quality_score: float
    processing_time: float
    errors: List[str]
    warnings: List[str]
    output_data: Any = None
    metadata: Dict[str, Any] = None

@dataclass
class DataQualityResult:
    """Result from data quality validation"""
    overall_score: float
    rule_results: List[Dict[str, Any]]
    violations: List[Dict[str, Any]]
    recommendations: List[str]

class DataProcessor(ABC):
    """Abstract base class for data processors"""
    
    @abstractmethod
    def process(self, data: Any, config: Dict[str, Any]) -> ProcessingResult:
        """Process data according to configuration"""
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate processor configuration"""
        pass

class DataIngestionProcessor(DataProcessor):
    """Handles data ingestion from various sources"""
    
    def __init__(self):
        self.supported_formats = ['json', 'csv', 'xml', 'avro', 'parquet', 'excel']
        self.max_batch_size = 10000
    
    def process(self, data: Any, config: Dict[str, Any]) -> ProcessingResult:
        """Ingest data from source"""
        start_time = datetime.now()
        
        try:
            source_type = config.get('source_type')
            data_format = config.get('data_format', 'json')
            
            if source_type == 'api':
                result_data = self._ingest_from_api(data, config)
            elif source_type == 'database':
                result_data = self._ingest_from_database(data, config)
            elif source_type == 'file':
                result_data = self._ingest_from_file(data, config)
            elif source_type == 'stream':
                result_data = self._ingest_from_stream(data, config)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
            
            # Convert to standardized format
            df = self._normalize_data(result_data, data_format)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                records_processed=len(df),
                records_successful=len(df),
                records_failed=0,
                data_quality_score=1.0,  # Will be calculated later
                processing_time=processing_time,
                errors=[],
                warnings=[],
                output_data=df,
                metadata={'source_type': source_type, 'format': data_format}
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Data ingestion failed: {e}")
            
            return ProcessingResult(
                success=False,
                records_processed=0,
                records_successful=0,
                records_failed=0,
                data_quality_score=0.0,
                processing_time=processing_time,
                errors=[str(e)],
                warnings=[],
                metadata={'source_type': source_type}
            )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate ingestion configuration"""
        required_fields = ['source_type', 'data_format']
        return all(field in config for field in required_fields)
    
    def _ingest_from_api(self, data: Any, config: Dict[str, Any]) -> Any:
        """Ingest data from API endpoint"""
        # Implementation would handle API calls, pagination, rate limiting
        return data
    
    def _ingest_from_database(self, data: Any, config: Dict[str, Any]) -> Any:
        """Ingest data from database"""
        # Implementation would handle database connections, queries
        return data
    
    def _ingest_from_file(self, data: Any, config: Dict[str, Any]) -> Any:
        """Ingest data from file"""
        # Implementation would handle file reading, parsing
        return data
    
    def _ingest_from_stream(self, data: Any, config: Dict[str, Any]) -> Any:
        """Ingest data from stream"""
        # Implementation would handle streaming data
        return data
    
    def _normalize_data(self, data: Any, data_format: str) -> pd.DataFrame:
        """Normalize data to pandas DataFrame"""
        if data_format == 'json':
            if isinstance(data, list):
                return pd.DataFrame(data)
            elif isinstance(data, dict):
                return pd.DataFrame([data])
        elif data_format == 'csv':
            return pd.read_csv(data) if isinstance(data, str) else pd.DataFrame(data)
        elif data_format == 'excel':
            return pd.read_excel(data) if isinstance(data, str) else pd.DataFrame(data)
        
        # Default: try to convert to DataFrame
        return pd.DataFrame(data)

class DataTransformationProcessor(DataProcessor):
    """Handles data transformation and enrichment"""
    
    def __init__(self):
        self.transformation_functions = {
            'clean_text': self._clean_text,
            'normalize_dates': self._normalize_dates,
            'extract_features': self._extract_features,
            'aggregate_data': self._aggregate_data,
            'join_data': self._join_data,
            'calculate_metrics': self._calculate_metrics,
            'enrich_data': self._enrich_data
        }
    
    def process(self, data: pd.DataFrame, config: Dict[str, Any]) -> ProcessingResult:
        """Transform data according to configuration"""
        start_time = datetime.now()
        
        try:
            df = data.copy()
            transformation_steps = config.get('transformation_steps', [])
            errors = []
            warnings = []
            
            for step in transformation_steps:
                step_type = step.get('type')
                step_config = step.get('config', {})
                
                if step_type in self.transformation_functions:
                    try:
                        df = self.transformation_functions[step_type](df, step_config)
                    except Exception as e:
                        error_msg = f"Transformation step '{step_type}' failed: {e}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                else:
                    warning_msg = f"Unknown transformation step: {step_type}"
                    warnings.append(warning_msg)
                    logger.warning(warning_msg)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=len(errors) == 0,
                records_processed=len(data),
                records_successful=len(df),
                records_failed=len(data) - len(df),
                data_quality_score=len(df) / len(data) if len(data) > 0 else 0,
                processing_time=processing_time,
                errors=errors,
                warnings=warnings,
                output_data=df,
                metadata={'transformation_steps': len(transformation_steps)}
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Data transformation failed: {e}")
            
            return ProcessingResult(
                success=False,
                records_processed=len(data),
                records_successful=0,
                records_failed=len(data),
                data_quality_score=0.0,
                processing_time=processing_time,
                errors=[str(e)],
                warnings=[],
                metadata={}
            )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate transformation configuration"""
        transformation_steps = config.get('transformation_steps', [])
        return isinstance(transformation_steps, list)
    
    def _clean_text(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Clean text fields"""
        text_fields = config.get('fields', [])
        
        for field in text_fields:
            if field in df.columns:
                # Remove extra whitespace, normalize case, etc.
                df[field] = df[field].astype(str).str.strip().str.lower()
                
                # Remove special characters if specified
                if config.get('remove_special_chars', False):
                    df[field] = df[field].str.replace(r'[^\w\s]', '', regex=True)
        
        return df
    
    def _normalize_dates(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Normalize date fields"""
        date_fields = config.get('fields', [])
        date_format = config.get('format', 'ISO')
        
        for field in date_fields:
            if field in df.columns:
                df[field] = pd.to_datetime(df[field], errors='coerce')
        
        return df
    
    def _extract_features(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Extract features from existing data"""
        feature_configs = config.get('features', [])
        
        for feature_config in feature_configs:
            feature_name = feature_config.get('name')
            feature_type = feature_config.get('type')
            source_field = feature_config.get('source_field')
            
            if feature_type == 'date_part':
                # Extract date parts (year, month, day, etc.)
                date_part = feature_config.get('part', 'year')
                df[feature_name] = getattr(df[source_field].dt, date_part)
            
            elif feature_type == 'text_length':
                # Calculate text length
                df[feature_name] = df[source_field].astype(str).str.len()
            
            elif feature_type == 'categorical_encoding':
                # Encode categorical variables
                df[feature_name] = pd.Categorical(df[source_field]).codes
        
        return df
    
    def _aggregate_data(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Aggregate data by specified dimensions"""
        group_by = config.get('group_by', [])
        aggregations = config.get('aggregations', {})
        
        if group_by and aggregations:
            df = df.groupby(group_by).agg(aggregations).reset_index()
        
        return df
    
    def _join_data(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Join with external data"""
        # Implementation would handle joining with other datasets
        return df
    
    def _calculate_metrics(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Calculate business metrics"""
        metrics = config.get('metrics', [])
        
        for metric in metrics:
            metric_name = metric.get('name')
            metric_formula = metric.get('formula')
            
            # Simple metric calculations
            if metric_formula == 'conversion_rate':
                conversions_col = metric.get('conversions_column')
                total_col = metric.get('total_column')
                if conversions_col in df.columns and total_col in df.columns:
                    df[metric_name] = df[conversions_col] / df[total_col]
            
            elif metric_formula == 'growth_rate':
                value_col = metric.get('value_column')
                if value_col in df.columns:
                    df[metric_name] = df[value_col].pct_change()
        
        return df
    
    def _enrich_data(self, df: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Enrich data with external sources"""
        # Implementation would handle data enrichment
        return df

class DataValidationProcessor(DataProcessor):
    """Handles data quality validation"""
    
    def __init__(self):
        self.validation_rules = {
            'completeness': self._check_completeness,
            'uniqueness': self._check_uniqueness,
            'format': self._check_format,
            'range': self._check_range,
            'consistency': self._check_consistency,
            'referential_integrity': self._check_referential_integrity
        }
    
    def process(self, data: pd.DataFrame, config: Dict[str, Any]) -> ProcessingResult:
        """Validate data quality"""
        start_time = datetime.now()
        
        try:
            validation_rules = config.get('validation_rules', [])
            quality_results = []
            overall_violations = 0
            total_checks = 0
            
            for rule in validation_rules:
                rule_type = rule.get('type')
                rule_config = rule.get('config', {})
                
                if rule_type in self.validation_rules:
                    result = self.validation_rules[rule_type](data, rule_config)
                    quality_results.append(result)
                    
                    total_checks += result['records_checked']
                    overall_violations += result['violations']
            
            # Calculate overall quality score
            quality_score = 1.0 - (overall_violations / total_checks) if total_checks > 0 else 1.0
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=True,
                records_processed=len(data),
                records_successful=len(data),
                records_failed=0,
                data_quality_score=quality_score,
                processing_time=processing_time,
                errors=[],
                warnings=[],
                output_data=data,
                metadata={
                    'quality_results': quality_results,
                    'total_violations': overall_violations,
                    'total_checks': total_checks
                }
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Data validation failed: {e}")
            
            return ProcessingResult(
                success=False,
                records_processed=len(data),
                records_successful=0,
                records_failed=len(data),
                data_quality_score=0.0,
                processing_time=processing_time,
                errors=[str(e)],
                warnings=[],
                metadata={}
            )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate validation configuration"""
        validation_rules = config.get('validation_rules', [])
        return isinstance(validation_rules, list)
    
    def _check_completeness(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check data completeness"""
        field = config.get('field')
        threshold = config.get('threshold', 0.95)
        
        if field not in df.columns:
            return {'rule': 'completeness', 'field': field, 'records_checked': 0, 'violations': 0, 'passed': False}
        
        non_null_count = df[field].notna().sum()
        total_count = len(df)
        completeness_rate = non_null_count / total_count if total_count > 0 else 0
        
        violations = total_count - non_null_count if completeness_rate < threshold else 0
        
        return {
            'rule': 'completeness',
            'field': field,
            'records_checked': total_count,
            'violations': violations,
            'completeness_rate': completeness_rate,
            'threshold': threshold,
            'passed': completeness_rate >= threshold
        }
    
    def _check_uniqueness(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check data uniqueness"""
        field = config.get('field')
        
        if field not in df.columns:
            return {'rule': 'uniqueness', 'field': field, 'records_checked': 0, 'violations': 0, 'passed': False}
        
        total_count = len(df)
        unique_count = df[field].nunique()
        duplicate_count = total_count - unique_count
        
        return {
            'rule': 'uniqueness',
            'field': field,
            'records_checked': total_count,
            'violations': duplicate_count,
            'unique_count': unique_count,
            'duplicate_count': duplicate_count,
            'passed': duplicate_count == 0
        }
    
    def _check_format(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check data format compliance"""
        field = config.get('field')
        pattern = config.get('pattern')
        
        if field not in df.columns or not pattern:
            return {'rule': 'format', 'field': field, 'records_checked': 0, 'violations': 0, 'passed': False}
        
        # Check format using regex
        valid_format = df[field].astype(str).str.match(pattern, na=False)
        total_count = len(df)
        violations = (~valid_format).sum()
        
        return {
            'rule': 'format',
            'field': field,
            'records_checked': total_count,
            'violations': violations,
            'pattern': pattern,
            'passed': violations == 0
        }
    
    def _check_range(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check data range compliance"""
        field = config.get('field')
        min_value = config.get('min_value')
        max_value = config.get('max_value')
        
        if field not in df.columns:
            return {'rule': 'range', 'field': field, 'records_checked': 0, 'violations': 0, 'passed': False}
        
        violations = 0
        total_count = len(df)
        
        if min_value is not None:
            violations += (df[field] < min_value).sum()
        
        if max_value is not None:
            violations += (df[field] > max_value).sum()
        
        return {
            'rule': 'range',
            'field': field,
            'records_checked': total_count,
            'violations': violations,
            'min_value': min_value,
            'max_value': max_value,
            'passed': violations == 0
        }
    
    def _check_consistency(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check data consistency"""
        # Implementation for consistency checks
        return {'rule': 'consistency', 'records_checked': len(df), 'violations': 0, 'passed': True}
    
    def _check_referential_integrity(self, df: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Check referential integrity"""
        # Implementation for referential integrity checks
        return {'rule': 'referential_integrity', 'records_checked': len(df), 'violations': 0, 'passed': True}

class DataPublishingProcessor(DataProcessor):
    """Handles data publishing to various destinations"""
    
    def __init__(self):
        self.publishers = {
            'database': self._publish_to_database,
            'api': self._publish_to_api,
            'file': self._publish_to_file,
            'stream': self._publish_to_stream,
            'cache': self._publish_to_cache
        }
    
    def process(self, data: pd.DataFrame, config: Dict[str, Any]) -> ProcessingResult:
        """Publish data to configured destinations"""
        start_time = datetime.now()
        
        try:
            destinations = config.get('destinations', [])
            errors = []
            warnings = []
            published_count = 0
            
            for destination in destinations:
                dest_type = destination.get('type')
                dest_config = destination.get('config', {})
                
                if dest_type in self.publishers:
                    try:
                        result = self.publishers[dest_type](data, dest_config)
                        if result:
                            published_count += 1
                    except Exception as e:
                        error_msg = f"Publishing to {dest_type} failed: {e}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                else:
                    warning_msg = f"Unknown destination type: {dest_type}"
                    warnings.append(warning_msg)
                    logger.warning(warning_msg)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return ProcessingResult(
                success=len(errors) == 0,
                records_processed=len(data),
                records_successful=len(data) if published_count > 0 else 0,
                records_failed=0,
                data_quality_score=1.0,
                processing_time=processing_time,
                errors=errors,
                warnings=warnings,
                output_data=data,
                metadata={'destinations_published': published_count}
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Data publishing failed: {e}")
            
            return ProcessingResult(
                success=False,
                records_processed=len(data),
                records_successful=0,
                records_failed=len(data),
                data_quality_score=0.0,
                processing_time=processing_time,
                errors=[str(e)],
                warnings=[],
                metadata={}
            )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate publishing configuration"""
        destinations = config.get('destinations', [])
        return isinstance(destinations, list) and len(destinations) > 0
    
    def _publish_to_database(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        """Publish data to database"""
        # Implementation would handle database connections and inserts
        return True
    
    def _publish_to_api(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        """Publish data to API endpoint"""
        # Implementation would handle API calls
        return True
    
    def _publish_to_file(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        """Publish data to file"""
        # Implementation would handle file writing
        return True
    
    def _publish_to_stream(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        """Publish data to stream"""
        # Implementation would handle streaming
        return True
    
    def _publish_to_cache(self, df: pd.DataFrame, config: Dict[str, Any]) -> bool:
        """Publish data to cache"""
        # Implementation would handle caching
        return True

class DataProcessingEngine:
    """Main data processing engine orchestrator"""
    
    def __init__(self):
        self.processors = {
            'ingestion': DataIngestionProcessor(),
            'transformation': DataTransformationProcessor(),
            'validation': DataValidationProcessor(),
            'publishing': DataPublishingProcessor()
        }
        
        self.executor = ThreadPoolExecutor(max_workers=mp.cpu_count())
    
    async def execute_pipeline(self, pipeline: DataPipeline, execution: PipelineExecution) -> ProcessingResult:
        """Execute a complete data pipeline"""
        logger.info(f"Starting pipeline execution: {pipeline.name}")
        
        try:
            # Update execution status
            execution.status = 'running'
            execution.started_at = datetime.now()
            execution.save()
            
            # Process each stage
            current_data = None
            overall_result = ProcessingResult(
                success=True,
                records_processed=0,
                records_successful=0,
                records_failed=0,
                data_quality_score=1.0,
                processing_time=0,
                errors=[],
                warnings=[]
            )
            
            # Ingestion stage
            if pipeline.source_configs:
                for source_config in pipeline.source_configs:
                    result = await self._execute_processor('ingestion', current_data, source_config)
                    self._merge_results(overall_result, result)
                    if result.success:
                        current_data = result.output_data
            
            # Transformation stage
            if pipeline.transformation_steps and current_data is not None:
                transform_config = {'transformation_steps': pipeline.transformation_steps}
                result = await self._execute_processor('transformation', current_data, transform_config)
                self._merge_results(overall_result, result)
                if result.success:
                    current_data = result.output_data
            
            # Validation stage
            if pipeline.validation_rules and current_data is not None:
                validation_config = {'validation_rules': pipeline.validation_rules}
                result = await self._execute_processor('validation', current_data, validation_config)
                self._merge_results(overall_result, result)
                overall_result.data_quality_score = result.data_quality_score
            
            # Publishing stage
            if pipeline.output_destinations and current_data is not None:
                publish_config = {'destinations': pipeline.output_destinations}
                result = await self._execute_processor('publishing', current_data, publish_config)
                self._merge_results(overall_result, result)
            
            # Update execution with results
            execution.status = 'completed' if overall_result.success else 'failed'
            execution.completed_at = datetime.now()
            execution.duration_seconds = overall_result.processing_time
            execution.records_processed = overall_result.records_processed
            execution.records_successful = overall_result.records_successful
            execution.records_failed = overall_result.records_failed
            execution.data_quality_score = overall_result.data_quality_score
            execution.save()
            
            logger.info(f"Pipeline execution completed: {pipeline.name}")
            return overall_result
            
        except Exception as e:
            logger.error(f"Pipeline execution failed: {e}")
            
            execution.status = 'failed'
            execution.completed_at = datetime.now()
            execution.error_message = str(e)
            execution.save()
            
            return ProcessingResult(
                success=False,
                records_processed=0,
                records_successful=0,
                records_failed=0,
                data_quality_score=0.0,
                processing_time=0,
                errors=[str(e)],
                warnings=[]
            )
    
    async def _execute_processor(self, processor_type: str, data: Any, config: Dict[str, Any]) -> ProcessingResult:
        """Execute a specific processor"""
        processor = self.processors.get(processor_type)
        if not processor:
            raise ValueError(f"Unknown processor type: {processor_type}")
        
        # Run processor in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, processor.process, data, config)
        
        return result
    
    def _merge_results(self, overall: ProcessingResult, stage: ProcessingResult):
        """Merge stage result into overall result"""
        overall.records_processed += stage.records_processed
        overall.records_successful += stage.records_successful
        overall.records_failed += stage.records_failed
        overall.processing_time += stage.processing_time
        overall.errors.extend(stage.errors)
        overall.warnings.extend(stage.warnings)
        
        if not stage.success:
            overall.success = False

# Global processing engine instance
data_processing_engine = DataProcessingEngine()
