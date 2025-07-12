"""
Model Fine-Tuning Pipeline
Automated fine-tuning system that adapts models to individual user patterns and business context
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

from .automated_training_engine import ModelType, TrainingStatus

logger = logging.getLogger(__name__)

class FineTuningTrigger(Enum):
    PERFORMANCE_DEGRADATION = "performance_degradation"
    NEW_DATA_PATTERN = "new_data_pattern"
    USER_FEEDBACK = "user_feedback"
    SCHEDULED = "scheduled"
    BUSINESS_CONTEXT_CHANGE = "business_context_change"

class FineTuningStrategy(Enum):
    INCREMENTAL_LEARNING = "incremental_learning"
    TRANSFER_LEARNING = "transfer_learning"
    HYPERPARAMETER_OPTIMIZATION = "hyperparameter_optimization"
    FEATURE_ADAPTATION = "feature_adaptation"
    ENSEMBLE_UPDATING = "ensemble_updating"

@dataclass
class FineTuningConfig:
    """Configuration for model fine-tuning"""
    user_id: str
    model_type: ModelType
    base_model_path: str
    trigger: FineTuningTrigger
    strategy: FineTuningStrategy
    new_data: Optional[pd.DataFrame] = None
    performance_threshold: float = 0.05  # Minimum improvement required
    max_tuning_iterations: int = 10
    learning_rate_adjustment: float = 0.1
    validation_split: float = 0.2
    preserve_base_knowledge: bool = True
    user_feedback: Optional[Dict[str, Any]] = None

@dataclass
class FineTuningResult:
    """Result of model fine-tuning"""
    tuning_id: str
    user_id: str
    model_type: ModelType
    trigger: FineTuningTrigger
    strategy: FineTuningStrategy
    status: TrainingStatus
    base_performance: Dict[str, float]
    improved_performance: Dict[str, float]
    performance_improvement: float
    tuned_model_path: Optional[str] = None
    tuning_duration: float = 0.0
    iterations_completed: int = 0
    adaptations_made: List[str] = field(default_factory=list)
    user_satisfaction_score: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

@dataclass
class UserModelProfile:
    """Profile of user's business patterns and preferences"""
    user_id: str
    industry: str
    business_size: str
    data_patterns: Dict[str, Any]
    performance_preferences: Dict[str, float]
    feedback_history: List[Dict[str, Any]]
    model_usage_patterns: Dict[str, Any]
    business_context: Dict[str, Any]
    last_updated: datetime = field(default_factory=datetime.now)

class ModelFineTuningPipeline:
    """Pipeline for automated model fine-tuning and personalization"""
    
    def __init__(self):
        self.tuning_queue = asyncio.Queue()
        self.active_tunings = {}  # tuning_id -> FineTuningResult
        self.user_profiles = {}   # user_id -> UserModelProfile
        self.model_registry = {}  # user_id -> {model_type: model_info}
        
        # Performance monitoring
        self.performance_history = {}  # user_id -> {model_type: [performance_over_time]}
        self.tuning_stats = {
            'total_tunings': 0,
            'successful_tunings': 0,
            'average_improvement': 0.0,
            'user_satisfaction_avg': 0.0
        }
    
    async def trigger_fine_tuning(self, config: FineTuningConfig) -> str:
        """Trigger model fine-tuning based on various conditions"""
        
        tuning_id = f"tune_{config.user_id}_{config.model_type.value}_{int(datetime.now().timestamp())}"
        
        # Create tuning result
        tuning_result = FineTuningResult(
            tuning_id=tuning_id,
            user_id=config.user_id,
            model_type=config.model_type,
            trigger=config.trigger,
            strategy=config.strategy,
            status=TrainingStatus.PENDING
        )
        
        # Add to active tunings
        self.active_tunings[tuning_id] = tuning_result
        
        # Add to tuning queue
        await self.tuning_queue.put((tuning_id, config))
        
        logger.info(f"Triggered fine-tuning {tuning_id} for user {config.user_id} due to {config.trigger.value}")
        
        return tuning_id
    
    async def monitor_model_performance(self, user_id: str, model_type: ModelType, 
                                      current_performance: Dict[str, float]):
        """Monitor model performance and trigger fine-tuning if needed"""
        
        # Initialize performance history if needed
        if user_id not in self.performance_history:
            self.performance_history[user_id] = {}
        
        if model_type not in self.performance_history[user_id]:
            self.performance_history[user_id][model_type] = []
        
        # Add current performance
        performance_entry = {
            'timestamp': datetime.now(),
            'metrics': current_performance
        }
        self.performance_history[user_id][model_type].append(performance_entry)
        
        # Check for performance degradation
        if len(self.performance_history[user_id][model_type]) >= 5:
            recent_performances = [entry['metrics'].get('primary_metric', 0) 
                                 for entry in self.performance_history[user_id][model_type][-5:]]
            
            # Calculate trend
            trend = np.polyfit(range(len(recent_performances)), recent_performances, 1)[0]
            
            # If performance is declining significantly, trigger fine-tuning
            if trend < -0.02:  # 2% decline trend
                await self._trigger_performance_based_tuning(user_id, model_type, current_performance)
    
    async def _trigger_performance_based_tuning(self, user_id: str, model_type: ModelType, 
                                              current_performance: Dict[str, float]):
        """Trigger fine-tuning due to performance degradation"""
        
        # Get base model path
        base_model_path = self._get_user_model_path(user_id, model_type)
        
        if not base_model_path:
            logger.warning(f"No base model found for user {user_id}, model type {model_type}")
            return
        
        # Create fine-tuning config
        config = FineTuningConfig(
            user_id=user_id,
            model_type=model_type,
            base_model_path=base_model_path,
            trigger=FineTuningTrigger.PERFORMANCE_DEGRADATION,
            strategy=FineTuningStrategy.HYPERPARAMETER_OPTIMIZATION,
            performance_threshold=0.03  # Require 3% improvement
        )
        
        await self.trigger_fine_tuning(config)
    
    async def process_user_feedback(self, user_id: str, model_type: ModelType, 
                                  feedback: Dict[str, Any]):
        """Process user feedback and trigger fine-tuning if needed"""
        
        # Update user profile with feedback
        await self._update_user_profile_with_feedback(user_id, feedback)
        
        # Check if feedback indicates need for fine-tuning
        satisfaction_score = feedback.get('satisfaction_score', 0)
        
        if satisfaction_score < 3.0:  # On a scale of 1-5
            # Trigger feedback-based fine-tuning
            base_model_path = self._get_user_model_path(user_id, model_type)
            
            if base_model_path:
                config = FineTuningConfig(
                    user_id=user_id,
                    model_type=model_type,
                    base_model_path=base_model_path,
                    trigger=FineTuningTrigger.USER_FEEDBACK,
                    strategy=FineTuningStrategy.FEATURE_ADAPTATION,
                    user_feedback=feedback
                )
                
                await self.trigger_fine_tuning(config)
    
    async def detect_new_data_patterns(self, user_id: str, new_data: pd.DataFrame):
        """Detect new patterns in user data and trigger fine-tuning if needed"""
        
        # Get user profile
        user_profile = await self._get_or_create_user_profile(user_id)
        
        # Analyze new data patterns
        new_patterns = self._analyze_data_patterns(new_data)
        
        # Compare with existing patterns
        pattern_drift = self._calculate_pattern_drift(user_profile.data_patterns, new_patterns)
        
        # If significant drift detected, trigger fine-tuning
        if pattern_drift > 0.3:  # 30% pattern change
            for model_type in user_profile.model_usage_patterns.keys():
                base_model_path = self._get_user_model_path(user_id, ModelType(model_type))
                
                if base_model_path:
                    config = FineTuningConfig(
                        user_id=user_id,
                        model_type=ModelType(model_type),
                        base_model_path=base_model_path,
                        trigger=FineTuningTrigger.NEW_DATA_PATTERN,
                        strategy=FineTuningStrategy.INCREMENTAL_LEARNING,
                        new_data=new_data
                    )
                    
                    await self.trigger_fine_tuning(config)
    
    async def process_tuning_queue(self):
        """Process fine-tuning queue continuously"""
        
        while True:
            try:
                # Get next tuning job
                tuning_id, config = await self.tuning_queue.get()
                
                # Process tuning
                await self._execute_fine_tuning(tuning_id, config)
                
                # Mark task as done
                self.tuning_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing tuning queue: {e}")
                await asyncio.sleep(5)
    
    async def _execute_fine_tuning(self, tuning_id: str, config: FineTuningConfig):
        """Execute the actual model fine-tuning"""
        
        tuning_result = self.active_tunings[tuning_id]
        start_time = datetime.now()
        
        try:
            # Update status
            tuning_result.status = TrainingStatus.TRAINING
            
            # Step 1: Load base model and get baseline performance
            logger.info(f"Loading base model for tuning {tuning_id}")
            base_model, base_performance = await self._load_base_model(config)
            tuning_result.base_performance = base_performance
            
            # Step 2: Prepare fine-tuning data
            tuning_data = await self._prepare_tuning_data(config)
            
            # Step 3: Apply fine-tuning strategy
            logger.info(f"Applying {config.strategy.value} strategy for tuning {tuning_id}")
            tuned_model = await self._apply_tuning_strategy(base_model, tuning_data, config)
            
            # Step 4: Evaluate improved model
            tuning_result.status = TrainingStatus.EVALUATING
            improved_performance = await self._evaluate_tuned_model(tuned_model, tuning_data, config)
            tuning_result.improved_performance = improved_performance
            
            # Step 5: Calculate improvement
            improvement = self._calculate_performance_improvement(base_performance, improved_performance)
            tuning_result.performance_improvement = improvement
            
            # Step 6: Validate improvement meets threshold
            if improvement < config.performance_threshold:
                raise ValueError(f"Improvement {improvement:.3f} below threshold {config.performance_threshold}")
            
            # Step 7: Deploy tuned model
            tuned_model_path = await self._deploy_tuned_model(tuned_model, config, tuning_id)
            tuning_result.tuned_model_path = tuned_model_path
            
            # Step 8: Update user profile
            await self._update_user_profile_with_tuning(config.user_id, tuning_result)
            
            # Complete tuning
            tuning_result.status = TrainingStatus.COMPLETED
            tuning_result.completed_at = datetime.now()
            tuning_result.tuning_duration = (tuning_result.completed_at - start_time).total_seconds()
            
            # Update statistics
            self._update_tuning_stats(tuning_result, success=True)
            
            logger.info(f"Fine-tuning {tuning_id} completed successfully with {improvement:.3f} improvement")
            
        except Exception as e:
            # Handle tuning failure
            tuning_result.status = TrainingStatus.FAILED
            tuning_result.completed_at = datetime.now()
            tuning_result.tuning_duration = (tuning_result.completed_at - start_time).total_seconds()
            
            self._update_tuning_stats(tuning_result, success=False)
            
            logger.error(f"Fine-tuning {tuning_id} failed: {e}")
    
    async def _load_base_model(self, config: FineTuningConfig) -> Tuple[Any, Dict[str, float]]:
        """Load base model and get baseline performance"""
        
        # TODO: Implement actual model loading
        # For now, create a mock model and performance
        
        mock_model = {
            'model_type': config.model_type.value,
            'user_id': config.user_id,
            'path': config.base_model_path
        }
        
        base_performance = {
            'primary_metric': 0.75,
            'secondary_metric': 0.68,
            'accuracy': 0.72
        }
        
        return mock_model, base_performance
    
    async def _prepare_tuning_data(self, config: FineTuningConfig) -> pd.DataFrame:
        """Prepare data for fine-tuning"""
        
        if config.new_data is not None:
            return config.new_data
        
        # TODO: Collect recent user data for tuning
        # For now, create sample data
        np.random.seed(42)
        
        return pd.DataFrame({
            'feature_1': np.random.randn(100),
            'feature_2': np.random.randn(100),
            'feature_3': np.random.randn(100),
            'target': np.random.randn(100)
        })
    
    async def _apply_tuning_strategy(self, base_model: Any, tuning_data: pd.DataFrame, 
                                   config: FineTuningConfig) -> Any:
        """Apply the selected fine-tuning strategy"""
        
        if config.strategy == FineTuningStrategy.HYPERPARAMETER_OPTIMIZATION:
            return await self._optimize_hyperparameters(base_model, tuning_data, config)
        
        elif config.strategy == FineTuningStrategy.INCREMENTAL_LEARNING:
            return await self._apply_incremental_learning(base_model, tuning_data, config)
        
        elif config.strategy == FineTuningStrategy.FEATURE_ADAPTATION:
            return await self._adapt_features(base_model, tuning_data, config)
        
        elif config.strategy == FineTuningStrategy.TRANSFER_LEARNING:
            return await self._apply_transfer_learning(base_model, tuning_data, config)
        
        else:
            # Default: return base model with minor adjustments
            tuned_model = base_model.copy()
            tuned_model['tuning_applied'] = config.strategy.value
            return tuned_model

    async def _optimize_hyperparameters(self, base_model: Any, tuning_data: pd.DataFrame,
                                       config: FineTuningConfig) -> Any:
        """Optimize model hyperparameters"""

        # Simulate hyperparameter optimization
        tuned_model = base_model.copy()
        tuned_model['hyperparameters_optimized'] = True
        tuned_model['learning_rate'] = tuned_model.get('learning_rate', 0.1) * (1 + config.learning_rate_adjustment)

        return tuned_model

    async def _apply_incremental_learning(self, base_model: Any, tuning_data: pd.DataFrame,
                                        config: FineTuningConfig) -> Any:
        """Apply incremental learning with new data"""

        # Simulate incremental learning
        tuned_model = base_model.copy()
        tuned_model['incremental_data_size'] = len(tuning_data)
        tuned_model['last_incremental_update'] = datetime.now().isoformat()

        return tuned_model

    async def _adapt_features(self, base_model: Any, tuning_data: pd.DataFrame,
                            config: FineTuningConfig) -> Any:
        """Adapt features based on user feedback"""

        # Simulate feature adaptation
        tuned_model = base_model.copy()

        if config.user_feedback:
            # Adjust feature weights based on feedback
            important_features = config.user_feedback.get('important_features', [])
            tuned_model['adapted_features'] = important_features

        return tuned_model

    async def _apply_transfer_learning(self, base_model: Any, tuning_data: pd.DataFrame,
                                     config: FineTuningConfig) -> Any:
        """Apply transfer learning techniques"""

        # Simulate transfer learning
        tuned_model = base_model.copy()
        tuned_model['transfer_learning_applied'] = True
        tuned_model['source_domain'] = 'industry_template'
        tuned_model['target_domain'] = f"user_{config.user_id}"

        return tuned_model

    async def _evaluate_tuned_model(self, tuned_model: Any, tuning_data: pd.DataFrame,
                                   config: FineTuningConfig) -> Dict[str, float]:
        """Evaluate the performance of the tuned model"""

        # Simulate improved performance
        base_performance = 0.75
        improvement_factor = np.random.uniform(1.02, 1.15)  # 2-15% improvement

        improved_performance = {
            'primary_metric': base_performance * improvement_factor,
            'secondary_metric': 0.68 * improvement_factor,
            'accuracy': 0.72 * improvement_factor
        }

        return improved_performance

    def _calculate_performance_improvement(self, base_performance: Dict[str, float],
                                         improved_performance: Dict[str, float]) -> float:
        """Calculate overall performance improvement"""

        base_primary = base_performance.get('primary_metric', 0)
        improved_primary = improved_performance.get('primary_metric', 0)

        if base_primary == 0:
            return 0.0

        return (improved_primary - base_primary) / base_primary

    async def _deploy_tuned_model(self, tuned_model: Any, config: FineTuningConfig,
                                tuning_id: str) -> str:
        """Deploy the tuned model"""

        # Create tuned model path
        tuned_model_path = f"models/{config.user_id}/{config.model_type.value}/tuned_{tuning_id}.pkl"

        # TODO: Implement actual model deployment
        logger.info(f"Tuned model deployed to {tuned_model_path}")

        return tuned_model_path

    async def _get_or_create_user_profile(self, user_id: str) -> UserModelProfile:
        """Get or create user profile"""

        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = UserModelProfile(
                user_id=user_id,
                industry='general',
                business_size='small',
                data_patterns={},
                performance_preferences={},
                feedback_history=[],
                model_usage_patterns={},
                business_context={}
            )

        return self.user_profiles[user_id]

    async def _update_user_profile_with_feedback(self, user_id: str, feedback: Dict[str, Any]):
        """Update user profile with feedback"""

        user_profile = await self._get_or_create_user_profile(user_id)

        # Add feedback to history
        feedback_entry = {
            'timestamp': datetime.now().isoformat(),
            'feedback': feedback
        }
        user_profile.feedback_history.append(feedback_entry)

        # Update performance preferences
        if 'preferred_metrics' in feedback:
            user_profile.performance_preferences.update(feedback['preferred_metrics'])

        # Update business context
        if 'business_context' in feedback:
            user_profile.business_context.update(feedback['business_context'])

        user_profile.last_updated = datetime.now()

    async def _update_user_profile_with_tuning(self, user_id: str, tuning_result: FineTuningResult):
        """Update user profile with tuning results"""

        user_profile = await self._get_or_create_user_profile(user_id)

        # Update model usage patterns
        model_type_str = tuning_result.model_type.value
        if model_type_str not in user_profile.model_usage_patterns:
            user_profile.model_usage_patterns[model_type_str] = {}

        user_profile.model_usage_patterns[model_type_str].update({
            'last_tuning': tuning_result.completed_at.isoformat() if tuning_result.completed_at else None,
            'performance_improvement': tuning_result.performance_improvement,
            'tuning_strategy': tuning_result.strategy.value,
            'tuning_trigger': tuning_result.trigger.value
        })

        user_profile.last_updated = datetime.now()

    def _analyze_data_patterns(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Analyze patterns in new data"""

        patterns = {}

        # Basic statistical patterns
        numeric_cols = data.select_dtypes(include=[np.number]).columns

        if len(numeric_cols) > 0:
            patterns['mean_values'] = data[numeric_cols].mean().to_dict()
            patterns['std_values'] = data[numeric_cols].std().to_dict()
            patterns['correlation_matrix'] = data[numeric_cols].corr().to_dict()

        # Categorical patterns
        categorical_cols = data.select_dtypes(include=['object']).columns

        if len(categorical_cols) > 0:
            patterns['categorical_distributions'] = {}
            for col in categorical_cols:
                patterns['categorical_distributions'][col] = data[col].value_counts().to_dict()

        # Temporal patterns (if date column exists)
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            patterns['temporal_patterns'] = {
                'date_range': [data['date'].min().isoformat(), data['date'].max().isoformat()],
                'frequency': 'daily'  # Simplified
            }

        return patterns

    def _calculate_pattern_drift(self, old_patterns: Dict[str, Any],
                               new_patterns: Dict[str, Any]) -> float:
        """Calculate drift between old and new data patterns"""

        if not old_patterns:
            return 1.0  # Complete drift if no old patterns

        drift_score = 0.0
        comparisons = 0

        # Compare mean values
        if 'mean_values' in old_patterns and 'mean_values' in new_patterns:
            old_means = old_patterns['mean_values']
            new_means = new_patterns['mean_values']

            for feature in set(old_means.keys()) & set(new_means.keys()):
                old_val = old_means[feature]
                new_val = new_means[feature]

                if old_val != 0:
                    relative_change = abs(new_val - old_val) / abs(old_val)
                    drift_score += min(relative_change, 1.0)  # Cap at 1.0
                    comparisons += 1

        # Compare categorical distributions
        if 'categorical_distributions' in old_patterns and 'categorical_distributions' in new_patterns:
            old_cats = old_patterns['categorical_distributions']
            new_cats = new_patterns['categorical_distributions']

            for feature in set(old_cats.keys()) & set(new_cats.keys()):
                # Simple comparison of top categories
                old_top = max(old_cats[feature], key=old_cats[feature].get) if old_cats[feature] else None
                new_top = max(new_cats[feature], key=new_cats[feature].get) if new_cats[feature] else None

                if old_top != new_top:
                    drift_score += 0.5

                comparisons += 1

        return drift_score / max(comparisons, 1)

    def _get_user_model_path(self, user_id: str, model_type: ModelType) -> Optional[str]:
        """Get the path to user's current model"""

        if user_id in self.model_registry:
            model_info = self.model_registry[user_id].get(model_type)
            if model_info:
                return model_info.get('model_path')

        return None

    def _update_tuning_stats(self, tuning_result: FineTuningResult, success: bool):
        """Update fine-tuning statistics"""

        self.tuning_stats['total_tunings'] += 1

        if success:
            self.tuning_stats['successful_tunings'] += 1

            # Update average improvement
            current_avg = self.tuning_stats['average_improvement']
            successful_count = self.tuning_stats['successful_tunings']
            new_avg = ((current_avg * (successful_count - 1)) + tuning_result.performance_improvement) / successful_count
            self.tuning_stats['average_improvement'] = new_avg

            # Update user satisfaction if available
            if tuning_result.user_satisfaction_score:
                current_satisfaction = self.tuning_stats['user_satisfaction_avg']
                new_satisfaction = ((current_satisfaction * (successful_count - 1)) + tuning_result.user_satisfaction_score) / successful_count
                self.tuning_stats['user_satisfaction_avg'] = new_satisfaction

    # Public interface methods
    def get_tuning_status(self, tuning_id: str) -> Optional[FineTuningResult]:
        """Get status of a fine-tuning job"""
        return self.active_tunings.get(tuning_id)

    def get_user_profile(self, user_id: str) -> Optional[UserModelProfile]:
        """Get user profile"""
        return self.user_profiles.get(user_id)

    def get_tuning_statistics(self) -> Dict[str, Any]:
        """Get fine-tuning statistics"""
        return self.tuning_stats.copy()

    async def schedule_periodic_tuning(self, user_id: str, model_type: ModelType,
                                     frequency: str = "weekly"):
        """Schedule periodic fine-tuning for a user's model"""

        base_model_path = self._get_user_model_path(user_id, model_type)

        if base_model_path:
            config = FineTuningConfig(
                user_id=user_id,
                model_type=model_type,
                base_model_path=base_model_path,
                trigger=FineTuningTrigger.SCHEDULED,
                strategy=FineTuningStrategy.INCREMENTAL_LEARNING
            )

            await self.trigger_fine_tuning(config)
            logger.info(f"Scheduled {frequency} fine-tuning for user {user_id}, model {model_type.value}")
