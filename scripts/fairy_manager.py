#!/usr/bin/env python3
"""
Fairy System Manager
Tool to manage MIST fairy systems - enable/disable as needed
"""

import os
import sys
import subprocess
import signal
from pathlib import Path

def find_fairy_processes():
    """Find all running fairy-related processes"""
    try:
        result = subprocess.run(['wmic', 'process', 'where', "name='python.exe'", 'get', 'commandline,processid'], 
                                capture_output=True, text=True, check=True)
        lines = result.stdout.split('\n')
        
        fairy_processes = []
        for line in lines:
            if 'fairy' in line.lower() or 'FAIRY' in line or 'orb' in line.lower():
                # Extract PID from the line
                parts = line.strip().split()
                if len(parts) > 1:
                    try:
                        pid = int([p for p in parts if p.isdigit()][-1])
                        fairy_processes.append({'pid': pid, 'cmdline': line})
                    except (ValueError, IndexError):
                        continue
        
        return fairy_processes
    except Exception as e:
        print(f"Error finding fairy processes: {e}")
        return []

def find_fairy_files():
    """Find all fairy-related Python files in the workspace"""
    workspace_path = Path("C:/Users/nator/clawd")
    fairy_files = []
    
    for ext in ['.py']:
        for file_path in workspace_path.rglob(f'*{ext}'):
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                if any(keyword in content.lower() for keyword in ['fairy', 'mist', 'avatar', 'orb']):
                    if any(fairy_type in file_path.name.lower() for fairy_type in ['fairy', 'avatar', 'orb', 'interface']):
                        fairy_files.append(str(file_path))
            except:
                continue
    
    return fairy_files

def stop_fairy_process(pid):
    """Stop a specific fairy process by PID"""
    try:
        os.kill(pid, signal.SIGTERM)
        print(f"Stopped fairy process with PID: {pid}")
        return True
    except Exception as e:
        print(f"Error stopping process {pid}: {e}")
        return False

def disable_fairy_systems():
    """Disable all fairy systems"""
    print("[MAGNIFYING GLASS EMOJI] Finding active fairy processes...")
    fairy_processes = find_fairy_processes()
    
    if fairy_processes:
        print(f"Found {len(fairy_processes)} active fairy process(es)")
        for proc in fairy_processes:
            print(f"  - PID: {proc['pid']}, Command: {proc['cmdline']}")
            stop_fairy_process(proc['pid'])
    else:
        print("No active fairy processes found")
    
    print("\n[MAGNIFYING GLASS EMOJI] Finding fairy-related files...")
    fairy_files = find_fairy_files()
    
    print(f"Found {len(fairy_files)} fairy-related files:")
    for file_path in fairy_files:
        print(f"  - {file_path}")
    
    print("\nTo permanently disable fairies, you can:")
    print("  1. Comment out or remove fairy initialization code in main scripts")
    print("  2. Rename fairy-related Python files with .bak extension")
    print("  3. Modify startup scripts to skip fairy loading")
    
    return fairy_files

if __name__ == "__main__":
    print("Fairy System Manager - Disabling Fairy Systems")
    print("=" * 50)
    
    disable_fairy_systems()
    
    print("\nThe fairy systems have been identified and any running processes stopped.")
    print("You can now continue with your work without the fairy interface.")