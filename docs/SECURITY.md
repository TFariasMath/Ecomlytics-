# 🔐 Security Guidelines

This document outlines security best practices for the Analytics Pipeline project.

---

## 🎯 Quick Security Checklist

Before committing code:
- [ ] No credentials in code
- [ ] `.env` file is gitignored
- [ ] No API keys/tokens in files
- [ ] Sensitive data properly handled
- [ ] Database files not committed

---

## 🔒 Credential Management

### DO ✅

- **Use environment variables** for all credentials
- **Store in `.env` file** (never commit)
- **Use different credentials** for dev/staging/prod
- **Rotate credentials** regularly (every 90 days)
- **Use read-only permissions** when possible
- **Revoke unused tokens** immediately

### DON'T ❌

- **Never hardcode** credentials in source code
- **Never commit** `.env` files
- **Never share** credentials via email/chat
- **Never use production keys** in development  
- **Never commit** database files with real data

---

## 📁 File Security

### Sensitive Files (NEVER Commit)

| File Pattern | Contains | Status |
|--------------|----------|--------|
| `.env` | API keys, tokens | ✅ In .gitignore |
| `*.db` | Customer PII | ✅ In .gitignore |
| `config/credentials/*.json` | Service account keys | ✅ In .gitignore |
| `logs/*.log` | Execution logs | ✅ In .gitignore |
| `backups/` | Database backups | ✅ In .gitignore |

### Safe to Commit

- `.env.example` - Template without real values
- Source code (`.py` files) using env variables
- Documentation
- Configuration templates

---

## 🗄️ Database Security

### Personal Data in Databases

The following databases contain **Personal Identifiable Information (PII)**:

**woocommerce.db:**
- Customer names, emails, phone numbers
- Billing and shipping addresses
- Purchase history

**analytics.db:**
- User behavior data
- Traffic sources

**facebook.db:**
- Social media metrics

### Best Practices

1. **Never commit** database files to version control
2. **Encrypt databases** in production environments
3. **Regular backups** to secure, encrypted storage
4. **Access control** - limit who can access databases
5. **Data retention** - delete old data per privacy policy
6. **Anonymize** test data - never use production data for testing

---

## 🌐 API Security

### WooCommerce

```bash
# In .env
WC_URL=https://your-store.com
WC_CONSUMER_KEY=ck_xxxxx
WC_CONSUMER_SECRET=cs_xxxxx
```

**Permissions**: Use read-only keys when possible

### Google Analytics

```bash
# In .env  
GA4_KEY_FILE=path/to/service-account.json
GA4_PROPERTY_ID=123456789
```

**Permissions**: Grant "Viewer" role to service account

### Facebook

```bash
# In .env
FB_ACCESS_TOKEN=EAAxxxxx
FB_PAGE_ID=123456789
```

**Permissions**: Use Page Access Token (doesn't expire)

---

## 🔄 Token Management

### Rotating Credentials

**When to rotate:**
- Every 90 days (scheduled)
- After team member leaves
- If token is exposed/leaked
- After security incident

**How to rotate:**
1. Generate new credentials in respective platform
2. Update `.env` file
3. Test connections via setup page
4. Revoke old credentials
5. Update documentation

### Revoking Exposed Tokens

**If a token is leaked:**

1. **Immediate**: Revoke in platform
   - WooCommerce: WooCommerce > Settings > Advanced > REST API
   - Google: Cloud Console > IAM > Service Accounts
   - Facebook: Developers > App Settings > Access Tokens

2. **Generate new** credentials
3. **Update** `.env` file
4. **Audit** access logs for suspicious activity
5. **Document** incident

---

## 🛡️ Code Security

### Secure Coding Practices

```python
# ✅ GOOD - Using environment variables
from config.settings import WooCommerceConfig
url = WooCommerceConfig.get_url()

# ❌ BAD - Hardcoded credentials
URL = "https://mystore.com"
API_KEY = "sk_live_xxxxx"
```

### Input Validation

```python
# Always validate user input
if not url or not url.startswith('https://'):
    raise ValueError("Invalid URL")
```

### Error Messages

```python
# ✅ GOOD - Generic error
logger.error("Authentication failed")

# ❌ BAD - Exposes token
logger.error(f"Token {token} is invalid")
```

---

## 📝 Logging Security

### What NOT to Log

- API keys, tokens, passwords
- Full credit card numbers
- Social security numbers
- Complete credentials

### Safe Logging

```python
# ✅ GOOD
logger.info(f"Connected to store: {url}")

# ❌ BAD
logger.info(f"Using key: {consumer_key}")
```

---

## 🏢 Production Deployment

### Environment Separation

Maintain separate credentials for:
- **Development** - Test accounts/sandbox
- **Staging** - Replica of production
- **Production** - Real customer data

### Secrets Management (Advanced)

For production deployments, use:
- **AWS Secrets Manager**
- **Azure Key Vault**
- **Google Cloud Secret Manager**
- **HashiCorp Vault**

Never store production secrets in `.env` on servers.

---

## 📊 Compliance

### GDPR (Europe)

Required for EU customer data:
- ✅ Data minimization
- ✅ Right to access
- ✅ Right to erasure
- ✅ Data portability
- ✅ Consent management

### CCPA (California)

Required for California residents:
- ✅ Data disclosure
- ✅ Opt-out of sale
- ✅ Data deletion
- ✅ Non-discrimination

### Best Practices

- Document what data you collect
- Implement data deletion workflows
- Provide privacy policy
- Regular compliance audits

---

## 🚨 Incident Response

### If Credentials Are Exposed

**Immediate Actions:**
1. Revoke compromised credentials
2. Generate new credentials
3. Update `.env` and restart services
4. Check access logs for unauthorized use
5. Notify affected parties if data accessed

**Follow-up:**
1. Document incident
2. Review how leak occurred
3. Implement preventive measures
4. Update team training
5. Consider security audit

---

## 🎓 Security Training

### For Developers

Required knowledge:
- Never commit secrets
- Use `.gitignore` properly
- Variable environment best practices
- Secure coding standards

### For Admins

Required knowledge:
- Credential rotation procedures
- Access control management
- Incident response protocols
- Compliance requirements

---

## 📞 Security Contacts

### Report Security Issues

If you discover a security vulnerability:
1. **DO NOT** create public issue
2. Email security contact (if available)
3. Provide detailed description
4. Allow time for patch before disclosure

---

## 🔍 Regular Audits

### Monthly

- Review access logs
- Check for exposed credentials in code
- Verify .gitignore effectiveness

### Quarterly

- Rotate all credentials
- Security code review
- Update dependencies
- Compliance check

### Annually

- Full security audit
- Penetration testing
- Policy review and update

---

**Last Updated**: December 21, 2025  
**Next Review**: March 21, 2026
