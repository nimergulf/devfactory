# DevFoundry Quick Start Guide

Get started with DevFoundry in under 10 minutes.

---

## What You'll Build

By the end of this guide, you'll have:
- ✅ DevFoundry platform deployed on GCP
- ✅ A working example: secure REST API with authentication
- ✅ Automated CI/CD pipeline
- ✅ Monitoring and logging dashboards

---

## Prerequisites

```bash
# Required tools
- Google Cloud account with billing enabled
- gcloud CLI installed
- Docker Desktop installed
- Basic knowledge of cloud concepts
```

---

## Step 1: Clone Repository (2 minutes)

```bash
# Clone the repository
git clone https://github.com/nimergulf/devfactory.git
cd devfactory

# Verify repository structure
ls -la
```

---

## Step 2: GCP Setup (3 minutes)

```bash
# Set your project ID (choose a unique name)
export PROJECT_ID="my-devfoundry-platform"
export REGION="us-central1"

# Create and configure project
gcloud projects create $PROJECT_ID
gcloud config set project $PROJECT_ID

# Link billing (replace with your billing account ID)
gcloud beta billing projects link $PROJECT_ID \
  --billing-account=YOUR-BILLING-ACCOUNT-ID

# Enable required APIs (this takes ~2 minutes)
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  secretmanager.googleapis.com
```

---

## Step 3: Quick Deploy (3 minutes)

```bash
# Run automated setup script
./scripts/quick-deploy.sh

# This script will:
# - Create service accounts
# - Set up Artifact Registry
# - Initialize Firestore
# - Build and deploy orchestrator
# - Configure basic monitoring
```

**Note**: If the script doesn't exist yet, use the manual deployment:

```bash
# Build orchestrator container
docker build -t gcr.io/$PROJECT_ID/orchestrator:latest .

# Push to Container Registry
docker push gcr.io/$PROJECT_ID/orchestrator:latest

# Deploy to Cloud Run
gcloud run deploy devfoundry-orchestrator \
  --image=gcr.io/$PROJECT_ID/orchestrator:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --set-env-vars="PROJECT_ID=$PROJECT_ID"
```

---

## Step 4: Verify Installation (1 minute)

```bash
# Get service URL
export SERVICE_URL=$(gcloud run services describe devfoundry-orchestrator \
  --region=$REGION --format='value(status.url)')

# Test health endpoint
curl $SERVICE_URL/health

# Expected output:
# {"status": "healthy", "version": "1.0.0"}
```

---

## Step 5: Build Your First Application (2 minutes)

### Option A: Using Web Console

1. Open the service URL in your browser
2. Enter your concept: "Build a secure REST API for managing tasks with user authentication"
3. Click "Generate"
4. Watch the agents work in real-time
5. Review generated artifacts

### Option B: Using CLI

```bash
# Install CLI
npm install -g @devfoundry/cli

# Configure
devfoundry config set \
  --api-url=$SERVICE_URL \
  --project-id=$PROJECT_ID

# Generate your first application
devfoundry generate \
  --requirement "Build a secure REST API for task management with JWT authentication" \
  --architecture microservice \
  --deployment cloud-run
```

### Option C: Using API

```bash
# Submit workflow via API
curl -X POST $SERVICE_URL/api/v1/workflows \
  -H "Content-Type: application/json" \
  -d '{
    "concept": "Build a secure REST API for task management",
    "requirements": {
      "architecture": "microservice",
      "deployment_target": "cloud-run",
      "compliance": ["owasp-top-10"],
      "features": [
        "User authentication (JWT)",
        "CRUD operations for tasks",
        "Role-based access control",
        "Audit logging"
      ]
    }
  }'

# Response includes workflow_id
# {"workflow_id": "wf-20241018-001", "status": "started"}

# Check status
curl $SERVICE_URL/api/v1/workflows/wf-20241018-001
```

---

## What DevFoundry Just Did

In those 2 minutes, DevFoundry:

1. **🧭 Conceptualized**
   - Analyzed your requirement
   - Identified security standards (OWASP)
   - Created feature breakdown

2. **🏛️ Architected**
   - Designed microservice architecture
   - Created API specification (OpenAPI 3.0)
   - Documented architecture decisions (ADRs)

3. **⚙️ Engineered**
   - Generated FastAPI code with JWT auth
   - Created PostgreSQL data models
   - Wrote comprehensive test suite (>80% coverage)
   - Built Dockerfile and Terraform configs

4. **🚀 Deployed**
   - Created Cloud Build pipeline
   - Deployed to Cloud Run
   - Set up monitoring dashboards
   - Configured auto-scaling

5. **🧩 Governed**
   - Generated SBOM
   - Ran vulnerability scans
   - Created audit trail
   - Produced compliance reports

---

## View Your Results

### Generated Artifacts

```bash
# View generated repository
export REPO_URL=$(curl $SERVICE_URL/api/v1/workflows/wf-20241018-001 | jq -r '.artifacts.repository')
echo $REPO_URL

# Clone and explore
git clone $REPO_URL
cd task-management-api
ls -la

# You'll see:
# - src/              # Application code
# - tests/            # Test suites
# - terraform/        # Infrastructure code
# - docs/             # Generated documentation
# - .github/workflows/# CI/CD pipelines
# - Dockerfile        # Container config
# - cloudbuild.yaml   # Cloud Build config
```

### Deployed Service

```bash
# Get service URL
export APP_URL=$(curl $SERVICE_URL/api/v1/workflows/wf-20241018-001 | jq -r '.artifacts.service_url')

# Test the API
curl $APP_URL/health
curl $APP_URL/docs  # OpenAPI documentation

# Create a user
curl -X POST $APP_URL/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'

# Get JWT token
curl -X POST $APP_URL/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "SecurePass123!"}'

# Use token to create task
export TOKEN="your-jwt-token"
curl -X POST $APP_URL/api/v1/tasks \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "First task", "description": "Created via DevFoundry"}'
```

### Monitoring Dashboards

```bash
# Open Cloud Console monitoring
echo "https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"

# View logs
gcloud run services logs read task-management-api \
  --region=$REGION \
  --limit=50
```

---

## Next Steps

### 1. Customize Your Application

```bash
# Edit generated code
cd task-management-api/src
vim api/routes/tasks.py

# Run tests locally
pytest tests/

# Deploy changes
git add .
git commit -m "Add custom feature"
git push origin main

# Cloud Build automatically deploys changes
```

### 2. Add More Features

```bash
# Request new features through DevFoundry
devfoundry enhance \
  --workflow-id=wf-20241018-001 \
  --features="Add email notifications for task assignments"
```

### 3. Deploy to Production

```bash
# DevFoundry includes production-ready setup
# Approve production deployment
devfoundry deploy \
  --workflow-id=wf-20241018-001 \
  --environment=production \
  --approval-required
```

### 4. Set Up Team Access

```bash
# Add team members
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="user:teammate@example.com" \
  --role="roles/run.developer"

# Share DevFoundry access
devfoundry team add teammate@example.com --role=developer
```

---

## Common Tasks

### View Workflow Progress

```bash
# Get workflow details
curl $SERVICE_URL/api/v1/workflows/wf-20241018-001

# Stream logs in real-time
curl $SERVICE_URL/api/v1/workflows/wf-20241018-001/logs \
  --no-buffer
```

### Download Artifacts

```bash
# Download generated code
curl $SERVICE_URL/api/v1/workflows/wf-20241018-001/artifacts/source_code \
  --output source_code.zip

# Download documentation
curl $SERVICE_URL/api/v1/workflows/wf-20241018-001/artifacts/documentation \
  --output docs.zip

# Download SBOM
curl $SERVICE_URL/api/v1/workflows/wf-20241018-001/artifacts/sbom \
  --output sbom.json
```

### Re-run with Modifications

```bash
# Create new workflow based on previous
devfoundry generate \
  --based-on=wf-20241018-001 \
  --modify="Add GraphQL API in addition to REST"
```

---

## Troubleshooting

### Issue: "Permission denied"
```bash
# Ensure you're authenticated
gcloud auth login
gcloud config set project $PROJECT_ID
```

### Issue: "Service unavailable"
```bash
# Check Cloud Run status
gcloud run services describe devfoundry-orchestrator --region=$REGION

# View recent errors
gcloud run services logs read devfoundry-orchestrator \
  --region=$REGION \
  --filter="severity>=ERROR" \
  --limit=20
```

### Issue: "Quota exceeded"
```bash
# Check quotas
gcloud compute project-info describe --project=$PROJECT_ID

# Request increase: https://console.cloud.google.com/iam-admin/quotas
```

---

## Cost Estimate

For the quick start example:
- **Cloud Run**: ~$0.50/day (low traffic)
- **Firestore**: ~$0.10/day
- **Cloud Storage**: ~$0.05/day
- **Vertex AI**: ~$0.20/day (development usage)
- **Total**: ~$0.85/day or ~$25/month

**Tips to minimize costs**:
- Set Cloud Run min instances to 0
- Use free tier for Firestore
- Delete unused artifacts from Cloud Storage
- Use pre-configured cost alerts

---

## Learning Resources

- **📚 Full Documentation**: See `/docs` folder
- **🎥 Video Tutorials**: https://youtube.com/devfoundry
- **💬 Community**: https://discord.gg/devfoundry
- **📝 Blog**: https://blog.devfoundry.com
- **🐛 Issues**: https://github.com/nimergulf/devfactory/issues

---

## What's Next?

### Explore Advanced Features

1. **Multi-Service Applications**
   ```bash
   devfoundry generate \
     --requirement "Build a microservices e-commerce platform" \
     --services="api-gateway,product-service,order-service,payment-service"
   ```

2. **Custom Compliance**
   ```bash
   devfoundry generate \
     --requirement "Healthcare patient portal" \
     --compliance="hipaa,iso27001"
   ```

3. **Multi-Cloud Deployment** (R1.2+)
   ```bash
   devfoundry deploy \
     --targets="gcp,aws,azure" \
     --strategy="active-active"
   ```

---

## Support

**Need help?**
- 💬 Community Slack: devfoundry-community.slack.com
- 📧 Email: support@devfoundry.com
- 📖 Docs: See `/docs/README.md`

**Found a bug?**
- Report: https://github.com/nimergulf/devfactory/issues

**Want to contribute?**
- See: CONTRIBUTING.md

---

## Success! 🎉

You've successfully:
- ✅ Deployed DevFoundry platform
- ✅ Built your first application
- ✅ Set up automated CI/CD
- ✅ Configured monitoring

**Welcome to the future of software development!**

---

**Built with ❤️ by the DevFoundry team**

*Transform any idea into a governed, deployable product — automatically*
