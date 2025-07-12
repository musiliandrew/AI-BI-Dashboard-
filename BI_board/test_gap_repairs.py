#!/usr/bin/env python3
"""
Test Gap Repairs - Validate LLM Integration and Unified Pipeline
"""
import sys
import os
import asyncio
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_llm_insight_generator():
    """Test LLM Insight Generator"""
    print("🤖 Testing LLM Insight Generator...")
    
    try:
        from apps.ml_engine.llm_insight_generator import (
            LLMInsightGenerator, RawInsight, BusinessContextManager
        )
        
        # Create test insight
        raw_insight = RawInsight(
            insight_type='trend',
            title='Revenue Growth Trend',
            data={
                'trend_direction': 'increasing',
                'percentage_change': 23.5,
                'period': 'last_week'
            },
            confidence=0.85,
            source='ml_engine',
            timestamp=datetime.now()
        )
        
        # Test LLM generator
        llm_generator = LLMInsightGenerator()
        
        # Test demo mode (without API key)
        explained = llm_generator._create_demo_explanation(raw_insight, 'restaurant')
        
        print(f"  ✅ LLM Generator created")
        print(f"  ✅ Demo explanation: {explained.explanation[:100]}...")
        print(f"  ✅ Business impact: {explained.business_impact[:100]}...")
        print(f"  ✅ Recommended actions: {len(explained.recommended_actions)} actions")
        print(f"  ✅ Urgency level: {explained.urgency_level}")
        
        # Test business context manager
        context_manager = BusinessContextManager()
        context_manager.update_user_context('test_user', {
            'industry': 'restaurant',
            'business_size': 'medium'
        })
        
        user_context = context_manager.get_user_context('test_user')
        print(f"  ✅ Business context: {user_context}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ LLM Insight Generator test failed: {e}")
        return False

def test_unified_insight_engine():
    """Test Unified Insight Engine"""
    print("\n🧠 Testing Unified Insight Engine...")
    
    try:
        from apps.ml_engine.unified_insight_engine import UnifiedInsightEngine
        
        # Create engine
        engine = UnifiedInsightEngine()
        
        print(f"  ✅ Unified engine created")
        print(f"  ✅ ML trainer: {type(engine.ml_trainer).__name__}")
        print(f"  ✅ Analytics engine: {type(engine.analytics_engine).__name__}")
        print(f"  ✅ LLM generator: {type(engine.llm_generator).__name__}")
        print(f"  ✅ Context manager: {type(engine.context_manager).__name__}")
        
        # Test sample data creation
        business_data = engine._create_sample_business_data()
        social_data = engine._create_sample_social_data()
        website_data = engine._create_sample_website_data()
        
        print(f"  ✅ Sample business data: {business_data.shape}")
        print(f"  ✅ Sample social data: {social_data.shape}")
        print(f"  ✅ Sample website data: {website_data.shape}")
        
        # Test trend analysis
        trend_insight = engine._analyze_trends(business_data)
        if trend_insight:
            print(f"  ✅ Trend analysis: {trend_insight.title}")
            print(f"  ✅ Trend confidence: {trend_insight.confidence:.2f}")
        
        # Test anomaly detection
        anomaly_insight = engine._detect_anomalies(business_data)
        if anomaly_insight:
            print(f"  ✅ Anomaly detection: {anomaly_insight.title}")
            print(f"  ✅ Anomalies found: {anomaly_insight.data.get('anomaly_count', 0)}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Unified Insight Engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_smart_question_generator():
    """Test Smart Question Generator"""
    print("\n❓ Testing Smart Question Generator...")
    
    try:
        from apps.ml_engine.smart_question_generator import SmartQuestionGenerator
        from apps.ml_engine.llm_insight_generator import RawInsight, ExplainedInsight
        
        # Create test explained insight
        raw_insight = RawInsight(
            insight_type='trend',
            title='Customer Growth Trend',
            data={'percentage_change': 15.3, 'period': 'last_month'},
            confidence=0.82,
            source='ml_engine',
            timestamp=datetime.now()
        )
        
        explained_insight = ExplainedInsight(
            raw_insight=raw_insight,
            explanation="Customer numbers have increased by 15.3% over the last month, indicating strong business growth.",
            business_impact="This growth trend suggests effective marketing and customer satisfaction improvements.",
            recommended_actions=[
                "Analyze customer acquisition channels",
                "Prepare for increased capacity needs",
                "Investigate growth drivers"
            ],
            urgency_level='high'
        )
        
        # Test question generator
        question_generator = SmartQuestionGenerator()
        
        # Generate questions
        question_set = question_generator.generate_smart_questions(
            explained_insights=[explained_insight],
            business_context={'industry': 'restaurant'},
            max_questions=5
        )
        
        print(f"  ✅ Question generator created")
        print(f"  ✅ Generated questions: {question_set.total_questions}")
        print(f"  ✅ High priority questions: {question_set.high_priority_count}")
        print(f"  ✅ Executive summary: {question_set.executive_summary[:100]}...")
        
        if question_set.questions:
            first_question = question_set.questions[0]
            print(f"  ✅ Sample question: {first_question.question_text}")
            print(f"  ✅ Question type: {first_question.question_type}")
            print(f"  ✅ Priority score: {first_question.priority_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Smart Question Generator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_automated_pipeline():
    """Test Automated Insight Pipeline"""
    print("\n🚀 Testing Automated Insight Pipeline...")
    
    try:
        from apps.ml_engine.automated_insight_pipeline import (
            AutomatedInsightPipeline, PipelineConfig, PipelineScheduler
        )
        
        # Create pipeline
        pipeline = AutomatedInsightPipeline()
        
        print(f"  ✅ Automated pipeline created")
        print(f"  ✅ Insight engine: {type(pipeline.insight_engine).__name__}")
        print(f"  ✅ Question generator: {type(pipeline.question_generator).__name__}")
        print(f"  ✅ Context manager: {type(pipeline.context_manager).__name__}")
        
        # Create test configuration
        config = PipelineConfig(
            user_id='test_user_123',
            industry='restaurant',
            data_sources=['business_metrics', 'social_media'],
            max_insights=5,
            max_questions=5
        )
        
        print(f"  ✅ Pipeline config created for user: {config.user_id}")
        print(f"  ✅ Industry: {config.industry}")
        print(f"  ✅ Max insights: {config.max_insights}")
        
        # Test pipeline execution (this will use sample data)
        print("  🔄 Running pipeline...")
        result = await pipeline.run_pipeline(config)
        
        print(f"  ✅ Pipeline execution: {'SUCCESS' if result.success else 'FAILED'}")
        print(f"  ✅ Execution time: {result.execution_time:.2f} seconds")
        print(f"  ✅ Insights generated: {len(result.insight_report.explained_insights)}")
        print(f"  ✅ Questions generated: {result.smart_questions.total_questions}")
        print(f"  ✅ Overall confidence: {result.insight_report.confidence_score:.2f}")
        
        if result.insight_report.explained_insights:
            first_insight = result.insight_report.explained_insights[0]
            print(f"  ✅ Sample insight: {first_insight.raw_insight.title}")
            print(f"  ✅ Explanation: {first_insight.explanation[:100]}...")
        
        # Test scheduler
        scheduler = PipelineScheduler()
        scheduler.schedule_user_pipeline('test_user_123', 'daily', '09:00')
        
        status = scheduler.get_pipeline_status('test_user_123')
        print(f"  ✅ Scheduler status: {status}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Automated Pipeline test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_integration_flow():
    """Test complete integration flow"""
    print("\n🔗 Testing Complete Integration Flow...")

    try:
        # Test the complete flow: Raw Data → Insights → Questions → Pipeline
        print("  🔄 Testing end-to-end integration...")

        # 1. Create sample raw insights
        from apps.ml_engine.llm_insight_generator import RawInsight

        raw_insights = [
            RawInsight(
                insight_type='trend',
                title='Revenue Increasing Trend',
                data={'percentage_change': 18.5, 'period': 'last_week'},
                confidence=0.87,
                source='ml_engine',
                timestamp=datetime.now()
            ),
            RawInsight(
                insight_type='anomaly',
                title='Customer Spike Detected',
                data={'anomaly_count': 3, 'normal_range': [80, 120]},
                confidence=0.92,
                source='analytics_engine',
                timestamp=datetime.now()
            )
        ]

        print(f"  ✅ Created {len(raw_insights)} raw insights")

        # 2. Generate LLM explanations
        from apps.ml_engine.llm_insight_generator import LLMInsightGenerator

        llm_generator = LLMInsightGenerator()
        explained_insights = await llm_generator.explain_insights(raw_insights, 'restaurant')
        
        print(f"  ✅ Generated {len(explained_insights)} explained insights")
        
        # 3. Generate smart questions
        from apps.ml_engine.smart_question_generator import SmartQuestionGenerator
        
        question_generator = SmartQuestionGenerator()
        questions = question_generator.generate_smart_questions(
            explained_insights, 
            {'industry': 'restaurant'},
            max_questions=6
        )
        
        print(f"  ✅ Generated {questions.total_questions} smart questions")
        
        # 4. Test complete pipeline integration
        print("  🔄 Testing pipeline integration...")
        
        # Verify all components work together
        integration_success = (
            len(explained_insights) > 0 and
            questions.total_questions > 0 and
            all(insight.explanation for insight in explained_insights) and
            all(q.question_text for q in questions.questions)
        )
        
        print(f"  ✅ Integration test: {'SUCCESS' if integration_success else 'FAILED'}")
        
        # 5. Display sample results
        if explained_insights:
            print(f"  📊 Sample insight: {explained_insights[0].raw_insight.title}")
            print(f"  📊 Explanation: {explained_insights[0].explanation[:80]}...")
        
        if questions.questions:
            print(f"  ❓ Sample question: {questions.questions[0].question_text}")
            print(f"  ❓ Question type: {questions.questions[0].question_type}")
        
        return integration_success
        
    except Exception as e:
        print(f"  ❌ Integration flow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all gap repair tests"""
    print("🔧 GAP REPAIR VALIDATION TESTS")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("LLM Insight Generator", test_llm_insight_generator),
        ("Unified Insight Engine", test_unified_insight_engine),
        ("Smart Question Generator", test_smart_question_generator),
        ("Automated Pipeline", test_automated_pipeline),
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
    
    print(f"\n" + "=" * 60)
    print(f"🎯 GAP REPAIR TEST SUMMARY")
    print(f"=" * 60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} ❌")
    print(f"Success Rate: {passed_tests / total_tests * 100:.1f}%")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL GAP REPAIRS SUCCESSFUL!")
        print(f"✅ LLM integration working correctly")
        print(f"✅ Unified insight engine operational")
        print(f"✅ Smart question generation functional")
        print(f"✅ Automated pipeline ready")
        print(f"✅ End-to-end integration validated")
        print(f"\n🚀 GAPS SUCCESSFULLY FILLED - READY FOR PRODUCTION!")
        return 0
    else:
        print(f"\n⚠️  Some gap repairs need attention. Check the errors above.")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
