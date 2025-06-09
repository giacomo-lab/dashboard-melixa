import os

import pandas as pd
import requests
from mlserver.codecs import PandasCodec
from mlserver.types import InferenceResponse
import streamlit as st
import numpy as np


def retrieve_predictions(data: pd.DataFrame) -> (np.array or None):

    host = f"{os.getenv('MLSERVER_USERNAME')}:{os.getenv('MLSERVER_PASSWORD')}@mlserver.u-hopper.com/honey_production/production"
    base_url = f"http://{host}/v2/models/honey_production"

    # get model schema
    cols = get_columns_from_model_schema(base_url).keys()

    # check columns and, in case missing, add zeros
    missing_cols = set(cols) - set(data.columns)

    st.warning(f"Missing columns: {missing_cols}")

    # add missing columns
    data = add_missing_columns(list(missing_cols), data)

    dict_data = prepare_data_input(data)
    headers = {'Content-Type': 'application/json'}
    response = requests.request("POST", base_url + "/infer", headers=headers, json=dict_data)

    if response.status_code == 200:
        raw_response = response.json()

        output_data = PandasCodec.decode_response(InferenceResponse(**raw_response))

        return output_data["output-1"].values
    else:
        return None


def get_columns_from_model_schema(base_url: str) -> dict:
    """
    Retrieve from base url the model schema: dictionary with column name and data type
    :param base_url:(the same url of invocations, without "/infer")
    """
    response = requests.request("GET", base_url)
    model_schema = response.json()

    columns = {i["name"]: i["datatype"] for i in model_schema["inputs"]}
    return columns


def add_missing_columns(missing_cols: list[str], data: pd.DataFrame) -> pd.DataFrame:
    """
    Add columns in missing_cols to data, having all zeros as values.
    """
    data[missing_cols] = 0
    return data


def prepare_data_input(data: pd.DataFrame) -> dict:
    """
    Prepare data to be input of POST invocation: encode with PandasCodec
    """
    inference_request = PandasCodec.encode_request(data, use_bytes=False)
    body = inference_request.model_dump()

    for i in range(len(body['inputs'])):
        body['inputs'][i]["shape"] = body['inputs'][i]["shape"][:1]

    return {"name": "honey_production", "inputs": body['inputs']}
