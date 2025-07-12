"""
Core Machine Learning Engine
Advanced ML/AI processing with industry-specific models and adaptive learning
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import pickle
try:
    import joblib
except ImportError:
    joblib = None
from abc import ABC, abstractmethod
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp

# ML Libraries
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression, Ridge, Lasso
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler, LabelEncoder, OneHotEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, mean_absolute_error, mean_squared_error, r2_score
from sklearn.decomposition import PCA
from sklearn.feature_selection import SelectKBest, f_regression, f_classif

# Time Series
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing

# Deep Learning (if available)
try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

logger = logging.getLogger(__name__)

@dataclass
class MLResult:
    """Result from ML operations"""
    success: bool
    model_id: str
    operation_type: str
    result_data: Any
    metrics: Dict[str, float]
    processing_time: float
    error_message: Optional[str] = None
    confidence: Optional[float] = None

@dataclass
class FeatureImportance:
    """Feature importance analysis"""
    feature_name: str
    importance_score: float
    correlation_with_target: float
    data_type: str

class MLAlgorithmRegistry:
    """Registry of available ML algorithms"""
    
    def __init__(self):
        self.algorithms = {
            # Regression Algorithms
            'linear_regression': {
                'class': LinearRegression,
                'type': 'regression',
                'params': {},
                'description': 'Simple linear regression for continuous targets'
            },
            'random_forest_regressor': {
                'class': RandomForestRegressor,
                'type': 'regression',
                'params': {'n_estimators': 100, 'random_state': 42},
                'description': 'Ensemble method for regression with feature importance'
            },
            'gradient_boosting_regressor': {
                'class': GradientBoostingRegressor,
                'type': 'regression',
                'params': {'n_estimators': 100, 'random_state': 42},
                'description': 'Gradient boosting for regression tasks'
            },
            'ridge_regression': {
                'class': Ridge,
                'type': 'regression',
                'params': {'alpha': 1.0},
                'description': 'Ridge regression with L2 regularization'
            },
            'lasso_regression': {
                'class': Lasso,
                'type': 'regression',
                'params': {'alpha': 1.0},
                'description': 'Lasso regression with L1 regularization'
            },
            
            # Classification Algorithms
            'logistic_regression': {
                'class': LogisticRegression,
                'type': 'classification',
                'params': {'random_state': 42},
                'description': 'Logistic regression for binary/multiclass classification'
            },
            'random_forest_classifier': {
                'class': RandomForestClassifier,
                'type': 'classification',
                'params': {'n_estimators': 100, 'random_state': 42},
                'description': 'Ensemble method for classification'
            },
            
            # Clustering Algorithms
            'kmeans': {
                'class': KMeans,
                'type': 'clustering',
                'params': {'n_clusters': 3, 'random_state': 42},
                'description': 'K-means clustering for customer segmentation'
            },
            'dbscan': {
                'class': DBSCAN,
                'type': 'clustering',
                'params': {'eps': 0.5, 'min_samples': 5},
                'description': 'Density-based clustering for anomaly detection'
            }
        }
    
    def get_algorithm(self, algorithm_name: str, params: Dict[str, Any] = None):
        """Get algorithm instance with parameters"""
        if algorithm_name not in self.algorithms:
            raise ValueError(f"Algorithm {algorithm_name} not found")
        
        algo_config = self.algorithms[algorithm_name]
        final_params = algo_config['params'].copy()
        if params:
            final_params.update(params)
        
        return algo_config['class'](**final_params)
    
    def get_algorithms_by_type(self, algorithm_type: str) -> List[str]:
        """Get algorithms by type (regression, classification, clustering)"""
        return [name for name, config in self.algorithms.items() 
                if config['type'] == algorithm_type]

class FeatureEngineer:
    """Advanced feature engineering for ML models"""
    
    def __init__(self):
        self.scalers = {}
        self.encoders = {}
        self.feature_selectors = {}
    
    def engineer_features(self, data: pd.DataFrame, target_column: str = None, 
                         feature_config: Dict[str, Any] = None) -> pd.DataFrame:
        """Comprehensive feature engineering"""
        
        if feature_config is None:
            feature_config = {}
        
        engineered_data = data.copy()
        
        # 1. Handle missing values
        engineered_data = self._handle_missing_values(engineered_data, feature_config)
        
        # 2. Create time-based features
        engineered_data = self._create_time_features(engineered_data)
        
        # 3. Create business-specific features
        engineered_data = self._create_business_features(engineered_data, feature_config)
        
        # 4. Create interaction features
        engineered_data = self._create_interaction_features(engineered_data, feature_config)
        
        # 5. Create aggregation features
        engineered_data = self._create_aggregation_features(engineered_data, feature_config)
        
        # 6. Encode categorical variables
        engineered_data = self._encode_categorical_features(engineered_data)
        
        # 7. Scale numerical features
        engineered_data = self._scale_numerical_features(engineered_data, target_column)
        
        # 8. Feature selection
        if target_column and target_column in engineered_data.columns:
            engineered_data = self._select_features(engineered_data, target_column, feature_config)
        
        return engineered_data
    
    def _handle_missing_values(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Handle missing values intelligently"""
        strategy = config.get('missing_value_strategy', 'auto')
        
        for column in data.columns:
            if data[column].isnull().sum() > 0:
                if data[column].dtype in ['int64', 'float64']:
                    # Numerical columns
                    if strategy == 'mean':
                        data[column].fillna(data[column].mean(), inplace=True)
                    elif strategy == 'median':
                        data[column].fillna(data[column].median(), inplace=True)
                    else:  # auto
                        data[column].fillna(data[column].median(), inplace=True)
                else:
                    # Categorical columns
                    data[column].fillna(data[column].mode()[0] if len(data[column].mode()) > 0 else 'unknown', inplace=True)
        
        return data
    
    def _create_time_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Create time-based features"""
        # Look for datetime columns
        datetime_columns = data.select_dtypes(include=['datetime64']).columns
        
        for col in datetime_columns:
            # Extract time components
            data[f'{col}_year'] = data[col].dt.year
            data[f'{col}_month'] = data[col].dt.month
            data[f'{col}_day'] = data[col].dt.day
            data[f'{col}_dayofweek'] = data[col].dt.dayofweek
            data[f'{col}_hour'] = data[col].dt.hour
            data[f'{col}_quarter'] = data[col].dt.quarter
            
            # Create business time features
            data[f'{col}_is_weekend'] = data[col].dt.dayofweek.isin([5, 6]).astype(int)
            data[f'{col}_is_month_start'] = data[col].dt.is_month_start.astype(int)
            data[f'{col}_is_month_end'] = data[col].dt.is_month_end.astype(int)
        
        return data
    
    def _create_business_features(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Create business-specific features"""
        industry = config.get('industry', 'general')
        
        if industry == 'automotive':
            # Automotive-specific features
            if 'price' in data.columns and 'mileage' in data.columns:
                data['price_per_mile'] = data['price'] / (data['mileage'] + 1)
            
            if 'year' in data.columns:
                current_year = datetime.now().year
                data['vehicle_age'] = current_year - data['year']
        
        elif industry == 'restaurant':
            # Restaurant-specific features
            if 'order_amount' in data.columns and 'items_count' in data.columns:
                data['avg_item_price'] = data['order_amount'] / (data['items_count'] + 1)
            
            if 'order_time' in data.columns:
                # Create meal period features
                hour = pd.to_datetime(data['order_time']).dt.hour
                data['is_breakfast'] = ((hour >= 6) & (hour < 11)).astype(int)
                data['is_lunch'] = ((hour >= 11) & (hour < 16)).astype(int)
                data['is_dinner'] = ((hour >= 16) & (hour < 22)).astype(int)
        
        elif industry == 'retail':
            # Retail-specific features
            if 'purchase_amount' in data.columns and 'quantity' in data.columns:
                data['avg_unit_price'] = data['purchase_amount'] / (data['quantity'] + 1)
            
            if 'customer_id' in data.columns:
                # Customer frequency features (would need historical data)
                pass
        
        return data
    
    def _create_interaction_features(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Create interaction features between important variables"""
        numerical_columns = data.select_dtypes(include=['int64', 'float64']).columns
        
        # Create interactions for top numerical features
        if len(numerical_columns) >= 2:
            important_features = numerical_columns[:5]  # Limit to top 5 to avoid explosion
            
            for i, col1 in enumerate(important_features):
                for col2 in important_features[i+1:]:
                    # Multiplication interaction
                    data[f'{col1}_x_{col2}'] = data[col1] * data[col2]
                    
                    # Ratio interaction (avoid division by zero)
                    data[f'{col1}_div_{col2}'] = data[col1] / (data[col2] + 1e-8)
        
        return data
    
    def _create_aggregation_features(self, data: pd.DataFrame, config: Dict[str, Any]) -> pd.DataFrame:
        """Create aggregation features"""
        group_by_columns = config.get('group_by_columns', [])
        
        if group_by_columns:
            numerical_columns = data.select_dtypes(include=['int64', 'float64']).columns
            
            for group_col in group_by_columns:
                if group_col in data.columns:
                    for num_col in numerical_columns:
                        if num_col != group_col:
                            # Create group-based aggregations
                            group_stats = data.groupby(group_col)[num_col].agg(['mean', 'std', 'count'])
                            data[f'{num_col}_group_mean'] = data[group_col].map(group_stats['mean'])
                            data[f'{num_col}_group_std'] = data[group_col].map(group_stats['std'])
                            data[f'{num_col}_group_count'] = data[group_col].map(group_stats['count'])
        
        return data
    
    def _encode_categorical_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical features"""
        categorical_columns = data.select_dtypes(include=['object']).columns
        
        for col in categorical_columns:
            if data[col].nunique() <= 10:  # One-hot encode low cardinality
                dummies = pd.get_dummies(data[col], prefix=col)
                data = pd.concat([data, dummies], axis=1)
                data.drop(col, axis=1, inplace=True)
            else:  # Label encode high cardinality
                le = LabelEncoder()
                data[f'{col}_encoded'] = le.fit_transform(data[col].astype(str))
                self.encoders[col] = le
                data.drop(col, axis=1, inplace=True)
        
        return data
    
    def _scale_numerical_features(self, data: pd.DataFrame, target_column: str = None) -> pd.DataFrame:
        """Scale numerical features"""
        numerical_columns = data.select_dtypes(include=['int64', 'float64']).columns
        
        # Exclude target column from scaling
        if target_column and target_column in numerical_columns:
            numerical_columns = numerical_columns.drop(target_column)
        
        if len(numerical_columns) > 0:
            scaler = StandardScaler()
            data[numerical_columns] = scaler.fit_transform(data[numerical_columns])
            self.scalers['standard'] = scaler
        
        return data
    
    def _select_features(self, data: pd.DataFrame, target_column: str, config: Dict[str, Any]) -> pd.DataFrame:
        """Select most important features"""
        max_features = config.get('max_features', 50)
        
        if len(data.columns) <= max_features + 1:  # +1 for target
            return data
        
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        # Use appropriate feature selection based on target type
        if y.dtype in ['int64', 'float64'] and y.nunique() > 10:
            # Regression
            selector = SelectKBest(score_func=f_regression, k=min(max_features, len(X.columns)))
        else:
            # Classification
            selector = SelectKBest(score_func=f_classif, k=min(max_features, len(X.columns)))
        
        X_selected = selector.fit_transform(X, y)
        selected_features = X.columns[selector.get_support()]
        
        self.feature_selectors['main'] = selector
        
        # Return data with selected features + target
        result_data = pd.DataFrame(X_selected, columns=selected_features, index=data.index)
        result_data[target_column] = y
        
        return result_data

class IndustrySpecificModels:
    """Industry-specific ML model configurations and templates"""
    
    @staticmethod
    def get_automotive_models() -> Dict[str, Dict[str, Any]]:
        """Automotive industry ML models"""
        return {
            'vehicle_price_prediction': {
                'model_type': 'revenue_forecasting',
                'algorithm': 'random_forest_regressor',
                'features': ['year', 'mileage', 'brand', 'model', 'fuel_type', 'transmission'],
                'target': 'price',
                'hyperparameters': {'n_estimators': 200, 'max_depth': 15},
                'business_value': 'Optimize vehicle pricing for maximum profit'
            },
            'customer_purchase_prediction': {
                'model_type': 'churn_prediction',
                'algorithm': 'random_forest_classifier',
                'features': ['age', 'income', 'previous_purchases', 'website_visits', 'social_engagement'],
                'target': 'will_purchase',
                'hyperparameters': {'n_estimators': 150, 'max_depth': 10},
                'business_value': 'Identify high-probability customers for targeted marketing'
            },
            'inventory_demand_forecasting': {
                'model_type': 'demand_forecasting',
                'algorithm': 'gradient_boosting_regressor',
                'features': ['season', 'economic_indicators', 'marketing_spend', 'competitor_pricing'],
                'target': 'monthly_sales',
                'hyperparameters': {'n_estimators': 100, 'learning_rate': 0.1},
                'business_value': 'Optimize inventory levels and reduce carrying costs'
            }
        }
    
    @staticmethod
    def get_restaurant_models() -> Dict[str, Dict[str, Any]]:
        """Restaurant industry ML models"""
        return {
            'demand_forecasting': {
                'model_type': 'demand_forecasting',
                'algorithm': 'random_forest_regressor',
                'features': ['day_of_week', 'weather', 'events', 'promotions', 'season'],
                'target': 'daily_customers',
                'hyperparameters': {'n_estimators': 100, 'max_depth': 12},
                'business_value': 'Optimize staffing and inventory based on predicted demand'
            },
            'menu_optimization': {
                'model_type': 'product_recommendation',
                'algorithm': 'random_forest_classifier',
                'features': ['item_category', 'price', 'ingredients', 'season', 'customer_preferences'],
                'target': 'item_popularity',
                'hyperparameters': {'n_estimators': 150},
                'business_value': 'Optimize menu items for profitability and customer satisfaction'
            },
            'customer_lifetime_value': {
                'model_type': 'customer_lifetime_value',
                'algorithm': 'gradient_boosting_regressor',
                'features': ['visit_frequency', 'avg_order_value', 'customer_age', 'location'],
                'target': 'lifetime_value',
                'hyperparameters': {'n_estimators': 200, 'learning_rate': 0.05},
                'business_value': 'Identify high-value customers for retention programs'
            }
        }
    
    @staticmethod
    def get_retail_models() -> Dict[str, Dict[str, Any]]:
        """Retail industry ML models"""
        return {
            'customer_segmentation': {
                'model_type': 'customer_segmentation',
                'algorithm': 'kmeans',
                'features': ['purchase_frequency', 'avg_order_value', 'product_categories', 'seasonality'],
                'target': None,  # Unsupervised
                'hyperparameters': {'n_clusters': 5},
                'business_value': 'Create targeted marketing campaigns for different customer segments'
            },
            'price_optimization': {
                'model_type': 'price_optimization',
                'algorithm': 'random_forest_regressor',
                'features': ['competitor_prices', 'demand_elasticity', 'inventory_levels', 'season'],
                'target': 'optimal_price',
                'hyperparameters': {'n_estimators': 200, 'max_depth': 15},
                'business_value': 'Maximize revenue through dynamic pricing strategies'
            },
            'churn_prediction': {
                'model_type': 'churn_prediction',
                'algorithm': 'logistic_regression',
                'features': ['days_since_last_purchase', 'purchase_frequency', 'customer_service_interactions'],
                'target': 'will_churn',
                'hyperparameters': {'C': 1.0, 'penalty': 'l2'},
                'business_value': 'Proactively retain customers at risk of churning'
            }
        }

class MLModelTrainer:
    """Advanced ML model training with automated hyperparameter tuning"""
    
    def __init__(self):
        self.algorithm_registry = MLAlgorithmRegistry()
        self.feature_engineer = FeatureEngineer()
        self.industry_models = IndustrySpecificModels()
        self.thread_pool = ThreadPoolExecutor(max_workers=mp.cpu_count())
    
    async def train_model(self, model_config: Dict[str, Any], training_data: pd.DataFrame) -> MLResult:
        """Train ML model with comprehensive pipeline"""
        start_time = datetime.now()
        
        try:
            # Extract configuration
            model_type = model_config.get('model_type')
            algorithm = model_config.get('algorithm')
            target_column = model_config.get('target_column')
            feature_config = model_config.get('feature_config', {})
            hyperparameters = model_config.get('hyperparameters', {})
            
            # Feature engineering
            engineered_data = self.feature_engineer.engineer_features(
                training_data, target_column, feature_config
            )
            
            # Prepare training data
            if target_column and target_column in engineered_data.columns:
                X = engineered_data.drop(columns=[target_column])
                y = engineered_data[target_column]
                
                # Split data
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
            else:
                # Unsupervised learning
                X_train = engineered_data
                X_test = None
                y_train = None
                y_test = None
            
            # Get algorithm
            model = self.algorithm_registry.get_algorithm(algorithm, hyperparameters)
            
            # Train model
            if y_train is not None:
                model.fit(X_train, y_train)
                
                # Evaluate model
                if X_test is not None and y_test is not None:
                    predictions = model.predict(X_test)
                    metrics = self._calculate_metrics(y_test, predictions, model_type)
                else:
                    metrics = {}
            else:
                # Unsupervised learning
                model.fit(X_train)
                metrics = {'silhouette_score': 0.5}  # Placeholder
            
            # Calculate feature importance
            feature_importance = self._get_feature_importance(model, X_train.columns)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return MLResult(
                success=True,
                model_id=model_config.get('model_id', 'unknown'),
                operation_type='training',
                result_data={
                    'model': model,
                    'feature_importance': feature_importance,
                    'training_data_shape': X_train.shape,
                    'test_data_shape': X_test.shape if X_test is not None else None
                },
                metrics=metrics,
                processing_time=processing_time,
                confidence=metrics.get('accuracy', metrics.get('r2_score', 0.5))
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Model training failed: {e}")
            
            return MLResult(
                success=False,
                model_id=model_config.get('model_id', 'unknown'),
                operation_type='training',
                result_data=None,
                metrics={},
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def _calculate_metrics(self, y_true, y_pred, model_type: str) -> Dict[str, float]:
        """Calculate appropriate metrics based on model type"""
        metrics = {}
        
        try:
            if model_type in ['revenue_forecasting', 'demand_forecasting', 'customer_lifetime_value']:
                # Regression metrics
                metrics['mae'] = mean_absolute_error(y_true, y_pred)
                metrics['rmse'] = np.sqrt(mean_squared_error(y_true, y_pred))
                metrics['r2_score'] = r2_score(y_true, y_pred)
                
            elif model_type in ['churn_prediction', 'lead_scoring', 'fraud_detection']:
                # Classification metrics
                metrics['accuracy'] = accuracy_score(y_true, y_pred)
                metrics['precision'] = precision_score(y_true, y_pred, average='weighted')
                metrics['recall'] = recall_score(y_true, y_pred, average='weighted')
                metrics['f1_score'] = f1_score(y_true, y_pred, average='weighted')
                
        except Exception as e:
            logger.warning(f"Error calculating metrics: {e}")
            metrics['error'] = str(e)
        
        return metrics
    
    def _get_feature_importance(self, model, feature_names: List[str]) -> List[FeatureImportance]:
        """Extract feature importance from trained model"""
        importance_list = []
        
        try:
            if hasattr(model, 'feature_importances_'):
                importances = model.feature_importances_
                for i, feature in enumerate(feature_names):
                    importance_list.append(FeatureImportance(
                        feature_name=feature,
                        importance_score=float(importances[i]),
                        correlation_with_target=0.0,  # Would need target data
                        data_type='numerical'  # Simplified
                    ))
            
            elif hasattr(model, 'coef_'):
                coefficients = model.coef_
                if coefficients.ndim > 1:
                    coefficients = coefficients[0]  # Take first class for multiclass
                
                for i, feature in enumerate(feature_names):
                    importance_list.append(FeatureImportance(
                        feature_name=feature,
                        importance_score=float(abs(coefficients[i])),
                        correlation_with_target=0.0,
                        data_type='numerical'
                    ))
        
        except Exception as e:
            logger.warning(f"Error extracting feature importance: {e}")
        
        return sorted(importance_list, key=lambda x: x.importance_score, reverse=True)

class AdvancedAnalyticsEngine:
    """Advanced mathematical and statistical analysis engine"""

    def __init__(self):
        self.statistical_models = {}
        self.time_series_models = {}

    def perform_statistical_analysis(self, data: pd.DataFrame, analysis_type: str,
                                   config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Perform comprehensive statistical analysis"""
        if config is None:
            config = {}

        results = {}

        if analysis_type == 'descriptive_statistics':
            results = self._descriptive_statistics(data)
        elif analysis_type == 'correlation_analysis':
            results = self._correlation_analysis(data)
        elif analysis_type == 'anomaly_detection':
            results = self._anomaly_detection(data, config)
        elif analysis_type == 'trend_analysis':
            results = self._trend_analysis(data, config)
        elif analysis_type == 'seasonality_analysis':
            results = self._seasonality_analysis(data, config)
        elif analysis_type == 'cohort_analysis':
            results = self._cohort_analysis(data, config)

        return results

    def _descriptive_statistics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Calculate comprehensive descriptive statistics"""
        numerical_columns = data.select_dtypes(include=['int64', 'float64']).columns

        stats = {}
        for col in numerical_columns:
            stats[col] = {
                'mean': float(data[col].mean()),
                'median': float(data[col].median()),
                'std': float(data[col].std()),
                'min': float(data[col].min()),
                'max': float(data[col].max()),
                'q25': float(data[col].quantile(0.25)),
                'q75': float(data[col].quantile(0.75)),
                'skewness': float(data[col].skew()),
                'kurtosis': float(data[col].kurtosis()),
                'null_count': int(data[col].isnull().sum()),
                'unique_count': int(data[col].nunique())
            }

        return {'descriptive_statistics': stats}

    def _correlation_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Perform correlation analysis"""
        numerical_data = data.select_dtypes(include=['int64', 'float64'])

        if len(numerical_data.columns) < 2:
            return {'error': 'Need at least 2 numerical columns for correlation analysis'}

        correlation_matrix = numerical_data.corr()

        # Find strong correlations
        strong_correlations = []
        for i in range(len(correlation_matrix.columns)):
            for j in range(i+1, len(correlation_matrix.columns)):
                corr_value = correlation_matrix.iloc[i, j]
                if abs(corr_value) > 0.7:  # Strong correlation threshold
                    strong_correlations.append({
                        'feature1': correlation_matrix.columns[i],
                        'feature2': correlation_matrix.columns[j],
                        'correlation': float(corr_value),
                        'strength': 'strong' if abs(corr_value) > 0.8 else 'moderate'
                    })

        return {
            'correlation_matrix': correlation_matrix.to_dict(),
            'strong_correlations': strong_correlations
        }

    def _anomaly_detection(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Detect anomalies using statistical methods"""
        numerical_columns = data.select_dtypes(include=['int64', 'float64']).columns
        method = config.get('method', 'iqr')

        anomalies = {}

        for col in numerical_columns:
            if method == 'iqr':
                Q1 = data[col].quantile(0.25)
                Q3 = data[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR

                anomaly_mask = (data[col] < lower_bound) | (data[col] > upper_bound)

            elif method == 'zscore':
                z_scores = np.abs((data[col] - data[col].mean()) / data[col].std())
                anomaly_mask = z_scores > 3

            anomaly_indices = data[anomaly_mask].index.tolist()
            anomaly_values = data.loc[anomaly_mask, col].tolist()

            anomalies[col] = {
                'count': len(anomaly_indices),
                'percentage': len(anomaly_indices) / len(data) * 100,
                'indices': anomaly_indices[:10],  # Limit to first 10
                'values': anomaly_values[:10]
            }

        return {'anomalies': anomalies, 'method': method}

    def _trend_analysis(self, data: pd.DataFrame, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze trends in time series data"""
        date_column = config.get('date_column')
        value_column = config.get('value_column')

        if not date_column or not value_column:
            return {'error': 'date_column and value_column required for trend analysis'}

        if date_column not in data.columns or value_column not in data.columns:
            return {'error': 'Specified columns not found in data'}

        # Sort by date
        data_sorted = data.sort_values(date_column)

        # Calculate trend using linear regression
        x = np.arange(len(data_sorted))
        y = data_sorted[value_column].values

        # Remove NaN values
        mask = ~np.isnan(y)
        x_clean = x[mask]
        y_clean = y[mask]

        if len(x_clean) < 2:
            return {'error': 'Insufficient data points for trend analysis'}

        # Linear regression
        slope, intercept = np.polyfit(x_clean, y_clean, 1)

        # Calculate R-squared
        y_pred = slope * x_clean + intercept
        ss_res = np.sum((y_clean - y_pred) ** 2)
        ss_tot = np.sum((y_clean - np.mean(y_clean)) ** 2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

        # Determine trend direction
        if slope > 0.01:
            trend_direction = 'increasing'
        elif slope < -0.01:
            trend_direction = 'decreasing'
        else:
            trend_direction = 'stable'

        return {
            'trend_slope': float(slope),
            'trend_intercept': float(intercept),
            'r_squared': float(r_squared),
            'trend_direction': trend_direction,
            'trend_strength': 'strong' if abs(r_squared) > 0.7 else 'moderate' if abs(r_squared) > 0.3 else 'weak'
        }

# Global ML engine instances
ml_algorithm_registry = MLAlgorithmRegistry()
feature_engineer = FeatureEngineer()
ml_model_trainer = MLModelTrainer()
analytics_engine = AdvancedAnalyticsEngine()
