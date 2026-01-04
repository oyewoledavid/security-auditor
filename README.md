# Cloud Resource Auditor (CSPM Lite) ☁️ 

A lightweight Cloud Security Posture Management (CSPM) platform built with FastAPI and Python. This application scans AWS infrastructure (S3, IAM, EC2) for security misconfigurations, persists findings in a PostgreSQL database, and provides a REST API for reporting and compliance scoring.

    Project Goal: To bridge the gap between Infrastructure Engineering and Backend Development by building a scalable, asynchronous auditing engine.

### Architecture

This project uses a non-blocking asynchronous architecture. Since AWS Boto3 calls are synchronous (blocking), they are offloaded to background threads to ensure the FastAPI event loop remains responsive.

```
graph LR
    User[User/Client] -->|POST /scan| API[FastAPI Server]
    API -->|Ack 202| User
    API -->|Trigger| BG[Background Task Worker]
    
    subgraph "Async Loop"
        BG -->|Thread| S3[AWS S3 Auditor]
        BG -->|Thread| IAM[AWS IAM Auditor]
        BG -->|Thread| EC2[AWS EC2 Auditor]
    end
    
    S3 -->|Result| DB[(PostgreSQL)]
    IAM -->|Result| DB
    EC2 -->|Result| DB
    
    User -->|GET /stats| API
    API -->|Query| DB
```

###  Features

- Multi-Service Auditing:

    -  S3: Checks if Bucket Versioning is enabled (Data Protection).

    - IAM: Checks if Users have MFA enabled (Access Control).

    - EC2: Checks if Security Groups allow SSH (Port 22) from 0.0.0.0/0 (Network Security).

- Asynchronous Processing: Long-running scans happen in the background without freezing the API.

- Data Persistence: All audit results are stored in PostgreSQL using SQLModel (SQLAlchemy + Pydantic).

- Analytics: Dedicated endpoints for compliance scores and filtering results (Pass/Fail).

###  Tech Stack

- Language: Python 3.10+

- Framework: FastAPI (ASGI)

- Database: PostgreSQL (Asyncpg driver)

- ORM: SQLModel

- Cloud SDK: AWS Boto3

- Task Management: FastAPI BackgroundTasks & asyncio

###  Getting Started
Prerequisites

- Python 3.10+

- PostgreSQL (Local or Docker container)

- AWS Credentials configured locally

1. Clone & Setup

```bash
git clone https://github.com/yourusername/cloud-resource-auditor.git
cd cloud-resource-auditor

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install "fastapi[all]" sqlmodel asyncpg boto3 pydantic-settings
```
2. Configure Environment

Create a `.env` file in the root directory:
```
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/auditor_db
AWS_REGION=us-east-1
```
Ensure you have a database named auditor_db created in Postgres.

3. Run the Server
```bash
uvicorn app.main:app --reload
```
The server will start at http://127.0.0.1:8000.

###  API Usage
Interactive Docs

Visit http://127.0.0.1:8000/docs to see the Swagger UI.  
#### Key Endpoints  

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/audit/run-full-scan` | Triggers a background scan of ALL AWS resources. Returns `202 Accepted`. |
| **GET** | `/audit-results/` | List findings. Supports filtering: `?service=iam&compliant=false`. |
| **GET** | `/audit/stats` | Returns a compliance summary (Total checks, Pass/Fail count, Score %). |
| **POST** | `/audit/s3/{bucket_name}` | Audit a single specific bucket immediately. |

###  Future Roadmap

- [ ] Containerization: Docker & Docker Compose setup.

- [ ] Authentication: API Key or JWT implementation for secure access.

- [ ] Frontend: A simple React dashboard to visualize the Compliance Score.

- [ ] Alerting: Integration with Slack/SNS for critical failures.
