# Chatbot Management Platform

A FastAPI-based backend for managing chatbots, document ingestion, query processing, billing, and usage tracking. Supports multi-tenancy with customer and user management.

## Table of Contents
- [Requirements](#requirements)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Database Management](#database-management)
- [API Endpoints](#api-endpoints)
- [Database Relations](#database-relations)
- [Important Notes](#important-notes)

## Requirements

**Python Dependencies** (install via `pip install -r requirements.txt`):
```
fastapi>=0.68.0
uvicorn>=0.15.0
sqlalchemy>=1.4.0
alembic>=1.7.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-dotenv>=0.19.0
langchain>=0.1.0
chromadb>=0.3.0
fireworks-ai>=0.5.0
```

**System Requirements**:
- PostgreSQL 13+
- Python 3.9+
- 4GB RAM minimum (8GB recommended for AI operations)

## Installation & Setup

1. Clone repository:
```bash
git clone https://github.com/your-username/tameem1-project2.git
cd tameem1-project2
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database:
```sql
CREATE DATABASE mydatabase;
CREATE USER myuser WITH PASSWORD 'mypassword';
GRANT ALL PRIVILEGES ON DATABASE mydatabase TO myuser;
```

## Configuration

Create `.env` file:
```ini
DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/mydatabase
SECRET_KEY=your-secure-secret-key-here
ALGORITHM=HS256
```

## Running the Application

**Development Mode**:
```bash
uvicorn main:app --reload
```

**Production Mode**:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Database Management

**Initial Setup**:
```bash
alembic upgrade head
```

**Create New Migration**:
```bash
alembic revision --autogenerate -m "description of changes"
alembic upgrade head
```

## API Endpoints

### Authentication
| Endpoint       | Method | Description              |
|----------------|--------|--------------------------|
| `/auth/register` | POST   | Register new user/customer |
| `/auth/token`    | POST   | Get JWT access token      |

### Chatbots
| Endpoint                          | Method | Description                      |
|-----------------------------------|--------|----------------------------------|
| `/api/chatbots`                   | POST   | Create new chatbot               |
| `/api/chatbots`                   | GET    | List all chatbots for customer   |
| `/api/chatbots/{chatbot_id}/snippet` | GET | Get embed code snippet for chatbot |

### Documents
| Endpoint                      | Method | Description          |
|-------------------------------|--------|----------------------|
| `/api/upload/{chatbot_id}`    | POST   | Upload document      |

### Query
| Endpoint                          | Method | Description                      |
|-----------------------------------|--------|----------------------------------|
| `/api/public/{chatbot_id}/query`  | POST   | Public query endpoint (API key)  |
| `/api/{customer_id}/{chatbot_id}/query` | POST | Authenticated query endpoint |

[View full API documentation](API_DOCS.md)

## Database Relations

```mermaid
erDiagram
    CUSTOMER {
        UUID id PK
        string name
        string contact_email
        json billing_info
        int usage_tokens
        datetime created_at
        datetime updated_at
    }
    
    USER {
        UUID id PK
        string username
        string password_hash
        UUID customer_id FK
        datetime created_at
        datetime updated_at
    }

    CHATBOT {
        UUID id PK
        UUID customer_id FK
        string name
        string description
        string api_key
        int demo_message_count
        datetime created_at
        datetime updated_at
    }

    DOCUMENT {
        UUID id PK
        UUID chatbot_id FK
        string filename
        string file_path
        string file_type
        json metadata_json
        datetime uploaded_at
    }

    CHAT_HISTORY {
        UUID id PK
        UUID chatbot_id FK
        UUID user_id FK
        text question
        text answer
        datetime timestamp
    }

    BILLING {
        UUID id PK
        UUID customer_id FK
        string invoice_number
        numeric(10,2) amount
        string status
        datetime issued_at
        datetime due_date
    }

    USAGE_TOKEN {
        UUID id PK
        UUID customer_id FK
        int tokens_used
        int tokens_remaining
        int input_tokens_used
        int output_tokens_used
        datetime last_updated
    }

    CUSTOMER ||--o{ USER : "has"
    CUSTOMER ||--o{ CHATBOT : "owns"
    CUSTOMER ||--o{ BILLING : "has"
    CUSTOMER ||--o{ USAGE_TOKEN : "tracks"
    CHATBOT ||--o{ DOCUMENT : "contains"
    CHATBOT ||--o{ CHAT_HISTORY : "maintains"
    USER ||--o{ CHAT_HISTORY : "generates"

**Key Relationships**:
- Customers have multiple Users and Chatbots
- Each Chatbot maintains its Document collection and Chat History
- UsageToken tracks token consumption per Customer
- Billing records are linked to Customers

## Important Notes

1. **JWT Authentication**:
   - Use `Authorization: Bearer <token>` header for protected endpoints
   - Tokens expire after 1 hour (configurable in auth_service.py)

2. **Vector Store**:
   - Documents are stored in `uploads/{customer_id}/{chatbot_id}`
   - ChromaDB vector stores are created in `chroma_dbs/{customer_id}/{chatbot_id}`

3. **Rate Limits**:
   - Demo endpoints are limited to 10 messages per user/chatbot
   - Production endpoints use token-based rate limiting

4. **API Keys**:
   - Chatbot API keys are generated automatically on creation
   - Rotate keys via `/api/chatbots/{chatbot_id}/rotate_key` endpoint

5. **Embedding Model**:
   - Uses `intfloat/multilingual-e5-large` embeddings
   - Configured for CPU usage (update device in embedding_utils.py for GPU)

6. **LLM Integration**:
   - Uses Fireworks.ai's `qwen2p5-coder-32b-instruct` model
   - Replace API key in query_service.py for production use
```
