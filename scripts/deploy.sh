#!/bin/bash
set -e

# Deployment script for BuyHive backend
# Usage: ./scripts/deploy.sh [environment] [image-tag]
# Example: ./scripts/deploy.sh production latest

ENVIRONMENT=${1:-staging}
IMAGE_TAG=${2:-latest}

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Deploying BuyHive backend to ${ENVIRONMENT}...${NC}"

# Validate environment
if [[ ! "$ENVIRONMENT" =~ ^(development|staging|production)$ ]]; then
    echo -e "${RED}❌ Invalid environment: $ENVIRONMENT${NC}"
    echo "Valid environments: development, staging, production"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi

# Build Docker image
echo -e "${YELLOW}📦 Building Docker image with tag: ${IMAGE_TAG}...${NC}"
docker build -t buyhive-backend:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Docker build failed!${NC}"
    exit 1
fi

# Check image size
IMAGE_SIZE=$(docker images buyhive-backend:${IMAGE_TAG} --format "{{.Size}}")
echo -e "${GREEN}✅ Image built successfully! Size: ${IMAGE_SIZE}${NC}"

# If ECR repository URL is provided, tag and push
if [ -n "$ECR_REPOSITORY" ]; then
    echo -e "${YELLOW}⬆️  Tagging image for ECR...${NC}"
    docker tag buyhive-backend:${IMAGE_TAG} ${ECR_REPOSITORY}:${IMAGE_TAG}
    docker tag buyhive-backend:${IMAGE_TAG} ${ECR_REPOSITORY}:latest
    
    echo -e "${YELLOW}⬆️  Pushing to ECR...${NC}"
    docker push ${ECR_REPOSITORY}:${IMAGE_TAG}
    docker push ${ECR_REPOSITORY}:latest
    
    echo -e "${GREEN}✅ Image pushed to ECR successfully!${NC}"
    echo -e "${YELLOW}📝 Next steps:${NC}"
    echo "1. Update ECS task definition with new image: ${ECR_REPOSITORY}:${IMAGE_TAG}"
    echo "2. Update ECS service to force new deployment"
else
    echo -e "${YELLOW}ℹ️  ECR_REPOSITORY not set. Skipping ECR push.${NC}"
    echo "To push to ECR, set ECR_REPOSITORY environment variable:"
    echo "  export ECR_REPOSITORY=your-account.dkr.ecr.us-east-1.amazonaws.com/buyhive-backend"
fi

echo -e "${GREEN}✅ Deployment image ready!${NC}"






