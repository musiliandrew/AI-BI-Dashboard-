"""
Machine Learning Engine Models
Comprehensive ML/AI infrastructure for business intelligence
"""
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.postgres.fields import JSONField, ArrayField
import json
from enum import Enum

class MLModelType(models.TextChoices):
    """Types of ML models supported"""
    # Predictive Models
    REVENUE_FORECASTING = 'revenue_forecasting', 'Revenue Forecasting'
    CUSTOMER_LIFETIME_VALUE = 'customer_ltv', 'Customer Lifetime Value'
    CHURN_PREDICTION = 'churn_prediction', 'Churn Prediction'
    DEMAND_FORECASTING = 'demand_forecasting', 'Demand Forecasting'
    PRICE_OPTIMIZATION = 'price_optimization', 'Price Optimization'
    
    # Classification Models
    CUSTOMER_SEGMENTATION = 'customer_segmentation', 'Customer Segmentation'
    SENTIMENT_ANALYSIS = 'sentiment_analysis', 'Sentiment Analysis'
    FRAUD_DETECTION = 'fraud_detection', 'Fraud Detection'
    LEAD_SCORING = 'lead_scoring', 'Lead Scoring'
    CONTENT_CLASSIFICATION = 'content_classification', 'Content Classification'
    
    # Anomaly Detection
    PERFORMANCE_ANOMALY = 'performance_anomaly', 'Performance Anomaly Detection'
    TRAFFIC_ANOMALY = 'traffic_anomaly', 'Traffic Anomaly Detection'
    FINANCIAL_ANOMALY = 'financial_anomaly', 'Financial Anomaly Detection'
    
    # Recommendation Systems
    PRODUCT_RECOMMENDATION = 'product_recommendation', 'Product Recommendation'
    CONTENT_RECOMMENDATION = 'content_recommendation', 'Content Recommendation'
    CROSS_SELL_UPSELL = 'cross_sell_upsell', 'Cross-sell/Upsell'
    
    # Time Series Analysis
    SEASONAL_ANALYSIS = 'seasonal_analysis', 'Seasonal Analysis'
    TREND_ANALYSIS = 'trend_analysis', 'Trend Analysis'
    CYCLICAL_ANALYSIS = 'cyclical_analysis', 'Cyclical Analysis'
    
    # Custom Models
    CUSTOM_REGRESSION = 'custom_regression', 'Custom Regression'
    CUSTOM_CLASSIFICATION = 'custom_classification', 'Custom Classification'
    CUSTOM_CLUSTERING = 'custom_clustering', 'Custom Clustering'

class IndustryType(models.TextChoices):
    """Industry-specific model configurations"""
    AUTOMOTIVE = 'automotive', 'Automotive'
    RESTAURANT = 'restaurant', 'Restaurant'
    RETAIL = 'retail', 'Retail'
    HEALTHCARE = 'healthcare', 'Healthcare'
    REAL_ESTATE = 'real_estate', 'Real Estate'
    LEGAL = 'legal', 'Legal'
    FINANCE = 'finance', 'Finance'
    EDUCATION = 'education', 'Education'
    TECHNOLOGY = 'technology', 'Technology'
    GENERAL = 'general', 'General'

class MLModel(models.Model):
    """Machine Learning Model Configuration and Metadata"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Model identification
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=50, choices=MLModelType.choices)
    industry = models.CharField(max_length=50, choices=IndustryType.choices, default=IndustryType.GENERAL)
    version = models.CharField(max_length=20, default='1.0.0')
    
    # Model configuration
    algorithm = models.CharField(max_length=100)  # RandomForest, XGBoost, LSTM, etc.
    hyperparameters = models.JSONField(default=dict)
    feature_config = models.JSONField(default=dict)
    target_variable = models.CharField(max_length=100, blank=True)
    
    # Data requirements
    required_data_sources = models.JSONField(default=list)  # ['social_media', 'payments', 'website']
    minimum_data_points = models.IntegerField(default=100)
    training_window_days = models.IntegerField(default=90)
    
    # Model performance
    accuracy_score = models.FloatField(null=True, blank=True)
    precision_score = models.FloatField(null=True, blank=True)
    recall_score = models.FloatField(null=True, blank=True)
    f1_score = models.FloatField(null=True, blank=True)
    mae = models.FloatField(null=True, blank=True)  # Mean Absolute Error
    rmse = models.FloatField(null=True, blank=True)  # Root Mean Square Error
    r2_score = models.FloatField(null=True, blank=True)  # R-squared
    
    # Model lifecycle
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('training', 'Training'),
        ('trained', 'Trained'),
        ('deployed', 'Deployed'),
        ('retraining', 'Retraining'),
        ('deprecated', 'Deprecated'),
        ('failed', 'Failed'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Training metadata
    last_trained_at = models.DateTimeField(null=True, blank=True)
    training_duration_seconds = models.FloatField(null=True, blank=True)
    training_data_size = models.IntegerField(default=0)
    
    # Deployment metadata
    deployed_at = models.DateTimeField(null=True, blank=True)
    prediction_count = models.IntegerField(default=0)
    last_prediction_at = models.DateTimeField(null=True, blank=True)
    
    # Auto-retraining configuration
    auto_retrain_enabled = models.BooleanField(default=True)
    retrain_frequency_days = models.IntegerField(default=7)
    performance_threshold = models.FloatField(default=0.8)  # Retrain if performance drops below
    
    # Ownership and access
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ml_models')
    is_template = models.BooleanField(default=False)  # Template models for industries
    is_public = models.BooleanField(default=False)  # Available to all users
    
    # Metadata
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['model_type', 'industry']),
            models.Index(fields=['status', 'last_trained_at']),
            models.Index(fields=['is_template', 'is_public']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.model_type})"

class MLTrainingJob(models.Model):
    """ML Model Training Job Tracking"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Job identification
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='training_jobs')
    job_id = models.CharField(max_length=100, unique=True)
    
    # Training configuration
    training_config = models.JSONField(default=dict)
    data_sources = models.JSONField(default=list)
    feature_selection = models.JSONField(default=list)
    
    # Job status
    STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('preparing_data', 'Preparing Data'),
        ('feature_engineering', 'Feature Engineering'),
        ('training', 'Training'),
        ('validating', 'Validating'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    
    # Execution details
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Data metrics
    total_records = models.IntegerField(default=0)
    training_records = models.IntegerField(default=0)
    validation_records = models.IntegerField(default=0)
    test_records = models.IntegerField(default=0)
    
    # Performance results
    training_metrics = models.JSONField(default=dict)
    validation_metrics = models.JSONField(default=dict)
    test_metrics = models.JSONField(default=dict)
    
    # Resource usage
    cpu_hours = models.FloatField(null=True, blank=True)
    memory_gb_hours = models.FloatField(null=True, blank=True)
    gpu_hours = models.FloatField(null=True, blank=True)
    
    # Error handling
    error_message = models.TextField(blank=True)
    error_details = models.JSONField(default=dict)
    
    # Model artifacts
    model_file_path = models.CharField(max_length=500, blank=True)
    feature_importance = models.JSONField(default=dict)
    model_size_mb = models.FloatField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['model', 'started_at']),
            models.Index(fields=['status', 'started_at']),
        ]

class MLPrediction(models.Model):
    """ML Model Predictions and Results"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Prediction identification
    model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='predictions')
    prediction_id = models.CharField(max_length=100, unique=True)
    
    # Input data
    input_data = models.JSONField(default=dict)
    input_features = models.JSONField(default=dict)
    data_source_ids = models.JSONField(default=list)  # Source data references
    
    # Prediction results
    prediction_value = models.JSONField(default=dict)  # Can be number, category, or complex object
    confidence_score = models.FloatField(null=True, blank=True)
    prediction_probabilities = models.JSONField(default=dict)  # For classification
    
    # Prediction metadata
    prediction_type = models.CharField(max_length=50)  # point, interval, distribution
    prediction_horizon = models.CharField(max_length=50, blank=True)  # 1d, 7d, 30d, etc.
    
    # Model version used
    model_version = models.CharField(max_length=20)
    model_training_job = models.ForeignKey(MLTrainingJob, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Execution details
    processing_time_ms = models.FloatField(null=True, blank=True)
    prediction_date = models.DateTimeField(auto_now_add=True)
    
    # Validation and feedback
    actual_value = models.JSONField(null=True, blank=True)  # For model performance tracking
    prediction_error = models.FloatField(null=True, blank=True)
    feedback_score = models.FloatField(null=True, blank=True)  # User feedback on prediction quality
    
    # Business context
    business_impact = models.CharField(max_length=100, blank=True)  # high, medium, low
    action_taken = models.TextField(blank=True)  # What action was taken based on prediction
    
    class Meta:
        indexes = [
            models.Index(fields=['model', 'prediction_date']),
            models.Index(fields=['prediction_type', 'prediction_date']),
        ]

class MLFeature(models.Model):
    """Feature definitions and engineering"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Feature identification
    name = models.CharField(max_length=200)
    feature_type = models.CharField(max_length=50)  # numerical, categorical, text, datetime
    data_type = models.CharField(max_length=50)  # int, float, string, boolean
    
    # Feature source
    source_table = models.CharField(max_length=100)
    source_column = models.CharField(max_length=100)
    transformation_logic = models.TextField(blank=True)  # SQL or Python code
    
    # Feature engineering
    engineering_type = models.CharField(max_length=50, blank=True)  # aggregation, encoding, scaling
    aggregation_window = models.CharField(max_length=50, blank=True)  # 1d, 7d, 30d
    aggregation_function = models.CharField(max_length=50, blank=True)  # sum, avg, count, max, min
    
    # Feature statistics
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    mean_value = models.FloatField(null=True, blank=True)
    std_value = models.FloatField(null=True, blank=True)
    null_percentage = models.FloatField(null=True, blank=True)
    
    # Feature importance
    importance_score = models.FloatField(null=True, blank=True)
    correlation_with_target = models.FloatField(null=True, blank=True)
    
    # Feature lifecycle
    is_active = models.BooleanField(default=True)
    last_computed_at = models.DateTimeField(null=True, blank=True)
    computation_frequency = models.CharField(max_length=20, default='daily')
    
    # Ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ml_features')
    
    # Metadata
    description = models.TextField(blank=True)
    tags = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'owner']
        indexes = [
            models.Index(fields=['feature_type', 'is_active']),
            models.Index(fields=['importance_score']),
        ]

class MLExperiment(models.Model):
    """ML Experimentation and A/B Testing"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Experiment identification
    name = models.CharField(max_length=200)
    experiment_type = models.CharField(max_length=50)  # model_comparison, feature_selection, hyperparameter_tuning
    
    # Experiment configuration
    models_to_compare = models.JSONField(default=list)  # List of model IDs
    experiment_config = models.JSONField(default=dict)
    success_metrics = models.JSONField(default=list)  # ['accuracy', 'precision', 'business_impact']
    
    # Experiment status
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Execution details
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.FloatField(null=True, blank=True)
    
    # Results
    experiment_results = models.JSONField(default=dict)
    winning_model = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_experiments')
    statistical_significance = models.FloatField(null=True, blank=True)
    
    # Business impact
    expected_improvement = models.FloatField(null=True, blank=True)
    actual_improvement = models.FloatField(null=True, blank=True)
    business_value_estimate = models.FloatField(null=True, blank=True)
    
    # Ownership
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ml_experiments')
    
    # Metadata
    description = models.TextField(blank=True)
    hypothesis = models.TextField(blank=True)
    conclusions = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class MLModelTemplate(models.Model):
    """Pre-built model templates for different industries and use cases"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Template identification
    name = models.CharField(max_length=200)
    model_type = models.CharField(max_length=50, choices=MLModelType.choices)
    industry = models.CharField(max_length=50, choices=IndustryType.choices)
    
    # Template configuration
    default_algorithm = models.CharField(max_length=100)
    default_hyperparameters = models.JSONField(default=dict)
    required_features = models.JSONField(default=list)
    optional_features = models.JSONField(default=list)
    
    # Performance benchmarks
    expected_accuracy = models.FloatField(null=True, blank=True)
    minimum_data_requirements = models.IntegerField(default=100)
    typical_training_time_hours = models.FloatField(null=True, blank=True)
    
    # Business context
    use_case_description = models.TextField()
    business_value_proposition = models.TextField()
    success_stories = models.JSONField(default=list)
    
    # Template metadata
    difficulty_level = models.CharField(max_length=20, default='intermediate')  # beginner, intermediate, advanced
    popularity_score = models.FloatField(default=0.0)
    usage_count = models.IntegerField(default=0)
    
    # Versioning
    version = models.CharField(max_length=20, default='1.0.0')
    is_active = models.BooleanField(default=True)
    
    # Ownership
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_templates')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['name', 'industry', 'version']
        indexes = [
            models.Index(fields=['industry', 'model_type']),
            models.Index(fields=['popularity_score', 'is_active']),
        ]

class MLInsight(models.Model):
    """AI-generated insights from ML models"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Insight identification
    title = models.CharField(max_length=200)
    insight_type = models.CharField(max_length=50)  # prediction, anomaly, trend, recommendation
    
    # Source information
    source_model = models.ForeignKey(MLModel, on_delete=models.CASCADE, related_name='insights')
    source_prediction = models.ForeignKey(MLPrediction, on_delete=models.SET_NULL, null=True, blank=True)
    data_sources = models.JSONField(default=list)
    
    # Insight content
    description = models.TextField()
    key_findings = models.JSONField(default=list)
    supporting_data = models.JSONField(default=dict)
    confidence_level = models.FloatField()  # 0-1
    
    # Business impact
    impact_level = models.CharField(max_length=20)  # critical, high, medium, low
    potential_value = models.FloatField(null=True, blank=True)  # Estimated business value
    recommended_actions = models.JSONField(default=list)
    
    # Insight lifecycle
    STATUS_CHOICES = [
        ('new', 'New'),
        ('reviewed', 'Reviewed'),
        ('acted_upon', 'Acted Upon'),
        ('dismissed', 'Dismissed'),
        ('expired', 'Expired'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    
    # User interaction
    viewed_by = models.ManyToManyField(User, related_name='viewed_insights', blank=True)
    feedback_score = models.FloatField(null=True, blank=True)  # User feedback on insight quality
    action_taken = models.TextField(blank=True)
    
    # Timing
    insight_date = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['insight_type', 'impact_level']),
            models.Index(fields=['status', 'insight_date']),
        ]
