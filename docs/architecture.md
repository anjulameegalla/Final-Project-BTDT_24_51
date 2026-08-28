# CloudGuard AI Architecture

```mermaid
flowchart TD
    User[User in browser]
    Frontend[React + Vite + Tailwind frontend\nNginx on port 3000]
    API[FastAPI backend\nUvicorn on port 8000]
    Auth[JWT authentication\nuser and admin authorization]
    Mongo[(MongoDB 7\nusers, AWS accounts, scans, reports, alerts)]
    AWS[AWS account\nIAM, S3, EC2, CloudTrail]
    Boto3[Boto3 scanners\nread-only API calls]
    Crypto[Encrypted AWS secret storage\napplication SECRET_KEY]
    AI[AI explanation service\nGemini or OpenAI]
    Fallback[Built-in explanation fallback]
    Score[Risk scoring service]
    PDF[ReportLab PDF generator]
    Disk[Local reports volume]
    SES[AWS SES\noptional email alerts]

    User --> Frontend
    Frontend -->|Bearer JWT / JSON API| API
    API --> Auth
    Auth --> Mongo
    API --> Mongo

    API -->|Connect and validate| AWS
    API -->|Store encrypted secret| Crypto
    Crypto --> Mongo
    API -->|Start scan| Boto3
    Boto3 -->|Read-only IAM, S3, EC2, CloudTrail| AWS
    Boto3 --> AI
    AI -->|Provider unavailable| Fallback
    AI --> Score
    Score --> Mongo
    Score --> PDF
    PDF --> Disk
    API -->|Authenticated download| Disk
    Score --> SES
    SES -->|Critical/High alert| User

    API -->|Health endpoint| Health[/api/health/]
```

## Main Flow

1. The user authenticates through the React frontend and receives a JWT.
2. The user connects a demo account or real AWS account.
3. Real AWS credentials are validated with STS. Access-key secrets are encrypted before storage.
4. The scan route verifies the account belongs to the authenticated user and starts a background scan.
5. Boto3 reads IAM, S3, EC2, and CloudTrail configuration using read-only permissions.
6. Findings are enriched with Gemini/OpenAI when available; the built-in fallback keeps scans working when AI is unavailable.
7. The scoring service calculates overall and per-service scores.
8. Findings and scan status are stored in MongoDB.
9. Critical/High findings create alert records and optionally send email through SES.
10. Reports are generated locally and can only be downloaded through an authenticated API route.

## Deployment

Docker Compose runs three services:

- `frontend`: Nginx serves the Vite production build on `http://localhost:3000`.
- `backend`: FastAPI serves the API on `http://localhost:8000`.
- `mongodb`: MongoDB stores application data on the internal Compose network.
