# How to Get Azure Bot Credentials

## Step-by-Step Guide to Get Your Azure Credentials

### 🔑 What You Need

You need these 3 values for your bot to work:

- **MicrosoftAppId** - Your app's unique identifier
- **MicrosoftAppPassword** - Your app's secret key
- **MicrosoftAppTenantId** - Your Azure organization's ID

---

## 📋 Step 1: Get Your Tenant ID (MicrosoftAppTenantId)

### Option A: From Azure Portal Home

1. Go to **https://portal.azure.com**
2. Sign in with your work/school account
3. On the home page, you'll see **Tenant ID** displayed
4. Copy this GUID (format: `12345678-1234-1234-1234-123456789abc`)

### Option B: From Azure Active Directory

1. Go to **Azure Portal** → **Azure Active Directory**
2. In the **Overview** section, find **Tenant ID**
3. Copy the GUID value

---

## 🏗️ Step 2: Create App Registration (MicrosoftAppId + MicrosoftAppPassword)

### Create New App Registration

1. **Navigate**: Azure Portal → **Azure Active Directory** → **App registrations**
2. **Click**: "**+ New registration**"
3. **Fill out the form**:
   ```
   Name: MyEchoBotRegistration
   Supported account types: ✅ Single tenant (Accounts in this organizational directory only)
   Redirect URI: (Leave blank)
   ```
4. **Click**: "**Register**"

### Get the App ID (MicrosoftAppId)

After registration, you'll see the app overview page:

1. **Copy** the **Application (client) ID**
2. This is your `MicrosoftAppId`
3. Format: `12345678-1234-1234-1234-123456789abc`

### Create App Secret (MicrosoftAppPassword)

1. **Navigate**: Still in your app registration → **Certificates & secrets** (left menu)
2. **Click**: "**+ New client secret**"
3. **Fill out**:
   ```
   Description: Bot Secret
   Expires: 24 months (recommended)
   ```
4. **Click**: "**Add**"
5. **⚠️ IMPORTANT**: Copy the **Value** immediately (not the Secret ID)
6. This value is your `MicrosoftAppPassword`
7. **You can only see this value once!** If you lose it, create a new secret.

---

## 🤖 Step 3: Optional - Create Bot Service Resource

If you want to use Azure Bot Service (recommended for production):

1. **Navigate**: Azure Portal → **Create a resource** → Search "**Bot Service**"
2. **Click**: "**Azure Bot**"
3. **Fill out**:
   ```
   Bot handle: my-echo-bot (must be globally unique)
   Subscription: Your subscription
   Resource group: Create new or use existing
   Pricing tier: F0 (Free)
   Microsoft App ID: ✅ Use existing app registration
   App ID: [Paste your MicrosoftAppId from Step 2]
   ```
4. **Click**: "**Review + create**" → "**Create**"

---

## 📝 Step 4: Update Your .env File

Replace the placeholder values in your `.env` file:

```env
MicrosoftAppType=SingleTenant
MicrosoftAppId=12345678-1234-1234-1234-123456789abc
MicrosoftAppPassword=your-secret-value-from-step-2
MicrosoftAppTenantId=87654321-4321-4321-4321-210987654321
```

**Example with real-looking values:**

```env
MicrosoftAppType=SingleTenant
MicrosoftAppId=a1b2c3d4-e5f6-7890-abcd-123456789012
MicrosoftAppPassword=Xy9~Q8W.e7R6t5Y4u3I2o1P0-_=+[]{}
MicrosoftAppTenantId=9f8e7d6c-5b4a-3928-1706-fedcba098765
```

---

## 🚨 Quick Troubleshooting

### "I can't find Azure Active Directory"

- Look for **"Microsoft Entra ID"** (new name for Azure AD)
- Or search "Active Directory" in the Azure Portal search bar

### "I don't have permissions to create app registrations"

- Contact your Azure administrator
- You need **Application Developer** role or higher

### "I lost my client secret"

- Go back to **Certificates & secrets** → Create a new client secret
- Update your `.env` file with the new secret value

### "My tenant ID doesn't look right"

- Tenant ID should be a GUID: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`
- It should be 36 characters long (including dashes)

---

## 🔍 Verification Steps

After getting your credentials:

1. **Run the validation script**:

   ```bash
   python validate_config.py
   ```

2. **Check the format**:

   - All IDs should be 36-character GUIDs
   - Password can be any string (usually contains special characters)

3. **Test locally** (optional):
   ```bash
   python app.py
   ```
   Then check: http://localhost:3978/health

---

## 🔐 Security Best Practices

1. **Never commit real credentials to Git**
2. **In Azure App Service**: Set these as **Application Settings**, not in `.env`
3. **Rotate secrets regularly** (every 6-12 months)
4. **Use different credentials for dev/test/prod environments**

---

## 📞 Need Help?

If you're still having trouble:

1. Check if you're signed into the correct Azure tenant
2. Verify you have the right permissions in Azure AD
3. Make sure you're copying the **Value** of the client secret, not the ID
4. Contact your Azure administrator for help with permissions

---

**Next Step**: Once you have all three values, update your `.env` file and proceed with deployment to Azure App Service!
