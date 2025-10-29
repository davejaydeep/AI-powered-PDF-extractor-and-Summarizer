import React, { useState } from 'react';
import FileUpload from './components/FileUpload';
import DataTable from './components/DataTable';
import { extractPDFData } from './services/api';
import type { ExtractedData } from './types';
import './App.css';

const App: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [extractedData, setExtractedData] = useState<ExtractedData | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleFileUpload = async (file: File) => {
    // File format validation
    const allowedTypes = ['application/pdf'];
    const allowedExtensions = ['.pdf'];
    
    // Check MIME type
    if (!allowedTypes.includes(file.type)) {
      setError(`Invalid file type: ${file.type}. Only PDF files are allowed.`);
      return;
    }
    
    // Check file extension
    const fileName = file.name.toLowerCase();
    const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
    
    if (!hasValidExtension) {
      setError(`Invalid file format. Please upload a PDF file (.pdf)`);
      return;
    }
    
    // Check file size (optional - e.g., 10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB in bytes
    if (file.size > maxSize) {
      setError(`File size too large. Maximum allowed size is 10MB. Your file is ${(file.size / 1024 / 1024).toFixed(2)}MB`);
      return;
    }

    setLoading(true);
    setError(null);
    setExtractedData(null);

    try {
      const data = await extractPDFData(file);
      setExtractedData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to extract data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>📄 AI-Powered PDF Data Extractor</h1>
        <p>Transform your PDF documents into structured data with the power of artificial intelligence</p>
      </header>

      <main className="app-main">
        <FileUpload onFileUpload={handleFileUpload} disabled={loading} />

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
            <p>🤖 AI is analyzing your PDF... Please wait while we extract the data.</p>
          </div>
        )}

        {error && (
          <div className="error">
            <p>⚠️ {error}</p>
          </div>
        )}

        {extractedData && (
          <div className="results">
            <h2>✨ Extracted Data</h2>
            {extractedData.data.summary && (
  <div className="summary">
    <h3>Summary</h3>
    <div className="summary-grid">
      <div className="summary-item">
        <strong>Total Amount</strong>
        <span className="summary-value">
          ${extractedData.data.summary.total_amount.toLocaleString('en-US', { 
            minimumFractionDigits: 2,
            maximumFractionDigits: 2 
          })}
        </span>
      </div>
      <div className="summary-item">
        <strong>Invoice Count</strong>
        <span className="summary-value">
          {extractedData.data.summary.invoice_count}
        </span>
      </div>
      <div className="summary-item">
        <strong>Date Range</strong>
        <span className="summary-value">
          {extractedData.data.summary.date_range}
        </span>
      </div>
    </div>
  </div>
)}

            {extractedData.data.tables && extractedData.data.tables.length > 0 ? (
              extractedData.data.tables.map((table, index) => (
                <DataTable key={index} table={table} />
              ))
            ) : (
              <p>No tabular data found in the PDF</p>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default App;