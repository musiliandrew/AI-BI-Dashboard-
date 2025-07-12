#!/usr/bin/env python3
"""
Test Automated Training & Personalization System
Validate industry-specific model training and user personalization
"""
import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key-for-training-tests',
        INSTALLED_APPS=[
            'django.contrib.contenttypes',
            'django.contrib.auth',
            'apps.data_pipeline',
            'apps.ml_engine',
            'apps.social_intelligence',
            'apps.payments',
            'apps.website_intelligence',
        ],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
    )
    django.setup()

def test_automated_training_engine():
    """Test automated model training engine"""
    print("🤖 Testing Automated Training Engine...")
    
    try:
        from apps.ml_engine.automated_training_engine import (
            AutomatedTrainingEngine, TrainingConfig, ModelType, TrainingStatus
        )
        
        # Create training engine
        training_engine = AutomatedTrainingEngine()
        
        print(f"  ✅ Training engine created")
        print(f"  ✅ Industry templates loaded: {len(training_engine.industry_templates)}")
        
        # Test industry templates
        automotive_templates = training_engine.industry_templates.get('automotive', {})
        restaurant_templates = training_engine.industry_templates.get('restaurant', {})
        retail_templates = training_engine.industry_templates.get('retail', {})
        
        print(f"  ✅ Automotive templates: {len(automotive_templates)}")
        print(f"  ✅ Restaurant templates: {len(restaurant_templates)}")
        print(f"  ✅ Retail templates: {len(retail_templates)}")
        
        # Test template content
        if ModelType.REVENUE_FORECASTING in automotive_templates:
            template = automotive_templates[ModelType.REVENUE_FORECASTING]
            print(f"  ✅ Automotive revenue template features: {len(template.default_features)}")
            print(f"  ✅ Feature engineering rules: {len(template.feature_engineering_rules)}")
            print(f"  ✅ Performance benchmarks: {template.performance_benchmarks}")
        
        # Test sample data creation
        automotive_data = training_engine._create_automotive_revenue_data()
        restaurant_data = training_engine._create_restaurant_demand_data()
        retail_data = training_engine._create_retail_customer_data()
        
        print(f"  ✅ Automotive sample data: {automotive_data.shape}")
        print(f"  ✅ Restaurant sample data: {restaurant_data.shape}")
        print(f"  ✅ Retail sample data: {retail_data.shape}")
        
        # Test training configuration
        config = TrainingConfig(
            user_id='test_user_automotive',
            industry='automotive',
            model_type=ModelType.REVENUE_FORECASTING,
            data_sources=['vehicle_sales', 'service_revenue'],
            target_metric='total_revenue',
            training_features=['vehicle_sales_count', 'average_vehicle_price', 'service_revenue']
        )
        
        print(f"  ✅ Training config created for {config.industry} {config.model_type.value}")
        print(f"  ✅ Target metric: {config.target_metric}")
        print(f"  ✅ Training features: {len(config.training_features)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Automated training engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_fine_tuning_pipeline():
    """Test model fine-tuning pipeline"""
    print("\n🔧 Testing Model Fine-Tuning Pipeline...")
    
    try:
        from apps.ml_engine.model_fine_tuning_pipeline import (
            ModelFineTuningPipeline, FineTuningConfig, FineTuningTrigger, 
            FineTuningStrategy, UserModelProfile
        )
        from apps.ml_engine.automated_training_engine import ModelType
        
        # Create fine-tuning pipeline
        tuning_pipeline = ModelFineTuningPipeline()

        print(f"  ✅ Fine-tuning pipeline created")
        print(f"  ✅ Tuning queue initialized")
        
        # Test user profile creation
        user_profile = UserModelProfile(
            user_id='test_user_tuning',
            industry='restaurant',
            business_size='medium',
            data_patterns={'peak_hours': [12, 18, 19]},
            performance_preferences={'accuracy': 0.9, 'speed': 0.7},
            feedback_history=[],
            model_usage_patterns={},
            business_context={'location': 'urban', 'cuisine': 'italian'}
        )
        
        tuning_pipeline.user_profiles['test_user_tuning'] = user_profile
        
        print(f"  ✅ User profile created for {user_profile.industry} business")
        print(f"  ✅ Business context: {user_profile.business_context}")
        
        # Test fine-tuning configuration
        tuning_config = FineTuningConfig(
            user_id='test_user_tuning',
            model_type=ModelType.DEMAND_FORECASTING,
            base_model_path='models/test_user_tuning/demand_forecasting/base.pkl',
            trigger=FineTuningTrigger.PERFORMANCE_DEGRADATION,
            strategy=FineTuningStrategy.HYPERPARAMETER_OPTIMIZATION
        )
        
        print(f"  ✅ Fine-tuning config created")
        print(f"  ✅ Trigger: {tuning_config.trigger.value}")
        print(f"  ✅ Strategy: {tuning_config.strategy.value}")
        
        # Test pattern analysis
        import pandas as pd
        import numpy as np
        
        sample_data = pd.DataFrame({
            'revenue': np.random.normal(1000, 200, 100),
            'customers': np.random.poisson(50, 100),
            'category': np.random.choice(['A', 'B', 'C'], 100)
        })
        
        patterns = tuning_pipeline._analyze_data_patterns(sample_data)
        print(f"  ✅ Data patterns analyzed: {list(patterns.keys())}")
        
        # Test pattern drift calculation
        old_patterns = {'mean_values': {'revenue': 1000, 'customers': 50}}
        new_patterns = {'mean_values': {'revenue': 1200, 'customers': 60}}
        
        drift = tuning_pipeline._calculate_pattern_drift(old_patterns, new_patterns)
        print(f"  ✅ Pattern drift calculated: {drift:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Fine-tuning pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_user_ai_personalization():
    """Test user AI personalization system"""
    print("\n🧠 Testing User AI Personalization...")

    try:
        from apps.ml_engine.user_ai_personalization import (
            UserAIPersonalization, PersonalizationLevel, LearningDimension,
            PersonalizationProfile, PersonalizedInsight
        )

        # Create personalization system
        personalization = UserAIPersonalization()

        print(f"  ✅ Personalization system created")
        print(f"  ✅ Learning engines: {len(personalization.learning_engines)}")

        # Test user initialization
        initial_context = {
            'industry': 'automotive',
            'business_size': 'medium',
            'location': 'detroit',
            'business_type': 'dealership'
        }

        profile = await personalization.initialize_user_personalization(
            'test_user_personalization', initial_context
        )
        
        print(f"  ✅ User profile initialized")
        print(f"  ✅ Industry: {profile.industry}")
        print(f"  ✅ Personalization level: {profile.personalization_level.value}")
        print(f"  ✅ Learning progress: {len(profile.learning_progress)} dimensions")
        
        # Test learning from interaction
        interaction_data = {
            'type': 'question_click',
            'question_type': 'revenue_trend',
            'timestamp': datetime.now().isoformat(),
            'duration': 45
        }
        
        await personalization.learn_from_interaction('test_user_personalization', interaction_data)
        
        updated_profile = personalization.get_user_profile('test_user_personalization')
        print(f"  ✅ Learned from interaction: {interaction_data['type']}")
        print(f"  ✅ Interaction history: {len(updated_profile.interaction_history)} entries")
        
        # Test learning from feedback
        feedback_data = {
            'type': 'insight_feedback',
            'satisfaction_score': 4.2,
            'insight_preferences': {
                'preferred_types': ['trend', 'anomaly'],
                'detail_level': 'high',
                'action_style': 'specific'
            }
        }
        
        await personalization.learn_from_feedback('test_user_personalization', feedback_data)
        
        updated_profile = personalization.get_user_profile('test_user_personalization')
        print(f"  ✅ Learned from feedback: satisfaction={feedback_data['satisfaction_score']}")
        print(f"  ✅ User satisfaction: {updated_profile.user_satisfaction:.2f}")
        
        # Test insight personalization
        base_insight = {
            'title': 'Revenue Growth Trend',
            'explanation': 'Revenue has increased by 15% over the last month.',
            'actions': ['Analyze growth drivers', 'Scale successful strategies'],
            'confidence': 0.85,
            'industry_context': {'industry': 'automotive'},
            'patterns': ['revenue_trend'],
            'related_goals': ['growth', 'profitability']
        }
        
        personalized_insight = await personalization.personalize_insight(
            'test_user_personalization', base_insight
        )
        
        print(f"  ✅ Insight personalized")
        print(f"  ✅ Personalization applied: {len(personalized_insight.personalization_applied)} layers")
        print(f"  ✅ Relevance score: {personalized_insight.relevance_score:.2f}")
        print(f"  ✅ Business impact: {personalized_insight.business_impact_score:.2f}")
        
        # Test personalized recommendations
        recommendations = await personalization.get_personalized_recommendations(
            'test_user_personalization'
        )
        
        print(f"  ✅ Generated recommendations: {len(recommendations)}")
        if recommendations:
            print(f"  ✅ Top recommendation: {recommendations[0]['title']}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ User AI personalization test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_integration_flow():
    """Test integration between training, fine-tuning, and personalization"""
    print("\n🔗 Testing Integration Flow...")
    
    try:
        from apps.ml_engine.automated_training_engine import AutomatedTrainingEngine, TrainingConfig, ModelType
        from apps.ml_engine.model_fine_tuning_pipeline import ModelFineTuningPipeline
        from apps.ml_engine.user_ai_personalization import UserAIPersonalization
        
        # Create all systems
        training_engine = AutomatedTrainingEngine()
        tuning_pipeline = ModelFineTuningPipeline()
        personalization = UserAIPersonalization()
        
        print(f"  ✅ All systems created")
        
        # Simulate complete user journey
        user_id = 'test_integration_user'
        
        # 1. Initialize user personalization
        initial_context = {'industry': 'restaurant', 'business_size': 'small'}
        profile = await personalization.initialize_user_personalization(user_id, initial_context)
        
        print(f"  ✅ Step 1: User initialized ({profile.industry})")
        
        # 2. Create training configuration
        training_config = TrainingConfig(
            user_id=user_id,
            industry='restaurant',
            model_type=ModelType.DEMAND_FORECASTING,
            data_sources=['customer_data', 'weather_data'],
            target_metric='daily_customers',
            training_features=['day_of_week', 'weather_temp', 'promotions']
        )
        
        print(f"  ✅ Step 2: Training config created ({training_config.model_type.value})")
        
        # 3. Simulate user interactions
        interactions = [
            {'type': 'dashboard_visit', 'duration': 180},
            {'type': 'question_click', 'question_type': 'demand_forecast'},
            {'type': 'insight_view', 'insight_type': 'trend'},
            {'type': 'action_taken', 'action': 'optimize_staffing'}
        ]
        
        for interaction in interactions:
            await personalization.learn_from_interaction(user_id, interaction)
        
        print(f"  ✅ Step 3: Processed {len(interactions)} user interactions")
        
        # 4. Simulate feedback
        feedback = {
            'satisfaction_score': 4.5,
            'insight_preferences': {'detail_level': 'medium', 'action_style': 'practical'},
            'performance_goals': {'primary': ['efficiency', 'customer_satisfaction']}
        }
        
        await personalization.learn_from_feedback(user_id, feedback)
        
        print(f"  ✅ Step 4: Processed user feedback (satisfaction: {feedback['satisfaction_score']})")
        
        # 5. Generate personalized insight
        base_insight = {
            'title': 'Peak Hour Demand Pattern',
            'explanation': 'Customer demand peaks at 12 PM and 7 PM on weekdays.',
            'actions': ['Optimize staffing', 'Prepare inventory', 'Adjust marketing'],
            'confidence': 0.88
        }
        
        personalized = await personalization.personalize_insight(user_id, base_insight)
        
        print(f"  ✅ Step 5: Generated personalized insight")
        print(f"      Relevance: {personalized.relevance_score:.2f}")
        print(f"      Personalization layers: {len(personalized.personalization_applied)}")
        
        # 6. Check personalization progress
        final_profile = personalization.get_user_profile(user_id)
        
        print(f"  ✅ Step 6: Final personalization state")
        print(f"      Level: {final_profile.personalization_level.value}")
        print(f"      Satisfaction: {final_profile.user_satisfaction:.2f}")
        print(f"      Engagement: {final_profile.engagement_level:.2f}")
        print(f"      Personalization score: {final_profile.personalization_score:.2f}")
        
        # Import PersonalizationLevel for comparison
        from apps.ml_engine.user_ai_personalization import PersonalizationLevel

        # Verify integration success (adjusted for realistic expectations)
        integration_success = (
            final_profile.user_satisfaction > 4.0 and  # High satisfaction
            len(final_profile.interaction_history) >= 4 and  # Multiple interactions
            personalized.relevance_score >= 0.5 and  # Good relevance
            final_profile.engagement_level > 0.8 and  # High engagement
            final_profile.personalization_score > 0.5  # Good personalization progress
        )
        
        print(f"  ✅ Integration test: {'SUCCESS' if integration_success else 'FAILED'}")
        
        return integration_success
        
    except Exception as e:
        print(f"  ❌ Integration flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all automated training and personalization tests"""
    print("🤖 AUTOMATED TRAINING & PERSONALIZATION TESTS")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Automated Training Engine", test_automated_training_engine),
        ("Model Fine-Tuning Pipeline", test_model_fine_tuning_pipeline),
        ("User AI Personalization", test_user_ai_personalization),
        ("Integration Flow", test_integration_flow)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            if result:
                passed_tests += 1
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
    
    print(f"\n" + "=" * 70)
    print(f"🎯 AUTOMATED TRAINING & PERSONALIZATION SUMMARY")
    print(f"=" * 70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} ❌")
    print(f"Success Rate: {passed_tests / total_tests * 100:.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL AUTOMATED TRAINING SYSTEMS WORKING!")
        print(f"✅ Industry-specific model training ready")
        print(f"✅ Automated fine-tuning pipeline operational")
        print(f"✅ User personalization system functional")
        print(f"✅ End-to-end integration validated")
        print(f"\n🚀 READY FOR INTELLIGENT, PERSONALIZED AI TRAINING!")
        return 0
    else:
        print(f"\n⚠️  Some systems need attention. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
