#!/bin/bash


echo "Running service..."

#
# Important note: env variables should not be passed as arguments to the module!
# This will allow for an easier automatisation of the docker support creation.
#




exec streamlit run demo/Home.py --server.port=8501 --server.address=0.0.0.0 --server.fileWatcherType none

