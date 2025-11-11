# DoctHER Deployment Guide

This guide covers deploying the DoctHER application to Streamlit Cloud with a PostgreSQL database hosted on Supabase.

## Prerequisites

- GitHub account (for deploying to Streamlit Cloud)
- Anthropic API key for Claude AI integration

## Database Setup: Supabase

### 1. Create a Supabase Account

1. Visit [https://supabase.com](https://supabase.com)
2. Click "Start your project" and sign up (free tier available)
3. Verify your email address

### 2. Create a New Project

1. From your Supabase dashboard, click "New Project"
2. Fill in the project details:
   - **Name**: `docther-db` (or your preferred name)
   - **Database Password**: Choose a strong password (save this - you'll need it later)
   - **Region**: Select the region closest to your users
   - **Pricing Plan**: Free tier is sufficient for development and demos
3. Click "Create new project"
4. Wait 2-3 minutes for the project to be provisioned

### 3. Get Your Database Connection String

1. In your Supabase project dashboard, go to **Settings** (gear icon in sidebar)
2. Navigate to **Database** section
3. Scroll down to **Connection string**
4. Click on the **URI** tab
5. Copy the connection string - it will look like:
   ```
   postgresql://postgres.xxxxxxxxxxxxxxxxxxxx:[YOUR-PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ```
6. Replace `[YOUR-PASSWORD]` with the database password you created in step 2
7. Save this complete connection string - you'll need it for Streamlit Cloud

### 4. Initialize Database Tables (Automatic)

The application will automatically create all required tables when it first connects to the database. No manual SQL scripts needed!

Tables that will be created:
- `users` - User accounts and authentication
- `chat_sessions` - Chat conversation history
- `messages` - Individual chat messages
- `tool_logs` - MCP tool usage logs
- `symptoms` - Symptom tracking records

## Streamlit Cloud Deployment

### 1. Prepare Your Repository

1. Ensure your code is pushed to GitHub
2. Make sure your repository includes:
   - `requirements.txt` (already configured with PostgreSQL support)
   - `demos/doct_her_stdio.py` (main application file)
   - All `components/` and `database/` directories

### 2. Deploy to Streamlit Cloud

1. Visit [https://share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"
4. Configure the deployment:
   - **Repository**: Select your GitHub repository
   - **Branch**: `main` (or your deployment branch)
   - **Main file path**: `demos/doct_her_stdio.py`
5. Click "Advanced settings"

### 3. Configure Secrets

In the "Secrets" section, paste the following configuration with your actual values:

```toml
# Anthropic API Key for Claude AI
ANTHROPIC_API_KEY = "sk-ant-api03-your-actual-api-key-here"

# Supabase PostgreSQL Database URL
# Replace with your actual connection string from Supabase
DATABASE_URL = "postgresql://postgres.xxxxxxxxxxxxxxxxxxxx:your-password@aws-0-us-east-1.pooler.supabase.com:6543/postgres"

# Optional: Add other API keys if using external services
# PUBMED_API_KEY = "your-key"
# SWAN_API_KEY = "your-key"
```

**Important**:
- Replace `ANTHROPIC_API_KEY` with your actual Anthropic API key
- Replace `DATABASE_URL` with your complete Supabase connection string (including your password)
- Do not use quotes around the actual values, Streamlit Cloud handles this automatically

### 4. Deploy

1. Click "Deploy"
2. Wait 2-5 minutes for the deployment to complete
3. Your app will be available at: `https://your-app-name.streamlit.app`

## Testing Your Deployment

### 1. Create Your First User

1. Open your deployed app URL
2. Click "Sign Up"
3. Create an account with:
   - Email: your email address
   - Password: a secure password
4. Log in with your credentials

### 2. Test Core Functionality

**Chat Interface:**
- Send a message: "Hello, I have a headache"
- Verify the AI responds appropriately

**Symptom Recording:**
- Type a symptom: "I had severe abdominal pain yesterday morning that lasted 3 hours"
- Click "Record Symptom" (🩺 button)
- Verify the symptom is extracted correctly with:
  - Type, location, duration
  - Correct timestamp (yesterday morning)
  - Severity converted from text

**Symptom Tracker:**
- Click the chart icon (📊) in the sidebar
- Verify symptoms are displayed
- Click "View Insights" (📈) to see visualizations
- Test delete functionality (🗑️ button)

**Chat History:**
- Click "Previous Chats" (💬) in sidebar
- Verify your conversation is saved
- Test loading a previous chat

## Database Verification

### Check Database Tables in Supabase

1. Go to your Supabase project dashboard
2. Click on **Table Editor** in the sidebar
3. You should see all tables created:
   - `users`
   - `chat_sessions`
   - `messages`
   - `tool_logs`
   - `symptoms`
4. Click on any table to view the data
5. Verify your test data appears correctly

### View Database Logs

1. In Supabase, go to **Database** > **Logs**
2. You can monitor all database queries and connections
3. Useful for debugging any issues

## Troubleshooting

### App Won't Start

**Error: "Could not connect to database"**
- Verify your `DATABASE_URL` in Streamlit Cloud secrets is correct
- Ensure you replaced `[YOUR-PASSWORD]` with your actual password
- Check the connection string doesn't have extra spaces or quotes

**Error: "Module not found"**
- Verify `requirements.txt` is in your repository root
- Check that `psycopg2-binary>=2.9.0` is in requirements.txt
- Try restarting the app from Streamlit Cloud dashboard

### Database Issues

**Error: "Could not create tables"**
- Check Supabase project is active (not paused)
- Verify your database password is correct
- Check Supabase project status in dashboard

**Data is being created but disappearing**
- If you see this, you might still be using SQLite - check your `DATABASE_URL` secret
- Ensure the URL starts with `postgresql://` not `sqlite://`

### Performance Issues

**App is slow to respond**
- Free tier Supabase pauses after inactivity - first request may be slow
- Consider upgrading Supabase plan for production use
- Check database connection pooling is working (should see multiple connections in Supabase)

## Local Development

To run locally with PostgreSQL (optional):

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Update your `.env` file:
   ```
   DATABASE_URL=postgresql://postgres.xxxx:[PASSWORD]@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   ANTHROPIC_API_KEY=sk-ant-api03-your-key
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   streamlit run demos/doct_her_stdio.py
   ```

**Or use SQLite for local development** (recommended):
```
DATABASE_URL=sqlite:///./womens_health_mcp.db
```

## Security Best Practices

### API Keys
- Never commit API keys to Git
- Use Streamlit Cloud secrets for production
- Use `.env` for local development (add `.env` to `.gitignore`)

### Database
- Use strong passwords for Supabase
- Enable Row Level Security (RLS) in Supabase for production
- Regularly backup your database (Supabase has automatic backups)

### User Data
- All passwords are hashed with bcrypt
- User data is isolated by user_id
- Consider enabling 2FA for your Supabase account

## Monitoring and Maintenance

### Supabase Dashboard
- **Database**: Monitor table sizes and row counts
- **Logs**: View all database queries
- **API**: Monitor API usage and rate limits

### Streamlit Cloud
- **Logs**: View application logs for errors
- **Analytics**: Monitor app usage and performance
- **Settings**: Manage secrets and deployment settings

## Upgrading

### To Update Your Deployment

1. Push changes to your GitHub repository
2. Streamlit Cloud will automatically redeploy
3. Database schema changes will be applied automatically (if using `Base.metadata.create_all`)

### Supabase Free Tier Limits

- **Database**: 500 MB storage
- **API Requests**: 50,000 monthly active users
- **Bandwidth**: 5 GB

If you exceed these limits, consider upgrading to Supabase Pro.

## Support

- **Streamlit Docs**: [https://docs.streamlit.io](https://docs.streamlit.io)
- **Supabase Docs**: [https://supabase.com/docs](https://supabase.com/docs)
- **Application Issues**: Open an issue on your GitHub repository

---

## Quick Reference

### Important URLs
- **Streamlit Cloud**: https://share.streamlit.io
- **Supabase**: https://supabase.com
- **Your App**: `https://your-app-name.streamlit.app` (after deployment)

### Key Files
- `demos/doct_her_stdio.py` - Main application
- `database/models.py` - Database schema
- `requirements.txt` - Python dependencies
- `.env.example` - Environment variables template

### Database Connection String Format
```
postgresql://postgres.[PROJECT-REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:6543/postgres
```
