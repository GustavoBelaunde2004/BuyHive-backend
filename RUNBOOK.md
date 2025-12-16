# BuyHive Backend - Operations Runbook (Railway)

This runbook covers common operational tasks when running BuyHive on Railway (Docker).

## Viewing Logs

- Railway → Project → **Deployments**
- Click the latest deployment → **Logs**

## Restarting the Service

- Railway → Project → **Deployments**
- Click **Redeploy** on the latest successful deployment

## Rolling Back

- Railway → Project → **Deployments**
- Find a previous known-good deployment
- Click **Redeploy** for that deployment

## Scaling

Railway scaling depends on your plan, but typically:
- Railway → Project → **Settings**
- Increase **replicas/instances** if available

## Health Checks

Use your Railway service URL:
- `GET /health`
- `GET /health/ready`
- `GET /health/live`

## Common Issues

### Service won’t start

- Check Railway logs for startup errors
- Confirm Railway variables are set:
  - `ENVIRONMENT=production`
  - `MONGO_URL`, `AUTH0_DOMAIN`, `AUTH0_AUDIENCE`, `ALLOWED_ORIGINS`
  - `GROQ_API_KEY`, `OPENAI_API_KEY`
  - `PORT=8000`
- Confirm MongoDB Atlas Network Access allows Railway egress IPs (or temporarily allow `0.0.0.0/0` while testing)

### CORS errors in browser

- Ensure `ALLOWED_ORIGINS` includes your frontend origin(s), comma-separated

### Auth0 401s

- Verify `AUTH0_DOMAIN` and `AUTH0_AUDIENCE` match your Auth0 API settings
- Verify your frontend is requesting tokens for the same audience

### Email sending doesn’t work

Email uses AWS SES but is optional. If you haven’t configured SES yet:
- Leave `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`, `SES_FROM_EMAIL` unset
- The backend will still run; the share-cart email endpoint will return a clear “not configured” error


