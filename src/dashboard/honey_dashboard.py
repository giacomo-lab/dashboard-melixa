import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
from typing import Dict, List
import folium
from streamlit_folium import st_folium
from streamlit_calendar import calendar
import plotly.colors as pc

# Page configuration
st.set_page_config(
    page_title="Honey Production Dashboard",
    page_icon="🍯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #FF8C00;
    text-align: center;
    margin-bottom: 2rem;
}
.metric-card {
    background-color: #FFF8DC;
    padding: 1rem;
    border-radius: 10px;
    border-left: 5px solid #FF8C00;
    margin: 0.5rem 0;
}
.selected-location {
    background-color: #F0FFF0;
    padding: 0.5rem;
    border-radius: 5px;
    margin: 0.2rem 0;
    border-left: 3px solid #32CD32;
}
</style>
""", unsafe_allow_html=True)

# Load and cache data
@st.cache_data
def load_data():
    """Load the honey production prediction data"""
    try:
        df = pd.read_csv('src/data/grid_trentino_for_dashboard.csv')
        return df
    except FileNotFoundError:
        st.error("Data file not found. Please ensure 'src/data/grid_trentino_for_dashboard.csv' is available.")
        return pd.DataFrame()

def prepare_data(df):
    """Prepare data for visualization"""
    if df.empty:
        return df
    
    # Get valid prediction columns that follow the week_X_prediction pattern
    prediction_cols, _ = get_prediction_columns(df)
    
    if not prediction_cols:
        # If no valid prediction columns found, return empty dataframe
        st.error("No valid prediction columns found. Expected format: week_X_prediction")
        return pd.DataFrame()
    
    # Calculate summary statistics for each location
    df['avg_prediction'] = df[prediction_cols].mean(axis=1)
    df['max_prediction'] = df[prediction_cols].max(axis=1)
    df['min_prediction'] = df[prediction_cols].min(axis=1)
    
    # Determine best weeks for each location
    df['best_week'] = df[prediction_cols].idxmax(axis=1)
    df['best_week_num'] = df['best_week'].str.extract(r'(\d+)').astype(int)
    
    return df

def get_prediction_columns(df):
    """Get list of prediction columns and week numbers"""
    prediction_cols = [col for col in df.columns if 'prediction' in col]
    
    # Extract week numbers only from columns that follow the pattern week_X_prediction
    week_numbers = []
    valid_prediction_cols = []
    
    for col in prediction_cols:
        parts = col.split('_')
        if len(parts) >= 3 and parts[0] == 'week' and parts[2] == 'prediction':
            try:
                week_num = int(parts[1])
                week_numbers.append(week_num)
                valid_prediction_cols.append(col)
            except ValueError:
                continue  # Skip columns that don't have valid week numbers
    
    return valid_prediction_cols, sorted(week_numbers)

def create_prediction_map(df, selected_week=None, metric='avg_prediction'):
    """Create an interactive map with prediction data"""
    if df.empty:
        return go.Figure()
    
    # Determine the metric to display
    if selected_week:
        week_col = f'week_{selected_week}_prediction'
        if week_col in df.columns:
            color_metric = week_col
            title = f"Honey Production Predictions - Week {selected_week}"
        else:
            color_metric = metric
            title = f"Honey Production Predictions - {metric.replace('_', ' ').title()}"
    else:
        color_metric = metric
        title = f"Honey Production Predictions - {metric.replace('_', ' ').title()}"
    
    # Create hover data
    hover_data = {
        "GRID_ID": True,
        "Altitudine": True,
        "avg_prediction": ":.3f",
        "max_prediction": ":.3f",
        "best_week_num": True
    }
    
    # Add selected week data to hover if available
    if selected_week and f'week_{selected_week}_prediction' in df.columns:
        hover_data[f'week_{selected_week}_prediction'] = ":.3f"
    
    fig = px.scatter_mapbox(
        df,
        lat="Latitudine",
        lon="Longitudin",
        color=color_metric,
        size="avg_prediction",
        hover_data=hover_data,
        color_continuous_scale="Viridis",
        size_max=15,
        zoom=8,
        mapbox_style="open-street-map",
        title=title,
        height=600
    )
    
    fig.update_layout(
        mapbox=dict(
            center=dict(lat=df['Latitudine'].mean(), lon=df['Longitudin'].mean())
        ),
        margin={"r":0,"t":50,"l":0,"b":0}
    )
    
    return fig

def create_folium_map(df, selected_locations=None, selected_week=None):
    """Create a Folium map with clickable markers"""
    if df.empty:
        return None
    
    # Center map on mean coordinates
    center_lat = df['Latitudine'].mean()
    center_lon = df['Longitudin'].mean()
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9)
    
    # Add markers for each location
    for idx, row in df.iterrows():
        # Get prediction score for selected week or use average
        if selected_week and f'week_{selected_week}_prediction' in df.columns:
            prediction_score = row[f'week_{selected_week}_prediction']
            score_label = f"Week {selected_week}"
        else:
            prediction_score = row['avg_prediction']
            score_label = "Avg"
        
        # Color based on prediction score
        color = 'red' if prediction_score < 0.3 else 'orange' if prediction_score < 0.6 else 'green'
        
        # Special styling for selected locations
        if selected_locations and row['GRID_ID'] in selected_locations:
            color = 'blue'
            icon = folium.Icon(color=color, icon='star')
        else:
            icon = folium.Icon(color=color)
        
        # Create popup content
        popup_content = f"""
        <b>ID:</b> {row['GRID_ID']}<br>
        <b>Altitude:</b> {row['Altitudine']}m<br>
        <b>{score_label} Prediction:</b> {prediction_score:.3f}<br>
        <b>Avg Prediction:</b> {row['avg_prediction']:.3f}<br>
        <b>Best Week:</b> {row['best_week_num']}
        """
        
        folium.Marker(
            [row['Latitudine'], row['Longitudin']],
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"ID: {row['GRID_ID']} | {score_label}: {prediction_score:.3f}",
            icon=icon
        ).add_to(m)
    
    return m

def create_weekly_predictions_chart(df, location_id):
    """Create a chart showing weekly predictions for a specific location"""
    if df.empty or location_id not in df['GRID_ID'].values:
        return go.Figure()
    
    location_data = df[df['GRID_ID'] == location_id].iloc[0]
    prediction_cols = [col for col in df.columns if 'prediction' in col]
    
    weeks = [int(col.split('_')[1]) for col in prediction_cols]
    predictions = [location_data[col] for col in prediction_cols]
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weeks,
        y=predictions,
        mode='lines+markers',
        name='Prediction Score',
        line=dict(color='#FF8C00', width=3),
        marker=dict(size=8)
    ))
    
    fig.update_layout(
        title=f"Weekly Predictions for {location_id}",
        xaxis_title="Week",
        yaxis_title="Prediction Score",
        hovermode='x unified',
        height=400
    )
    
    return fig

def create_calendar_events(scheduled_events):
    """Convert scheduled events to calendar format"""
    events = []
    for event in scheduled_events:
        events.append({
            "title": f"🐝 {event['location_id']} - {event['hives']} hives",
            "start": event['start_date'],
            "end": event['end_date'],
            "color": "#FFD700"
        })
    return events

# Initialize session state
if 'selected_locations' not in st.session_state:
    st.session_state.selected_locations = {}

if 'scheduled_events' not in st.session_state:
    st.session_state.scheduled_events = []

if 'map_clicks' not in st.session_state:
    st.session_state.map_clicks = 0

# Main dashboard
def main():
    st.markdown('<h1 class="main-header">🍯 Honey Production Location Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    if df.empty:
        st.error("Cannot proceed without data.")
        return
    
    df = prepare_data(df)
    
    # Get available weeks
    prediction_cols, available_weeks = get_prediction_columns(df)
    
    # Sidebar filters
    #st.sidebar.header("") #📊 Filters & Controls
    
    # Week selector
    #st.sidebar.subheader("📅 Week Selection")
    selected_week = st.sidebar.slider(
        "Select Week",
        min_value=min(available_weeks),
        max_value=max(available_weeks),
        value=min(available_weeks),
        step=1,
        help="Choose which week's predictions to display on the map"
    )
    st.sidebar.info(f"Showing predictions for Week {selected_week}")
    
    # Prediction score filter
    min_score, max_score = st.sidebar.slider(
        "Prediction Score Range",
        min_value=float(df['avg_prediction'].min()),
        max_value=float(df['avg_prediction'].max()),
        value=(float(df['avg_prediction'].min()), float(df['avg_prediction'].max())),
        step=0.01
    )
    
    # Altitude filter
    min_alt, max_alt = st.sidebar.slider(
        "Altitude Range (m)",
        min_value=int(df['Altitudine'].min()),
        max_value=int(df['Altitudine'].max()),
        value=(int(df['Altitudine'].min()), int(df['Altitudine'].max())),
        step=10
    )
    
    # Apply filters
    filtered_df = df[
        (df['avg_prediction'] >= min_score) & 
        (df['avg_prediction'] <= max_score) &
        (df['Altitudine'] >= min_alt) & 
        (df['Altitudine'] <= max_alt)
    ]
    
    # Main content tabs
    tab1, tab2 = st.tabs(["🗺️ Map Explorer", "📅 Calendar"])
    
    with tab1:
        st.subheader("Interactive Prediction Map")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Create prediction map with selection capability
            fig = create_prediction_map(filtered_df, selected_week)
            
            # Add visual indicators for already selected locations
            if st.session_state.selected_locations:
                selected_locations_df = filtered_df[filtered_df['GRID_ID'].isin(st.session_state.selected_locations.keys())]
                if not selected_locations_df.empty:
                    # Add selected locations as a separate trace with different styling
                    fig.add_trace(
                        go.Scattermapbox(
                            lat=selected_locations_df["Latitudine"],
                            lon=selected_locations_df["Longitudin"],
                            mode='markers',
                            marker=dict(
                                size=20,
                                color='gold',
                                symbol='star'
                            ),
                            text=selected_locations_df['GRID_ID'],
                            name='Selected Locations',
                            hovertemplate='<b>SELECTED:</b> %{text}<extra></extra>'
                        )
                    )
            
            st.info("💡 **Click on map points to select locations for hive placement**")
            
            # Enable selection with rerun on click
            chart_selection = st.plotly_chart(
                fig, 
                use_container_width=True,
                on_select="rerun",
                selection_mode=["points"],
                key="map_selection"
            )
            
            # Handle point selections
            if chart_selection and hasattr(chart_selection, 'selection') and chart_selection.selection and chart_selection.selection.get('points'):
                selected_points = chart_selection.selection['points']
                
                for point in selected_points:
                    # Get the point index to identify the location
                    point_index = point.get('point_index', point.get('pointIndex'))
                    
                    # Get the corresponding location from filtered_df
                    if point_index is not None and point_index < len(filtered_df):
                        selected_location = filtered_df.iloc[point_index]
                        location_id = selected_location['GRID_ID']
                        
                        # Add to selected locations if not already there
                        if location_id not in st.session_state.selected_locations:
                            st.session_state.selected_locations[location_id] = {
                                'id': location_id,
                                'latitude': selected_location['Latitudine'],
                                'longitude': selected_location['Longitudin'],
                                'altitude': selected_location['Altitudine'],
                                'avg_prediction': selected_location['avg_prediction'],
                                'best_week': selected_location['best_week_num'],
                                'label': f"Location {len(st.session_state.selected_locations) + 1}"
                            }
                            st.success(f"✅ Added {location_id} to selection!")
                            st.rerun()
        
        with col2:
            st.subheader("🎯 Selected Locations")
            
            if st.session_state.selected_locations:
                for loc_id, loc_data in st.session_state.selected_locations.items():
                    # Get current week prediction if week is selected
                    current_prediction = loc_data['avg_prediction']
                    prediction_label = "Avg"
                    
                    if selected_week:
                        location_row = df[df['GRID_ID'] == loc_id]
                        if not location_row.empty:
                            week_col = f'week_{selected_week}_prediction'
                            if week_col in location_row.columns:
                                current_prediction = location_row[week_col].iloc[0]
                                prediction_label = f"W{selected_week}"
                    
                    # Simplified display
                    with st.container():
                        col_info, col_remove = st.columns([4, 1])
                        
                        with col_info:
                            st.write(f"**📍 {loc_data['label']}** ({loc_id})")
                            st.write(f"🍯 {prediction_label}: {current_prediction:.3f} | ⛰️ {loc_data['altitude']}m")
                        
                        with col_remove:
                            if st.button("🗑️", key=f"remove_{loc_id}", 
                                       help=f"Remove {loc_data['label']}"):
                                del st.session_state.selected_locations[loc_id]
                                st.rerun()
                        
                        st.divider()
                
                # Summary and actions
                st.subheader("📊 Summary")
                st.write(f"**{len(st.session_state.selected_locations)}** locations selected")
                
                if st.button("🗑️ Clear All", type="secondary"):
                    st.session_state.selected_locations = {}
                    st.rerun()
                    
            else:
                st.info("🗺️ Click on map points to select locations")
                st.write("**Instructions:**")
                st.write("1. Click on any point on the map")
                st.write("2. Selected locations appear here")
                st.write("3. Selected locations show as ⭐ gold stars")
    
    with tab2:
        st.subheader("Schedule Hive Placements")
        
        if not st.session_state.selected_locations:
            st.warning("Please select locations first in the Map Explorer tab.")
        else:
            # Form section
            st.subheader("📝 New Schedule")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                
                selected_loc_for_schedule = st.selectbox(
                    "Select Location",
                    list(st.session_state.selected_locations.keys()),
                    format_func=lambda x: st.session_state.selected_locations[x]['label']
                )
                
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now().date()
                )
                
                duration = st.number_input(
                    "Duration (days)",
                    min_value=1,
                    max_value=365,
                    value=30
                )
                
                end_date = start_date + timedelta(days=duration)
                st.write(f"End Date: {end_date}")
                
                num_hives = st.number_input(
                    "Number of Hives",
                    min_value=1,
                    max_value=100,
                    value=5
                )
                
                notes = st.text_area(
                    "Notes",
                    placeholder="Add any additional notes about this hive placement..."
                )
                
                if st.button("📅 Schedule Placement"):
                    new_event = {
                        'id': len(st.session_state.scheduled_events),
                        'location_id': selected_loc_for_schedule,
                        'location_label': st.session_state.selected_locations[selected_loc_for_schedule]['label'],
                        'start_date': start_date.isoformat(),
                        'end_date': end_date.isoformat(),
                        'hives': num_hives,
                        'notes': notes,
                        'created_at': datetime.now().isoformat()
                    }
                    
                    st.session_state.scheduled_events.append(new_event)
                    st.success("✅ Hive placement scheduled!")
                    st.rerun()
            
            with col2:
                st.info("📝 Use the form on the left to schedule hive placements")
                
        # Calendar section - moved outside columns for better rendering
        st.markdown("---")
        st.subheader("📅 Interactive Calendar")
        
        # Calendar view options
        calendar_view = st.radio(
            "Calendar View", 
            ["dayGridMonth", "dayGridWeek", "listWeek"],
            index=0,
            horizontal=True,
            help="Choose how to display the calendar"
        )
        
        # Prepare events for streamlit-calendar
        calendar_events = []
        if st.session_state.scheduled_events:
            for event in st.session_state.scheduled_events:
                calendar_events.append({
                    "id": str(event['id']),
                    "title": f"🐝 {event['location_label']} ({event['hives']} hives)",
                    "start": event['start_date'],
                    "end": event['end_date'],
                    "backgroundColor": "#FFD700",
                    "borderColor": "#FF8C00",
                    "textColor": "#000000",
                    "extendedProps": {
                        "location_id": event['location_id'],
                        "location_label": event['location_label'],
                        "hives": event['hives'],
                        "notes": event['notes']
                    }
                })
        
        # Calendar configuration - simplified
        calendar_options = {
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,dayGridWeek,listWeek"
            },
            "initialView": calendar_view,
            "height": 600,
            "editable": True,
            "selectable": True,
            "weekends": True
        }
        
        # Debug: Show calendar data before rendering
        if st.checkbox("🔍 Debug Calendar", help="Show calendar configuration for debugging"):
            st.write("**Calendar Events:**", calendar_events)
            st.write("**Calendar Options:**", calendar_options)
            st.write(f"**Number of events:** {len(calendar_events)}")
        
        # Display the calendar with simplified approach
        st.write("---")  # Visual separator
        st.write("**Calendar should appear below:**")
        
        # Try without custom CSS first
        calendar_state = calendar(
            events=calendar_events,
            options=calendar_options,
            key=f"hive_calendar_{calendar_view}"  # Dynamic key based on view
        )
        
        st.write("**Calendar component called successfully**")
        
        # Show calendar state for debugging
        if st.checkbox("🔍 Show Calendar State"):
            st.write("**Calendar State:**", calendar_state)
        
        # Handle calendar events (editing, deleting, etc.)
        if calendar_state.get("eventsSet"):
            # Handle event changes
            pass
            
        if calendar_state.get("eventClick"):
            clicked_event = calendar_state["eventClick"]["event"]
            st.info(f"📍 **{clicked_event.get('title', 'Unknown Event')}**")
            
            # Show event details
            extended_props = clicked_event.get("extendedProps", {})
            if extended_props:
                st.write(f"**Location:** {extended_props.get('location_label', 'N/A')}")
                st.write(f"**Hives:** {extended_props.get('hives', 'N/A')}")
                st.write(f"**Notes:** {extended_props.get('notes', 'No notes')}")
                
                # Option to delete the event
                if st.button("🗑️ Delete Event", key=f"delete_calendar_event_{clicked_event.get('id')}"):
                    event_id = int(clicked_event.get('id', -1))
                    st.session_state.scheduled_events = [
                        e for e in st.session_state.scheduled_events 
                        if e['id'] != event_id
                    ]
                    st.success("Event deleted!")
                    st.rerun()
        
        if calendar_state.get("select"):
            selection = calendar_state["select"]
            st.info(f"📅 **Date Range Selected:** {selection['start']} to {selection['end']}")
            st.info("💡 Use the form above to create a new hive placement for the selected dates.")
        
        # Show summary if no events
        if not st.session_state.scheduled_events:
            st.info("📅 No hive placements scheduled yet. Use the form above to create your first schedule!")
        
        # Export functionality
        if st.session_state.scheduled_events:
            st.subheader("📤 Export Schedule")
            
            export_data = pd.DataFrame(st.session_state.scheduled_events)
            csv = export_data.to_csv(index=False)
            
            st.download_button(
                label="💾 Download Schedule as CSV",
                data=csv,
                file_name=f"hive_schedule_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    #with tab3:
    #    st.subheader("📊 Analytics & Insights")
    #    
    #    col1, col2 = st.columns(2)
    #    
    #    with col1:
    #        # Distribution of prediction scores
    #        fig_dist = px.histogram(
    #            filtered_df,
    #            x='avg_prediction',
    #            nbins=20,
    #            title="Distribution of Average Prediction Scores",
    #            labels={'avg_prediction': 'Average Prediction Score', 'count': 'Number of Locations'}
    #        )
    #        fig_dist.update_layout(showlegend=False)
    #        st.plotly_chart(fig_dist, use_container_width=True)
    #        
    #        # Show weekly predictions if a specific week is selected
    #        if selected_week:
    #            week_col = f'week_{selected_week}_prediction'
    #            if week_col in filtered_df.columns:
    #                fig_week = px.histogram(
    #                    filtered_df,
    #                    x=week_col,
    #                    nbins=20,
    #                    title=f"Distribution of Week {selected_week} Predictions",
    #                    labels={week_col: f'Week {selected_week} Prediction Score', 'count': 'Number of Locations'}
    #                )
    #                fig_week.update_layout(showlegend=False)
    #                st.plotly_chart(fig_week, use_container_width=True)
    #        else:
    #            # Altitude vs Prediction correlation
    #            fig_corr = px.scatter(
    #                filtered_df,
    #                x='Altitudine',
    #                y='avg_prediction',
    #                color='best_week_num',
    #                title="Altitude vs Average Prediction Score",
    #                labels={'Altitudine': 'Altitude (m)', 'avg_prediction': 'Avg Prediction Score'}
    #            )
    #            st.plotly_chart(fig_corr, use_container_width=True)
    #    
    #    with col2:
    #        # Best weeks distribution
    #        week_counts = filtered_df['best_week_num'].value_counts().sort_index()
    #        fig_weeks = px.bar(
    #            x=week_counts.index,
    #            y=week_counts.values,
    #            title="Distribution of Best Performance Weeks",
    #            labels={'x': 'Week Number', 'y': 'Number of Locations'}
    #        )
    #        st.plotly_chart(fig_weeks, use_container_width=True)
    #        
    #        # Summary statistics
    #        st.subheader("📈 Summary Statistics")
    #        
    #        col_stat1, col_stat2 = st.columns(2)
    #        
    #        with col_stat1:
    #            st.metric(
    #                "🗺️ Total Locations",
    #                len(filtered_df),
    #                delta=f"{len(filtered_df) - len(df)} filtered"
    #            )
    #            st.metric(
    #                "🏔️ Avg Altitude",
    #                f"{filtered_df['Altitudine'].mean():.0f}m"
    #            )
    #        
    #        with col_stat2:
    #            st.metric(
    #                "🍯 Avg Prediction",
    #                f"{filtered_df['avg_prediction'].mean():.3f}"
    #            )
    #            st.metric(
    #                "📅 Most Common Best Week",
    #                int(filtered_df['best_week_num'].mode()[0])
    #            )
    #    
    #    # Scheduled events analytics
    #    if st.session_state.scheduled_events:
    #        st.subheader("📊 Scheduled Events Analytics")
    #        
    #        events_df = pd.DataFrame(st.session_state.scheduled_events)
    #        events_df['start_date'] = pd.to_datetime(events_df['start_date'])
    #        events_df['end_date'] = pd.to_datetime(events_df['end_date'])
    #        events_df['duration'] = (events_df['end_date'] - events_df['start_date']).dt.days
    #        
    #        col_event1, col_event2, col_event3 = st.columns(3)
    #        
    #        with col_event1:
    #            st.metric("📅 Total Events", len(events_df))
    #        with col_event2:
    #            st.metric("🐝 Total Hives", events_df['hives'].sum())
    #        with col_event3:
    #            st.metric("📊 Avg Duration", f"{events_df['duration'].mean():.1f} days")

if __name__ == "__main__":
    main() 