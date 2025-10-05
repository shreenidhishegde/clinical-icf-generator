#!/bin/bash

# Clinical Protocol Information Extractor - Setup Script
# This script sets up the development environment

echo "🚀 Setting up Clinical Protocol Information Extractor..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 16+ first."
    exit 1
fi

echo "✅ Python and Node.js are installed"

# Setup backend
echo "📦 Setting up backend..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from example..."
    cp env.example .env
    echo "⚠️  Please edit backend/.env file and add your actual API keys"
    echo "   Get your OpenAI API key from: https://platform.openai.com/api-keys"
else
    echo "✅ .env file already exists"
fi

# Setup frontend
echo "📦 Setting up frontend..."
cd frontend
npm install
cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Start backend: python manage.py runserver"
echo "3. In another terminal, start frontend: cd frontend && npm run dev"
echo ""
echo "Backend will be available at: http://127.0.0.1:8000"
echo "Frontend will be available at: http://localhost:5173"
