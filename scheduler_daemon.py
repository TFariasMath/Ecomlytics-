"""
Scheduler Daemon

Runs in background to keep the ETL scheduler active.
Execute: python scheduler_daemon.py &

Uses configuration from .env:
- SCHEDULE_ENABLED=true
- SCHEDULE_TIME=02:00
- SCHEDULE_FREQUENCY=daily|6h|12h
- SCHEDULE_EXTRACTORS=woocommerce,analytics,facebook
"""

import time
import os
import sys
import signal
from pathlib import Path

# Add project root
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.scheduler import ETLScheduler
from config.logging_config import setup_logger
from dotenv import load_dotenv

# Setup
logger = setup_logger(__name__)
load_dotenv()

# Global scheduler instance
scheduler = None


def signal_handler(sig, frame):
    """Handle graceful shutdown"""
    global scheduler
    print("\n🛑 Received shutdown signal...")
    if scheduler:
        scheduler.stop()
    print("✅ Scheduler stopped cleanly")
    sys.exit(0)


def main():
    """Main daemon loop"""
    global scheduler
    
    # Check if scheduling is enabled
    if os.getenv('SCHEDULE_ENABLED', 'false').lower() != 'true':
        print("⚠️  Scheduling is not enabled in .env")
        print("   Set SCHEDULE_ENABLED=true to enable automatic scheduling")
        return
    
    # Load configuration
    schedule_time = os.getenv('SCHEDULE_TIME', '02:00')
    schedule_frequency = os.getenv('SCHEDULE_FREQUENCY', 'daily')
    extractors_str = os.getenv('SCHEDULE_EXTRACTORS', 'woocommerce,analytics,facebook')
    extractors = [e.strip() for e in extractors_str.split(',') if e.strip()]
    
    if not extractors:
        print("⚠️  No extractors configured in SCHEDULE_EXTRACTORS")
        return
    
    # Parse time
    try:
        hour, minute = map(int, schedule_time.split(':'))
    except:
        print(f"❌ Invalid time format: {schedule_time}. Use HH:MM")
        return
    
    # Initialize scheduler
    scheduler = ETLScheduler()
    
    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Schedule based on frequency
    if schedule_frequency == 'daily':
        scheduler.schedule_daily(hour, minute, extractors)
        print(f"✅ Scheduled daily ETL at {hour:02d}:{minute:02d}")
        
    elif schedule_frequency in ['6h', '12h']:
        hours = int(schedule_frequency.replace('h', ''))
        scheduler.schedule_periodic(hours, extractors)
        print(f"✅ Scheduled periodic ETL every {hours} hours")
        
    else:
        print(f"❌ Invalid frequency: {schedule_frequency}")
        print("   Use: daily, 6h, or 12h")
        return
    
    # Start scheduler
    scheduler.start()
    
    print(f"\n{'='*50}")
    print(f"  ETL Scheduler Daemon Running")
    print(f"{'='*50}")
    print(f"  Extractors: {', '.join(extractors)}")
    print(f"  Frequency: {schedule_frequency}")
    if schedule_frequency == 'daily':
        print(f"  Time: {hour:02d}:{minute:02d}")
    print(f"{'='*50}\n")
    
    # Show next run times
    jobs = scheduler.get_jobs()
    if jobs:
        print("Scheduled Jobs:")
        for job in jobs:
            print(f"  • {job['name']}")
            print(f"    Next run: {job['next_run']}")
            print()
    
    print("Press Ctrl+C to stop\n")
    
    # Keep alive
    try:
        while True:
            time.sleep(60)
            # Optionally log heartbeat
            # logger.debug("Scheduler daemon heartbeat")
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()
