# BuyHive Backend - Deployment Guide

This guide covers deploying BuyHive backend to AWS using Docker and ECS Fargate.

## Prerequisites

- AWS account with billing alerts configured
- Docker installed and running
- AWS CLI installed and configured
- GitHub repository with Actions enabled
- MongoDB Atlas cluster (or self-hosted MongoDB)
- Auth0 account configured
- API keys: Groq, OpenAI

## Quick Start

### 1. Local Testing with Docker

```bash
# Build the image
docker build -t buyhive-backend:latest .

# Run locally
docker run -p 8000:8000 --env-file .env buyhive-backend:latest

# Test health endpoint
curl http://localhost:8000/health
```

### 2. Using Docker Compose (with MongoDB)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

## AWS Setup

See [AWS_CONSOLE_SETUP.md](./AWS_CONSOLE_SETUP.md) for detailed step-by-step AWS Console instructions.

### Overview of AWS Resources Needed

1. **ECR Repository** - Store Docker images
2. **IAM Roles** - Permissions for ECS tasks
3. **ECS Cluster** - Run containers
4. **ECS Task Definition** - Container configuration
5. **Security Group** - Network access rules
6. **ECS Service** - Run and maintain tasks
7. **CloudWatch Logs** - Application logging

## Environment Configuration

### Development

1. Copy `.env.example` to `.env`
2. Fill in all required variables
3. Run locally: `uvicorn main:app --reload`

### Production

1. Copy `.env.example` to `.env.production`
2. Fill in production values
3. Set `ENVIRONMENT=production`
4. Deploy via CI/CD or manually

### Required Environment Variables

See `.env.example` for complete list. Minimum required:

- `MONGO_URL` - MongoDB connection string
- `AUTH0_DOMAIN` - Auth0 tenant domain
- `AUTH0_AUDIENCE` - Auth0 API identifier
- `ALLOWED_ORIGINS` - Comma-separated allowed origins
- `AWS_REGION` - AWS region (e.g., us-east-1)
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `SES_FROM_EMAIL` - Verified SES email address

## Manual Deployment

### 1. Build and Push to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin \
  YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t buyhive-backend:latest .

# Tag for ECR
docker tag buyhive-backend:latest \
  YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/buyhive-backend:latest

# Push to ECR
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/buyhive-backend:latest
```

### 2. Update ECS Service

```bash
# Force new deployment
aws ecs update-service \
  --cluster buyhive-cluster \
  --service buyhive-backend-service \
  --force-new-deployment \
  --region us-east-1
```

## CI/CD Pipeline

The GitHub Actions workflow automatically:

1. Runs tests on every push
2. Builds Docker image on push to `main`
3. Pushes to ECR
4. Updates ECS service
5. Waits for deployment to stabilize

### Setting Up GitHub Secrets

1. Go to GitHub repository → Settings → Secrets and variables → Actions
2. Add secrets:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`

### Creating IAM User for CI/CD

1. AWS Console → IAM → Users → Create user
2. Name: `github-actions-buyhive`
3. Attach policies:
   - `AmazonEC2ContainerRegistryFullAccess`
   - `AmazonECS_FullAccess`
4. Create access key
5. Add to GitHub secrets

## Monitoring

### CloudWatch Logs

View application logs:

```bash
aws logs tail /ecs/buyhive-backend --follow --region us-east-1
```

Or in AWS Console:
1. CloudWatch → Log groups → `/ecs/buyhive-backend`
2. Select log stream
3. View real-time logs

### Health Checks

- Health endpoint: `https://your-domain.com/health`
- Readiness: `https://your-domain.com/health/ready`
- Liveness: `https://your-domain.com/health/live`

## Scaling

### Manual Scaling

```bash
aws ecs update-service \
  --cluster buyhive-cluster \
  --service buyhive-backend-service \
  --desired-count 2 \
  --region us-east-1
```

### Auto Scaling (Future)

Configure ECS Auto Scaling based on CPU/memory metrics.

## Rollback

### Rollback to Previous Version

1. Find previous task definition revision
2. Update service to use previous revision:

```bash
aws ecs update-service \
  --cluster buyhive-cluster \
  --service buyhive-backend-service \
  --task-definition buyhive-backend:PREVIOUS_REVISION \
  --region us-east-1
```

## Cost Estimation

### Free Tier (First 12 Months)

- ECS Fargate: 20 GB-hours/month free
- ECR: 500 MB storage free
- CloudWatch: 10 custom metrics, 5 GB logs free
- SES: 62,000 emails/month free
- Data Transfer: 100 GB/month free

### Expected Monthly Cost

- **Free Tier**: $0/month (within limits)
- **After Free Tier**: ~$5-10/month (low traffic)
- **With Growth**: Scales with usage

### Cost Optimization Tips

1. Use Fargate Spot for non-critical workloads (70% savings)
2. Set CloudWatch log retention to 7 days
3. Monitor and set up billing alerts
4. Use reserved capacity for predictable workloads

## Troubleshooting

### Container Won't Start

1. Check CloudWatch logs
2. Verify environment variables in task definition
3. Check security group allows port 8000
4. Verify ECR image exists and is accessible

### Health Check Failing

1. Check application logs
2. Verify database connectivity
3. Check ML models load correctly
4. Verify all environment variables are set

### Deployment Stuck

1. Check ECS service events
2. Verify task definition is valid
3. Check IAM role permissions
4. Verify security group configuration

## Security Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Use IAM roles** - Don't hardcode AWS credentials
3. **Rotate secrets regularly** - Update API keys periodically
4. **Restrict security groups** - Only allow necessary ports
5. **Enable CloudWatch logging** - Monitor for suspicious activity
6. **Use HTTPS** - Add Application Load Balancer with SSL certificate

## Next Steps

- [ ] Set up Application Load Balancer
- [ ] Configure custom domain with SSL
- [ ] Set up auto-scaling
- [ ] Configure backup strategy
- [ ] Set up monitoring alerts
- [ ] Implement blue-green deployments

## Support

For issues or questions:
- Check [RUNBOOK.md](./RUNBOOK.md) for common operations
- Review [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for API details
- Open an issue on GitHub






