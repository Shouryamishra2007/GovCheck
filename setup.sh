#!/bin/bash
set -e

echo "🚀 GovCheck AI Platform - Setup"
echo "================================"

# 1. Virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Dependencies
pip install -r requirements.txt

# 3. Environment
cp .env.example .env
echo "⚠️  Edit .env and add your GEMINI_API_KEY"

# 4. Run
echo "Starting GovCheck..."
python main.py