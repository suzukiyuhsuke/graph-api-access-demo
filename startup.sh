#!/bin/bash
# Startup script for Azure App Service

# Install dependencies
python -m pip install --upgrade pip --no-cache-dir
pip install -r requirements.txt --no-cache-dir

# Run Streamlit application
python -m streamlit run app.py --server.port=8000 --server.address=0.0.0.0 --server.headless=true
