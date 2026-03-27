"""
ETL Scheduler Module

Manages automatic scheduled execution of ETL extractors using APScheduler.
Allows users to configure daily/periodic extractions without manual intervention.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

logger = logging.getLogger(__name__)


class ETLScheduler:
    """
    Manages scheduled ETL executions
    """
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.jobs = {}
        logger.info("ETLScheduler initialized")
    
    def schedule_daily(self, hour: int, minute: int, extractors: list):
        """
        Schedule daily ETL execution
        
        Args:
            hour: Hour to run (0-23)
            minute: Minute to run (0-59)
            extractors: List of extractor names to run
        """
        job_id = 'daily_etl'
        
        # Remove existing job if any
        if job_id in self.jobs:
            try:
                self.scheduler.remove_job(job_id)
                logger.info(f"Removed existing job: {job_id}")
            except Exception:
                pass
        
        # Create new job
        trigger = CronTrigger(hour=hour, minute=minute)
        job = self.scheduler.add_job(
            func=self._run_scheduled_etl,
            trigger=trigger,
            args=[extractors],
            id=job_id,
            replace_existing=True,
            name=f"Daily ETL at {hour:02d}:{minute:02d}"
        )
        
        self.jobs[job_id] = job
        logger.info(f"Scheduled daily ETL at {hour:02d}:{minute:02d} for: {', '.join(extractors)}")
        
        return True
    
    def schedule_periodic(self, hours: int, extractors: list):
        """
        Schedule periodic ETL execution every N hours
        
        Args:
            hours: Interval in hours (e.g., 6 for every 6 hours)
            extractors: List of extractor names
        """
        job_id = f'periodic_etl_{hours}h'
        
        # Remove existing
        if job_id in self.jobs:
            try:
                self.scheduler.remove_job(job_id)
            except Exception:
                pass
        
        # Create interval job
        from apscheduler.triggers.interval import IntervalTrigger
        trigger = IntervalTrigger(hours=hours)
        
        job = self.scheduler.add_job(
            func=self._run_scheduled_etl,
            trigger=trigger,
            args=[extractors],
            id=job_id,
            replace_existing=True,
            name=f"ETL every {hours}h"
        )
        
        self.jobs[job_id] = job
        logger.info(f"Scheduled periodic ETL every {hours}h for: {', '.join(extractors)}")
        
        return True
    
    def _run_scheduled_etl(self, extractors: list):
        """
        Execute scheduled ETL
        
        Args:
            extractors: List of extractor names to run
        """
        logger.info(f"🕐 Executing scheduled ETL: {extractors}")
        
        try:
            from utils.etl_runner import run_all_etl_extractors
            
            # Run extractors
            results = run_all_etl_extractors()
            
            # Log results
            for name, result in results.items():
                if result['status'] == 'success':
                    logger.info(f"✅ {name}: Success - {result.get('message', '')}")
                elif result['status'] == 'error':
                    logger.error(f"❌ {name}: Error - {result.get('message', '')}")
                else:
                    logger.info(f"⚪ {name}: Skipped - {result.get('message', '')}")
            
            # Check for errors
            errors = [r for r in results.values() if r['status'] == 'error']
            if errors:
                logger.warning(f"⚠️ {len(errors)} extractor(s) failed during scheduled run")
            else:
                logger.info("✅ All scheduled extractors completed successfully")
                
        except Exception as e:
            logger.error(f"Error in scheduled ETL execution: {str(e)}", exc_info=True)
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("✅ Scheduler started")
            return True
        else:
            logger.warning("Scheduler already running")
            return False
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("🛑 Scheduler stopped")
            return True
        else:
            logger.warning("Scheduler not running")
            return False
    
    def get_jobs(self):
        """Get all scheduled jobs"""
        jobs_info = []
        for job in self.scheduler.get_jobs():
            jobs_info.append({
                'id': job.id,
                'name': job.name,
                'next_run': job.next_run_time.strftime('%Y-%m-%d %H:%M:%S') if job.next_run_time else None
            })
        return jobs_info
    
    def clear_all_jobs(self):
        """Remove all scheduled jobs"""
        self.scheduler.remove_all_jobs()
        self.jobs.clear()
        logger.info("All jobs cleared")
