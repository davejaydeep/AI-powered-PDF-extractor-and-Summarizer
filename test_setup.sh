#!/bin/bash
echo "🚀 Quick Test Script for PDF Backend"
echo "======================================"
echo ""

echo "1️⃣ Activating conda environment..."
conda activate pdf-processor-env

echo ""
echo "2️⃣ Testing backend functionality..."
cd /mnt/f/workspaces/interviews/AI-powered-PDF-extractor-and-Summarizer/backend
python debug_backend.py

echo ""
echo "3️⃣ Starting the backend server..."
echo "After fixing your API key, run:"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "4️⃣ Frontend is available at: http://localhost:5173"
echo "5️⃣ Backend API is available at: http://localhost:8000"
echo "6️⃣ API health check: http://localhost:8000/health"