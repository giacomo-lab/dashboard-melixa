#!/usr/bin/env python3
"""
Run script for the Honey Production Dashboard

This script sets up the proper paths and runs the Streamlit dashboard.
"""

import sys
import os
import subprocess
from pathlib import Path


def setup_paths():
    """Setup the Python path to include the project directories"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent

    # Add project root to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    # Change to project root directory
    os.chdir(project_root)

    return project_root


def check_requirements():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'pandas',
        'plotly',
        'numpy',
        'folium',
        'streamlit_folium'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print("Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall them with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    return True


def check_data_file():
    """Check if the data file exists"""
    data_file = Path("src/data/grid_trentino_for_dashboard.csv")
    if not data_file.exists():
        print(f"Data file not found: {data_file}")
        print("Please ensure the CSV file is in the correct location.")
        return False
    return True


def run_dashboard():
    """Run the Streamlit dashboard"""
    dashboard_path = Path("src/dashboard/honey_dashboard.py")

    if not dashboard_path.exists():
        print(f"Dashboard file not found: {dashboard_path}")
        return False

    try:
        # Run Streamlit
        cmd = [sys.executable, "-m", "streamlit", "run", str(dashboard_path)]
        subprocess.run(cmd)
        return True
    except Exception as e:
        print(f"Error running dashboard: {e}")
        return False


def main():
    """Main function"""
    print("🍯 Honey Production Dashboard Launcher")
    print("=" * 40)

    # Setup paths
    project_root = setup_paths()
    print(f"Project root: {project_root}")

    # Check requirements
    print("\nChecking requirements...")
    if not check_requirements():
        return 1
    print("✅ All required packages are installed")

    # Check data file
    print("\nChecking data file...")
    if not check_data_file():
        return 1
    print("✅ Data file found")

    # Run dashboard
    print("\n🚀 Starting dashboard...")
    print("The dashboard will open in your default web browser.")
    print("If it doesn't open automatically, go to http://localhost:8501")
    print("\nPress Ctrl+C to stop the dashboard")

    if run_dashboard():
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main()) 