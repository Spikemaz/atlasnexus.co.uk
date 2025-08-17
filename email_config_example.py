"""
Email Configuration for Security Alerts
Copy this file to email_config.py and fill in your details
"""

# For Gmail, you'll need to use an App Password
# 1. Go to https://myaccount.google.com/security
# 2. Enable 2-factor authentication
# 3. Generate an App Password for "Mail"

# Gmail Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your-email@gmail.com"
SMTP_PASSWORD = "your-app-password-here"

# For other email providers:

# Outlook/Hotmail
# SMTP_SERVER = "smtp-mail.outlook.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "your-email@outlook.com"
# SMTP_PASSWORD = "your-password"

# Yahoo
# SMTP_SERVER = "smtp.mail.yahoo.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "your-email@yahoo.com"
# SMTP_PASSWORD = "your-password"

# Custom/Corporate Email
# SMTP_SERVER = "mail.yourdomain.com"
# SMTP_PORT = 587
# SMTP_USERNAME = "you@yourdomain.com"
# SMTP_PASSWORD = "your-password"

# Alert Settings
ALERT_EMAIL = "marcus@atlasnexus.co.uk"  # Where to send alerts
ALERT_FROM_NAME = "AtlasNexus Security"

# Set as environment variables for production:
# export SMTP_SERVER="smtp.gmail.com"
# export SMTP_PORT="587"
# export SMTP_USERNAME="your-email@gmail.com"
# export SMTP_PASSWORD="your-app-password"