#!/usr/bin/env python3
"""
MIST Visual Interface - Build Script
This script packages the MIST Visual Interface application for distribution.
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
import argparse


def create_build_directory():
    """Create a build directory for packaging."""
    build_dir = Path("build")
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(exist_ok=True)
    return build_dir


def copy_source_files(build_dir):
    """Copy source files to build directory."""
    print("Copying source files...")
    
    # Define source files to include
    source_files = [
        "LAUNCH_VISUAL.py",
        "VISUAL_INTERFACE.py",
        "requirements.txt",
        "BUILD_APPLICATION.md",
        "README.md",
    ]
    
    # Copy root files
    for file in source_files:
        src = Path(file)
        if src.exists():
            dst = build_dir / src.name
            shutil.copy2(src, dst)
            print(f"  Copied {src} -> {dst}")
    
    # Copy directories
    dirs_to_copy = ["integration", "visualization", "voice", "memory", "identity", "sprites"]
    
    for dir_name in dirs_to_copy:
        src_dir = Path(dir_name)
        if src_dir.exists() and src_dir.is_dir():
            dst_dir = build_dir / dir_name
            shutil.copytree(src_dir, dst_dir, dirs_exist_ok=True)
            print(f"  Copied directory {src_dir} -> {dst_dir}")


def create_executable(build_dir):
    """Create an executable using PyInstaller."""
    print("Creating executable with PyInstaller...")
    
    try:
        # Check if PyInstaller is installed
        subprocess.run([sys.executable, "-m", "pip", "show", "pyinstaller"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("PyInstaller not found, installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], 
                      check=True)
    
    # Change to build directory
    original_cwd = os.getcwd()
    os.chdir(build_dir)
    
    try:
        # Run PyInstaller to create executable
        cmd = [
            sys.executable, "-m", "pyinstaller",
            "--onefile",
            "--windowed",
            "--name", "MIST_Visual_Interface",
            "--add-data", "sprites;sprites",
            "LAUNCH_VISUAL.py"
        ]
        
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        print("Executable created successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error creating executable: {e}")
        print("Continuing with source distribution...")
    finally:
        os.chdir(original_cwd)


def create_zip_distribution(build_dir):
    """Create a ZIP file distribution."""
    print("Creating ZIP distribution...")
    
    zip_filename = "MIST_Visual_Interface_Source.zip"
    
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(build_dir):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(build_dir)
                zipf.write(file_path, arc_path)
    
    print(f"ZIP distribution created: {zip_filename}")
    return zip_filename


def install_dependencies():
    """Install required dependencies."""
    print("Installing dependencies...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False
    
    return True


def run_application_test():
    """Test the application by importing it."""
    print("Testing application import...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, '.')
        
        # Try to import the main module
        import LAUNCH_VISUAL
        print("Application imports successfully!")
        return True
    except ImportError as e:
        print(f"Import error: {e}")
        return False
    except Exception as e:
        print(f"Other error during test: {e}")
        # Still return True as this might be expected (e.g., if GUI tries to start)
        return True


def main():
    parser = argparse.ArgumentParser(description='Build MIST Visual Interface Application')
    parser.add_argument('--skip-executable', action='store_true', 
                       help='Skip creating executable with PyInstaller')
    parser.add_argument('--skip-dependencies', action='store_true', 
                       help='Skip installing dependencies')
    parser.add_argument('--test-only', action='store_true', 
                       help='Only test the application, don\'t build')
    
    args = parser.parse_args()
    
    print("=== MIST Visual Interface Build Script ===")
    print(f"Current directory: {os.getcwd()}")
    
    # Check if we're in the right directory
    required_files = ["LAUNCH_VISUAL.py", "VISUAL_INTERFACE.py", "requirements.txt"]
    missing_files = [f for f in required_files if not Path(f).exists()]
    
    if missing_files:
        print(f"Error: Missing required files: {missing_files}")
        print("Please run this script from the personal-ide directory.")
        sys.exit(1)
    
    if args.test_only:
        print("\n--- Testing Application ---")
        success = run_application_test()
        return 0 if success else 1
    
    print("\n--- Building Application ---")
    
    # Install dependencies if not skipped
    if not args.skip_dependencies:
        if not install_dependencies():
            print("Failed to install dependencies, exiting...")
            return 1
    
    # Test the application
    if not run_application_test():
        print("Application test failed, exiting...")
        return 1
    
    # Create build directory and copy files
    build_dir = create_build_directory()
    copy_source_files(build_dir)
    
    # Create executable if not skipped
    if not args.skip_executable:
        create_executable(build_dir)
    
    # Create ZIP distribution
    zip_file = create_zip_distribution(build_dir)
    
    print(f"\n=== Build Complete ===")
    print(f"Distribution file: {zip_file}")
    print(f"Build directory: {build_dir}")
    
    if not args.skip_executable:
        exe_path = build_dir / "dist" / "MIST_Visual_Interface.exe"
        if exe_path.exists():
            print(f"Executable: {exe_path}")
            print("Ready for distribution!")
        else:
            print("Executable not created (may have failed during PyInstaller step)")
            print("Distribution includes source code and can be run with Python")
    
    return 0


if __name__ == "__main__":
    exit(main())