# Cloud Resource Auditor (CSPM Lite) ☁️ 

A robust, asynchronous Cloud Security Posture Management (CSPM) platform built with FastAPI. This application scans AWS infrastructure (S3, IAM, EC2) for security misconfigurations, persists findings in PostgreSQL, and provides a REST API for compliance reporting.

    Key Differentiator: Built with a non-blocking architecture using asyncio for the API and threaded workers for blocking AWS Boto3 calls.

### Architecture
```
graph LR
    User[User/Client] -->|X-API-Key| API[FastAPI Server]
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

    - S3: Detects disabled Bucket Versioning.

    - IAM: Flags users without MFA enabled.

    - EC2: Identifies Security Groups with Port 22 (SSH) open to the world (0.0.0.0/0).

- Secure by Design: API Key authentication using Dependency Injection.

- Asynchronous Workers: Scans run in the background without blocking the main event loop.
- Analytics: Dedicated endpoints for compliance scores and filtering results (Pass/Fail).

- Containerized: Fully Dockerized with docker-compose for one-command deployment.

- Test Coverage: Comprehensive Unit and Integration tests using pytest and unittest.mock.

- CI/CD: Automated testing pipeline via GitHub Actions.

###  Tech Stack

- Core: Python 3.12, FastAPI

- Database: PostgreSQL (Asyncpg + SQLModel)

- Infrastructure: Docker, Docker Compose

- AWS SDK: Boto3

- Testing: Pytest, HTTPX

###  Getting Started
Prerequisites

- Python 3.10+

- PostgreSQL (Local or Docker container)

- AWS Credentials configured locally

1. Clone & Setup

```bash
git clone https://github.com/oyewoledavid/security-auditor
cd cloud-resource-auditor
```
2. Configure Environment

Create a `.env` file in the root directory, you most provide AWS Credentials:
```
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/auditor_db
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
API_KEY=my-secret-key-123
```
Ensure you have a database named auditor_db created in Postgres.

3. Run with Docker Compose
```bash
docker compose up --build
```
The server will start at http://127.0.0.1:8000.

### Running Tests

This project enforces code quality via Pytest. To run tests locally (outside Docker):
```bash
pip install pytest pytest-asyncio httpx
pytest -v
```
`Note: The tests use Mocks and do NOT make real calls to AWS.`

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

- [ ] Frontend: A simple React dashboard to visualize the Compliance Score.

- [ ] Alerting: Integration with Slack/SNS for critical failures.
