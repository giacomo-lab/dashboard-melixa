import pandas as pd
import numpy as np
import re
from typing import Dict, List


def load_and_validate_data(file_path: str) -> pd.DataFrame:
    """
    Load and validate the honey production data
    
    Args:
        file_path: Path to the CSV file
        
    Returns:
        DataFrame with validated data
    """
    try:
        df = pd.read_csv(file_path)
        
        # Validate required columns
        required_cols = ['GRID_ID', 'Altitudine', 'Longitudin', 'Latitudine']
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Check for prediction columns
        prediction_cols = [col for col in df.columns if 'prediction' in col.lower()]
        if not prediction_cols:
            raise ValueError("No prediction columns found in the data")
        
        # Basic data validation
        if df['Latitudine'].isnull().any() or df['Longitudin'].isnull().any():
            print("Warning: Some locations have missing coordinates")
        
        if df['Altitudine'].isnull().any():
            print("Warning: Some locations have missing altitude data")
        
        return df
        
    except Exception as e:
        print(f"Error loading data: {e}")
        return pd.DataFrame()


def calculate_prediction_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate various prediction metrics for each location

    Args:
        df: DataFrame with prediction columns
        
    Returns:
        DataFrame with additional metric columns
    """
    if df.empty:
        return df
    
    # Get prediction columns
    prediction_cols = [col for col in df.columns if 'prediction' in col.lower()]
    
    if not prediction_cols:
        return df
    
    # Calculate basic statistics
    df['avg_prediction'] = df[prediction_cols].mean(axis=1)
    df['max_prediction'] = df[prediction_cols].max(axis=1)
    df['min_prediction'] = df[prediction_cols].min(axis=1)
    df['prediction_std'] = df[prediction_cols].std(axis=1)
    df['prediction_range'] = df['max_prediction'] - df['min_prediction']
    
    # Find best and worst weeks
    df['best_week'] = df[prediction_cols].idxmax(axis=1)
    df['worst_week'] = df[prediction_cols].idxmin(axis=1)
    
    # Extract week numbers
    df['best_week_num'] = df['best_week'].apply(extract_week_number)
    df['worst_week_num'] = df['worst_week'].apply(extract_week_number)
    
    # Calculate consistency score (inverse of coefficient of variation)
    df['consistency_score'] = 1 - (df['prediction_std'] / df['avg_prediction'])
    df['consistency_score'] = df['consistency_score'].fillna(0)
    
    # Calculate peak performance periods
    df['peak_period'] = df.apply(lambda row: get_peak_period(row, prediction_cols), axis=1)
    
    # Quality scoring (combination of average and consistency)
    df['quality_score'] = (df['avg_prediction'] * 0.7) + (df['consistency_score'] * 0.3)
    
    return df


def extract_week_number(week_column: str) -> int:
    """Extract week number from column name"""
    if pd.isna(week_column):
        return 0
    
    match = re.search(r'(\d+)', str(week_column))
    return int(match.group(1)) if match else 0


def get_peak_period(row: pd.Series, prediction_cols: List[str]) -> str:
    """
    Determine the peak performance period for a location
    
    Args:
        row: DataFrame row
        prediction_cols: List of prediction column names
        
    Returns:
        String describing the peak period
    """
    predictions = [row[col] for col in prediction_cols]
    
    # Find weeks with predictions above 75th percentile
    threshold = np.percentile(predictions, 75)
    high_weeks = [i+1 for i, pred in enumerate(predictions) if pred >= threshold]
    
    if not high_weeks:
        return "Low performance"
    
    # Group consecutive weeks
    periods = []
    current_period = [high_weeks[0]]
    
    for week in high_weeks[1:]:
        if week == current_period[-1] + 1:
            current_period.append(week)
        else:
            periods.append(current_period)
            current_period = [week]
    periods.append(current_period)
    
    # Find longest period
    longest_period = max(periods, key=len)
    
    if len(longest_period) == 1:
        return f"Week {longest_period[0]}"
    elif len(longest_period) <= 3:
        return f"Weeks {longest_period[0]}-{longest_period[-1]}"
    else:
        return f"Extended period (Weeks {longest_period[0]}-{longest_period[-1]})"


def filter_data(df: pd.DataFrame, filters: Dict) -> pd.DataFrame:
    """
    Apply filters to the dataframe
    
    Args:
        df: DataFrame to filter
        filters: Dictionary with filter criteria
        
    Returns:
        Filtered DataFrame
    """
    filtered_df = df.copy()
    
    # Prediction score filter
    if 'min_prediction' in filters and 'max_prediction' in filters:
        filtered_df = filtered_df[
            (filtered_df['avg_prediction'] >= filters['min_prediction']) &
            (filtered_df['avg_prediction'] <= filters['max_prediction'])
        ]
    
    # Altitude filter
    if 'min_altitude' in filters and 'max_altitude' in filters:
        filtered_df = filtered_df[
            (filtered_df['Altitudine'] >= filters['min_altitude']) &
            (filtered_df['Altitudine'] <= filters['max_altitude'])
        ]
    
    # Best week filter
    if 'selected_weeks' in filters and filters['selected_weeks']:
        filtered_df = filtered_df[filtered_df['best_week_num'].isin(filters['selected_weeks'])]
    
    # Geographic bounding box
    if all(key in filters for key in ['min_lat', 'max_lat', 'min_lon', 'max_lon']):
        filtered_df = filtered_df[
            (filtered_df['Latitudine'] >= filters['min_lat']) &
            (filtered_df['Latitudine'] <= filters['max_lat']) &
            (filtered_df['Longitudin'] >= filters['min_lon']) &
            (filtered_df['Longitudin'] <= filters['max_lon'])
        ]
    
    # Quality score filter
    if 'min_quality' in filters:
        filtered_df = filtered_df[filtered_df['quality_score'] >= filters['min_quality']]
    
    return filtered_df


def get_location_recommendations(df: pd.DataFrame, n_recommendations: int = 5) -> List[Dict]:
    """
    Get top location recommendations based on various criteria
    
    Args:
        df: DataFrame with location data
        n_recommendations: Number of recommendations to return
        
    Returns:
        List of recommendation dictionaries
    """
    if df.empty:
        return []
    
    recommendations = []
    
    # Top by average prediction
    top_avg = df.nlargest(n_recommendations, 'avg_prediction')
    for _, row in top_avg.iterrows():
        recommendations.append({
            'id': row['GRID_ID'],
            'type': 'High Average Score',
            'score': row['avg_prediction'],
            'reason': f"Average prediction score of {row['avg_prediction']:.3f}",
            'best_week': row['best_week_num']
        })
    
    # Top by quality score (consistency + performance)
    top_quality = df.nlargest(n_recommendations, 'quality_score')
    for _, row in top_quality.iterrows():
        if row['GRID_ID'] not in [r['id'] for r in recommendations]:
            recommendations.append({
                'id': row['GRID_ID'],
                'type': 'High Quality Score',
                'score': row['quality_score'],
                'reason': f"Quality score of {row['quality_score']:.3f} (combines performance and consistency)",
                'best_week': row['best_week_num']
            })
    
    # Most consistent locations
    top_consistent = df.nlargest(n_recommendations, 'consistency_score')
    for _, row in top_consistent.iterrows():
        if row['GRID_ID'] not in [r['id'] for r in recommendations]:
            recommendations.append({
                'id': row['GRID_ID'],
                'type': 'Most Consistent',
                'score': row['consistency_score'],
                'reason': f"Consistency score of {row['consistency_score']:.3f}",
                'best_week': row['best_week_num']
            })
    
    return recommendations[:n_recommendations * 2]  # Return some variety


def calculate_spatial_clusters(df: pd.DataFrame, n_clusters: int = 5) -> pd.DataFrame:
    """
    Identify spatial clusters of high-performing locations
    
    Args:
        df: DataFrame with location data
        n_clusters: Number of clusters to identify
        
    Returns:
        DataFrame with cluster assignments
    """
    try:
        from sklearn.cluster import KMeans
        
        # Prepare data for clustering
        features = df[['Latitudine', 'Longitudin', 'avg_prediction']].copy()
        features = features.dropna()
        
        if len(features) < n_clusters:
            n_clusters = len(features)
        
        # Normalize coordinates and predictions
        features_normalized = features.copy()
        features_normalized['Latitudine'] = (features['Latitudine'] - features['Latitudine'].mean()) / features['Latitudine'].std()
        features_normalized['Longitudin'] = (features['Longitudin'] - features['Longitudin'].mean()) / features['Longitudin'].std()
        features_normalized['avg_prediction'] = (features['avg_prediction'] - features['avg_prediction'].mean()) / features['avg_prediction'].std()
        
        # Perform clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        features['cluster'] = kmeans.fit_predict(features_normalized)
        
        # Merge back to original dataframe
        df_with_clusters = df.merge(
            features[['cluster']], 
            left_index=True, 
            right_index=True, 
            how='left'
        )
        
        return df_with_clusters
        
    except ImportError:
        print("sklearn not available for clustering")
        df['cluster'] = 0
        return df


def generate_summary_stats(df: pd.DataFrame) -> Dict:
    """
    Generate summary statistics for the dataset
    
    Args:
        df: DataFrame with location data
        
    Returns:
        Dictionary with summary statistics
    """
    if df.empty:
        return {}
    
    prediction_cols = [col for col in df.columns if 'prediction' in col.lower()]
    
    stats = {
        'total_locations': len(df),
        'avg_prediction_score': df['avg_prediction'].mean(),
        'prediction_std': df['avg_prediction'].std(),
        'altitude_range': (df['Altitudine'].min(), df['Altitudine'].max()),
        'coordinate_bounds': {
            'lat_min': df['Latitudine'].min(),
            'lat_max': df['Latitudine'].max(),
            'lon_min': df['Longitudin'].min(),
            'lon_max': df['Longitudin'].max()
        },
        'best_weeks_distribution': df['best_week_num'].value_counts().to_dict(),
        'high_quality_locations': len(df[df['quality_score'] > df['quality_score'].quantile(0.75)]),
        'prediction_weeks': len(prediction_cols)
    }
    
    return stats


def export_location_data(locations: Dict, format: str = 'csv') -> str:
    """
    Export selected location data
    
    Args:
        locations: Dictionary of selected locations
        format: Export format ('csv', 'json')
        
    Returns:
        Exported data as string
    """
    if not locations:
        return ""
    
    df = pd.DataFrame.from_dict(locations, orient='index')
    
    if format == 'csv':
        return df.to_csv(index=False)
    elif format == 'json':
        return df.to_json(orient='records', indent=2)
    else:
        return str(df)


def validate_coordinates(lat: float, lon: float) -> bool:
    """
    Validate latitude and longitude coordinates
    
    Args:
        lat: Latitude
        lon: Longitude
        
    Returns:
        True if coordinates are valid
    """
    return (-90 <= lat <= 90) and (-180 <= lon <= 180) 