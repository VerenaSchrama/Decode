# HerFoodCode RAG Backend

This repository contains the RAG (Retrieval-Augmented Generation) backend components extracted from the original HerFoodCode application. This is the core AI/ML pipeline that powers personalized health advice generation.

## 🏗️ **Architecture Overview**

### **RAG Pipeline Components**
- **Document Processing**: PDF → Text → Chunks → Vector Embeddings
- **Vector Database**: ChromaDB for similarity search
- **LLM Integration**: OpenAI GPT-4 for content generation
- **Strategy Database**: CSV-based strategy management

### **Core Technology Stack**
- **Python 3.13** - Programming language
- **LangChain** - Conversational AI framework
- **OpenAI GPT-4** - Language model
- **ChromaDB** - Vector database
- **Pandas** - Data manipulation
- **PDF Processing** - Text extraction from health books

## 📁 **Repository Structure**

```
hfc_app_v2/
├── backend/
│   ├── rag_pipeline.py          # Main RAG pipeline
│   ├── build_strategy_store.py  # Vector store builder
│   ├── requirements.txt         # Python dependencies
│   └── data/
│       ├── strategies.csv       # Strategy database
│       ├── raw_book/
│       │   ├── InFloBook.pdf    # Source health book
│       │   └── InFloBook.txt    # Extracted text
│       ├── processed/
│       │   └── chunks_AlisaVita.json  # Processed text chunks
│       └── vectorstore/         # ChromaDB vector stores
│           ├── chroma/          # Main vector store
│           └── strategies_chroma/  # Strategy-specific vector store
├── build_vectorstore.py         # PDF processing script
└── README.md                    # This file
```

## 🚀 **Quick Start**

### **1. Environment Setup**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### **2. Environment Variables**
Create a `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### **3. Build Vector Store**
```bash
# Process PDF and create vector store
python build_vectorstore.py

# Build strategy vector store
python backend/build_strategy_store.py
```

### **4. Test RAG Pipeline**
```python
from backend.rag_pipeline import generate_advice

# Generate advice using RAG
result = generate_advice(
    user_question="What should I eat for PCOS?",
    user_context="I have PCOS and insulin resistance"
)
print(result["answer"])
```

## 🔄 **RAG Pipeline Flow**

### **1. Document Processing**
```
InFloBook.pdf → Text Extraction → Chunking → Embeddings → ChromaDB
```

### **2. Query Processing**
```
User Question → Vector Search → Context Retrieval → GPT-4 → Response
```

### **3. Strategy Retrieval**
```
User Context → Strategy Matching → Personalized Recommendations
```

## 📊 **Data Sources**

### **Primary Content**
- **InFloBook.pdf**: Comprehensive health and nutrition guide
- **strategies.csv**: Structured strategy database with metadata

### **Vector Stores**
- **Main Store**: General health content from the book
- **Strategy Store**: Specific intervention strategies

## 🛠️ **Development**

### **Adding New Strategies**
1. Update `backend/data/strategies.csv`
2. Rebuild vector store: `python backend/build_strategy_store.py`

### **Modifying RAG Pipeline**
- Edit `backend/rag_pipeline.py` for core RAG logic

### **Testing Changes**
```bash
# Test vector store creation
python backend/build_strategy_store.py

# Test RAG pipeline
python -c "from backend.rag_pipeline import generate_advice; print(generate_advice('test question'))"
```

## 📈 **Performance Considerations**

- **Chunk Size**: 500 characters with 100 character overlap
- **Embedding Model**: OpenAI text-embedding-ada-002
- **Retrieval**: Top 3 most similar documents
- **LLM Model**: GPT-4 with temperature 0 for consistency

## 🔒 **Security**

- API keys stored in environment variables
- No sensitive data in repository
- Vector stores contain only processed health content

## 📝 **Usage Examples**

### **Basic RAG Query**
```python
from backend.rag_pipeline import generate_advice

result = generate_advice(
    user_question="How can I manage insulin resistance?",
    user_context="I have PCOS and want to improve my blood sugar"
)
```


## 🤝 **Contributing**

This is the core RAG backend extracted from the original HerFoodCode application. It's designed to be integrated into new frontend applications while maintaining the powerful AI-driven health advice generation capabilities.

## 📄 **License**

[Add your license information here]

---

**Note**: This repository contains only the RAG backend components. The original application's frontend, database schemas, and other components have been archived separately.
