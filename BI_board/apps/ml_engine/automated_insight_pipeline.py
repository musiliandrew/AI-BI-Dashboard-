"""
Automated Insight Pipeline
Orchestrates the complete flow: Data → Analysis → Insight Generation → LLM Explanation → Business Recommendations
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

from .unified_insight_engine import UnifiedInsightEngine, ComprehensiveInsightReport
from .smart_question_generator import SmartQuestionGenerator, QuestionSet
from .llm_insight_generator import BusinessContextManager
from ..data_pipeline.models import DataSource, DataPipeline

logger = logging.getLogger(__name__)

@dataclass
class PipelineResult:
    """Result of the automated insight pipeline"""
    insight_report: ComprehensiveInsightReport
    smart_questions: QuestionSet
    pipeline_metadata: Dict[str, Any]
    execution_time: float
    success: bool
    error_message: Optional[str] = None

@dataclass
class PipelineConfig:
    """Configuration for the insight pipeline"""
    user_id: str
    industry: Optional[str] = None
    data_sources: Optional[List[str]] = None
    max_insights: int = 10
    max_questions: int = 8
    min_confidence: float = 0.6
    include_industry_analysis: bool = True
    generate_executive_summary: bool = True

class AutomatedInsightPipeline:
    """Automated pipeline for generating business insights"""
    
    def __init__(self):
        self.insight_engine = UnifiedInsightEngine()
        self.question_generator = SmartQuestionGenerator()
        self.context_manager = BusinessContextManager()
        
        # Pipeline statistics
        self.execution_stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'average_execution_time': 0.0,
            'last_run': None
        }
    
    async def run_pipeline(self, config: PipelineConfig) -> PipelineResult:
        """Run the complete automated insight pipeline"""
        
        start_time = datetime.now()
        logger.info(f"Starting automated insight pipeline for user {config.user_id}")
        
        try:
            # Update statistics
            self.execution_stats['total_runs'] += 1
            self.execution_stats['last_run'] = start_time
            
            # Step 1: Generate comprehensive insights
            logger.info("Step 1: Generating comprehensive insights...")
            insight_report = await self.insight_engine.generate_comprehensive_insights(
                user_id=config.user_id,
                data_sources=config.data_sources,
                industry=config.industry
            )
            
            # Step 2: Generate smart questions
            logger.info("Step 2: Generating smart questions...")
            business_context = self.context_manager.get_user_context(config.user_id)
            smart_questions = self.question_generator.generate_smart_questions(
                explained_insights=insight_report.explained_insights,
                business_context=business_context,
                max_questions=config.max_questions
            )
            
            # Step 3: Create pipeline metadata
            execution_time = (datetime.now() - start_time).total_seconds()
            pipeline_metadata = self._create_pipeline_metadata(config, insight_report, smart_questions, execution_time)
            
            # Update success statistics
            self.execution_stats['successful_runs'] += 1
            self._update_average_execution_time(execution_time)
            
            logger.info(f"Pipeline completed successfully in {execution_time:.2f} seconds")
            
            return PipelineResult(
                insight_report=insight_report,
                smart_questions=smart_questions,
                pipeline_metadata=pipeline_metadata,
                execution_time=execution_time,
                success=True
            )
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            error_message = f"Pipeline failed: {str(e)}"
            logger.error(error_message)
            
            return PipelineResult(
                insight_report=self._create_empty_report(),
                smart_questions=self._create_empty_questions(),
                pipeline_metadata={'error': error_message, 'execution_time': execution_time},
                execution_time=execution_time,
                success=False,
                error_message=error_message
            )
    
    async def run_scheduled_pipeline(self, user_id: str, schedule_type: str = 'daily') -> PipelineResult:
        """Run pipeline on a schedule (daily, weekly, monthly)"""
        
        logger.info(f"Running scheduled {schedule_type} pipeline for user {user_id}")
        
        # Get user context to determine configuration
        business_context = self.context_manager.get_user_context(user_id)
        
        # Create configuration based on schedule type
        config = PipelineConfig(
            user_id=user_id,
            industry=business_context.get('industry'),
            data_sources=business_context.get('data_sources'),
            max_insights=12 if schedule_type == 'weekly' else 10,
            max_questions=10 if schedule_type == 'weekly' else 8,
            min_confidence=0.5 if schedule_type == 'daily' else 0.6
        )
        
        return await self.run_pipeline(config)
    
    async def run_real_time_pipeline(self, user_id: str, trigger_event: str, 
                                   event_data: Dict[str, Any]) -> PipelineResult:
        """Run pipeline triggered by real-time events"""
        
        logger.info(f"Running real-time pipeline for user {user_id}, trigger: {trigger_event}")
        
        # Create focused configuration for real-time analysis
        config = PipelineConfig(
            user_id=user_id,
            max_insights=5,  # Fewer insights for real-time
            max_questions=5,
            min_confidence=0.7,  # Higher confidence for real-time alerts
            include_industry_analysis=False  # Skip for speed
        )
        
        # Add trigger context
        business_context = self.context_manager.get_user_context(user_id)
        business_context['trigger_event'] = trigger_event
        business_context['event_data'] = event_data
        self.context_manager.update_user_context(user_id, business_context)
        
        return await self.run_pipeline(config)
    
    def _create_pipeline_metadata(self, config: PipelineConfig, 
                                insight_report: ComprehensiveInsightReport,
                                smart_questions: QuestionSet,
                                execution_time: float) -> Dict[str, Any]:
        """Create metadata about the pipeline execution"""
        
        return {
            'pipeline_version': '1.0',
            'execution_time_seconds': execution_time,
            'config': {
                'user_id': config.user_id,
                'industry': config.industry,
                'max_insights': config.max_insights,
                'max_questions': config.max_questions,
                'min_confidence': config.min_confidence
            },
            'results_summary': {
                'total_insights': len(insight_report.explained_insights),
                'critical_insights': sum(1 for i in insight_report.explained_insights if i.urgency_level == 'critical'),
                'high_priority_insights': sum(1 for i in insight_report.explained_insights if i.urgency_level == 'high'),
                'total_questions': smart_questions.total_questions,
                'high_priority_questions': smart_questions.high_priority_count,
                'overall_confidence': insight_report.confidence_score
            },
            'data_sources_analyzed': config.data_sources or [],
            'generated_at': datetime.now().isoformat(),
            'pipeline_stats': self.execution_stats.copy()
        }
    
    def _update_average_execution_time(self, execution_time: float):
        """Update average execution time statistics"""
        
        current_avg = self.execution_stats['average_execution_time']
        successful_runs = self.execution_stats['successful_runs']
        
        # Calculate new average
        new_avg = ((current_avg * (successful_runs - 1)) + execution_time) / successful_runs
        self.execution_stats['average_execution_time'] = new_avg
    
    def _create_empty_report(self) -> ComprehensiveInsightReport:
        """Create empty report for failed pipeline"""
        
        return ComprehensiveInsightReport(
            explained_insights=[],
            recommendations=["Check data connections", "Verify data quality", "Contact support"],
            executive_summary="Unable to generate insights due to pipeline failure.",
            key_metrics={},
            priority_actions=["Review pipeline logs"],
            generated_at=datetime.now(),
            confidence_score=0.0
        )
    
    def _create_empty_questions(self) -> QuestionSet:
        """Create empty question set for failed pipeline"""
        
        return QuestionSet(
            questions=[],
            executive_summary="No questions available due to pipeline failure.",
            total_questions=0,
            high_priority_count=0,
            generated_at=datetime.now()
        )

class PipelineScheduler:
    """Scheduler for automated insight pipelines"""
    
    def __init__(self):
        self.pipeline = AutomatedInsightPipeline()
        self.scheduled_users = {}  # user_id -> schedule_config
        self.running_tasks = {}    # user_id -> asyncio.Task
    
    def schedule_user_pipeline(self, user_id: str, schedule_type: str = 'daily', 
                             schedule_time: str = '09:00'):
        """Schedule automated pipeline for a user"""
        
        self.scheduled_users[user_id] = {
            'schedule_type': schedule_type,
            'schedule_time': schedule_time,
            'last_run': None,
            'next_run': self._calculate_next_run(schedule_type, schedule_time)
        }
        
        logger.info(f"Scheduled {schedule_type} pipeline for user {user_id} at {schedule_time}")
    
    def unschedule_user_pipeline(self, user_id: str):
        """Remove scheduled pipeline for a user"""
        
        if user_id in self.scheduled_users:
            del self.scheduled_users[user_id]
        
        if user_id in self.running_tasks:
            self.running_tasks[user_id].cancel()
            del self.running_tasks[user_id]
        
        logger.info(f"Unscheduled pipeline for user {user_id}")
    
    async def run_scheduled_pipelines(self):
        """Run all scheduled pipelines that are due"""
        
        current_time = datetime.now()
        
        for user_id, schedule_config in self.scheduled_users.items():
            next_run = schedule_config['next_run']
            
            if current_time >= next_run and user_id not in self.running_tasks:
                # Start pipeline task
                task = asyncio.create_task(
                    self._run_user_pipeline(user_id, schedule_config)
                )
                self.running_tasks[user_id] = task
    
    async def _run_user_pipeline(self, user_id: str, schedule_config: Dict[str, Any]):
        """Run pipeline for a specific user"""
        
        try:
            schedule_type = schedule_config['schedule_type']
            
            # Run the pipeline
            result = await self.pipeline.run_scheduled_pipeline(user_id, schedule_type)
            
            # Update schedule
            schedule_config['last_run'] = datetime.now()
            schedule_config['next_run'] = self._calculate_next_run(
                schedule_type, schedule_config['schedule_time']
            )
            
            # Log result
            if result.success:
                logger.info(f"Scheduled pipeline completed for user {user_id}: "
                          f"{len(result.insight_report.explained_insights)} insights, "
                          f"{result.smart_questions.total_questions} questions")
            else:
                logger.error(f"Scheduled pipeline failed for user {user_id}: {result.error_message}")
        
        except Exception as e:
            logger.error(f"Error running scheduled pipeline for user {user_id}: {e}")
        
        finally:
            # Remove from running tasks
            if user_id in self.running_tasks:
                del self.running_tasks[user_id]
    
    def _calculate_next_run(self, schedule_type: str, schedule_time: str) -> datetime:
        """Calculate next run time based on schedule"""
        
        now = datetime.now()
        hour, minute = map(int, schedule_time.split(':'))
        
        if schedule_type == 'daily':
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
        
        elif schedule_type == 'weekly':
            # Run on Mondays
            days_ahead = 0 - now.weekday()  # Monday is 0
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        elif schedule_type == 'monthly':
            # Run on the 1st of each month
            if now.day == 1 and now.hour < hour:
                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                # Next month
                if now.month == 12:
                    next_run = now.replace(year=now.year + 1, month=1, day=1, 
                                         hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    next_run = now.replace(month=now.month + 1, day=1, 
                                         hour=hour, minute=minute, second=0, microsecond=0)
        
        else:
            # Default to daily
            next_run = now + timedelta(days=1)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        return next_run
    
    def get_pipeline_status(self, user_id: str) -> Dict[str, Any]:
        """Get pipeline status for a user"""
        
        if user_id not in self.scheduled_users:
            return {'scheduled': False}
        
        schedule_config = self.scheduled_users[user_id]
        is_running = user_id in self.running_tasks
        
        return {
            'scheduled': True,
            'schedule_type': schedule_config['schedule_type'],
            'schedule_time': schedule_config['schedule_time'],
            'last_run': schedule_config['last_run'].isoformat() if schedule_config['last_run'] else None,
            'next_run': schedule_config['next_run'].isoformat(),
            'is_running': is_running
        }
