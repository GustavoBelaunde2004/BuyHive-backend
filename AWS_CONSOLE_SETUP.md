# AWS Console Setup - Step-by-Step Guide

This guide provides detailed, step-by-step instructions for setting up all AWS resources needed for BuyHive backend deployment.

## Prerequisites

- AWS account created and logged in
- Billing alerts configured (see main conversation for details)
- Basic understanding of AWS services

---

## Step 1: Create ECR Repository (15 minutes)

### Purpose
Store your Docker images in AWS.

### Steps

1. **Navigate to ECR**
   - In AWS Console, search for "ECR" in the top search bar
   - Click "Elastic Container Registry" or "ECR"

2. **Create Repository**
   - Click "Repositories" in left sidebar
   - Click "Create repository" button (top right)

3. **Configure Repository**
   - **Visibility settings**: Select "Private"
   - **Repository name**: Enter `buyhive-backend`
   - **Tag immutability**: Leave as "Disabled" (for now)
   - **Scan on push**: Select "Enable" (optional, for security scanning)
   - Click "Create repository"

4. **Save Repository URI**
   - After creation, you'll see the repository details
   - Copy the **Repository URI** (format: `YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/buyhive-backend`)
   - Save this for later use

5. **Get Login Command**
   - Click "View push commands" button
   - Copy the login command (you'll use this later to push images)

**✅ Checkpoint**: You should see `buyhive-backend` repository in your ECR repositories list.

---

## Step 2: Create IAM Roles (30 minutes)

### Purpose
Give ECS the permissions it needs to run your containers and access AWS services.

### 2.1 Create ECS Task Execution Role

1. **Navigate to IAM**
   - Search for "IAM" in AWS Console
   - Click "IAM"

2. **Create Role**
   - Click "Roles" in left sidebar
   - Click "Create role" button

3. **Select Trust Entity**
   - Under "Use case", select "Elastic Container Service"
   - Under "Use case for Elastic Container Service", select "Elastic Container Service Task"
   - Click "Next"

4. **Add Permissions**
   - Search for and select: `AmazonECSTaskExecutionRolePolicy`
   - Click "Next"

5. **Name Role**
   - **Role name**: `buyhive-ecs-task-execution-role`
   - **Description**: "Execution role for BuyHive ECS tasks"
   - Click "Create role"

**✅ Checkpoint**: Role `buyhive-ecs-task-execution-role` should appear in your roles list.

### 2.2 Create ECS Task Role

1. **Create Another Role**
   - Click "Create role" again

2. **Select Trust Entity**
   - Select "Elastic Container Service"
   - Select "Elastic Container Service Task"
   - Click "Next"

3. **Add Permissions**
   - Click "Create policy" (opens in new tab)
   - Switch to JSON tab
   - Paste this policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "ses:SendEmail",
           "ses:SendRawEmail"
         ],
         "Resource": "*"
       },
       {
         "Effect": "Allow",
         "Action": [
           "logs:CreateLogGroup",
           "logs:CreateLogStream",
           "logs:PutLogEvents"
         ],
         "Resource": "arn:aws:logs:*:*:*"
       }
     ]
   }
   ```
   - Click "Next"
   - **Policy name**: `buyhive-ecs-task-policy`
   - Click "Create policy"
   - Close the new tab, return to role creation

4. **Attach Policy**
   - Refresh the policies list
   - Search for `buyhive-ecs-task-policy`
   - Select it
   - Click "Next"

5. **Name Role**
   - **Role name**: `buyhive-ecs-task-role`
   - **Description**: "Task role for BuyHive ECS tasks"
   - Click "Create role"

**✅ Checkpoint**: Both roles should now exist:
- `buyhive-ecs-task-execution-role`
- `buyhive-ecs-task-role`

---

## Step 3: Create ECS Cluster (10 minutes)

### Purpose
A cluster is a logical grouping of tasks and services.

### Steps

1. **Navigate to ECS**
   - Search for "ECS" in AWS Console
   - Click "Elastic Container Service"

2. **Create Cluster**
   - Click "Clusters" in left sidebar
   - Click "Create cluster" button

3. **Configure Cluster**
   - **Cluster name**: `buyhive-cluster`
   - **Infrastructure**: Select "AWS Fargate (serverless)"
   - Leave other settings as default
   - Click "Create"

**✅ Checkpoint**: Cluster `buyhive-cluster` should appear in your clusters list.

---

## Step 4: Create Security Group (15 minutes)

### Purpose
Control network access to your application (like a firewall).

### Steps

1. **Navigate to EC2**
   - Search for "EC2" in AWS Console
   - Click "EC2"

2. **Go to Security Groups**
   - In left sidebar, under "Network & Security", click "Security Groups"

3. **Create Security Group**
   - Click "Create security group" button

4. **Configure Security Group**
   - **Name**: `buyhive-backend-sg`
   - **Description**: "Security group for BuyHive backend"
   - **VPC**: Select "Default VPC" (or your VPC)

5. **Add Inbound Rule**
   - Click "Add rule"
   - **Type**: Custom TCP
   - **Port range**: `8000`
   - **Source**: `0.0.0.0/0` (for testing - restrict later in production)
   - **Description**: "Allow FastAPI on port 8000"

6. **Outbound Rules**
   - Leave default (All traffic)

7. **Create**
   - Click "Create security group" button

**✅ Checkpoint**: Security group `buyhive-backend-sg` should appear in your security groups list.

---

## Step 5: Create ECS Task Definition (30 minutes)

### Purpose
Define how your container should run (CPU, memory, environment variables, etc.).

### Steps

1. **Navigate to ECS**
   - Go back to ECS Console
   - Click "Task Definitions" in left sidebar
   - Click "Create new task definition"

2. **Configure Task Definition**
   - **Task definition family**: `buyhive-backend`
   - **Launch type**: Select "Fargate"
   - **Operating system/Architecture**: Leave as default (Linux/X86_64)

3. **Task Size**
   - **Task size (vCPU)**: `0.5 vCPU`
   - **Task size (Memory)**: `1 GB`

4. **Task Execution Role**
   - **Task execution role**: Select `buyhive-ecs-task-execution-role`
   - **Task role**: Select `buyhive-ecs-task-role`

5. **Network Mode**
   - Leave as "awsvpc" (default for Fargate)

6. **Add Container**
   - Scroll down and click "Add container"

7. **Container Configuration**
   - **Container name**: `buyhive-backend`
   - **Image URI**: Paste your ECR repository URI + `:latest`
     - Example: `123456789012.dkr.ecr.us-east-1.amazonaws.com/buyhive-backend:latest`
   - **Essential container**: Leave checked

8. **Port Mappings**
   - **Container port**: `8000`
   - **Protocol**: TCP
   - Leave "Host port" empty (Fargate handles this)

9. **Environment Variables**
   - Click "Add environment variable" for each variable
   - Add all variables from your `.env.production`:
     - `ENVIRONMENT=production`
     - `MONGO_URL=your-mongo-url`
     - `AUTH0_DOMAIN=your-domain.auth0.com`
     - `AUTH0_AUDIENCE=your-api-identifier`
     - `ALLOWED_ORIGINS=your-allowed-origins`
     - `AWS_REGION=us-east-1`
     - `AWS_ACCESS_KEY_ID=your-key`
     - `AWS_SECRET_ACCESS_KEY=your-secret`
     - `SES_FROM_EMAIL=your-email@domain.com`
     - `GROQ_API_KEY=your-key`
     - `OPENAI_API_KEY=your-key`
     - `CLIP_THRESHOLD=0.28`
     - `ENABLE_VISION_FALLBACK=true`
     - `RATE_LIMIT_ENABLED=true`
     - Add all other required variables

10. **Health Check**
    - Scroll to "Health check" section
    - **Command**: Select "CMD-SHELL"
    - **Command**: `curl -f http://localhost:8000/health || exit 1`
    - **Interval**: `30`
    - **Timeout**: `5`
    - **Start period**: `60`
    - **Retries**: `3`

11. **Logging**
    - **Log driver**: Select "awslogs"
    - **Log group**: `/ecs/buyhive-backend`
    - **Log stream prefix**: `ecs`
    - **Region**: Your AWS region (e.g., `us-east-1`)

12. **Create**
    - Click "Create" at the bottom
    - Wait for task definition to be created

**✅ Checkpoint**: Task definition `buyhive-backend` should appear in your task definitions list.

---

## Step 6: Create CloudWatch Log Group (5 minutes)

### Purpose
Store application logs for debugging and monitoring.

### Steps

1. **Navigate to CloudWatch**
   - Search for "CloudWatch" in AWS Console
   - Click "CloudWatch"

2. **Go to Log Groups**
   - In left sidebar, under "Logs", click "Log groups"

3. **Create Log Group**
   - Click "Create log group" button
   - **Log group name**: `/ecs/buyhive-backend`
   - **Retention**: Select "7 days" (free tier)
   - Click "Create"

**✅ Checkpoint**: Log group `/ecs/buyhive-backend` should appear in your log groups list.

---

## Step 7: Create ECS Service (20 minutes)

### Purpose
Run and maintain your application containers.

### Steps

1. **Navigate to ECS Cluster**
   - Go to ECS Console
   - Click "Clusters" → `buyhive-cluster`

2. **Create Service**
   - Click "Services" tab
   - Click "Create" button

3. **Configure Service**
   - **Launch type**: Select "Fargate"
   - **Task Definition**: Select `buyhive-backend:latest` (or latest revision)
   - **Service name**: `buyhive-backend-service`
   - **Desired tasks**: `1`

4. **Networking**
   - **Cluster VPC**: Select your default VPC
   - **Subnets**: Select 2+ public subnets (check the boxes)
   - **Security groups**: Select `buyhive-backend-sg`
   - **Auto-assign public IP**: Select "ENABLED"

5. **Load Balancing** (Skip for now)
   - Leave as "None" (we'll add ALB later if needed)

6. **Service Discovery** (Skip)
   - Leave disabled

7. **Auto Scaling** (Skip for now)
   - Leave disabled

8. **Deployment Configuration**
   - **Deployment type**: "Rolling update"
   - **Minimum healthy percent**: `100`
   - **Maximum percent**: `200`

9. **Create Service**
   - Click "Create" button
   - Wait for service to be created and tasks to start

**✅ Checkpoint**: 
- Service should show "Running" status
- Task should show "Running" status
- Check logs in CloudWatch to verify application started

---

## Step 8: Verify Deployment (10 minutes)

### Steps

1. **Get Public IP**
   - In ECS Console → Clusters → `buyhive-cluster` → Services → `buyhive-backend-service`
   - Click on the service
   - Click "Tasks" tab
   - Click on the running task
   - Find "Public IP" in the task details
   - Copy the IP address

2. **Test Health Endpoint**
   - Open browser or use curl:
   ```bash
   curl http://YOUR_PUBLIC_IP:8000/health
   ```
   - Should return JSON with health status

3. **Check CloudWatch Logs**
   - CloudWatch → Log groups → `/ecs/buyhive-backend`
   - Select latest log stream
   - Verify application logs are appearing

**✅ Checkpoint**: Health endpoint should return `200 OK` with service status.

---

## Step 9: Configure GitHub Secrets (10 minutes)

### Purpose
Allow GitHub Actions to deploy to AWS.

### Steps

1. **Create IAM User for GitHub**
   - IAM Console → Users → "Create user"
   - **User name**: `github-actions-buyhive`
   - Click "Next"

2. **Attach Policies**
   - Click "Attach policies directly"
   - Search and select:
     - `AmazonEC2ContainerRegistryFullAccess`
     - `AmazonECS_FullAccess`
   - Click "Next" → "Create user"

3. **Create Access Key**
   - Click on the user you just created
   - Go to "Security credentials" tab
   - Click "Create access key"
   - Select "Application running outside AWS"
   - Click "Next"
   - Add description: "GitHub Actions CI/CD"
   - Click "Create access key"
   - **IMPORTANT**: Copy both:
     - Access key ID
     - Secret access key
   - Save these securely (you won't see the secret again!)

4. **Add to GitHub Secrets**
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - **Name**: `AWS_ACCESS_KEY_ID`
   - **Value**: Paste access key ID
   - Click "Add secret"
   - Repeat for `AWS_SECRET_ACCESS_KEY`

**✅ Checkpoint**: Both secrets should appear in GitHub repository secrets.

---

## Step 10: Test CI/CD Pipeline (15 minutes)

### Steps

1. **Update Workflow Variables** (if needed)
   - Check `.github/workflows/deploy.yml`
   - Verify `ECR_REPOSITORY`, `ECS_CLUSTER`, `ECS_SERVICE` match your setup

2. **Make a Test Change**
   - Make a small change (e.g., update README)
   - Commit and push to `main` branch

3. **Watch GitHub Actions**
   - Go to GitHub repository → Actions tab
   - Watch the workflow run
   - Should see: Test → Build → Deploy

4. **Verify Deployment**
   - Check ECS service for new deployment
   - Verify new task is running
   - Test health endpoint again

**✅ Checkpoint**: CI/CD pipeline should automatically deploy on push to main.

---

## Troubleshooting

### Service Won't Start

1. **Check Task Logs**
   - ECS → Clusters → Service → Tasks → Click task → Logs tab

2. **Common Issues**
   - Missing environment variables → Check task definition
   - Security group blocking → Verify port 8000 is open
   - IAM permissions → Check task execution role
   - Image not found → Verify ECR repository and image exists

### Health Check Failing

1. **Check Application Logs**
   - CloudWatch → Log groups → `/ecs/buyhive-backend`

2. **Verify Health Endpoint**
   - Container should respond to `/health` endpoint
   - Check if database connection works
   - Verify ML models load correctly

### Can't Access Application

1. **Check Security Group**
   - Verify inbound rule allows port 8000
   - Check source IP (0.0.0.0/0 for testing)

2. **Check Task Status**
   - Task should be "Running"
   - Check if public IP is assigned

---

## Next Steps

After completing all steps:

1. ✅ Set up Application Load Balancer (optional)
2. ✅ Configure custom domain (optional)
3. ✅ Set up auto-scaling (optional)
4. ✅ Configure monitoring alerts
5. ✅ Review and restrict security groups for production

---

## Cost Check

After setup, verify costs:

1. **Billing Dashboard**
   - AWS Console → Billing → Cost and Billing Dashboard
   - Should show $0.00 (within free tier)

2. **Set Up Billing Alerts** (if not done)
   - CloudWatch → Alarms → Create alarm
   - Metric: EstimatedCharges
   - Threshold: $1.00
   - Email notification

---

## Summary

You've now set up:

✅ ECR Repository - Docker image storage  
✅ IAM Roles - Permissions for ECS  
✅ ECS Cluster - Container orchestration  
✅ Security Group - Network access control  
✅ Task Definition - Container configuration  
✅ CloudWatch Logs - Application logging  
✅ ECS Service - Running application  
✅ GitHub Secrets - CI/CD automation  

Your BuyHive backend should now be running on AWS! 🎉

