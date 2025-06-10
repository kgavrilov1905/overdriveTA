import fitz  # PyMuPDF
import re
from typing import List, Dict, Any, Tuple
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    async def extract_text_from_pdf(self, file_content: bytes) -> Tuple[str, List[Dict[str, Any]]]:
        """Extract text from PDF and return full text plus page-wise metadata"""
        try:
            # Open PDF from bytes
            pdf_document = fitz.open(stream=file_content, filetype="pdf")
            
            full_text = ""
            pages_data = []
            
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                page_text = page.get_text()
                
                # Clean up the text
                page_text = self._clean_text(page_text)
                
                if page_text.strip():  # Only add non-empty pages
                    pages_data.append({
                        "page_number": page_num + 1,
                        "text": page_text,
                        "char_count": len(page_text)
                    })
                    full_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"
            
            pdf_document.close()
            
            return full_text, pages_data
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"Failed to process PDF: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page headers/footers patterns (common in reports)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)  # Remove standalone page numbers
        
        # Fix common OCR issues
        text = text.replace('ﬁ', 'fi').replace('ﬂ', 'fl')
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text.strip()
    
    async def create_intelligent_chunks(self, text: str, pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create intelligent chunks that respect document structure"""
        chunks = []
        
        # First, try to split by sections/headings
        section_chunks = self._split_by_sections(text)
        
        # If no clear sections, fall back to paragraph-based chunking
        if len(section_chunks) <= 1:
            section_chunks = self._split_by_paragraphs(text)
        
        # Further split large chunks
        final_chunks = []
        for section in section_chunks:
            if len(section) > self.chunk_size:
                final_chunks.extend(self._split_large_chunk(section))
            else:
                final_chunks.append(section)
        
        # Create chunk objects with metadata
        for idx, chunk_text in enumerate(final_chunks):
            if chunk_text.strip():  # Only add non-empty chunks
                # Determine which page this chunk likely comes from
                page_number = self._estimate_page_number(chunk_text, pages_data)
                
                chunks.append({
                    "chunk_text": chunk_text.strip(),
                    "chunk_index": idx,
                    "page_number": page_number,
                    "char_count": len(chunk_text),
                    "metadata": {
                        "chunk_method": "intelligent",
                        "estimated_page": page_number
                    }
                })
        
        return chunks
    
    def _split_by_sections(self, text: str) -> List[str]:
        """Split text by section headers"""
        # Look for common section patterns in economic reports
        section_patterns = [
            r'\n\s*(?:CHAPTER|Chapter)\s+\d+[:\-\s]',
            r'\n\s*(?:SECTION|Section)\s+\d+[:\-\s]',
            r'\n\s*\d+\.\s+[A-Z][A-Za-z\s]{10,50}\n',
            r'\n\s*[A-Z][A-Z\s]{15,80}\n\s*\n',  # ALL CAPS headers
            r'\n\s*(?:Executive Summary|Introduction|Methodology|Results|Conclusion|Appendix)',
        ]
        
        for pattern in section_patterns:
            sections = re.split(pattern, text, flags=re.IGNORECASE)
            if len(sections) > 2:  # Found meaningful sections
                return [section.strip() for section in sections if section.strip()]
        
        return [text]  # Return original text if no sections found
    
    def _split_by_paragraphs(self, text: str) -> List[str]:
        """Split text by paragraphs, grouping small ones together"""
        paragraphs = re.split(r'\n\s*\n', text)
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            
            # If adding this paragraph would exceed chunk size, start new chunk
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                chunks.append(current_chunk)
                current_chunk = paragraph
            else:
                current_chunk += "\n\n" + paragraph if current_chunk else paragraph
        
        if current_chunk:
            chunks.append(current_chunk)
        
        return chunks
    
    def _split_large_chunk(self, text: str) -> List[str]:
        """Split large chunks using sliding window approach"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # If this is not the last chunk, try to break at sentence boundary
            if end < len(text):
                # Look for sentence end within overlap range
                sentence_end = text.rfind('.', end - self.chunk_overlap, end)
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
            
            # Prevent infinite loop
            if start >= end:
                start = end
        
        return chunks
    
    def _estimate_page_number(self, chunk_text: str, pages_data: List[Dict[str, Any]]) -> int:
        """Estimate which page a chunk comes from by finding best text match"""
        best_match_page = 1
        best_match_score = 0
        
        # Take first 100 characters of chunk for matching
        chunk_sample = chunk_text[:100].lower()
        
        for page_data in pages_data:
            page_text = page_data["text"].lower()
            
            # Simple containment score
            if chunk_sample in page_text:
                score = len(chunk_sample)
            else:
                # Calculate similarity based on common words
                chunk_words = set(chunk_sample.split())
                page_words = set(page_text.split())
                common_words = chunk_words.intersection(page_words)
                score = len(common_words)
            
            if score > best_match_score:
                best_match_score = score
                best_match_page = page_data["page_number"]
        
        return best_match_page
    
    async def get_document_title(self, text: str, filename: str) -> str:
        """Extract or generate a meaningful title for the document"""
        # Try to find title in first few lines
        lines = text.split('\n')[:10]
        
        for line in lines:
            line = line.strip()
            # Look for title-like patterns
            if (len(line) > 20 and len(line) < 100 and 
                line.isupper() and 
                not re.match(r'^\d+\s', line)):
                return line.title()
        
        # Fall back to filename without extension
        return filename.replace('.pdf', '').replace('_', ' ').replace('-', ' ').title()

# Singleton instance
document_processor = DocumentProcessor() 