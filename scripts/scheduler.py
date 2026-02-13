"""
Scheduler for Nightly Build Routine
Manages automatic execution of maintenance tasks during sleep
"""

import schedule
import time
from datetime import datetime, timedelta
import subprocess
import threading
from pathlib import Path
import sys
import os

def run_nightly_build():
    """Execute the nightly build routine"""
    print(f"[{datetime.now()}] Starting scheduled Nightly Build...")
    
    try:
        # Run the nightly build script
        result = subprocess.run([
            sys.executable, 
            str(Path(__file__).parent / "nightly_build.py")
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"[{datetime.now()}] Nightly Build completed successfully!")
        else:
            print(f"[{datetime.now()}] Nightly Build completed with warnings")
            if result.stderr:
                print(f"Errors: {result.stderr}")
                
    except Exception as e:
        print(f"[{datetime.now()}] Error running nightly build: {e}")

def start_scheduler():
    """Start the scheduler in a background thread"""
    
    # Schedule the nightly build for 3:00 AM daily
    schedule.every().day.at("03:00").do(run_nightly_build)
    
    print("Nightly Build Scheduler Started")
    print("Scheduled to run daily at 3:00 AM")
    print("This will run autonomously while you sleep to fix friction points")
    print("-" * 50)
    
    def run_scheduler():
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    # Start scheduler in background thread
    scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
    scheduler_thread.start()
    
    return scheduler_thread

if __name__ == "__main__":
    print("Setting up Nightly Build Scheduler...")
    
    # Start the scheduler
    scheduler_thread = start_scheduler()
    
    print("The Nightly Build routine is now scheduled!")
    print("Every night at 3:00 AM, I'll:")
    print("  - Check system health")
    print("  - Clean up temporary files") 
    print("  - Organize your workspace")
    print("  - Check for updates")
    print("  - Generate a morning briefing")
    print("")
    print("You'll wake up to improvements and a report of what was done!")
    print("The scheduler will continue running in the background.")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(3600)  # Sleep for an hour before checking again
    except KeyboardInterrupt:
        print("\\nScheduler interrupted. Nightly builds will continue running according to schedule.")