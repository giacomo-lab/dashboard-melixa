# 🍯 Honey Production Location Dashboard

A comprehensive Streamlit dashboard for analyzing honey production predictions, selecting optimal hive locations, and scheduling hive placements.

## Features

### 🗺️ Interactive Map Visualization
- **Plotly Interactive Maps**: Zoom, pan, and hover over locations to see detailed prediction data
- **Folium Clickable Maps**: Click on markers to select locations for hive placement
- **Color-coded Markers**: 
  - 🟢 Green: High prediction scores (>0.6)
  - 🟡 Orange: Medium prediction scores (0.3-0.6)
  - 🔴 Red: Low prediction scores (<0.3)
  - 🔵 Blue: Selected locations

### 📊 Advanced Filtering
- **Prediction Score Range**: Filter locations by average prediction scores
- **Altitude Range**: Filter by elevation (useful for accessibility planning)
- **Best Performance Weeks**: Find locations that peak during specific weeks
- **Geographic Bounds**: Focus on specific regions

### 📍 Location Selection & Management
- **Smart Selection**: Add promising locations to your selection list
- **Custom Labels**: Name your selected locations for easy identification
- **Detailed Information**: View coordinates, altitude, scores, and best weeks
- **Weekly Charts**: Analyze 26-week prediction patterns for each location

### 📅 Hive Placement Scheduling
- **Calendar Integration**: Schedule hive placements with start and end dates
- **Resource Management**: Track number of hives per location
- **Notes & Documentation**: Add detailed notes for each placement
- **Schedule Overview**: View all scheduled events in an organized timeline

### 📊 Analytics & Insights
- **Distribution Analysis**: Understand the spread of prediction scores
- **Altitude Correlation**: Analyze how elevation affects honey production
- **Seasonal Patterns**: Identify the best weeks across all locations
- **Performance Metrics**: Summary statistics and recommendations

### 📤 Export Capabilities
- **Schedule Export**: Download your hive placement schedule as CSV
- **Location Data**: Export selected locations with all metrics
- **Data Persistence**: Session state maintains your selections

## Installation & Setup

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Required Packages
Install the required dependencies:

```bash
pip install streamlit pandas plotly numpy folium streamlit-folium streamlit-calendar
```

Or install from the requirements file:

```bash
pip install -r src/dashboard/requirements.txt
```

### Data Requirements
Ensure your CSV file (`src/data/grid_trentino_for_dashboard.csv`) contains:
- `GRID_ID`: Unique identifier for each location
- `Latitudine`: Latitude coordinates
- `Longitudin`: Longitude coordinates
- `Altitudine`: Elevation in meters
- `week_X_prediction`: Weekly prediction scores (week_1_prediction through week_26_prediction)

## Running the Dashboard

### Option 1: Using the Launch Script
```bash
python src/dashboard/run_dashboard.py
```

### Option 2: Direct Streamlit Command
```bash
cd /path/to/project
streamlit run src/dashboard/honey_dashboard.py
```

### Option 3: Development Mode
```bash
# From project root
cd src/dashboard
streamlit run honey_dashboard.py
```

## Dashboard Usage Guide

### 1. Map Explorer Tab
1. **Choose Map Type**: Select between Plotly Interactive or Folium Clickable maps
2. **Apply Filters**: Use the sidebar to filter locations by various criteria
3. **Explore Locations**: Hover over or click on markers to view details
4. **Select Locations**: Use the dropdown to add promising locations to your selection

### 2. Selected Locations Tab
1. **Review Selections**: View all your selected locations with detailed metrics
2. **Customize Labels**: Rename locations for better organization
3. **Analyze Patterns**: Click "View Chart" to see weekly prediction patterns
4. **Manage Selection**: Remove locations or clear all selections

### 3. Schedule Hives Tab
1. **Create Schedules**: Select a location, choose dates, and specify number of hives
2. **Add Details**: Include notes about the hive placement
3. **View Calendar**: See all scheduled events in chronological order
4. **Export Schedule**: Download your complete schedule as CSV

### 4. Analytics Tab
1. **Explore Distributions**: Understand the data patterns
2. **Correlation Analysis**: See how factors like altitude affect predictions
3. **Summary Statistics**: Get key insights about your filtered data
4. **Event Analytics**: Analyze your scheduled hive placements

## Data Understanding

### Prediction Scores
- **Range**: 0.0 to 1.0 (higher is better)
- **Interpretation**: Probability of successful honey production
- **Calculation**: Based on machine learning model predictions

### Derived Metrics
- **Average Prediction**: Mean score across all 26 weeks
- **Max Prediction**: Highest weekly score
- **Consistency Score**: Measure of prediction stability
- **Quality Score**: Combined performance and consistency metric
- **Best Week**: Week with highest predicted performance

### Geographic Considerations
- **Altitude Effects**: Higher elevations may have different flowering patterns
- **Coordinate System**: Uses standard latitude/longitude (WGS84)
- **Region**: Data covers the Trentino region in Northern Italy

## Tips for Optimal Use

### Location Selection Strategy
1. **Balance Performance and Consistency**: Look for locations with both high average scores and low variability
2. **Consider Accessibility**: Factor in altitude and geographic accessibility
3. **Seasonal Planning**: Select locations with complementary peak weeks
4. **Risk Distribution**: Choose locations in different geographic areas

### Scheduling Best Practices
1. **Match Peak Weeks**: Schedule hive placements to align with location peak performance
2. **Weather Considerations**: Account for local weather patterns and flowering seasons
3. **Resource Planning**: Balance the number of hives across locations
4. **Documentation**: Keep detailed notes for future reference

### Filtering Techniques
1. **Start Broad**: Begin with minimal filters to see all options
2. **Iterative Refinement**: Gradually narrow down based on your requirements
3. **Quality First**: Use quality score filter to focus on best locations
4. **Geographic Clustering**: Filter by coordinate bounds for regional focus

## Technical Features

### Performance Optimizations
- **Data Caching**: Uses Streamlit's `@st.cache_data` for fast loading
- **Session State**: Maintains selections across page refreshes
- **Lazy Loading**: Charts and maps load only when needed

### Visualization Features
- **Interactive Maps**: Zoom, pan, and hover capabilities
- **Responsive Design**: Adapts to different screen sizes
- **Color Coding**: Intuitive color schemes for data interpretation
- **Custom Styling**: Professional appearance with custom CSS

### Data Processing
- **Real-time Filtering**: Instant updates as you adjust filters
- **Statistical Calculations**: Automated computation of derived metrics
- **Data Validation**: Built-in checks for data integrity

## Troubleshooting

### Common Issues

**Dashboard won't start**
- Check Python version (3.7+ required)
- Verify all packages are installed
- Ensure data file exists in correct location

**Map not displaying**
- Check internet connection (required for map tiles)
- Try refreshing the page
- Switch between map types

**Filters not working**
- Ensure data contains the expected columns
- Check for data type compatibility
- Try resetting filters

**Performance issues**
- Reduce the number of displayed locations with filters
- Close other browser tabs
- Check system memory usage

### Data Issues

**Missing coordinates**
- Check latitude/longitude columns for null values
- Verify coordinate format (decimal degrees)

**Prediction columns not found**
- Ensure column names match expected format: `week_X_prediction`
- Check for case sensitivity

**Invalid prediction values**
- Values should be between 0 and 1
- Check for negative values or values > 1

## Contributing

To contribute to the dashboard:

1. **Report Issues**: Use the project's issue tracker
2. **Feature Requests**: Suggest new functionality
3. **Code Contributions**: Submit pull requests with improvements
4. **Documentation**: Help improve this README and code comments

## Future Enhancements

### Planned Features
- **Weather Integration**: Incorporate weather forecast data
- **Advanced Analytics**: Machine learning insights and recommendations
- **Mobile Optimization**: Improved mobile device support
- **Real-time Updates**: Live data integration capabilities
- **Collaboration Features**: Share selections and schedules between users

### Data Enhancements
- **Historical Data**: Track actual vs predicted performance
- **Additional Metrics**: Soil quality, flower density, etc.
- **Satellite Imagery**: Visual context for locations
- **Road Network**: Accessibility analysis

## License & Usage

This dashboard is designed for honey production analysis and hive placement planning. Please ensure you have appropriate permissions for any commercial use of the underlying prediction data.

---

For questions, issues, or suggestions, please contact the development team or create an issue in the project repository. 