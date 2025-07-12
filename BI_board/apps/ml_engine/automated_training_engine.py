"""
Automated Model Training Engine
Automatically trains industry-specific ML models using user data with continuous learning
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
from enum import Enum

logger = logging.getLogger(__name__)

class TrainingStatus(Enum):
    PENDING = "pending"
    TRAINING = "training"
    COMPLETED = "completed"
    FAILED = "failed"
    EVALUATING = "evaluating"

class ModelType(Enum):
    REVENUE_FORECASTING = "revenue_forecasting"
    CUSTOMER_SEGMENTATION = "customer_segmentation"
    CHURN_PREDICTION = "churn_prediction"
    DEMAND_FORECASTING = "demand_forecasting"
    PRICE_OPTIMIZATION = "price_optimization"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    ANOMALY_DETECTION = "anomaly_detection"

@dataclass
class TrainingConfig:
    """Configuration for automated model training"""
    user_id: str
    industry: str
    model_type: ModelType
    data_sources: List[str]
    target_metric: str
    training_features: List[str]
    validation_split: float = 0.2
    max_training_time: int = 3600  # seconds
    min_data_points: int = 100
    performance_threshold: float = 0.7
    auto_deploy: bool = True
    retrain_frequency: str = "weekly"  # daily, weekly, monthly

@dataclass
class TrainingResult:
    """Result of automated model training"""
    training_id: str
    user_id: str
    model_type: ModelType
    status: TrainingStatus
    performance_metrics: Dict[str, float]
    model_path: Optional[str] = None
    training_duration: float = 0.0
    data_quality_score: float = 0.0
    feature_importance: Dict[str, float] = field(default_factory=dict)
    validation_results: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

@dataclass
class IndustryModelTemplate:
    """Pre-configured model template for specific industry"""
    industry: str
    model_type: ModelType
    default_features: List[str]
    feature_engineering_rules: Dict[str, Any]
    hyperparameters: Dict[str, Any]
    performance_benchmarks: Dict[str, float]
    business_context: Dict[str, Any]

class AutomatedTrainingEngine:
    """Engine for automated ML model training and optimization"""
    
    def __init__(self):
        self.training_queue = asyncio.Queue()
        self.active_trainings = {}  # training_id -> TrainingResult
        self.user_models = {}       # user_id -> {model_type: model_info}
        self.industry_templates = self._load_industry_templates()
        
        # Training statistics
        self.training_stats = {
            'total_trainings': 0,
            'successful_trainings': 0,
            'failed_trainings': 0,
            'average_training_time': 0.0,
            'best_performances': {}  # model_type -> best_score
        }
    
    def _load_industry_templates(self) -> Dict[str, Dict[ModelType, IndustryModelTemplate]]:
        """Load pre-configured industry model templates"""
        
        templates = {}
        
        # Automotive Industry Templates
        templates['automotive'] = {
            ModelType.REVENUE_FORECASTING: IndustryModelTemplate(
                industry='automotive',
                model_type=ModelType.REVENUE_FORECASTING,
                default_features=[
                    'vehicle_sales_count', 'average_vehicle_price', 'service_revenue',
                    'parts_revenue', 'financing_revenue', 'seasonal_factor',
                    'economic_indicator', 'inventory_level', 'marketing_spend'
                ],
                feature_engineering_rules={
                    'seasonal_features': ['month', 'quarter', 'is_holiday'],
                    'lag_features': ['sales_lag_1', 'sales_lag_7', 'sales_lag_30'],
                    'rolling_features': ['sales_7d_avg', 'sales_30d_avg'],
                    'interaction_features': ['price_x_marketing', 'inventory_x_demand']
                },
                hyperparameters={
                    'n_estimators': 100,
                    'max_depth': 10,
                    'learning_rate': 0.1,
                    'random_state': 42
                },
                performance_benchmarks={
                    'mape': 0.15,  # Mean Absolute Percentage Error
                    'r2_score': 0.85,
                    'rmse_normalized': 0.12
                },
                business_context={
                    'key_metrics': ['vehicle_sales', 'service_revenue', 'customer_satisfaction'],
                    'seasonality': 'high',
                    'forecast_horizon': 90,  # days
                    'business_cycles': ['monthly', 'quarterly', 'yearly']
                }
            ),
            
            ModelType.CUSTOMER_SEGMENTATION: IndustryModelTemplate(
                industry='automotive',
                model_type=ModelType.CUSTOMER_SEGMENTATION,
                default_features=[
                    'purchase_frequency', 'average_order_value', 'service_visits',
                    'vehicle_age', 'customer_age', 'income_level', 'location',
                    'financing_used', 'warranty_purchases', 'referral_count'
                ],
                feature_engineering_rules={
                    'rfm_features': ['recency', 'frequency', 'monetary'],
                    'behavioral_features': ['service_preference', 'payment_method'],
                    'demographic_features': ['age_group', 'income_bracket'],
                    'interaction_features': ['frequency_x_value', 'age_x_income']
                },
                hyperparameters={
                    'n_clusters': 5,
                    'algorithm': 'kmeans',
                    'random_state': 42
                },
                performance_benchmarks={
                    'silhouette_score': 0.6,
                    'calinski_harabasz_score': 100,
                    'davies_bouldin_score': 1.0
                },
                business_context={
                    'segments': ['VIP', 'Regular', 'Service-Only', 'Price-Sensitive', 'New'],
                    'key_behaviors': ['purchase_patterns', 'service_usage', 'loyalty'],
                    'business_value': 'customer_lifetime_value'
                }
            )
        }
        
        # Restaurant Industry Templates
        templates['restaurant'] = {
            ModelType.DEMAND_FORECASTING: IndustryModelTemplate(
                industry='restaurant',
                model_type=ModelType.DEMAND_FORECASTING,
                default_features=[
                    'historical_customers', 'day_of_week', 'hour_of_day', 'weather_temp',
                    'weather_condition', 'local_events', 'promotions', 'menu_changes',
                    'staff_count', 'table_capacity', 'delivery_orders'
                ],
                feature_engineering_rules={
                    'time_features': ['hour', 'day_of_week', 'month', 'is_weekend'],
                    'weather_features': ['temp_category', 'weather_score'],
                    'lag_features': ['customers_lag_1', 'customers_lag_7'],
                    'rolling_features': ['customers_7d_avg', 'customers_30d_avg']
                },
                hyperparameters={
                    'n_estimators': 150,
                    'max_depth': 8,
                    'learning_rate': 0.05,
                    'random_state': 42
                },
                performance_benchmarks={
                    'mape': 0.20,
                    'r2_score': 0.80,
                    'mae_normalized': 0.15
                },
                business_context={
                    'key_metrics': ['daily_customers', 'revenue_per_customer', 'table_turnover'],
                    'seasonality': 'medium',
                    'forecast_horizon': 14,  # days
                    'peak_periods': ['lunch', 'dinner', 'weekend']
                }
            ),
            
            ModelType.PRICE_OPTIMIZATION: IndustryModelTemplate(
                industry='restaurant',
                model_type=ModelType.PRICE_OPTIMIZATION,
                default_features=[
                    'item_category', 'ingredient_cost', 'preparation_time', 'popularity_score',
                    'competitor_prices', 'demand_elasticity', 'profit_margin',
                    'customer_segment', 'time_of_day', 'seasonal_demand'
                ],
                feature_engineering_rules={
                    'cost_features': ['cost_ratio', 'margin_percentage'],
                    'demand_features': ['elasticity_score', 'popularity_rank'],
                    'competitive_features': ['price_vs_competitor', 'market_position'],
                    'interaction_features': ['cost_x_demand', 'time_x_popularity']
                },
                hyperparameters={
                    'n_estimators': 200,
                    'max_depth': 12,
                    'learning_rate': 0.08,
                    'random_state': 42
                },
                performance_benchmarks={
                    'profit_improvement': 0.15,  # 15% profit increase
                    'demand_retention': 0.90,    # 90% demand retention
                    'price_accuracy': 0.85
                },
                business_context={
                    'optimization_goal': 'profit_maximization',
                    'constraints': ['min_margin', 'max_price_increase'],
                    'business_rules': ['happy_hour_discounts', 'premium_items']
                }
            )
        }
        
        # Retail Industry Templates
        templates['retail'] = {
            ModelType.CUSTOMER_SEGMENTATION: IndustryModelTemplate(
                industry='retail',
                model_type=ModelType.CUSTOMER_SEGMENTATION,
                default_features=[
                    'purchase_frequency', 'average_order_value', 'total_spent',
                    'product_categories', 'brand_preferences', 'channel_preference',
                    'return_rate', 'review_scores', 'loyalty_program', 'geographic_location'
                ],
                feature_engineering_rules={
                    'rfm_features': ['recency', 'frequency', 'monetary'],
                    'behavioral_features': ['category_diversity', 'brand_loyalty'],
                    'engagement_features': ['review_activity', 'social_engagement'],
                    'value_features': ['clv_score', 'profit_contribution']
                },
                hyperparameters={
                    'n_clusters': 6,
                    'algorithm': 'kmeans',
                    'random_state': 42
                },
                performance_benchmarks={
                    'silhouette_score': 0.65,
                    'business_value_score': 0.80,
                    'segment_stability': 0.85
                },
                business_context={
                    'segments': ['Champions', 'Loyal', 'Potential', 'New', 'At-Risk', 'Lost'],
                    'key_behaviors': ['shopping_patterns', 'brand_loyalty', 'price_sensitivity'],
                    'business_applications': ['targeted_marketing', 'inventory_planning', 'pricing']
                }
            ),
            
            ModelType.CHURN_PREDICTION: IndustryModelTemplate(
                industry='retail',
                model_type=ModelType.CHURN_PREDICTION,
                default_features=[
                    'days_since_last_purchase', 'purchase_frequency_decline', 'order_value_trend',
                    'support_tickets', 'return_frequency', 'engagement_score',
                    'competitor_activity', 'satisfaction_scores', 'payment_issues'
                ],
                feature_engineering_rules={
                    'trend_features': ['purchase_trend', 'value_trend', 'engagement_trend'],
                    'behavioral_features': ['activity_decline', 'pattern_changes'],
                    'interaction_features': ['support_x_satisfaction', 'returns_x_value'],
                    'risk_features': ['churn_risk_score', 'loyalty_score']
                },
                hyperparameters={
                    'n_estimators': 100,
                    'max_depth': 8,
                    'class_weight': 'balanced',
                    'random_state': 42
                },
                performance_benchmarks={
                    'precision': 0.75,
                    'recall': 0.80,
                    'f1_score': 0.77,
                    'auc_roc': 0.85
                },
                business_context={
                    'prediction_horizon': 30,  # days
                    'intervention_strategies': ['discount_offers', 'personal_outreach', 'loyalty_rewards'],
                    'business_impact': 'customer_retention_value'
                }
            )
        }
        
        return templates
    
    async def start_automated_training(self, config: TrainingConfig) -> str:
        """Start automated model training for a user"""
        
        training_id = f"train_{config.user_id}_{config.model_type.value}_{int(datetime.now().timestamp())}"
        
        # Create training result object
        training_result = TrainingResult(
            training_id=training_id,
            user_id=config.user_id,
            model_type=config.model_type,
            status=TrainingStatus.PENDING
        )
        
        # Add to active trainings
        self.active_trainings[training_id] = training_result
        
        # Add to training queue
        await self.training_queue.put((training_id, config))
        
        logger.info(f"Started automated training {training_id} for user {config.user_id}")
        
        return training_id
    
    async def process_training_queue(self):
        """Process training queue continuously"""
        
        while True:
            try:
                # Get next training job
                training_id, config = await self.training_queue.get()
                
                # Process training
                await self._execute_training(training_id, config)
                
                # Mark task as done
                self.training_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing training queue: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _execute_training(self, training_id: str, config: TrainingConfig):
        """Execute the actual model training"""
        
        training_result = self.active_trainings[training_id]
        start_time = datetime.now()
        
        try:
            # Update status
            training_result.status = TrainingStatus.TRAINING
            
            # Step 1: Data collection and validation
            logger.info(f"Collecting data for training {training_id}")
            training_data = await self._collect_training_data(config)
            
            if training_data is None or len(training_data) < config.min_data_points:
                raise ValueError(f"Insufficient data: {len(training_data) if training_data is not None else 0} < {config.min_data_points}")
            
            # Step 2: Data quality assessment
            data_quality_score = self._assess_data_quality(training_data, config)
            training_result.data_quality_score = data_quality_score
            
            if data_quality_score < 0.6:
                raise ValueError(f"Data quality too low: {data_quality_score}")
            
            # Step 3: Feature engineering
            logger.info(f"Engineering features for training {training_id}")
            engineered_data = await self._engineer_features(training_data, config)
            
            # Step 4: Model training
            logger.info(f"Training model for training {training_id}")
            model, performance_metrics = await self._train_model(engineered_data, config)
            
            # Step 5: Model validation
            training_result.status = TrainingStatus.EVALUATING
            validation_results = await self._validate_model(model, engineered_data, config)
            
            # Step 6: Performance evaluation
            if performance_metrics.get('primary_metric', 0) < config.performance_threshold:
                raise ValueError(f"Model performance below threshold: {performance_metrics.get('primary_metric', 0)} < {config.performance_threshold}")
            
            # Step 7: Model deployment (if auto_deploy is enabled)
            model_path = None
            if config.auto_deploy:
                model_path = await self._deploy_model(model, config, training_id)
            
            # Update training result
            training_result.status = TrainingStatus.COMPLETED
            training_result.performance_metrics = performance_metrics
            training_result.model_path = model_path
            training_result.validation_results = validation_results
            training_result.completed_at = datetime.now()
            training_result.training_duration = (training_result.completed_at - start_time).total_seconds()
            
            # Update user models
            if config.user_id not in self.user_models:
                self.user_models[config.user_id] = {}
            
            self.user_models[config.user_id][config.model_type] = {
                'training_id': training_id,
                'model_path': model_path,
                'performance': performance_metrics,
                'created_at': training_result.completed_at,
                'industry': config.industry
            }
            
            # Update statistics
            self._update_training_stats(training_result, success=True)
            
            logger.info(f"Training {training_id} completed successfully in {training_result.training_duration:.2f} seconds")
            
        except Exception as e:
            # Handle training failure
            training_result.status = TrainingStatus.FAILED
            training_result.error_message = str(e)
            training_result.completed_at = datetime.now()
            training_result.training_duration = (training_result.completed_at - start_time).total_seconds()
            
            self._update_training_stats(training_result, success=False)
            
            logger.error(f"Training {training_id} failed: {e}")
    
    async def _collect_training_data(self, config: TrainingConfig) -> Optional[pd.DataFrame]:
        """Collect and prepare training data"""
        
        try:
            # TODO: Implement actual data collection from user's data sources
            # For now, create sample data based on industry and model type
            
            if config.industry == 'automotive' and config.model_type == ModelType.REVENUE_FORECASTING:
                return self._create_automotive_revenue_data()
            elif config.industry == 'restaurant' and config.model_type == ModelType.DEMAND_FORECASTING:
                return self._create_restaurant_demand_data()
            elif config.industry == 'retail' and config.model_type == ModelType.CUSTOMER_SEGMENTATION:
                return self._create_retail_customer_data()
            else:
                # Generic business data
                return self._create_generic_business_data()
                
        except Exception as e:
            logger.error(f"Error collecting training data: {e}")
            return None

    def _assess_data_quality(self, data: pd.DataFrame, config: TrainingConfig) -> float:
        """Assess the quality of training data"""

        quality_score = 1.0

        # Check for missing values
        missing_ratio = data.isnull().sum().sum() / (len(data) * len(data.columns))
        quality_score -= missing_ratio * 0.3

        # Check data volume
        if len(data) < config.min_data_points * 2:
            quality_score -= 0.2

        # Check feature availability
        available_features = set(data.columns)
        required_features = set(config.training_features)
        missing_features = required_features - available_features

        if missing_features:
            quality_score -= len(missing_features) / len(required_features) * 0.3

        # Check target variable quality
        if config.target_metric in data.columns:
            target_missing = data[config.target_metric].isnull().sum() / len(data)
            quality_score -= target_missing * 0.4

        return max(0.0, quality_score)

    async def _engineer_features(self, data: pd.DataFrame, config: TrainingConfig) -> pd.DataFrame:
        """Engineer features based on industry template"""

        # Get industry template
        template = self.industry_templates.get(config.industry, {}).get(config.model_type)

        if not template:
            return data  # Return original data if no template

        engineered_data = data.copy()

        # Apply feature engineering rules
        rules = template.feature_engineering_rules

        # Time-based features
        if 'time_features' in rules and 'date' in engineered_data.columns:
            engineered_data['hour'] = pd.to_datetime(engineered_data['date']).dt.hour
            engineered_data['day_of_week'] = pd.to_datetime(engineered_data['date']).dt.dayofweek
            engineered_data['month'] = pd.to_datetime(engineered_data['date']).dt.month
            engineered_data['is_weekend'] = engineered_data['day_of_week'].isin([5, 6]).astype(int)

        # Lag features
        if 'lag_features' in rules and config.target_metric in engineered_data.columns:
            for lag in [1, 7, 30]:
                if f'{config.target_metric}_lag_{lag}' in rules['lag_features']:
                    engineered_data[f'{config.target_metric}_lag_{lag}'] = engineered_data[config.target_metric].shift(lag)

        # Rolling features
        if 'rolling_features' in rules and config.target_metric in engineered_data.columns:
            for window in [7, 30]:
                if f'{config.target_metric}_{window}d_avg' in rules['rolling_features']:
                    engineered_data[f'{config.target_metric}_{window}d_avg'] = engineered_data[config.target_metric].rolling(window=window).mean()

        # Remove rows with NaN values created by feature engineering
        engineered_data = engineered_data.dropna()

        return engineered_data

    async def _train_model(self, data: pd.DataFrame, config: TrainingConfig) -> Tuple[Any, Dict[str, float]]:
        """Train the ML model"""

        try:
            # Import ML libraries
            from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
            from sklearn.cluster import KMeans
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, silhouette_score

            # Get industry template for hyperparameters
            template = self.industry_templates.get(config.industry, {}).get(config.model_type)
            hyperparams = template.hyperparameters if template else {}

            # Prepare features and target
            feature_cols = [col for col in config.training_features if col in data.columns]
            X = data[feature_cols]

            performance_metrics = {}

            if config.model_type in [ModelType.REVENUE_FORECASTING, ModelType.DEMAND_FORECASTING, ModelType.PRICE_OPTIMIZATION]:
                # Regression models
                y = data[config.target_metric]
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=config.validation_split, random_state=42)

                model = RandomForestRegressor(**hyperparams)
                model.fit(X_train, y_train)

                # Evaluate
                y_pred = model.predict(X_test)
                performance_metrics = {
                    'r2_score': r2_score(y_test, y_pred),
                    'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
                    'mape': np.mean(np.abs((y_test - y_pred) / y_test)) * 100,
                    'primary_metric': r2_score(y_test, y_pred)
                }

            elif config.model_type == ModelType.CHURN_PREDICTION:
                # Classification model
                y = data[config.target_metric]
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=config.validation_split, random_state=42)

                model = RandomForestClassifier(**hyperparams)
                model.fit(X_train, y_train)

                # Evaluate
                y_pred = model.predict(X_test)
                performance_metrics = {
                    'accuracy': accuracy_score(y_test, y_pred),
                    'primary_metric': accuracy_score(y_test, y_pred)
                }

            elif config.model_type == ModelType.CUSTOMER_SEGMENTATION:
                # Clustering model
                model = KMeans(**hyperparams)
                clusters = model.fit_predict(X)

                # Evaluate
                silhouette_avg = silhouette_score(X, clusters)
                performance_metrics = {
                    'silhouette_score': silhouette_avg,
                    'n_clusters': hyperparams.get('n_clusters', 5),
                    'primary_metric': silhouette_avg
                }

            else:
                raise ValueError(f"Unsupported model type: {config.model_type}")

            return model, performance_metrics

        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise

    async def _validate_model(self, model: Any, data: pd.DataFrame, config: TrainingConfig) -> Dict[str, Any]:
        """Validate the trained model"""

        validation_results = {
            'validation_date': datetime.now().isoformat(),
            'data_size': len(data),
            'feature_count': len(config.training_features),
            'model_type': config.model_type.value
        }

        # Add model-specific validation
        if hasattr(model, 'feature_importances_'):
            feature_importance = dict(zip(config.training_features, model.feature_importances_))
            validation_results['feature_importance'] = feature_importance

        return validation_results

    async def _deploy_model(self, model: Any, config: TrainingConfig, training_id: str) -> str:
        """Deploy the trained model"""

        try:
            # Create model path
            model_path = f"models/{config.user_id}/{config.model_type.value}/{training_id}.pkl"

            # TODO: Implement actual model saving
            # For now, just return the path
            logger.info(f"Model deployed to {model_path}")

            return model_path

        except Exception as e:
            logger.error(f"Error deploying model: {e}")
            raise

    def _update_training_stats(self, training_result: TrainingResult, success: bool):
        """Update training statistics"""

        self.training_stats['total_trainings'] += 1

        if success:
            self.training_stats['successful_trainings'] += 1

            # Update average training time
            current_avg = self.training_stats['average_training_time']
            total_successful = self.training_stats['successful_trainings']
            new_avg = ((current_avg * (total_successful - 1)) + training_result.training_duration) / total_successful
            self.training_stats['average_training_time'] = new_avg

            # Update best performances
            model_type = training_result.model_type.value
            primary_metric = training_result.performance_metrics.get('primary_metric', 0)

            if model_type not in self.training_stats['best_performances']:
                self.training_stats['best_performances'][model_type] = primary_metric
            else:
                self.training_stats['best_performances'][model_type] = max(
                    self.training_stats['best_performances'][model_type],
                    primary_metric
                )
        else:
            self.training_stats['failed_trainings'] += 1

    # Sample data creation methods for testing
    def _create_automotive_revenue_data(self) -> pd.DataFrame:
        """Create sample automotive revenue data"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=365, freq='D')

        return pd.DataFrame({
            'date': dates,
            'vehicle_sales_count': np.random.poisson(5, 365),
            'average_vehicle_price': np.random.normal(35000, 8000, 365),
            'service_revenue': np.random.normal(2000, 500, 365),
            'parts_revenue': np.random.normal(800, 200, 365),
            'financing_revenue': np.random.normal(1200, 300, 365),
            'marketing_spend': np.random.normal(3000, 800, 365),
            'inventory_level': np.random.normal(50, 15, 365),
            'economic_indicator': np.random.normal(100, 10, 365),
            'total_revenue': np.random.normal(45000, 12000, 365)  # target
        })

    def _create_restaurant_demand_data(self) -> pd.DataFrame:
        """Create sample restaurant demand data"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=365, freq='D')

        return pd.DataFrame({
            'date': dates,
            'day_of_week': dates.dayofweek,
            'weather_temp': np.random.normal(20, 10, 365),
            'weather_condition': np.random.choice(['sunny', 'rainy', 'cloudy'], 365),
            'local_events': np.random.choice([0, 1], 365, p=[0.9, 0.1]),
            'promotions': np.random.choice([0, 1], 365, p=[0.8, 0.2]),
            'staff_count': np.random.normal(8, 2, 365),
            'table_capacity': np.random.normal(40, 5, 365),
            'daily_customers': np.random.poisson(120, 365)  # target
        })

    def _create_retail_customer_data(self) -> pd.DataFrame:
        """Create sample retail customer data"""
        np.random.seed(42)
        n_customers = 1000

        return pd.DataFrame({
            'customer_id': range(n_customers),
            'purchase_frequency': np.random.exponential(2, n_customers),
            'average_order_value': np.random.lognormal(4, 1, n_customers),
            'total_spent': np.random.lognormal(6, 1.5, n_customers),
            'return_rate': np.random.beta(2, 8, n_customers),
            'review_scores': np.random.normal(4.2, 0.8, n_customers),
            'loyalty_program': np.random.choice([0, 1], n_customers, p=[0.6, 0.4]),
            'days_since_last_purchase': np.random.exponential(30, n_customers),
            'segment': np.random.choice(['A', 'B', 'C', 'D'], n_customers)  # target for clustering
        })

    def _create_generic_business_data(self) -> pd.DataFrame:
        """Create generic business data"""
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=180, freq='D')

        return pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(10000, 2000, 180),
            'customers': np.random.poisson(100, 180),
            'marketing_spend': np.random.normal(1500, 400, 180),
            'conversion_rate': np.random.normal(0.05, 0.01, 180),
            'target_metric': np.random.normal(100, 20, 180)
        })

    def get_training_status(self, training_id: str) -> Optional[TrainingResult]:
        """Get status of a training job"""
        return self.active_trainings.get(training_id)

    def get_user_models(self, user_id: str) -> Dict[ModelType, Dict[str, Any]]:
        """Get all models for a user"""
        return self.user_models.get(user_id, {})

    def get_training_statistics(self) -> Dict[str, Any]:
        """Get overall training statistics"""
        return self.training_stats.copy()
