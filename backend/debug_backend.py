#!/usr/bin/env python3
"""
Debug script for PDF processor backend
This script helps identify and fix common issues
"""

import os
import sys
from pathlib import Path

def check_environment():
    """Check if conda environment and packages are working"""
    print("🔍 Checking Python environment...")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        return False
    
    try:
        import PyPDF2
        print("✅ PyPDF2 imported successfully")
    except ImportError as e:
        print(f"❌ PyPDF2 import failed: {e}")
        return False
    
    try:
        import fastapi
        print(f"✅ FastAPI {fastapi.__version__} imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    return True

def check_env_file():
    """Check if .env file exists and has API key"""
    print("\n🔍 Checking environment configuration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found")
        print("📝 Creating .env template...")
        with open(".env", "w") as f:
            f.write("# Gemini API Configuration\n")
            f.write("# Get your API key from: https://makersuite.google.com/app/apikey\n")
            f.write("GEMINI_API_KEY=your_api_key_here\n\n")
            f.write("# Server Configuration\n")
            f.write("MAX_FILE_SIZE=10485760  # 10MB\n")
        print("✅ .env template created - please add your API key")
        return False
    else:
        print("✅ .env file exists")
        
        # Check if API key is configured
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            print("❌ GEMINI_API_KEY not configured in .env file")
            print("🔗 Get your API key from: https://makersuite.google.com/app/apikey")
            return False
        else:
            print(f"✅ GEMINI_API_KEY configured (starts with: {api_key[:10]}...)")
            return True

def test_gemini_connection():
    """Test connection to Gemini API"""
    print("\n🔍 Testing Gemini API connection...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            print("❌ API key not configured")
            return False
        
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Test with simple text
        response = model.generate_content("Test: Extract any numbers from this text: Price $25.99, Quantity 3")
        
        if response and response.text:
            print("✅ Gemini API connection successful")
            print(f"📄 Test response: {response.text[:100]}...")
            return True
        else:
            print("❌ Gemini API returned empty response")
            return False
            
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def test_pdf_processing():
    """Test PDF processing with a sample"""
    print("\n🔍 Testing PDF processing...")
    
    try:
        # Create a simple test PDF content (this is just a test)
        test_text = """
        Invoice #12345
        Date: 2024-01-15
        
        Item 1: Widget A - Qty: 2 - Price: $15.99 - Total: $31.98
        Item 2: Widget B - Qty: 1 - Price: $25.50 - Total: $25.50
        
        Subtotal: $57.48
        Tax: $5.75
        Total: $63.23
        """
        
        from app.services.gemini_service import GeminiService
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your_api_key_here":
            print("❌ Cannot test - API key not configured")
            return False
        
        gemini_service = GeminiService(api_key=api_key)
        result = gemini_service.extract_tables(test_text)
        
        if result and "tables" in result and len(result["tables"]) > 0:
            print("✅ PDF text processing successful")
            print(f"📊 Found {len(result['tables'])} table(s)")
            for i, table in enumerate(result["tables"]):
                print(f"   Table {i+1}: {table.get('title', 'Untitled')} - {len(table.get('rows', []))} rows")
            return True
        else:
            print("❌ PDF processing failed - no tables extracted")
            print(f"📄 Result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ PDF processing test failed: {e}")
        return False

def main():
    """Run all diagnostic checks"""
    print("🚀 PDF Processor Backend Diagnostics\n")
    
    checks_passed = 0
    total_checks = 4
    
    if check_environment():
        checks_passed += 1
    
    if check_env_file():
        checks_passed += 1
    
    if test_gemini_connection():
        checks_passed += 1
    
    if test_pdf_processing():
        checks_passed += 1
    
    print(f"\n📊 Diagnostic Results: {checks_passed}/{total_checks} checks passed")
    
    if checks_passed == total_checks:
        print("🎉 All checks passed! Your backend should be working.")
        print("\n🚀 To start the server:")
        print("   conda activate pdf-processor-env")
        print("   cd backend")
        print("   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        if checks_passed < 2:
            print("\n🔧 Quick fixes:")
            print("1. Make sure you're in the pdf-processor-env conda environment")
            print("2. Run: pip install -r requirements.txt")
            print("3. Get a Gemini API key from: https://makersuite.google.com/app/apikey")
            print("4. Add the API key to your .env file")

if __name__ == "__main__":
    main()