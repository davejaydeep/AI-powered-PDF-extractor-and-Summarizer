// frontend/src/components/FileUpload.tsx
import React, { useRef, useState } from 'react';

interface FileUploadProps {
  onFileUpload: (file: File) => void;
  disabled?: boolean;
}

const FileUpload: React.FC<FileUploadProps> = ({ onFileUpload, disabled }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  const validateFile = (file: File): string | null => {
    // Check file type
    const validTypes = ['application/pdf'];
    if (!validTypes.includes(file.type) && !file.name.toLowerCase().endsWith('.pdf')) {
      return `❌ Invalid file type. Only PDF files are allowed. You uploaded: ${file.type || 'unknown type'}`;
    }

    // Check file extension
    const fileName = file.name.toLowerCase();
    if (!fileName.endsWith('.pdf')) {
      const extension = fileName.split('.').pop() || 'no extension';
      return `❌ Invalid file extension ".${extension}". Only .pdf files are allowed.`;
    }

    // Check file size (10MB limit)
    const maxSize = 10 * 1024 * 1024; // 10MB
    if (file.size > maxSize) {
      const sizeInMB = (file.size / 1024 / 1024).toFixed(2);
      return `❌ File too large (${sizeInMB}MB). Maximum size is 10MB.`;
    }

    // Check if file is empty
    if (file.size === 0) {
      return '❌ File is empty. Please upload a valid PDF file.';
    }

    return null; // No errors
  };

  const handleFile = (file: File) => {
    setValidationError(null);
    
    const error = validateFile(file);
    if (error) {
      setValidationError(error);
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file.name);
    setValidationError(null);
    onFileUpload(file);
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  return (
    <div className="file-upload-container">
      <div
        className={`file-upload ${dragActive ? 'drag-active' : ''} ${disabled ? 'disabled' : ''} ${validationError ? 'error-state' : ''}`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,application/pdf"
          onChange={handleChange}
          disabled={disabled}
          style={{ display: 'none' }}
        />
        
        <div className="upload-icon">�</div>
        <p>Drag and drop your PDF here</p>
        <p className="upload-or">OR</p>
        <button
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled}
          className="upload-button btn-primary"
        >
          📁 Browse Files
        </button>
        
        <p className="file-requirements">
          Only PDF files • Maximum 10MB
        </p>
        
        {selectedFile && !validationError && (
          <p className="selected-file">✅ Selected: {selectedFile}</p>
        )}
        
        {validationError && (
          <div className="validation-error">
            <p>{validationError}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default FileUpload;