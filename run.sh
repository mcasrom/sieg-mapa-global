#!/bin/bash

cd /home/miguelc/sieg-mapa-global

source venv/bin/activate

streamlit run app.py --server.port 8501 --server.address 0.0.0.0
