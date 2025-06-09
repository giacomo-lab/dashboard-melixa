import streamlit as st
import pandas as pd

from demo.utils.predictions_utils import retrieve_predictions

st.write("Hello world")

# get data
df = pd.read_csv("data/predict_data.csv", index_col=0)

if st.button("Get predictions"):

    # retrieve predictions
    predictions_df = retrieve_predictions(df)

    if predictions_df is not None:

        st.dataframe(predictions_df)
    else:
        st.error("Something went wrong, no predictions found.")
