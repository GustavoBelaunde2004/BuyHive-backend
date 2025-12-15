# BuyHive Backend - Operations Runbook

This runbook provides step-by-step procedures for common operations and troubleshooting.

## Table of Contents

- [Viewing Logs](#viewing-logs)
- [Restarting Service](#restarting-service)
- [Rolling Back Deployment](#rolling-back-deployment)
- [Scaling Service](#scaling-service)
- [Checking Service Health](#checking-service-health)
- [Common Issues](#common-issues)
- [Emergency Procedures](#emergency-procedures)

---

## Viewing Logs

### CloudWatch Logs (AWS Console)

1. **Navigate to CloudWatch**
   - AWS Console → CloudWatch
   - Click "Logs" → "Log groups"
   - Select `/ecs/buyhive-backend`

2. **View Log Streams**
   - Click on latest log stream
   - View real-time logs
   - Use search to filter logs

### CloudWatch Logs (AWS CLI)

```bash
# Tail logs in real-time
aws logs tail /ecs/buyhive-backend --follow --region us-east-1

# View last 100 lines
aws logs tail /ecs/buyhive-backend --since 1h --region us-east-1

# Search for errors
aws logs filter-log-events \
  --log-group-name /ecs/buyhive-backend \
  --filter-pattern "ERROR" \
  --region us-east-1
```

### ECS Task Logs

1. **AWS Console**
   - ECS → Clusters → `buyhive-cluster`
   - Services → `buyhive-backend-service`
   - Tasks tab → Click on running task
   - Logs tab → View container logs

---

## Restarting Service

### Force New Deployment (Recommended)

This creates new tasks with the current task definition.

**AWS Console**:
1. ECS → Clusters → `buyhive-cluster`
2. Services → `buyhive-backend-service`
3. Click "Update"
4. Check "Force new deployment"
5. Click "Update"

**AWS CLI**:
```bash
aws ecs update-service \
  --cluster buyhive-cluster \
  --service buyhive-backend-service \
  --force-new-deployment \
  --region us-east-1
```

### Stop and Start Service

**Stop**:
```bash
aws ecs update-service \
  --cluster buyhive-cluster \
  --service buyhive-backend-service \
  --desired-count 0 \
  --region us-east-1
```

**Start**:
```bash
aws ecs update-service \
  --cluster buyhive-cluster \
  --service buyhive-backend-service \
  --desired-count 1 \
  --region us-east-1
```

---

## Rolling Back Deployment

### Method 1: Use Previous Task Definition Revision

1. **Find Previous Revision**
   - ECS → Task Definitions → `buyhive-backend`
   - Note the revision number (e.g., `buyhive-backend:5`)

2. **Update Service**
   - ECS → Clusters → `buyhive-cluster`
   - Services → `buyhive-backend-service` → Update
   - Task Definition: Select previous revision
   - Force new deployment: Yes
   - Update

**AWS CLI**:
```bash
aws ecs update-service \
  --cluster buyhive-cluster \
  --service buyhive-backend-service \
  --task-definition buyhive-backend:PREVIOUS_REVISION \
  --force-new-deployment \
  --region us-east-1
```

### Method 2: Deploy Previous Docker Image

1. **Find Previous Image Tag**
   - ECR → Repositories → `buyhive-backend`
   - Find previous image (by timestamp or tag)

2. **Update Task Definition**
   - ECS → Task Definitions → `buyhive-backend`
   - Create new revision
   - Update container image to previous tag
   - Create revision

3. **Update Service**
   - Update service to use new task definition revision

---

## Scaling Service

### Manual Scaling

**Increase Tasks**:
```bash
aws ecs update-service \
  --cluster buyhive-cluster \
  --service buyhive-backend-service \
  --desired-count 2 \
  --region us-east-1
```

**Decrease Tasks**:
```bash
aws ecs update-service \
  --cluster buyhive-cluster \
  --service buyhive-backend-service \
  --desired-count 1 \
  --region us-east-1
```

### Auto Scaling (Future)

Configure ECS Auto Scaling based on:
- CPU utilization
- Memory utilization
- Request count (if using ALB)

---

## Checking Service Health

### Health Endpoint

```bash
# Get public IP from ECS task
PUBLIC_IP=$(aws ecs describe-tasks \
  --cluster buyhive-cluster \
  --tasks $(aws ecs list-tasks \
    --cluster buyhive-cluster \
    --service-name buyhive-backend-service \
    --query 'taskArns[0]' \
    --output text) \
  --query 'tasks[0].attachments[0].details[?name==`networkInterfaceId`].value' \
  --output text | xargs -I {} aws ec2 describe-network-interfaces \
    --network-interface-ids {} \
    --query 'NetworkInterfaces[0].Association.PublicIp' \
    --output text)

# Check health
curl http://$PUBLIC_IP:8000/health
```

### Service Status

**AWS Console**:
- ECS → Clusters → `buyhive-cluster`
- Services → `buyhive-backend-service`
- Check:
  - Running count = Desired count
  - Task status = "Running"
  - Service status = "Active"

**AWS CLI**:
```bash
aws ecs describe-services \
  --cluster buyhive-cluster \
  --services buyhive-backend-service \
  --region us-east-1
```

---

## Common Issues

### Issue: Service Won't Start

**Symptoms**:
- Tasks keep stopping
- Service shows "Stopped" tasks

**Troubleshooting**:
1. **Check Task Logs**
   ```bash
   aws logs tail /ecs/buyhive-backend --follow
   ```

2. **Check Task Definition**
   - Verify environment variables are set
   - Check container image exists in ECR
   - Verify IAM roles are correct

3. **Check Security Group**
   - Verify inbound rules allow necessary traffic
   - Check outbound rules allow database access

4. **Check Resource Limits**
   - Verify CPU/memory allocation is sufficient
   - Check if tasks are being killed due to OOM

**Solution**:
- Fix issues found in logs
- Update task definition if needed
- Restart service

### Issue: Health Check Failing

**Symptoms**:
- Health endpoint returns 503
- Tasks restarting frequently

**Troubleshooting**:
1. **Check Application Logs**
   ```bash
   aws logs tail /ecs/buyhive-backend --follow
   ```

2. **Test Health Endpoint Manually**
   ```bash
   curl http://PUBLIC_IP:8000/health
   ```

3. **Check Database Connection**
   - Verify `MONGO_URL` is correct
   - Check MongoDB Atlas allows connections from AWS IPs

4. **Check ML Models**
   - Verify CLIP model loads (check logs)
   - Check BERT model path if using

**Solution**:
- Fix database connection issues
- Ensure ML models can load
- Update environment variables if needed

### Issue: Can't Access Application

**Symptoms**:
- Can't reach application from browser
- Connection timeout

**Troubleshooting**:
1. **Check Security Group**
   - Verify port 8000 is open
   - Check source IP is allowed

2. **Check Task Status**
   - Verify task is "Running"
   - Check if public IP is assigned

3. **Check Network Configuration**
   - Verify subnets are public
   - Check route tables

**Solution**:
- Update security group rules
- Ensure tasks are in public subnets
- Verify auto-assign public IP is enabled

### Issue: High Memory Usage

**Symptoms**:
- Tasks restarting
- CloudWatch shows high memory

**Troubleshooting**:
1. **Check Memory Metrics**
   - CloudWatch → Metrics → ECS/ContainerInsights
   - Check memory utilization

2. **Review Application**
   - Check for memory leaks
   - Verify ML models aren't loading multiple times

**Solution**:
- Increase task memory allocation
- Optimize application code
- Implement model caching

### Issue: Slow Response Times

**Symptoms**:
- API requests taking too long
- Timeouts

**Troubleshooting**:
1. **Check Database Performance**
   - MongoDB Atlas → Performance Advisor
   - Check query performance

2. **Check ML Model Loading**
   - Verify lazy loading is working
   - Check if models are being reloaded

3. **Check Network Latency**
   - CloudWatch → Metrics → Network
   - Check connection times

**Solution**:
- Optimize database queries
- Ensure model caching is working
- Scale up service if needed

---

## Emergency Procedures

### Complete Service Outage

1. **Immediate Actions**
   - Check CloudWatch logs for errors
   - Verify ECS service is running
   - Check database connectivity

2. **Rollback**
   - Rollback to previous task definition
   - Or rollback to previous Docker image

3. **Scale Down and Up**
   - Set desired count to 0
   - Wait 30 seconds
   - Set desired count back to 1

### Database Connection Lost

1. **Check MongoDB Atlas**
   - Verify cluster is running
   - Check IP whitelist includes AWS IPs
   - Verify connection string is correct

2. **Update Environment Variables**
   - Update task definition with correct `MONGO_URL`
   - Force new deployment

### Security Incident

1. **Immediate Actions**
   - Review CloudWatch logs for suspicious activity
   - Check IAM roles for unauthorized access
   - Review security group rules

2. **Containment**
   - Restrict security group to known IPs
   - Rotate API keys and secrets
   - Update IAM policies if needed

3. **Recovery**
   - Update all credentials
   - Review and fix security issues
   - Deploy updated configuration

---

## Monitoring Checklist

Daily:
- [ ] Check service health endpoint
- [ ] Review error logs
- [ ] Check task status

Weekly:
- [ ] Review CloudWatch metrics
- [ ] Check costs in billing dashboard
- [ ] Review security group rules
- [ ] Verify backups (if configured)

Monthly:
- [ ] Review and rotate credentials
- [ ] Update dependencies
- [ ] Review and optimize costs
- [ ] Security audit

---

## Useful Commands

### Get Service Status
```bash
aws ecs describe-services \
  --cluster buyhive-cluster \
  --services buyhive-backend-service \
  --region us-east-1 \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}'
```

### Get Task Public IP
```bash
TASK_ARN=$(aws ecs list-tasks \
  --cluster buyhive-cluster \
  --service-name buyhive-backend-service \
  --query 'taskArns[0]' \
  --output text)

aws ecs describe-tasks \
  --cluster buyhive-cluster \
  --tasks $TASK_ARN \
  --query 'tasks[0].attachments[0].details' \
  --output json
```

### List Recent Deployments
```bash
aws ecs describe-services \
  --cluster buyhive-cluster \
  --services buyhive-backend-service \
  --region us-east-1 \
  --query 'services[0].deployments[*].{Status:status,TaskDef:taskDefinition,Created:createdAt}'
```

---

## Support Contacts

- **AWS Support**: AWS Console → Support Center
- **MongoDB Support**: MongoDB Atlas Dashboard
- **GitHub Issues**: Repository issues page

---

## Document Updates

Keep this runbook updated as procedures change. Document any new issues and their solutions.






