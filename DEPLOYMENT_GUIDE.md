# Azure Bot Service Deployment Guide

## Pre-deployment Checklist

### 1. Azure App Registration Setup

1. Go to [Azure Portal](https://portal.azure.com) → Azure Active Directory → App registrations
2. Click "New registration"
3. Name: `YourBotName-Registration`
4. Supported account types: **Single tenant** (Accounts in this organizational directory only)
5. Redirect URI: Leave blank for now
6. Click "Register"

### 2. Configure App Registration

1. Copy the **Application (client) ID** → This is your `MicrosoftAppId`
2. Copy the **Directory (tenant) ID** → This is your `MicrosoftAppTenantId`
3. Go to "Certificates & secrets" → "New client secret"
4. Description: "Bot Secret", Expires: 24 months
5. Copy the **Value** (not the ID) → This is your `MicrosoftAppPassword`

### 3. Update Environment Variables

Update your `.env` file or Azure App Service Configuration:

```
MicrosoftAppType=SingleTenant
MicrosoftAppId=<your-application-client-id>
MicrosoftAppPassword=<your-client-secret-value>
MicrosoftAppTenantId=<your-directory-tenant-id>
```

## Azure App Service Deployment

### Option 1: Manual Deployment via Azure Portal

1. **Create App Service**:

   - Resource type: Web App
   - OS: Linux
   - Runtime stack: Python 3.9 or 3.10
   - Region: Choose closest to your users

2. **Configure App Service**:

   - Go to Configuration → Application settings
   - Add the environment variables from your `.env` file
   - Set `SCM_DO_BUILD_DURING_DEPLOYMENT` to `true`

3. **Set Startup Command**:

   - Go to Configuration → General settings
   - Startup Command: `gunicorn --bind 0.0.0.0 --worker-class aiohttp.worker.GunicornWebWorker --timeout 600 app:APP`

4. **Deploy Code**:
   - Use VS Code Azure extension, GitHub Actions, or ZIP deployment
   - Ensure all files are uploaded including `requirements.txt`

### Option 2: ARM Template Deployment

Use the provided ARM templates in the `deploymentTemplates` folder:

- `template-with-new-rg.json` - Creates new resource group
- `template-with-preexisting-rg.json` - Uses existing resource group

## Bot Service Registration

1. **Create Bot Service**:

   - Go to Azure Portal → Create resource → Bot Service
   - Bot handle: Unique name for your bot
   - Subscription & Resource group: Same as App Service
   - Pricing tier: F0 (free) for testing
   - Microsoft App ID: Select "Use existing app registration"
   - App ID: Your `MicrosoftAppId`

2. **Configure Messaging Endpoint**:
   - Messaging endpoint: `https://your-app-name.azurewebsites.net/api/messages`
   - Enable "Microsoft Teams" channel for testing

## Testing Your Bot

### 1. Health Check

- Navigate to: `https://your-app-name.azurewebsites.net/health`
- Should return: `{"status": "healthy", "timestamp": "..."}`

### 2. Web Chat Test

1. Go to Azure Portal → Your Bot Service → Test in Web Chat
2. Type a message → Should echo back "Echo: [your message]"

### 3. Teams Testing (if enabled)

1. Go to Bot Service → Channels → Microsoft Teams → "Microsoft Teams Commercial"
2. Click the Teams link to add bot to Teams
3. Test messaging in Teams

## Troubleshooting

### Common Issues

1. **401 Unauthorized**:

   - Check `MicrosoftAppId` and `MicrosoftAppPassword` are correct
   - Verify App Registration is in correct tenant
   - Ensure client secret hasn't expired

2. **500 Internal Server Error**:

   - Check application logs in Azure App Service → Log stream
   - Verify all required packages are in `requirements.txt`
   - Check startup command is correct

3. **Bot not responding**:
   - Verify messaging endpoint URL is correct
   - Check App Service is running (not stopped)
   - Test health endpoint first

### Debugging Steps

1. **Check App Service Logs**:

   ```
   Azure Portal → App Service → Monitoring → Log stream
   ```

2. **Test Health Endpoint**:

   ```
   curl https://your-app-name.azurewebsites.net/health
   ```

3. **Verify Environment Variables**:

   ```
   Azure Portal → App Service → Configuration → Application settings
   ```

4. **Check Deployment**:
   ```
   Azure Portal → App Service → Deployment → Deployment Center
   ```

## Security Best Practices

1. **Environment Variables**: Never commit secrets to source control
2. **App Service**: Enable HTTPS only
3. **Bot Channels**: Only enable required channels
4. **Monitoring**: Enable Application Insights for production
5. **Authentication**: Use managed identity where possible

## Monitoring & Maintenance

1. **Application Insights**: Enable for production monitoring
2. **Health Checks**: Monitor `/health` endpoint
3. **Log Analytics**: Configure for centralized logging
4. **Alerts**: Set up alerts for failures and performance issues

## Startup Command for Azure App Service

Use this as your startup command in Azure App Service:

```bash
gunicorn --bind 0.0.0.0 --worker-class aiohttp.worker.GunicornWebWorker --timeout 600 app:APP
```

Or for enhanced logging:

```bash
gunicorn --bind 0.0.0.0 --worker-class aiohttp.worker.GunicornWebWorker --workers 1 --timeout 600 --keep-alive 2 --max-requests 1000 --access-logfile - --error-logfile - app:APP
```
