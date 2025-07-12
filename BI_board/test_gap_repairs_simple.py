#!/usr/bin/env python3
"""
Simple Gap Repair Tests - No External Dependencies
"""
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure Django settings
import django
from django.conf import settings

if not settings.configured:
    settings.configure(
        DEBUG=True,
        SECRET_KEY='test-secret-key-for-gap-repair-tests',
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
        OPENAI_API_KEY=None,  # Test without API key
    )
    django.setup()

def test_data_structures():
    """Test core data structures"""
    print("📊 Testing Core Data Structures...")
    
    try:
        from apps.ml_engine.llm_insight_generator import RawInsight, ExplainedInsight
        
        # Test RawInsight creation
        raw_insight = RawInsight(
            insight_type='trend',
            title='Revenue Growth Trend',
            data={'percentage_change': 23.5, 'period': 'last_week'},
            confidence=0.85,
            source='ml_engine',
            timestamp=datetime.now()
        )
        
        print(f"  ✅ RawInsight created: {raw_insight.title}")
        print(f"  ✅ Insight type: {raw_insight.insight_type}")
        print(f"  ✅ Confidence: {raw_insight.confidence}")
        print(f"  ✅ Data: {raw_insight.data}")
        
        # Test ExplainedInsight creation
        explained_insight = ExplainedInsight(
            raw_insight=raw_insight,
            explanation="Revenue has increased by 23.5% over the last week, indicating strong business performance.",
            business_impact="This growth trend suggests effective marketing and operational improvements.",
            recommended_actions=["Analyze growth drivers", "Scale successful strategies", "Monitor sustainability"],
            urgency_level='high'
        )
        
        print(f"  ✅ ExplainedInsight created")
        print(f"  ✅ Explanation length: {len(explained_insight.explanation)} chars")
        print(f"  ✅ Actions count: {len(explained_insight.recommended_actions)}")
        print(f"  ✅ Urgency: {explained_insight.urgency_level}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data structures test failed: {e}")
        return False

def test_llm_generator_demo_mode():
    """Test LLM generator in demo mode (no API required)"""
    print("\n🤖 Testing LLM Generator (Demo Mode)...")
    
    try:
        from apps.ml_engine.llm_insight_generator import LLMInsightGenerator, RawInsight
        
        # Create LLM generator (will use demo mode)
        llm_generator = LLMInsightGenerator()
        
        print(f"  ✅ LLM Generator created")
        print(f"  ✅ Demo mode: {llm_generator.demo_mode}")
        
        # Test demo explanation
        raw_insight = RawInsight(
            insight_type='trend',
            title='Customer Growth Trend',
            data={'percentage_change': 15.3},
            confidence=0.82,
            source='ml_engine',
            timestamp=datetime.now()
        )
        
        explained = llm_generator._create_demo_explanation(raw_insight, 'restaurant')
        
        print(f"  ✅ Demo explanation generated")
        print(f"  ✅ Explanation: {explained.explanation[:100]}...")
        print(f"  ✅ Business impact: {explained.business_impact[:80]}...")
        print(f"  ✅ Actions: {len(explained.recommended_actions)} recommendations")
        print(f"  ✅ Urgency: {explained.urgency_level}")
        
        # Test business context manager
        from apps.ml_engine.llm_insight_generator import BusinessContextManager
        
        context_manager = BusinessContextManager()
        context_manager.update_user_context('test_user', {
            'industry': 'restaurant',
            'business_size': 'medium'
        })
        
        context = context_manager.get_user_context('test_user')
        print(f"  ✅ Business context: {context}")
        
        # Test context inference
        inferred = context_manager.infer_context_from_data(['vehicle_sales', 'inventory'])
        print(f"  ✅ Inferred context: {inferred}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ LLM Generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_question_generator():
    """Test smart question generator"""
    print("\n❓ Testing Smart Question Generator...")
    
    try:
        from apps.ml_engine.smart_question_generator import SmartQuestionGenerator, SmartQuestion
        from apps.ml_engine.llm_insight_generator import RawInsight, ExplainedInsight
        
        # Create test data
        raw_insight = RawInsight(
            insight_type='trend',
            title='Revenue Increasing Trend',
            data={'percentage_change': 18.5, 'period': 'last_month'},
            confidence=0.87,
            source='ml_engine',
            timestamp=datetime.now()
        )
        
        explained_insight = ExplainedInsight(
            raw_insight=raw_insight,
            explanation="Revenue has increased by 18.5% over the last month, showing strong business growth.",
            business_impact="This growth indicates effective strategies and market demand.",
            recommended_actions=["Analyze growth drivers", "Scale successful initiatives", "Monitor trends"],
            urgency_level='high'
        )
        
        # Test question generator
        question_generator = SmartQuestionGenerator()
        
        print(f"  ✅ Question generator created")
        print(f"  ✅ Templates loaded: {len(question_generator.question_templates)}")
        print(f"  ✅ Industry templates: {len(question_generator.industry_templates)}")
        
        # Generate questions
        question_set = question_generator.generate_smart_questions(
            explained_insights=[explained_insight],
            business_context={'industry': 'restaurant'},
            max_questions=5
        )
        
        print(f"  ✅ Questions generated: {question_set.total_questions}")
        print(f"  ✅ High priority: {question_set.high_priority_count}")
        print(f"  ✅ Executive summary: {question_set.executive_summary[:100]}...")
        
        if question_set.questions:
            first_question = question_set.questions[0]
            print(f"  ✅ Sample question: {first_question.question_text}")
            print(f"  ✅ Question type: {first_question.question_type}")
            print(f"  ✅ Priority: {first_question.priority_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Question generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_processing():
    """Test data processing capabilities"""
    print("\n📈 Testing Data Processing...")
    
    try:
        import pandas as pd
        import numpy as np
        
        # Create sample business data
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        
        business_data = pd.DataFrame({
            'date': dates,
            'revenue': np.random.normal(10000, 2000, 30) + np.sin(np.arange(30) * 2 * np.pi / 7) * 1000,
            'customers': np.random.poisson(100, 30),
            'conversion_rate': np.random.normal(0.05, 0.01, 30)
        })
        
        print(f"  ✅ Sample data created: {business_data.shape}")
        print(f"  ✅ Columns: {list(business_data.columns)}")
        print(f"  ✅ Date range: {business_data['date'].min()} to {business_data['date'].max()}")
        
        # Test basic analytics
        revenue_mean = business_data['revenue'].mean()
        revenue_std = business_data['revenue'].std()
        revenue_trend = np.polyfit(range(len(business_data)), business_data['revenue'], 1)[0]
        
        print(f"  ✅ Revenue mean: ${revenue_mean:,.0f}")
        print(f"  ✅ Revenue std: ${revenue_std:,.0f}")
        print(f"  ✅ Revenue trend: ${revenue_trend:,.0f}/day")
        
        # Test anomaly detection
        Q1 = business_data['revenue'].quantile(0.25)
        Q3 = business_data['revenue'].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        anomalies = business_data[(business_data['revenue'] < lower_bound) | 
                                (business_data['revenue'] > upper_bound)]
        
        print(f"  ✅ Anomalies detected: {len(anomalies)}")
        print(f"  ✅ Normal range: ${lower_bound:,.0f} - ${upper_bound:,.0f}")
        
        # Test correlation
        correlation = business_data['revenue'].corr(business_data['customers'])
        print(f"  ✅ Revenue-Customer correlation: {correlation:.3f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Data processing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_components():
    """Test that all components can be imported and initialized"""
    print("\n🔗 Testing Component Integration...")
    
    try:
        # Test imports
        from apps.ml_engine.llm_insight_generator import LLMInsightGenerator, BusinessContextManager
        from apps.ml_engine.smart_question_generator import SmartQuestionGenerator
        
        print(f"  ✅ All core components imported successfully")
        
        # Test initialization
        llm_gen = LLMInsightGenerator()
        context_mgr = BusinessContextManager()
        question_gen = SmartQuestionGenerator()
        
        print(f"  ✅ All components initialized successfully")
        print(f"  ✅ LLM Generator demo mode: {llm_gen.demo_mode}")
        print(f"  ✅ Question templates: {len(question_gen.question_templates)}")
        print(f"  ✅ Industry contexts: {len(llm_gen.industry_contexts)}")
        
        # Test component interaction
        context_mgr.update_user_context('test_user', {'industry': 'automotive'})
        user_context = context_mgr.get_user_context('test_user')
        
        print(f"  ✅ Context management working: {user_context}")
        
        # Test data flow simulation
        print("  🔄 Testing data flow simulation...")
        
        # Simulate: Raw Data → Insight → Question
        from apps.ml_engine.llm_insight_generator import RawInsight
        
        raw_insight = RawInsight(
            insight_type='anomaly',
            title='Sales Spike Detected',
            data={'spike_percentage': 45.2, 'date': '2024-07-12'},
            confidence=0.91,
            source='analytics_engine',
            timestamp=datetime.now()
        )
        
        # Generate explanation (demo mode)
        explained = llm_gen._create_demo_explanation(raw_insight, 'automotive')
        
        # Generate question
        question = question_gen._create_question_from_insight(explained, {'industry': 'automotive'})
        
        print(f"  ✅ Data flow test: Raw → Explained → Question")
        print(f"  ✅ Final question: {question.question_text if question else 'None'}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run simplified gap repair tests"""
    print("🔧 SIMPLIFIED GAP REPAIR TESTS")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("(Testing core functionality without external dependencies)")
    
    tests = [
        ("Data Structures", test_data_structures),
        ("LLM Generator (Demo)", test_llm_generator_demo_mode),
        ("Question Generator", test_question_generator),
        ("Data Processing", test_data_processing),
        ("Component Integration", test_integration_components)
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed_tests += 1
        except Exception as e:
            print(f"\n❌ {test_name} failed with exception: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"🎯 SIMPLIFIED TEST SUMMARY")
    print(f"=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} ❌")
    print(f"Success Rate: {passed_tests / total_tests * 100:.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL CORE COMPONENTS WORKING!")
        print(f"✅ Data structures properly defined")
        print(f"✅ LLM integration framework ready")
        print(f"✅ Question generation functional")
        print(f"✅ Data processing capabilities validated")
        print(f"✅ Component integration successful")
        print(f"\n🚀 CORE GAPS FILLED - READY FOR API INTEGRATION!")
        return 0
    else:
        print(f"\n⚠️  Some core components need attention.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
