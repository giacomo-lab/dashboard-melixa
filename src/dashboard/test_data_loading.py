#!/usr/bin/env python3
"""
Test script to verify data loading functionality
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_data_loading():
    """Test that the CSV data loads correctly"""
    try:
        # Load the data
        df = pd.read_csv('src/data/grid_trentino_for_dashboard.csv')
        print(f"✅ Data loaded successfully!")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {list(df.columns)}")

        # Check for prediction columns
        prediction_cols = [col for col in df.columns if 'prediction' in col]
        print(f"   Prediction columns: {len(prediction_cols)}")

        if prediction_cols:
            week_numbers = [int(col.split('_')[1]) for col in prediction_cols]
            print(f"   Available weeks: {sorted(week_numbers)}")

            # Check data ranges
            print(f"   Latitude range: {df['Latitudine'].min():.4f} to {df['Latitudine'].max():.4f}")
            print(f"   Longitude range: {df['Longitudin'].min():.4f} to {df['Longitudin'].max():.4f}")
            print(f"   Altitude range: {df['Altitudine'].min():.0f}m to {df['Altitudine'].max():.0f}m")

            # Calculate some statistics
            df['avg_prediction'] = df[prediction_cols].mean(axis=1)
            print(f"   Average prediction range: {df['avg_prediction'].min():.3f} to {df['avg_prediction'].max():.3f}")

        return True

    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False


if __name__ == "__main__":
    print("Testing honey production dashboard data loading...")
    test_data_loading()