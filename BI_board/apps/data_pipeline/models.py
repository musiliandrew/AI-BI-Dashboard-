"""
Enterprise Data Pipeline Models
Core data pipeline infrastructure for handling massive multi-source data streams
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import models
import json
from enum import Enum

class DataSource(models.Model):
    """Data source configuration and metadata"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Source identification
    name = models.CharField(max_length=200)
    source_type = models.CharField(max_length=50)  # api, database, file, stream, etc.
    source_category = models.CharField(max_length=50)  # social, payment, website, business, etc.
    
    # Connection details
    connection_config = models.JSONField(default=dict)  # API endpoints, credentials, etc.
    authentication_config = models.JSONField(default=dict)  # Auth tokens, keys, etc.
    
    # Data characteristics
    data_format = models.CharField(max_length=30, default='json')  # json, csv, xml, avro, etc.
    expected_schema = models.JSONField(default=dict)  # Expected data structure
    data_frequency = models.CharField(max_length=20, default='real_time')  # real_time, hourly, daily, etc.
    
    # Volume and performance
    estimated_daily_volume = models.BigIntegerField(default=0)  # Records per day
    estimated_size_mb = models.FloatField(default=0)  # MB per day
    max_batch_size = models.IntegerField(default=1000)
    
    # Quality and reliability
    data_quality_score = models.FloatField(default=0.0)  # 0-1 score
    reliability_score = models.FloatField(default=0.0)  # 0-1 score
    last_quality_check = models.DateTimeField(null=True, blank=True)
    
    # Processing configuration
    requires_transformation = models.BooleanField(default=True)
    requires_validation = models.BooleanField(default=True)
    requires_enrichment = models.BooleanField(default=False)
    
    # Status and monitoring
    is_active = models.BooleanField(default=True)
    is_healthy = models.BooleanField(default=True)
    last_successful_sync = models.DateTimeField(null=True, blank=True)
    last_error = models.TextField(blank=True)
    error_count = models.IntegerField(default=0)
    
    # Metadata
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_sources')
    tags = models.JSONField(default=list)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['source_type', 'source_category']),
            models.Index(fields=['is_active', 'is_healthy']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.source_type})"

class DataPipeline(models.Model):
    """Data pipeline configuration and orchestration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Pipeline identification
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    pipeline_type = models.CharField(max_length=30)  # batch, streaming, hybrid
    
    # Pipeline configuration
    source_configs = models.JSONField(default=list)  # List of source configurations
    transformation_steps = models.JSONField(default=list)  # Ordered transformation steps
    validation_rules = models.JSONField(default=list)  # Data validation rules
    output_destinations = models.JSONField(default=list)  # Where to publish data
    
    # Scheduling and triggers
    schedule_type = models.CharField(max_length=20, default='cron')  # cron, interval, event
    schedule_config = models.JSONField(default=dict)  # Schedule configuration
    trigger_conditions = models.JSONField(default=list)  # Event-based triggers
    
    # Performance and scaling
    max_parallel_workers = models.IntegerField(default=4)
    memory_limit_mb = models.IntegerField(default=2048)
    timeout_seconds = models.IntegerField(default=3600)
    retry_config = models.JSONField(default=dict)
    
    # Quality and monitoring
    data_quality_threshold = models.FloatField(default=0.95)  # Minimum quality score
    alert_on_failure = models.BooleanField(default=True)
    alert_recipients = models.JSONField(default=list)
    
    # Status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('error', 'Error'),
        ('deprecated', 'Deprecated'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Execution tracking
    total_executions = models.IntegerField(default=0)
    successful_executions = models.IntegerField(default=0)
    failed_executions = models.IntegerField(default=0)
    last_execution_at = models.DateTimeField(null=True, blank=True)
    next_execution_at = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='data_pipelines')
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.pipeline_type})"

class PipelineExecution(models.Model):
    """Individual pipeline execution tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Execution identification
    pipeline = models.ForeignKey(DataPipeline, on_delete=models.CASCADE, related_name='executions')
    execution_id = models.CharField(max_length=100, unique=True)
    
    # Execution details
    trigger_type = models.CharField(max_length=20)  # scheduled, manual, event
    trigger_metadata = models.JSONField(default=dict)
    
    # Status and timing
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('timeout', 'Timeout'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Data processing metrics
    records_processed = models.BigIntegerField(default=0)
    records_successful = models.BigIntegerField(default=0)
    records_failed = models.BigIntegerField(default=0)
    data_size_mb = models.FloatField(default=0)
    
    # Quality metrics
    data_quality_score = models.FloatField(null=True, blank=True)
    validation_errors = models.JSONField(default=list)
    transformation_errors = models.JSONField(default=list)
    
    # Resource usage
    memory_used_mb = models.FloatField(null=True, blank=True)
    cpu_time_seconds = models.FloatField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict)
    retry_count = models.IntegerField(default=0)
    
    # Output tracking
    output_destinations = models.JSONField(default=list)
    output_metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['pipeline', 'started_at']),
            models.Index(fields=['status', 'started_at']),
        ]

class DataQualityRule(models.Model):
    """Data quality validation rules"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Rule identification
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    rule_type = models.CharField(max_length=30)  # completeness, accuracy, consistency, etc.
    
    # Rule configuration
    field_name = models.CharField(max_length=100, blank=True)  # Field to validate
    rule_expression = models.TextField()  # Validation logic
    rule_parameters = models.JSONField(default=dict)
    
    # Severity and actions
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('warning', 'Warning'),
        ('error', 'Error'),
        ('critical', 'Critical'),
    ]
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='error')
    
    # Actions on rule violation
    action_on_violation = models.CharField(max_length=30, default='flag')  # flag, reject, fix
    auto_fix_enabled = models.BooleanField(default=False)
    auto_fix_logic = models.TextField(blank=True)
    
    # Applicability
    applicable_sources = models.JSONField(default=list)  # Source types this applies to
    applicable_pipelines = models.JSONField(default=list)  # Pipeline IDs
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Metadata
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quality_rules')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class DataQualityCheck(models.Model):
    """Data quality check results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Check identification
    execution = models.ForeignKey(PipelineExecution, on_delete=models.CASCADE, related_name='quality_checks')
    rule = models.ForeignKey(DataQualityRule, on_delete=models.CASCADE)
    
    # Check results
    records_checked = models.BigIntegerField(default=0)
    records_passed = models.BigIntegerField(default=0)
    records_failed = models.BigIntegerField(default=0)
    pass_rate = models.FloatField(default=0.0)  # Percentage
    
    # Violation details
    violation_count = models.IntegerField(default=0)
    violation_examples = models.JSONField(default=list)  # Sample violations
    violation_summary = models.JSONField(default=dict)
    
    # Actions taken
    action_taken = models.CharField(max_length=30, blank=True)
    records_fixed = models.BigIntegerField(default=0)
    records_rejected = models.BigIntegerField(default=0)
    
    # Timing
    check_duration_seconds = models.FloatField(default=0)
    checked_at = models.DateTimeField(auto_now_add=True)

class DataLineage(models.Model):
    """Data lineage tracking for governance and debugging"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Lineage identification
    source_dataset = models.CharField(max_length=200)
    target_dataset = models.CharField(max_length=200)
    transformation_type = models.CharField(max_length=50)
    
    # Lineage details
    pipeline_execution = models.ForeignKey(PipelineExecution, on_delete=models.CASCADE, related_name='lineage_records')
    transformation_logic = models.TextField(blank=True)
    transformation_parameters = models.JSONField(default=dict)
    
    # Data flow
    source_fields = models.JSONField(default=list)
    target_fields = models.JSONField(default=list)
    field_mappings = models.JSONField(default=dict)
    
    # Impact tracking
    records_affected = models.BigIntegerField(default=0)
    data_volume_mb = models.FloatField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

class DataCatalog(models.Model):
    """Data catalog for data discovery and governance"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Dataset identification
    dataset_name = models.CharField(max_length=200, unique=True)
    display_name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # Dataset characteristics
    dataset_type = models.CharField(max_length=30)  # table, view, stream, file, etc.
    data_format = models.CharField(max_length=30)
    schema_definition = models.JSONField(default=dict)
    
    # Business context
    business_domain = models.CharField(max_length=50, blank=True)
    business_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_datasets')
    technical_owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_datasets')
    
    # Data characteristics
    record_count = models.BigIntegerField(default=0)
    size_mb = models.FloatField(default=0)
    update_frequency = models.CharField(max_length=20, blank=True)
    last_updated = models.DateTimeField(null=True, blank=True)
    
    # Quality and usage
    quality_score = models.FloatField(default=0.0)
    usage_count = models.IntegerField(default=0)  # How many pipelines use this
    popularity_score = models.FloatField(default=0.0)
    
    # Governance
    classification = models.CharField(max_length=20, default='internal')  # public, internal, confidential, restricted
    retention_policy = models.CharField(max_length=100, blank=True)
    compliance_tags = models.JSONField(default=list)
    
    # Discovery metadata
    tags = models.JSONField(default=list)
    keywords = models.JSONField(default=list)
    related_datasets = models.JSONField(default=list)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_deprecated = models.BooleanField(default=False)
    deprecation_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['business_domain', 'is_active']),
            models.Index(fields=['quality_score', 'popularity_score']),
        ]

class DataProfile(models.Model):
    """Data profiling results for understanding data characteristics"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Profile identification
    dataset = models.ForeignKey(DataCatalog, on_delete=models.CASCADE, related_name='profiles')
    field_name = models.CharField(max_length=100)
    
    # Basic statistics
    total_records = models.BigIntegerField(default=0)
    non_null_records = models.BigIntegerField(default=0)
    null_records = models.BigIntegerField(default=0)
    null_percentage = models.FloatField(default=0.0)
    
    # Data type information
    inferred_data_type = models.CharField(max_length=30)
    data_type_confidence = models.FloatField(default=0.0)
    
    # Value statistics
    unique_values = models.BigIntegerField(default=0)
    duplicate_values = models.BigIntegerField(default=0)
    most_frequent_values = models.JSONField(default=list)
    value_distribution = models.JSONField(default=dict)
    
    # Numeric statistics (if applicable)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    mean_value = models.FloatField(null=True, blank=True)
    median_value = models.FloatField(null=True, blank=True)
    std_deviation = models.FloatField(null=True, blank=True)
    
    # String statistics (if applicable)
    min_length = models.IntegerField(null=True, blank=True)
    max_length = models.IntegerField(null=True, blank=True)
    avg_length = models.FloatField(null=True, blank=True)
    
    # Pattern analysis
    common_patterns = models.JSONField(default=list)
    format_compliance = models.JSONField(default=dict)
    
    # Quality indicators
    completeness_score = models.FloatField(default=0.0)
    consistency_score = models.FloatField(default=0.0)
    validity_score = models.FloatField(default=0.0)
    
    # Profiling metadata
    profiling_date = models.DateTimeField(auto_now_add=True)
    profiling_duration_seconds = models.FloatField(default=0)
    sample_size = models.BigIntegerField(default=0)
    
    class Meta:
        unique_together = ['dataset', 'field_name', 'profiling_date']
        indexes = [
            models.Index(fields=['dataset', 'profiling_date']),
        ]

class DataAlert(models.Model):
    """Data pipeline and quality alerts"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Alert identification
    alert_type = models.CharField(max_length=30)  # pipeline_failure, quality_issue, performance, etc.
    severity = models.CharField(max_length=20)  # info, warning, error, critical
    
    # Alert details
    title = models.CharField(max_length=200)
    description = models.TextField()
    alert_data = models.JSONField(default=dict)
    
    # Related objects
    pipeline = models.ForeignKey(DataPipeline, on_delete=models.CASCADE, null=True, blank=True)
    execution = models.ForeignKey(PipelineExecution, on_delete=models.CASCADE, null=True, blank=True)
    data_source = models.ForeignKey(DataSource, on_delete=models.CASCADE, null=True, blank=True)
    
    # Status and resolution
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('acknowledged', 'Acknowledged'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    
    # Assignment and resolution
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Notification tracking
    notification_sent = models.BooleanField(default=False)
    notification_recipients = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['alert_type', 'severity', 'status']),
            models.Index(fields=['created_at', 'status']),
        ]
