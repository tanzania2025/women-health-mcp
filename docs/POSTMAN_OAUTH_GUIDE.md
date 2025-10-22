# OAuth with Postman Callback - Quick Guide

Your NHS application is now configured to use Postman's OAuth callback service: `https://oauth.pstmn.io/v1/callback`

This is **easier than localhost** because Postman will display the authorization code clearly for you!

## ✅ What's Configured

- **Callback URL in NHS Portal**: `https://oauth.pstmn.io/v1/callback`
- **Server Configuration**: Updated to match
- **Server Built**: ✅ Ready to use

## 🚀 Quick Test

### Try This URL Now:

```
https://int.api.service.nhs.uk/oauth2/authorize?client_id=ib1b5Spxp1nci7Lxr0P7lVPML7uZFpbl&redirect_uri=https%3A%2F%2Foauth.pstmn.io%2Fv1%2Fcallback&response_type=code&scope=openid+profile+email+nhs-number&state=test123
```

### What Will Happen:

1. **Visit the URL** - You'll be taken to NHS Login
2. **Log in** - Use your NHS credentials or test credentials
3. **Authorize** - Grant "Doct-her" access to your data
4. **Redirected to Postman** - Postman's page will show:
   - ✅ The authorization **code** (clearly displayed)
   - ✅ The state parameter
   - ✅ Easy copy button

5. **Copy the code** - Just click to copy or select it
6. **Exchange in Claude Desktop** - Tell Claude: "Exchange this authorization code: YOUR_CODE"

## 📱 What Postman's Callback Page Looks Like

When you're redirected to Postman, you'll see a page that says:

```
Authentication complete

You can close this tab and return to your application.

Authorization Code:
abc123xyz789...  [Copy]

State:
test123
```

Just copy the authorization code!

## 🎯 Complete Flow in Claude Desktop

Once you've added the server to Claude Desktop:

### Step 1: Get Auth URL
**Ask Claude:**
```
Get my NHS authorization URL
```

### Step 2: Visit URL & Login
- Click the URL Claude provides
- Log in with NHS credentials
- Authorize the app

### Step 3: Copy Code from Postman
- Postman shows the code clearly
- Click copy or select the code

### Step 4: Exchange Code
**Tell Claude:**
```
Exchange this authorization code: abc123xyz789
```

### Step 5: Access Your Data
**Now you can ask:**
```
Show me my patient information
What medications am I prescribed?
Show my vaccination history
```

## 🔄 Why Postman's Callback is Better

### ✅ Advantages:
- **HTTPS** - Accepted by NHS portal (no localhost issues)
- **Clear Display** - Code is shown clearly, not in URL bar
- **Copy Button** - Easy to copy
- **No Server Needed** - No need to run localhost
- **Always Available** - Postman maintains this service

### Compared to localhost:
- ❌ Localhost shows "can't connect" error page
- ❌ Code hidden in browser URL bar
- ❌ HTTP might be rejected by some OAuth providers

## 🧪 Testing Different Scenarios

### Test 1: Application-Restricted (No OAuth)
```
Get an application access token
```
This uses your API key only - no browser needed.

### Test 2: User-Restricted (OAuth with Postman)
```
Get my NHS authorization URL
```
Follow the Postman callback flow - full patient data access.

## ⚠️ Troubleshooting

### "Invalid redirect_uri" error
**Problem**: Callback URL mismatch

**Solution**: Verify in NHS portal it's exactly:
```
https://oauth.pstmn.io/v1/callback
```

### "Invalid client" error
**Problem**: Client ID not recognized

**Solution**:
- Double-check Client ID in `.env` matches NHS portal
- Ensure you're using the dev environment endpoint

### Code exchange fails
**Problem**: Code expired or already used

**Solution**:
- Get a fresh authorization URL
- Go through the flow again
- Codes are single-use and expire quickly

### Can't log into NHS Login
**Problem**: Need credentials

**Solution**:
- For **dev environment**: You may need test credentials
- For **production**: Need real NHS Login
- Check with NHS support for dev test accounts

## 🔐 Security Notes

- Postman's callback is a public service (used by thousands)
- **Never share your authorization codes** publicly
- Codes expire quickly (usually 10 minutes)
- Codes are single-use
- Once exchanged, you get access tokens - treat them like passwords

## 📊 What Data You Can Access

Once authenticated with user-restricted OAuth:

### Personal Information
- ✅ Name, NHS number, date of birth
- ✅ Address, contact details
- ✅ GP registration

### Medical Records
- ✅ Medications and prescriptions
- ✅ Immunization history
- ✅ Appointments
- ✅ Medical conditions and diagnoses
- ✅ Allergies and intolerances

### Limitations
- ⚠️ Development environment = Test data only
- ⚠️ May not have complete records
- ⚠️ Some endpoints might not be fully implemented in dev

## 🎉 You're Ready!

Your server is now configured to work with Postman's OAuth callback service. This is the easiest way to handle the OAuth flow.

**Next steps:**
1. ✅ Add server to Claude Desktop (if not already done)
2. ✅ Restart Claude Desktop
3. ✅ Ask for authorization URL
4. ✅ Test the flow!

---

**Quick test**: Try the authorization URL above and see if you can get to the NHS Login page!
