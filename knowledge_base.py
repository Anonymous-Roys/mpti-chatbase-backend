import os
import logging
import hashlib

logger = logging.getLogger(__name__)

class KnowledgeBase:
    def __init__(self):
        self.available = False
        self.collection = None
        self.initialize_knowledge_base()
    
    def initialize_knowledge_base(self):
        """Initialize knowledge base with error handling"""
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            
            self.client = chromadb.Client()
            self.collection = self.client.create_collection("mpti_documents")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.available = True
            logger.info("✅ Knowledge base initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Knowledge base dependencies not available: {e}")
            self.available = False
        except Exception as e:
            logger.error(f"Knowledge base initialization failed: {e}")
            self.available = False
    
    def is_available(self):
        return self.available
    
    def process_document(self, file_path, document_type):
        """Process document with basic text extraction"""
        try:
            text = self.extract_text(file_path)
            return self.chunk_text(text)
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return []
    
    def extract_text(self, file_path):
        """Extract text from various file types"""
        text = ""
        
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                
        elif file_path.endswith('.pdf'):
            text = self.extract_pdf_text(file_path)
            
        elif file_path.endswith('.docx'):
            text = self.extract_docx_text(file_path)
        
        return text
    
    def extract_pdf_text(self, file_path):
        """Extract text from PDF files"""
        try:
            import PyPDF2
            
            text = ""
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
            
        except ImportError:
            logger.warning("PyPDF2 not available for PDF extraction")
            return "PDF content - install PyPDF2 for text extraction"
    
    def extract_docx_text(self, file_path):
        """Extract text from DOCX files"""
        try:
            import docx
            
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
            
        except ImportError:
            logger.warning("python-docx not available for DOCX extraction")
            return "DOCX content - install python-docx for text extraction"
    
    def chunk_text(self, text, chunk_size=500):
        """Split text into manageable chunks"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i + chunk_size])
            chunks.append(chunk)
            
        return chunks
    
    def add_documents(self, documents, metadata=None):
        """Add documents to knowledge base"""
        if not self.available:
            logger.warning("Knowledge base not available")
            return False
        
        try:
            embeddings = self.model.encode(documents).tolist()
            ids = [f"doc_{hashlib.md5(doc.encode()).hexdigest()[:8]}" for doc in documents]
            
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadata or [{}] * len(documents),
                ids=ids
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            return False
    
    def search(self, query, n_results=3):
        """Search knowledge base"""
        if not self.available:
            return {'documents': [], 'distances': []}
        
        try:
            query_embedding = self.model.encode([query]).tolist()
            
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Knowledge base search failed: {e}")
            return {'documents': [], 'distances': []}