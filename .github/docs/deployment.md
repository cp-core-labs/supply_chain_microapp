# Deployment Guide

This document outlines the deployment instructions and best practices for the **Supply Chain & Inventory Optimization Platform**.

## Local Deployment

### 1. Manual Setup
Activate your environment according to your operating system:

- **Windows (PowerShell):**
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\Activate
  pip install -r requirements-dev.txt
  streamlit run app.py