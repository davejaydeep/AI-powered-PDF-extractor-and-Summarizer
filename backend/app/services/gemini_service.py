import google.generativeai as genai
import json
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def extract_tables(self, text: str) -> Dict[str, Any]:
        """Use Gemini to extract and structure tabular data from text"""
        try:
            # Limit text length to avoid API limits
            text_to_analyze = text[:8000] if len(text) > 8000 else text
            
            prompt = """
            You are a data extraction specialist. Analyze the following text and extract ALL tabular data.
            Look for:
            - Invoice/receipt line items
            - Product descriptions, quantities, prices, totals
            - Dates, invoice numbers, vendor information
            - Any structured data that can be presented in tables
            
            IMPORTANT: Even if the data seems unstructured, try to create meaningful tables from any relevant information.
            
            Return data in this EXACT JSON format (no extra text):
            {
                "tables": [
                    {
                        "title": "Invoice Items",
                        "headers": ["Description", "Quantity", "Unit Price", "Total"],
                        "rows": [
                            ["Product A", "2", "$50.00", "$100.00"],
                            ["Product B", "1", "$75.00", "$75.00"]
                        ]
                    }
                ],
                "summary": {
                    "total_amount": 175.00,
                    "invoice_count": 1,
                    "date_range": "2024-01-01"
                }
            }
            
            If you find ANY numerical data, prices, or structured information, create a table for it.
            Do not return empty tables unless there is truly NO structured data at all.
            
            Text to analyze:
            """ + text_to_analyze
            
            logger.info(f"Sending {len(text_to_analyze)} characters to Gemini...")
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.error("Empty response from Gemini")
                return {
                    "tables": [],
                    "summary": None,
                    "error": "Empty response from AI service"
                }
            
            # Parse the response
            response_text = response.text.strip()
            logger.info(f"Gemini response length: {len(response_text)}")
            logger.debug(f"Raw Gemini response: {response_text[:500]}...")
            
            # Clean up the response to extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    response_text = response_text[json_start:json_end]
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                if json_end != -1:
                    response_text = response_text[json_start:json_end]
            elif "{" in response_text and "}" in response_text:
                # Extract JSON from the response
                start = response_text.find("{")
                end = response_text.rfind("}") + 1
                response_text = response_text[start:end]
            
            try:
                data = json.loads(response_text)
                logger.info(f"Successfully parsed JSON with {len(data.get('tables', []))} tables")
                
                # Validate structure
                if not isinstance(data, dict):
                    raise ValueError("Response is not a dictionary")
                
                if "tables" not in data:
                    data["tables"] = []
                
                # Ensure all tables have required fields
                for table in data["tables"]:
                    if "title" not in table:
                        table["title"] = "Extracted Data"
                    if "headers" not in table:
                        table["headers"] = []
                    if "rows" not in table:
                        table["rows"] = []
                
                return data
                
            except json.JSONDecodeError as e:
                logger.warning(f"Could not parse Gemini response as JSON: {e}")
                logger.debug(f"Cleaned response text: {response_text}")
                
                # Try to create a fallback table from the response
                return {
                    "tables": [{
                        "title": "Raw Extracted Data",
                        "headers": ["Content"],
                        "rows": [[response_text[:200] + "..." if len(response_text) > 200 else response_text]]
                    }],
                    "summary": None,
                    "warning": "Could not parse structured data, showing raw response"
                }
            
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            return {
                "tables": [],
                "summary": None,
                "error": f"AI processing failed: {str(e)}"
            }