# 🍯 Honey Production Location Dashboard

A Streamlit dashboard for analyzing honey production predictions and scheduling hive placements in Trentino, Italy.

## Features

### 🗺️ Map Explorer
- **Interactive Map**: Click on locations to select them for hive placement
- **Week Selection**: Use slider to view predictions for weeks 1-26
- **Smart Filtering**: Filter by prediction score range and altitude
- **Visual Selection**: Selected locations appear as green markers
- **Location Details**: View coordinates, altitude, and prediction scores

### 📅 Calendar Scheduling
- **Hive Placement**: Schedule hive placements for selected locations
- **Calendar Views**: Month, week, and list views of scheduled events
- **Event Management**: Add dates, hive counts, and notes
- **Export**: Download schedules as CSV

## Quick Start

### Installation
```bash
pip install -r requirements.txt
```

### Run Dashboard
```bash
streamlit run src/dashboard/honey_dashboard.py
```

## Data Requirements

Your CSV file should contain:
- `GRID_ID`: Location identifier
- `Latitudine`, `Longitudin`: Coordinates  
- `Altitudine`: Elevation (meters)
- `week_X_prediction`: Weekly scores (week_1_prediction through week_26_prediction)

## How to Use

1. **Select Week**: Use the sidebar slider to choose which week's predictions to view
2. **Filter Locations**: Adjust prediction score and altitude ranges
3. **Select Locations**: Click on map points to select promising locations
4. **Schedule Hives**: Go to Calendar tab and create hive placement schedules
5. **Export**: Download your schedule as CSV

## Data Overview

- **Prediction Scores**: 0.0 to 1.0 (higher = better honey production potential)
- **Coverage**: ~1000 locations across Trentino region
- **Time Period**: 26-week seasonal predictions
- **Metrics**: Average, best week, altitude correlation

---
