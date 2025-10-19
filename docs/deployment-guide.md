# DevFoundry Deployment Guide

## Complete Deployment Instructions for Release 1

This guide provides step-by-step instructions for deploying DevFoundry Platform Release 1 on Google Cloud Platform.

---

## Prerequisites

### Required Tools

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# Install Terraform
brew install terraform

# Install Docker
brew install --cask docker

# Install kubectl
gcloud components install kubectl

# Install Python 3.11+
brew install python@3.11

# Install Node.js 18+
brew install node@18
```

### GCP Project Setup

```bash
# Set project variables
export PROJECT_ID="devfoundry-platform"
export REGION="us-central1"
export ZONE="us-central1-a"

# Create project (if new)
gcloud projects create $PROJECT_ID --name="DevFoundry Platform"

# Set active project
gcloud config set project $PROJECT_ID
gcloud config set compute/region $REGION
gcloud config set compute/zone $ZONE

# Link billing account
gcloud beta billing accounts list
export BILLING_ACCOUNT="012345-67890A-BCDEF0"
gcloud beta billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT
```

### Enable Required APIs

```bash
# Enable all required GCP services
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iam.googleapis.com \
  compute.googleapis.com \
  vpcaccess.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  aiplatform.googleapis.com \
  storage-api.googleapis.com \
  pubsub.googleapis.com \
  iap.googleapis.com \
  cloudscheduler.googleapis.com
```

---

## Infrastructure Setup

### 1. Create Service Accounts

```bash
# Orchestrator service account
gcloud iam service-accounts create devfoundry-orchestrator \
  --display-name="DevFoundry Orchestrator" \
  --description="Service account for orchestrator service"

# Builder service account
gcloud iam service-accounts create devfoundry-builder \
  --display-name="DevFoundry Builder" \
  --description="Service account for Cloud Build"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:devfoundry-orchestrator@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:devfoundry-orchestrator@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/aiplatform.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:devfoundry-builder@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.builder"
```

### 2. Create Artifact Registry

```bash
# Create Docker repository
gcloud artifacts repositories create devfoundry-images \
  --repository-format=docker \
  --location=$REGION \
  --description="DevFoundry container images"

# Configure Docker authentication
gcloud auth configure-docker $REGION-docker.pkg.dev
```

### 3. Create Storage Buckets

```bash
# Terraform state bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-tfstate
gsutil versioning set on gs://$PROJECT_ID-tfstate

# Artifacts bucket
gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$PROJECT_ID-artifacts
gsutil versioning set on gs://$PROJECT_ID-artifacts

# Set lifecycle policies
cat > lifecycle.json <<EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 90,
          "matchesPrefix": ["temp/"]
        }
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://$PROJECT_ID-artifacts
```

### 4. Initialize Firestore

```bash
# Create Firestore database (Native mode)
gcloud firestore databases create \
  --location=$REGION \
  --type=firestore-native

# Create indexes (add to firestore.indexes.json)
cat > firestore.indexes.json <<EOF
{
  "indexes": [
    {
      "collectionGroup": "workflows",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "status", "order": "ASCENDING"},
        {"fieldPath": "created_at", "order": "DESCENDING"}
      ]
    },
    {
      "collectionGroup": "artifacts",
      "queryScope": "COLLECTION",
      "fields": [
        {"fieldPath": "workflow_id", "order": "ASCENDING"},
        {"fieldPath": "created_at", "order": "DESCENDING"}
      ]
    }
  ]
}
EOF

gcloud firestore indexes composite create --file=firestore.indexes.json
```

### 5. Configure Secret Manager

```bash
# Create secrets for API keys
echo -n "your-vertex-ai-api-key" | gcloud secrets create vertex-ai-key \
  --data-file=- \
  --replication-policy="automatic"

# Grant access to orchestrator
gcloud secrets add-iam-policy-binding vertex-ai-key \
  --member="serviceAccount:devfoundry-orchestrator@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 6. Create VPC and Networking

```bash
# Create VPC
gcloud compute networks create devfoundry-vpc \
  --subnet-mode=custom \
  --bgp-routing-mode=regional

# Create subnet
gcloud compute networks subnets create devfoundry-subnet \
  --network=devfoundry-vpc \
  --region=$REGION \
  --range=10.0.0.0/24

# Create VPC Access Connector for Cloud Run
gcloud compute networks vpc-access connectors create devfoundry-connector \
  --network=devfoundry-vpc \
  --region=$REGION \
  --range=10.8.0.0/28
```

---

## Application Deployment

### 1. Clone Repository

```bash
git clone https://github.com/nimergulf/devfactory.git
cd devfactory
```

### 2. Configure Environment

```bash
# Create .env file
cat > .env <<EOF
PROJECT_ID=$PROJECT_ID
REGION=$REGION
VERTEX_AI_LOCATION=$REGION
FIRESTORE_DATABASE="(default)"
ARTIFACTS_BUCKET=$PROJECT_ID-artifacts
LOG_LEVEL=INFO
ENVIRONMENT=production
EOF
```

### 3. Build Orchestrator Image

```bash
# Build and push orchestrator
docker build -t $REGION-docker.pkg.dev/$PROJECT_ID/devfoundry-images/orchestrator:latest \
  -f Dockerfile .

docker push $REGION-docker.pkg.dev/$PROJECT_ID/devfoundry-images/orchestrator:latest
```

### 4. Deploy Orchestrator to Cloud Run

```bash
gcloud run deploy devfoundry-orchestrator \
  --image=$REGION-docker.pkg.dev/$PROJECT_ID/devfoundry-images/orchestrator:latest \
  --platform=managed \
  --region=$REGION \
  --service-account=devfoundry-orchestrator@$PROJECT_ID.iam.gserviceaccount.com \
  --vpc-connector=devfoundry-connector \
  --set-env-vars="PROJECT_ID=$PROJECT_ID,REGION=$REGION" \
  --set-secrets="VERTEX_AI_KEY=vertex-ai-key:latest" \
  --allow-unauthenticated \
  --min-instances=1 \
  --max-instances=10 \
  --memory=2Gi \
  --cpu=2 \
  --timeout=3600 \
  --concurrency=80

# Get service URL
export ORCHESTRATOR_URL=$(gcloud run services describe devfoundry-orchestrator \
  --region=$REGION \
  --format='value(status.url)')

echo "Orchestrator deployed at: $ORCHESTRATOR_URL"
```

### 5. Configure Identity-Aware Proxy (IAP)

```bash
# Create OAuth consent screen (first time only)
# Follow: https://console.cloud.google.com/apis/credentials/consent

# Create OAuth client ID
gcloud iap oauth-brands create \
  --application_title="DevFoundry Platform" \
  --support_email="support@yourdomain.com"

# Enable IAP on Cloud Run
gcloud iap web enable \
  --resource-type=cloud-run \
  --service=devfoundry-orchestrator

# Grant access to users
gcloud iap web add-iam-policy-binding \
  --resource-type=cloud-run \
  --service=devfoundry-orchestrator \
  --member="user:admin@yourdomain.com" \
  --role="roles/iap.httpsResourceAccessor"
```

### 6. Deploy Using Terraform (Alternative)

```bash
cd terraform/environments/production

# Initialize Terraform
terraform init \
  -backend-config="bucket=$PROJECT_ID-tfstate" \
  -backend-config="prefix=production"

# Review plan
terraform plan \
  -var="project_id=$PROJECT_ID" \
  -var="region=$REGION"

# Apply configuration
terraform apply \
  -var="project_id=$PROJECT_ID" \
  -var="region=$REGION" \
  -auto-approve
```

---

## CI/CD Pipeline Setup

### 1. Connect GitHub Repository

```bash
# Install Cloud Build GitHub app
# Visit: https://github.com/apps/google-cloud-build

# Create build trigger
gcloud builds triggers create github \
  --name="devfoundry-orchestrator-deploy" \
  --repo-name="devfactory" \
  --repo-owner="nimergulf" \
  --branch-pattern="^main$" \
  --build-config="cloudbuild.yaml" \
  --service-account="projects/$PROJECT_ID/serviceAccounts/devfoundry-builder@$PROJECT_ID.iam.gserviceaccount.com"
```

### 2. Configure Cloud Build

```yaml
# cloudbuild.yaml
steps:
  # Step 1: Run tests
  - name: 'python:3.11'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        pip install -r requirements.txt
        pytest orchestrator/tests/ -v --cov

  # Step 2: Build container
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/devfoundry-images/orchestrator:$SHORT_SHA'
      - '-t'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/devfoundry-images/orchestrator:latest'
      - '-f'
      - 'Dockerfile'
      - '.'

  # Step 3: Push to Artifact Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - '--all-tags'
      - '${_REGION}-docker.pkg.dev/$PROJECT_ID/devfoundry-images/orchestrator'

  # Step 4: Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: 'gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'devfoundry-orchestrator'
      - '--image=${_REGION}-docker.pkg.dev/$PROJECT_ID/devfoundry-images/orchestrator:$SHORT_SHA'
      - '--region=${_REGION}'
      - '--platform=managed'

substitutions:
  _REGION: 'us-central1'

options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
```

---

## Monitoring Setup

### 1. Create Monitoring Dashboards

```bash
# Create custom dashboard
gcloud monitoring dashboards create --config-from-file=monitoring-dashboard.json
```

**monitoring-dashboard.json**:
```json
{
  "displayName": "DevFoundry Platform",
  "dashboardFilters": [],
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Request Rate",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" resource.labels.service_name=\"devfoundry-orchestrator\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
```

### 2. Configure Alerting

```bash
# Create alerting policy
gcloud alpha monitoring policies create \
  --notification-channels=$NOTIFICATION_CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

### 3. Set Up Log-Based Metrics

```bash
# Create log-based metric for errors
gcloud logging metrics create agent_failures \
  --description="Count of agent execution failures" \
  --log-filter='resource.type="cloud_run_revision"
    resource.labels.service_name="devfoundry-orchestrator"
    severity="ERROR"
    jsonPayload.agent_status="failed"'
```

---

## Verification

### 1. Health Check

```bash
# Check orchestrator health
curl -X GET $ORCHESTRATOR_URL/health

# Expected response:
# {"status": "healthy", "version": "1.0.0", "timestamp": "2024-10-18T..."}
```

### 2. Test Agent Execution

```bash
# Submit test concept
curl -X POST $ORCHESTRATOR_URL/api/v1/workflows \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)" \
  -d '{
    "concept": "Build a simple REST API for managing tasks",
    "requirements": {
      "architecture": "microservice",
      "deployment_target": "cloud-run",
      "compliance": ["basic-security"]
    }
  }'

# Check workflow status
curl -X GET $ORCHESTRATOR_URL/api/v1/workflows/{workflow_id} \
  -H "Authorization: Bearer $(gcloud auth print-identity-token)"
```

### 3. View Logs

```bash
# Stream orchestrator logs
gcloud run services logs read devfoundry-orchestrator \
  --region=$REGION \
  --limit=50 \
  --format="table(timestamp,severity,textPayload)"

# Filter for errors
gcloud run services logs read devfoundry-orchestrator \
  --region=$REGION \
  --filter="severity>=ERROR" \
  --limit=20
```

---

## Scaling Configuration

### Auto-Scaling Settings

```bash
# Update auto-scaling parameters
gcloud run services update devfoundry-orchestrator \
  --region=$REGION \
  --min-instances=2 \
  --max-instances=100 \
  --cpu-throttling \
  --concurrency=80 \
  --memory=4Gi \
  --cpu=4
```

### Resource Quotas

```bash
# Check current quotas
gcloud compute project-info describe --project=$PROJECT_ID

# Request quota increase if needed
# Visit: https://console.cloud.google.com/iam-admin/quotas
```

---

## Backup and Recovery

### 1. Automated Backups

```bash
# Enable Firestore backups
gcloud firestore backups schedules create \
  --database='(default)' \
  --recurrence=daily \
  --retention=7d

# List backups
gcloud firestore backups list
```

### 2. Terraform State Backup

```bash
# Backup Terraform state
gsutil cp gs://$PROJECT_ID-tfstate/production/default.tfstate \
  gs://$PROJECT_ID-tfstate/backups/production-$(date +%Y%m%d).tfstate
```

### 3. Disaster Recovery Test

```bash
# Test restoration process
gcloud firestore import gs://$PROJECT_ID-artifacts/firestore-backup-YYYYMMDD

# Verify data integrity
python scripts/verify_data_integrity.py
```

---

## Security Hardening

### 1. Enable Binary Authorization

```bash
# Create policy
gcloud container binauthz policy import policy.yaml

# Policy example (policy.yaml):
cat > policy.yaml <<EOF
admissionWhitelistPatterns:
- namePattern: gcr.io/google_containers/*
defaultAdmissionRule:
  requireAttestationsBy:
    - projects/$PROJECT_ID/attestors/devfoundry-attestor
  enforcementMode: ENFORCED_BLOCK_AND_AUDIT_LOG
EOF
```

### 2. Configure VPC Service Controls

```bash
# Create access policy
gcloud access-context-manager policies create \
  --organization=$ORG_ID \
  --title="DevFoundry Security Perimeter"

# Create service perimeter
gcloud access-context-manager perimeters create devfoundry_perimeter \
  --title="DevFoundry Perimeter" \
  --resources=projects/$PROJECT_NUMBER \
  --restricted-services=run.googleapis.com,storage.googleapis.com
```

### 3. Enable Cloud Armor

```bash
# Create security policy
gcloud compute security-policies create devfoundry-armor \
  --description="WAF rules for DevFoundry"

# Add rate limiting rule
gcloud compute security-policies rules create 1000 \
  --security-policy=devfoundry-armor \
  --expression="origin.region_code == 'CN'" \
  --action=deny-403
```

---

## Maintenance

### Regular Tasks

**Daily**:
- Review error logs
- Check system health dashboards
- Monitor cost tracking

**Weekly**:
- Review security scan results
- Update dependencies
- Review performance metrics
- Test backup restoration

**Monthly**:
- Security audit
- Capacity planning review
- Cost optimization analysis
- Update documentation

### Update Procedure

```bash
# 1. Test in staging
gcloud run deploy devfoundry-orchestrator-staging \
  --image=new-version \
  --tag=staging

# 2. Run integration tests
pytest tests/integration/ --environment=staging

# 3. Gradual rollout to production
gcloud run services update-traffic devfoundry-orchestrator \
  --to-revisions=new-revision=10 \
  --region=$REGION

# 4. Monitor for 30 minutes, then increase to 100%
gcloud run services update-traffic devfoundry-orchestrator \
  --to-revisions=new-revision=100 \
  --region=$REGION
```

---

## Troubleshooting

### Common Issues

**Issue**: Orchestrator not starting
```bash
# Check logs
gcloud run services logs read devfoundry-orchestrator --region=$REGION --limit=100

# Verify environment variables
gcloud run services describe devfoundry-orchestrator --region=$REGION --format=yaml

# Check service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:devfoundry-orchestrator@*"
```

**Issue**: Agent execution failures
```bash
# Check Vertex AI quota
gcloud services list --enabled | grep aiplatform

# Verify API key
gcloud secrets versions access latest --secret=vertex-ai-key

# Test Vertex AI connection
curl -X POST https://aiplatform.googleapis.com/v1/projects/$PROJECT_ID/locations/$REGION/publishers/google/models/gemini-pro:predict \
  -H "Authorization: Bearer $(gcloud auth print-access-token)"
```

**Issue**: Firestore timeouts
```bash
# Check Firestore indexes
gcloud firestore indexes list

# Monitor Firestore metrics
gcloud monitoring time-series list \
  --filter='metric.type="firestore.googleapis.com/api/request_count"' \
  --interval-start-time=$(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%SZ) \
  --interval-end-time=$(date -u +%Y-%m-%dT%H:%M:%SZ)
```

---

## Support

### Documentation
- **Architecture**: See `docs/architecture.md`
- **Agent Specs**: See `docs/agent-specifications.md`
- **Product Description**: See `docs/product-description.md`

### Contact
- **Technical Support**: support@devfoundry.com
- **Enterprise Support**: enterprise@devfoundry.com
- **GitHub Issues**: https://github.com/nimergulf/devfactory/issues

---

**Document Version**: 1.0
**Last Updated**: October 2024
**Maintained By**: DevFoundry DevOps Team
