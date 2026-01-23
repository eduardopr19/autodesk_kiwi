# Email Configuration for AutoDesk Kiwi

This guide explains how to configure Outlook and Protonmail email access.

## Configuration Outlook (Microsoft 365)

### Step 1: Create an Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** > **App registrations**
3. Click **New registration**
4. Fill in:
   - **Name**: `AutoDesk Kiwi Email`
   - **Supported account types**: `Accounts in any organizational directory and personal Microsoft accounts`
   - **Redirect URI**:
     - Type: `Web`
     - URL: `http://localhost:8000/email/outlook/callback`
5. Click **Register**

### Step 2: Get Credentials

1. On your application page, copy the **Application (client) ID**
2. Go to **Certificates & secrets**
3. Click **New client secret**
4. Give a description (e.g., "AutoDesk Kiwi") and choose an expiration
5. Copy the secret **Value** (you won't be able to see it again!)

### Step 3: Configure Permissions

1. Go to **API permissions**
2. Click **Add a permission**
3. Choose **Microsoft Graph**
4. Select **Delegated permissions**
5. Add: `Mail.Read`
6. Click **Add permissions**
7. (Optional) Click **Grant admin consent** if you're an admin

### Step 4: Add to .env

Create a `.env` file in the `api/` folder with:

```env
OUTLOOK_CLIENT_ID=your-application-client-id
OUTLOOK_CLIENT_SECRET=your-client-secret
OUTLOOK_TENANT_ID=common
OUTLOOK_REDIRECT_URI=http://localhost:8000/email/outlook/callback
```

## Protonmail Configuration

### Step 1: Get API Key

1. Log in to [Protonmail](https://mail.proton.me)
2. Go to **Settings** (gear icon)
3. Navigate to **Security** > **API Access**
4. Click **Generate API Key**
5. Give it a name (e.g., "AutoDesk Kiwi")
6. Copy the generated key

### Step 2: Add to .env

Add to your `.env` file:

```env
PROTONMAIL_API_KEY=your-protonmail-api-key
PROTONMAIL_API_URL=https://api.protonmail.ch
```

## Usage

### 1. First Outlook Login

1. Start the application
2. Go to `http://localhost:8000/email/outlook/login`
3. Copy the returned URL and open it in your browser
4. Log in with your Microsoft account
5. Accept the permissions
6. You will be redirected to the callback page

### 2. Check Emails

- **Outlook**: `http://localhost:8000/email/outlook/unread`
- **Protonmail**: `http://localhost:8000/email/proton/unread`
- **Summary**: `http://localhost:8000/email/summary`

## Important Notes

- OAuth2 tokens are stored in memory and will be lost on restart
- For production use, use a secure database
- Never share your `.env` files or secrets
- Protonmail API keys may have rate limitations
