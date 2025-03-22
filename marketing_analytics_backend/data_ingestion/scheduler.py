"""
Scheduler module for data ingestion tasks.
Initializes and configures the APScheduler for periodic data fetching.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import current_app

scheduler = None

def init_scheduler(app):
    """Initialize the scheduler with the application context."""
    global scheduler
    
    if scheduler is None:
        jobstores = {
            'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
        }
        
        scheduler = BackgroundScheduler(jobstores=jobstores)
        
        # Add jobs from configuration
        for job in app.config.get('JOBS', []):
            module, func = job['func'].split(':')
            job_func = getattr(__import__(module, fromlist=[func]), func)
            
            if job.get('trigger') == 'interval':
                scheduler.add_job(
                    func=job_func,
                    trigger='interval',
                    id=job['id'],
                    hours=job.get('hours', 24),
                    minutes=job.get('minutes', 0),
                    replace_existing=True
                )
            elif job.get('trigger') == 'cron':
                scheduler.add_job(
                    func=job_func,
                    trigger='cron',
                    id=job['id'],
                    hour=job.get('hour', 0),
                    minute=job.get('minute', 0),
                    replace_existing=True
                )
        
        scheduler.start()
        app.logger.info('Scheduler started')
        
        # Shut down scheduler when app is shutting down
        app.teardown_appcontext(lambda _: scheduler.shutdown(wait=False))
