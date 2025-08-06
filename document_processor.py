"""
Document processor - handles various file types
"""

from pathlib import Path
from typing import Optional
from loguru import logger


def process_document(file_path: str, file_type: Optional[str] = None) -> str:
    """
    Process a document and extract its text content
    
    Args:
        file_path: Path to the document
        file_type: MIME type of the document
    
    Returns:
        Extracted text content
    """
    
    path = Path(file_path)
    
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Get file extension
    extension = path.suffix.lower()
    
    try:
        # Text files
        if extension in ['.txt', '.md', '.markdown']:
            return process_text_file(file_path)
        
        # CSV files
        elif extension == '.csv':
            return process_csv_file(file_path)
        
        # PDF files (requires additional library)
        elif extension == '.pdf':
            return process_pdf_file(file_path)
        
        # Word documents (requires additional library)
        elif extension in ['.docx', '.doc']:
            return process_word_file(file_path)
        
        # Default: try to read as text
        else:
            return process_text_file(file_path)
            
    except Exception as e:
        logger.error(f"Error processing document {file_path}: {e}")
        raise


def process_text_file(file_path: str) -> str:
    """Process plain text files"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()


def process_csv_file(file_path: str) -> str:
    """Process CSV files"""
    import csv
    
    content = []
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            content.append(', '.join(row))
    
    return '\n'.join(content)


def process_pdf_file(file_path: str) -> str:
    """Process PDF files"""
    try:
        import PyPDF2
        
        content = []
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                content.append(page.extract_text())
        
        return '\n'.join(content)
        
    except ImportError:
        logger.warning("PyPDF2 not installed. Install with: pip install PyPDF2")
        return "PDF processing not available. Please install PyPDF2."
    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        return f"Error processing PDF: {str(e)}"


def process_word_file(file_path: str) -> str:
    """Process Word documents"""
    try:
        from docx import Document
        
        doc = Document(file_path)
        content = []
        for paragraph in doc.paragraphs:
            content.append(paragraph.text)
        
        return '\n'.join(content)
        
    except ImportError:
        logger.warning("python-docx not installed. Install with: pip install python-docx")
        return "Word document processing not available. Please install python-docx."
    except Exception as e:
        logger.error(f"Error processing Word document: {e}")
        return f"Error processing Word document: {str(e)}"
