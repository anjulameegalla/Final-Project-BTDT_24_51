# CloudGuard-AI 



## Architecture

See the detailed [architecture diagram](docs/architecture.md).

```
cloudguard-ai/
├── backend/                  # FastAPI + Python
│   ├── app/
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── config.py         # Settings (pydantic-settings)
│   │   ├── database.py       # MongoDB / mongomock connection
│   │   ├── models/           # Pydantic DB models
│   │   ├── schemas/          # Request/Response schemas
│   │   ├── routes/           # API route handlers
│   │   │   ├── auth.py       # Register, Login, Me
│   │   │   ├── aws.py        # Connect AWS account
│   │   │   ├── scan.py       # Start/Get/History scans
│   │   │   ├── report.py     # Generate/Download PDF
│   │   │   ├── alerts.py     # Alert history
│   │   │   └── admin.py      # Admin panel APIs
│   │   ├── services/
│   │   │   ├── aws/
│   │   │   │   ├── iam_scanner.py
│   │   │   │   ├── s3_scanner.py
│   │   │   │   ├── ec2_scanner.py
│   │   │   │   └── cloudtrail_analyzer.py
│   │   │   ├── ai_service.py       # Gemini/OpenAI/Fallback
│   │   │   ├── scoring_service.py  # Risk score calculation
│   │   │   ├── alert_service.py    # SES email alerts
│   │   │   ├── report_service.py   # PDF generation
│   │   │   └── scan_service.py     # Scan orchestration
│   │   └── auth/             # JWT + dependencies
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/                 # React + Vite + Tailwind
│   ├── src/
│   │   ├── pages/            # All UI pages
│   │   ├── components/       # Reusable components
│   │   ├── services/         # Axios API calls
│   │   ├── context/          # Auth context
│   │   └── utils/            # Helpers
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── docker-compose.yml
└── docs/
  ├── architecture.md
  └── iam-policy.json
```

---

## Environment Variables

### Backend (`backend/.env`)
```env
SECRET_KEY=your-secret-key
APP_ENV=development
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=cloudguard_db

# AI Provider (optional — uses built-in fallback if not set)
AI_PROVIDER=gemini
GEMINI_API_KEY=your-gemini-key
OPENAI_API_KEY=your-openai-key

# AWS (optional — leave blank for demo mode)
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1

# Email Alerts (optional; sender and recipient must be verified in SES)
ALERT_EMAIL_FROM=alerts@yourdomain.com
ALERT_EMAIL_TO=admin@yourdomain.com
SES_REGION=us-east-1

# Use true only for demo mode. Docker Compose overrides this to false.
DEMO_MODE=true
```

In production, use a strong `SECRET_KEY` of at least 32 characters. Never commit `.env` or share AWS/API credentials.

AWS access-key secrets are encrypted before being stored in MongoDB. IAM role authentication is preferred for long-term deployments.

---

## Required AWS IAM Policy

Attach this read-only policy to the IAM role/user used for scanning:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iam:ListUsers", "iam:ListMFADevices", "iam:ListAttachedUserPolicies",
      "iam:ListAccessKeys", "iam:GetAccessKeyLastUsed", "iam:ListPolicies",
      "iam:GetPolicyVersion", "iam:GetPolicy", "iam:ListUserPolicies",
      "iam:GetUserPolicy", "s3:ListAllMyBuckets", "s3:GetBucketPublicAccessBlock",
      "s3:GetBucketPolicy", "s3:GetBucketEncryption", "s3:GetBucketVersioning",
      "s3:GetBucketLogging", "s3:GetBucketAcl", "ec2:DescribeSecurityGroups",
      "ec2:DescribeInstances", "ec2:DescribeRegions", "cloudtrail:LookupEvents",
      "cloudtrail:GetTrailStatus", "cloudtrail:DescribeTrails", "sts:GetCallerIdentity"
    ],
    "Resource": "*"
  }]
}
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| Database | MongoDB (Motor async driver) |
| AWS SDK | Boto3 |
| AI | Google Gemini / OpenAI GPT-4o with built-in fallback |
| PDF | ReportLab |
| Auth | JWT (python-jose), bcrypt |
| Frontend | React 18, Vite, Tailwind CSS |
| Charts | Recharts |
| Animations | Framer Motion |
| Alerts | AWS SES |
| Container | Docker, Docker Compose |

