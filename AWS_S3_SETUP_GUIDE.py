"""
AWS S3 Setup Guide for AegisAI
================================

STEP 1: Create IAM User for Programmatic Access
------------------------------------------------
1. Go to AWS Console: https://console.aws.amazon.com/
2. Navigate to IAM (Identity and Access Management)
3. Click "Users" in left sidebar
4. Click "Create user" button
5. User name: "aegisai-reports-user"
6. Click "Next"

STEP 2: Set Permissions
------------------------
1. Select "Attach policies directly"
2. Search and select: "AmazonS3FullAccess" (or create custom policy below)
3. Click "Next"
4. Click "Create user"

STEP 3: Create Access Keys
---------------------------
1. Click on the newly created user "aegisai-reports-user"
2. Go to "Security credentials" tab
3. Scroll down to "Access keys" section
4. Click "Create access key"
5. Select "Application running outside AWS"
6. Click "Next"
7. Add description: "AegisAI Reports Service"
8. Click "Create access key"

STEP 4: Save Credentials
-------------------------
You'll see:
- Access key ID: AKIA... (20 characters)
- Secret access key: (40 characters)

⚠️ IMPORTANT: Copy these NOW! Secret key is shown only once!

STEP 5: Update .env File
-------------------------
Open: d:\AegisAI\aegisai-connectors\.env

Add these lines:
AWS_ACCESS_KEY_ID=AKIA...your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-bucket-name

STEP 6: Verify S3 Bucket Name
------------------------------
1. Go to S3 Console: https://s3.console.aws.amazon.com/
2. Find your bucket name (e.g., "aegisai-reports")
3. Copy exact bucket name to .env

STEP 7: Test Connection
------------------------
Run this test script:

python test_s3_connection.py

If successful, you'll see: "✓ S3 connection successful!"

---

CUSTOM IAM POLICY (More Secure - Optional)
-------------------------------------------
Instead of AmazonS3FullAccess, use this custom policy:

{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name/*",
        "arn:aws:s3:::your-bucket-name"
      ]
    }
  ]
}

Replace "your-bucket-name" with your actual bucket name.

---

TROUBLESHOOTING
---------------
Error: "NoCredentialsError"
→ Check .env file has correct AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

Error: "AccessDenied"
→ Check IAM user has S3 permissions

Error: "NoSuchBucket"
→ Check S3_BUCKET_NAME matches exactly (case-sensitive)

Error: "InvalidAccessKeyId"
→ Regenerate access keys in IAM console
"""

print(__doc__)
