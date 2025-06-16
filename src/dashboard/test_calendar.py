#!/usr/bin/env python3
"""
Simple test for streamlit-calendar component
"""

import streamlit as st
from datetime import datetime, timedelta

# Test if streamlit-calendar is installed and working
try:
    from streamlit_calendar import calendar
    st.success("✅ streamlit-calendar imported successfully!")
except ImportError as e:
    st.error(f"❌ streamlit-calendar import failed: {e}")
    st.info("Please install with: pip install streamlit-calendar")
    st.stop()

st.title("🔍 Calendar Component Test")

st.info("This is a simple test to verify streamlit-calendar is working correctly.")

# Test 1: Empty calendar
st.subheader("Test 1: Basic Empty Calendar")

try:
    basic_calendar = calendar(
        events=[],
        options={
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth"
            },
            "initialView": "dayGridMonth",
            "height": 400
        },
        key="test_basic"
    )
    st.success("✅ Basic calendar rendered successfully!")
    st.write("Calendar state:", basic_calendar)
except Exception as e:
    st.error(f"❌ Basic calendar failed: {e}")

# Test 2: Calendar with sample events
st.subheader("Test 2: Calendar with Sample Events")

sample_events = [
    {
        "id": "1",
        "title": "Test Event 1",
        "start": datetime.now().strftime("%Y-%m-%d"),
        "end": (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
        "backgroundColor": "#FFD700"
    },
    {
        "id": "2", 
        "title": "Test Event 2",
        "start": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "end": (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        "backgroundColor": "#FF8C00"
    }
]

try:
    events_calendar = calendar(
        events=sample_events,
        options={
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title", 
                "right": "dayGridMonth,dayGridWeek"
            },
            "initialView": "dayGridMonth",
            "height": 500,
            "editable": True,
            "selectable": True
        },
        key="test_events"
    )
    st.success("✅ Calendar with events rendered successfully!")
    st.write("Calendar state:", events_calendar)
except Exception as e:
    st.error(f"❌ Calendar with events failed: {e}")

# Test 3: Different views
st.subheader("Test 3: Different Calendar Views")

view_option = st.selectbox("Select View", ["dayGridMonth", "dayGridWeek", "listWeek"])

try:
    view_calendar = calendar(
        events=sample_events,
        options={
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,dayGridWeek,listWeek"
            },
            "initialView": view_option,
            "height": 500
        },
        key=f"test_view_{view_option}"
    )
    st.success(f"✅ {view_option} view rendered successfully!")
except Exception as e:
    st.error(f"❌ {view_option} view failed: {e}")

st.markdown("---")
st.info("If all tests pass, the calendar component is working correctly. If any fail, there may be an installation or compatibility issue.") 