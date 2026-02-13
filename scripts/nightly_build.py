"""
Nightly Build Routine - Autonomous Maintenance and Improvement Script
Runs during sleep to fix friction points and prepare new tools for morning briefing
"""

import os
import sys
import time
import subprocess
import json
from datetime import datetime
import psutil
import shutil
from pathlib import Path

class NightlyBuild:
    def __init__(self):
        self.build_log = []
        self.friction_points = []
        self.workspace_dir = Path.cwd()
        self.log_file = self.workspace_dir / "nightly_build_log.txt"
        
    def log(self, message):
        """Add message to build log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.build_log.append(log_entry)
        print(log_entry)
        
    def check_system_health(self):
        """Check overall system health"""
        self.log("🔍 Checking system health...")
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        self.log(f"   CPU Usage: {cpu_percent}%")
        
        # Memory usage
        memory = psutil.virtual_memory()
        self.log(f"   Memory Usage: {memory.percent}% ({memory.used // 1024 // 1024}MB used)")
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        self.log(f"   Disk Usage: {disk_percent:.1f}% ({disk.free // 1024 // 1024 // 1024}GB free)")
        
        # If any usage is high, add to friction points
        if cpu_percent > 80:
            self.friction_points.append(f"High CPU usage: {cpu_percent}%")
        if memory.percent > 85:
            self.friction_points.append(f"High memory usage: {memory.percent}%")
        if disk_percent > 85:
            self.friction_points.append(f"High disk usage: {disk_percent:.1f}%")
    
    def cleanup_temp_files(self):
        """Clean up temporary files and logs"""
        self.log("🧹 Cleaning up temporary files...")
        
        temp_dirs = [
            Path.home() / ".cache",
            Path.home() / ".tmp",
            self.workspace_dir / "temp",
            self.workspace_dir / "tmp",
            self.workspace_dir / "logs"
        ]
        
        cleaned_count = 0
        for temp_dir in temp_dirs:
            if temp_dir.exists():
                for file_path in temp_dir.rglob("*"):
                    if file_path.is_file():
                        try:
                            # Only delete files older than 7 days
                            if time.time() - file_path.stat().st_mtime > 7 * 24 * 3600:
                                file_path.unlink()
                                cleaned_count += 1
                        except:
                            continue  # Skip files that can't be deleted
        
        self.log(f"   Cleaned {cleaned_count} temporary files")
    
    def update_workspace(self):
        """Update workspace files and organize"""
        self.log("📦 Organizing workspace...")
        
        # Look for unorganized files in workspace
        unorganized_files = []
        for file_path in self.workspace_dir.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in ['.txt', '.log', '.tmp']:
                unorganized_files.append(file_path.name)
        
        if unorganized_files:
            org_dir = self.workspace_dir / "organized"
            org_dir.mkdir(exist_ok=True)
            
            for filename in unorganized_files:
                file_path = self.workspace_dir / filename
                try:
                    shutil.move(str(file_path), str(org_dir / filename))
                except:
                    continue  # Skip if can't move
            
            self.log(f"   Organized {len(unorganized_files)} files into organized/ directory")
        else:
            self.log("   No unorganized files found")
    
    def check_for_updates(self):
        """Check for system updates"""
        self.log("🔄 Checking for updates...")
        
        # Check if git repos need pulling
        git_repos = []
        for item in self.workspace_dir.iterdir():
            if item.is_dir() and (item / ".git").exists():
                git_repos.append(item)
        
        updated_repos = []
        for repo in git_repos:
            try:
                result = subprocess.run(['git', '-C', str(repo), 'pull'], 
                                      capture_output=True, text=True, timeout=30)
                if result.returncode == 0 and "Already up to date" not in result.stdout:
                    updated_repos.append(repo.name)
            except:
                continue  # Skip if git command fails
        
        if updated_repos:
            self.log(f"   Updated Git repositories: {', '.join(updated_repos)}")
        else:
            self.log("   Git repositories already up to date")
    
    def generate_briefing(self):
        """Generate morning briefing"""
        self.log("📋 Generating morning briefing...")
        
        briefing = f"""
=== NIGHTLY BUILD REPORT ===
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Status: {'SUCCESS' if not self.friction_points else 'ISSUES FOUND'}

SUMMARY OF CHANGES:
"""
        
        for entry in self.build_log:
            if any(keyword in entry for keyword in ['Cleaned', 'Organized', 'Updated', 'Created']):
                briefing += f"- {entry.split(']', 1)[1].strip()}\n"
        
        if self.friction_points:
            briefing += "\nFRICTION POINTS DETECTED:\n"
            for point in self.friction_points:
                briefing += f"- {point}\n"
        else:
            briefing += "\nNo major friction points detected.\n"
        
        briefing += f"\nTotal actions performed: {len([e for e in self.build_log if any(k in e for k in ['Cleaned', 'Organized', 'Updated', 'Created'])])}"
        briefing += "\n\nHave a productive day! ✨"
        
        # Save briefing to file
        briefing_file = self.workspace_dir / "morning_briefing.txt"
        with open(briefing_file, 'w', encoding='utf-8') as f:
            f.write(briefing)
        
        self.log(f"   Briefing saved to {briefing_file.name}")
    
    def run(self):
        """Execute the nightly build routine"""
        self.log("🚀 Starting Nightly Build Routine")
        self.log("=" * 50)
        
        try:
            # Perform all checks and maintenance
            self.check_system_health()
            self.cleanup_temp_files()
            self.update_workspace()
            self.check_for_updates()
            self.generate_briefing()
            
            # Write full log
            with open(self.log_file, 'w', encoding='utf-8') as f:
                for entry in self.build_log:
                    f.write(entry + '\n')
            
            self.log("=" * 50)
            self.log("✅ Nightly Build Complete!")
            
        except Exception as e:
            self.log(f"❌ Error during nightly build: {str(e)}")
            raise


def schedule_nightly_build():
    """Function to schedule the nightly build using system scheduler"""
    import platform
    
    script_path = Path(__file__).resolve()
    if platform.system() == "Windows":
        # Create a scheduled task using Windows Task Scheduler
        try:
            task_command = [
                "schtasks",
                "/create",
                "/tn",
                "MIST_Nightly_Build",
                "/tr",
                f"python {script_path}",
                "/sc",
                "daily",
                "/st",
                "03:00",
                "/f",
            ]
            subprocess.run(task_command, check=True)
            print("📅 Scheduled Nightly Build for 3:00 AM daily")
        except:
            print("⚠️ Could not schedule task automatically. Please set up manually.")
    else:
        # For Unix-like systems, could use cron
        print("🔧 To schedule nightly builds, add this to your crontab:")
        print("   0 3 * * * python3", script_path)


if __name__ == "__main__":
    # Run the nightly build
    build = NightlyBuild()
    build.run()
    
    # Optionally schedule future runs
    print("\n" + "="*50)
    print("Would you like to schedule future nightly builds?")
    print("This will run the routine automatically every night at 3:00 AM.")
    
    response = input("Schedule nightly builds? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        schedule_nightly_build()
