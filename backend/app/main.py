from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any
import traceback

from .services.pdf_processor import PDFProcessor
from .services.ocr_service import OCRService
from .services.gemini_service import GeminiService
from .config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PDF Data Extractor API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
pdf_processor = PDFProcessor()
ocr_service = OCRService()

# Initialize Gemini service with error handling
try:
    gemini_service = GeminiService(api_key=settings.GEMINI_API_KEY)
    logger.info("Gemini service initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini service: {e}")
    gemini_service = None
@app.get("/")
async def root():
    return {"message": "PDF Data Extractor API is running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "api_key_configured": bool(gemini_service),
        "services": {
            "pdf_processor": bool(pdf_processor),
            "ocr_service": bool(ocr_service),
            "gemini_service": bool(gemini_service)
        }
    }

@app.post("/api/extract")
async def extract_pdf_data(file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Extract tabular data from uploaded PDF file
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Read file content
        logger.info(f"Processing file: {file.filename}")
        content = await file.read()
        
        # Extract text from PDF
        logger.info("Extracting text from PDF...")
        text_content = pdf_processor.extract_text(content)
        logger.info(f"Extracted {len(text_content)} characters from PDF")
        
        # If no text found, try OCR
        if not text_content.strip():
            logger.info("No text found with direct extraction, attempting OCR...")
            try:
                images = pdf_processor.pdf_to_images(content)
                text_content = ocr_service.extract_text_from_images(images)
                logger.info(f"OCR extracted {len(text_content)} characters")
            except Exception as e:
                logger.warning(f"OCR failed: {e}")
        
        if not text_content.strip():
            raise HTTPException(status_code=422, detail="Could not extract any text from the PDF. The file might be corrupted, scanned without text, or protected.")
        
        # Check if Gemini service is available
        if not gemini_service:
            raise HTTPException(status_code=500, detail="AI service is not configured. Please check your API key configuration.")
        
        # Use Gemini to extract and structure tabular data
        logger.info("Sending text to Gemini for table extraction...")
        logger.info(f"Text preview: {text_content[:200]}...")
        
        extracted_data = gemini_service.extract_tables(text_content)
        
        # Validate the response
        if not extracted_data:
            logger.warning("Gemini returned empty response")
            extracted_data = {
                "tables": [],
                "summary": None,
                "message": "No tabular data found in the document"
            }
        
        # Ensure tables exist in response
        if "tables" not in extracted_data:
            extracted_data["tables"] = []
        
        logger.info(f"Found {len(extracted_data.get('tables', []))} tables")
        
        return {
            "success": True,
            "filename": file.filename,
            "data": extracted_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)