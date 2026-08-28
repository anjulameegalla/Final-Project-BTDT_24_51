"""
CloudGuard AI – AI Explanation & Recommendation Engine
Supports: Google Gemini, OpenAI GPT-4, and a built-in fallback.
"""

import asyncio
from typing import Dict, Any, Optional
from app.config import settings

# ── Built-in fallback explanations (no API key needed) ───────────────────────
FALLBACK_EXPLANATIONS: Dict[str, Dict[str, Any]] = {
    "IAM User Without MFA Enabled": {
        "explanation": "Multi-Factor Authentication (MFA) adds a second layer of security beyond just a password. Without MFA, if an attacker obtains the user's password through phishing or a data breach, they can immediately access your AWS account.",
        "why_dangerous": "Password-only authentication is vulnerable to phishing, credential stuffing, and brute-force attacks. A compromised IAM user without MFA gives attackers full access to all resources that user can access.",
        "business_impact": "Unauthorized access can lead to data theft, resource abuse (crypto mining), ransomware deployment, and significant financial losses from unexpected AWS bills.",
        "fix_steps": [
            "Go to AWS Console → IAM → Users",
            "Select the affected user",
            "Click 'Security credentials' tab",
            "Under 'Multi-factor authentication (MFA)', click 'Assign MFA device'",
            "Follow the wizard to set up a virtual MFA device (Google Authenticator, Authy)",
            "Enforce MFA via IAM policy: add condition 'aws:MultiFactorAuthPresent': 'true'",
        ],
        "cli_command": "aws iam enable-mfa-device --user-name USERNAME --serial-number arn:aws:iam::ACCOUNT:mfa/DEVICE --authentication-code1 CODE1 --authentication-code2 CODE2",
        "best_practice": "Enable MFA for all IAM users, especially those with console access. Use hardware MFA tokens for privileged accounts.",
    },
    "IAM User With Administrator Access": {
        "explanation": "The AdministratorAccess policy grants unrestricted access to all AWS services and resources. This violates the principle of least privilege.",
        "why_dangerous": "If this account is compromised, an attacker gains complete control over your entire AWS environment — they can create backdoor accounts, exfiltrate data, delete resources, or run up massive bills.",
        "business_impact": "Complete AWS account takeover, data breach, service disruption, compliance violations (PCI-DSS, HIPAA, SOC2), and potential regulatory fines.",
        "fix_steps": [
            "Identify what services the user actually needs access to",
            "Create a custom IAM policy with only required permissions",
            "Go to IAM → Users → Select user → Permissions tab",
            "Detach the AdministratorAccess policy",
            "Attach the new least-privilege policy",
            "Test that the user can still perform their required tasks",
        ],
        "cli_command": "aws iam detach-user-policy --user-name USERNAME --policy-arn arn:aws:iam::aws:policy/AdministratorAccess",
        "best_practice": "Follow the principle of least privilege. Only the root account or a break-glass admin account should have administrator access, and it should be rarely used.",
    },
    "S3 Bucket Is Publicly Accessible": {
        "explanation": "This S3 bucket can be accessed by anyone on the internet without authentication. Any files stored in this bucket are publicly readable.",
        "why_dangerous": "Sensitive data such as customer PII, financial records, application secrets, database backups, or internal documents could be exposed to the entire internet.",
        "business_impact": "Data breach, GDPR/HIPAA violations, reputational damage, customer trust loss, and regulatory fines that can reach millions of dollars.",
        "fix_steps": [
            "Go to AWS Console → S3 → Select the bucket",
            "Click 'Permissions' tab",
            "Under 'Block public access', click 'Edit'",
            "Enable all four Block Public Access settings",
            "Click 'Save changes' and confirm",
            "Review and update the bucket policy to remove any public access grants",
            "Review bucket ACL and remove public grants",
        ],
        "cli_command": "aws s3api put-public-access-block --bucket BUCKET_NAME --public-access-block-configuration BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true",
        "best_practice": "All S3 buckets should have Block Public Access enabled by default. Use pre-signed URLs for temporary access to private content.",
    },
    "SSH Port 22 Open to the Internet": {
        "explanation": "The security group allows SSH connections from any IP address (0.0.0.0/0). This means anyone on the internet can attempt to connect to your EC2 instances via SSH.",
        "why_dangerous": "Automated bots constantly scan the internet for open SSH ports and attempt brute-force attacks. A successful attack gives the attacker shell access to your server.",
        "business_impact": "Server compromise, data theft, ransomware installation, use of your server as a botnet node, and potential lateral movement to other internal systems.",
        "fix_steps": [
            "Go to EC2 → Security Groups → Select the security group",
            "Click 'Inbound rules' → 'Edit inbound rules'",
            "Find the SSH rule (port 22, source 0.0.0.0/0)",
            "Change the source to your specific IP address or corporate IP range",
            "Alternatively, remove the rule and use AWS Systems Manager Session Manager instead",
            "Click 'Save rules'",
        ],
        "cli_command": "aws ec2 revoke-security-group-ingress --group-id SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0",
        "best_practice": "Never open SSH to 0.0.0.0/0. Use AWS Systems Manager Session Manager for shell access without opening any inbound ports.",
    },
    "Root Account Login Detected": {
        "explanation": "The AWS root account has been used to log into the console. The root account has unrestricted access to all AWS services and cannot have its permissions restricted.",
        "why_dangerous": "The root account is the most powerful account in AWS. Its credentials cannot be restricted by IAM policies. If compromised, an attacker has complete, irrevocable control.",
        "business_impact": "Complete account takeover, inability to recover access, potential for account closure, and total data loss.",
        "fix_steps": [
            "Immediately review what actions were taken with the root account",
            "If unauthorized, contact AWS Support immediately",
            "Enable MFA on the root account if not already done",
            "Delete root account access keys if they exist",
            "Create IAM users with appropriate permissions for daily tasks",
            "Store root credentials securely and only use for account-level tasks",
            "Set up CloudWatch alarm for root account usage",
        ],
        "cli_command": "aws iam delete-virtual-mfa-device --serial-number arn:aws:iam::ACCOUNT_ID:mfa/root-account-mfa  # Only if replacing MFA",
        "best_practice": "Lock away root credentials. Enable MFA. Never use root for daily operations. Create an IAM admin user instead.",
    },
    "Access Key Older Than 90 Days": {
        "explanation": "This IAM access key has not been rotated in over 90 days. Long-lived credentials increase the risk of compromise going undetected.",
        "why_dangerous": "If the key was leaked (in code, logs, or a breach), an attacker could have been using it for months without detection. Older keys are more likely to have been exposed.",
        "business_impact": "Prolonged unauthorized access, data exfiltration, resource abuse, and compliance violations.",
        "fix_steps": [
            "Create a new access key for the user",
            "Update all applications/services using the old key with the new key",
            "Test that everything works with the new key",
            "Deactivate the old key (don't delete yet)",
            "Monitor for any failures, then delete the old key after 24-48 hours",
        ],
        "cli_command": "aws iam create-access-key --user-name USERNAME\naws iam update-access-key --user-name USERNAME --access-key-id OLD_KEY_ID --status Inactive\naws iam delete-access-key --user-name USERNAME --access-key-id OLD_KEY_ID",
        "best_practice": "Rotate access keys every 90 days. Use IAM roles instead of long-term access keys wherever possible (EC2, Lambda, ECS).",
    },
    "S3 Bucket Encryption Disabled": {
        "explanation": "This S3 bucket does not have server-side encryption enabled. Data stored in this bucket is not encrypted at rest.",
        "why_dangerous": "If AWS storage media is ever physically compromised or if there is unauthorized access to the bucket, the data would be readable without any decryption.",
        "business_impact": "Data exposure, compliance violations (HIPAA, PCI-DSS require encryption at rest), and potential regulatory fines.",
        "fix_steps": [
            "Go to S3 → Select bucket → Properties tab",
            "Scroll to 'Default encryption'",
            "Click 'Edit'",
            "Select 'Server-side encryption with Amazon S3 managed keys (SSE-S3)' or SSE-KMS",
            "Click 'Save changes'",
        ],
        "cli_command": "aws s3api put-bucket-encryption --bucket BUCKET_NAME --server-side-encryption-configuration '{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"AES256\"}}]}'",
        "best_practice": "Enable SSE-KMS for sensitive data to get audit trails of key usage. Use SSE-S3 as a minimum for all buckets.",
    },
    "RDP Port 3389 Open to the Internet": {
        "explanation": "The security group allows RDP connections from any IP address. This exposes Windows instances to brute-force and exploitation attacks.",
        "why_dangerous": "RDP has historically been a major attack vector. Vulnerabilities like BlueKeep allow unauthenticated remote code execution. Bots constantly scan for open RDP ports.",
        "business_impact": "Server compromise, ransomware (RDP is the #1 ransomware entry point), data theft, and lateral movement.",
        "fix_steps": [
            "Restrict RDP source to specific IP addresses only",
            "Use AWS Systems Manager Fleet Manager for RDP without opening port 3389",
            "Consider using a VPN or bastion host",
            "Enable Network Level Authentication (NLA)",
        ],
        "cli_command": "aws ec2 revoke-security-group-ingress --group-id SG_ID --protocol tcp --port 3389 --cidr 0.0.0.0/0",
        "best_practice": "Never expose RDP to the internet. Use AWS Systems Manager Session Manager or a VPN.",
    },
}

DEFAULT_EXPLANATION = {
    "explanation": "This security misconfiguration exposes your AWS environment to potential threats.",
    "why_dangerous": "Misconfigurations are the leading cause of cloud security breaches.",
    "business_impact": "Potential data breach, compliance violations, and financial losses.",
    "fix_steps": [
        "Review the AWS Security Best Practices documentation",
        "Apply the principle of least privilege",
        "Enable AWS Security Hub for continuous monitoring",
        "Review and remediate the specific misconfiguration",
    ],
    "cli_command": "aws securityhub get-findings",
    "best_practice": "Regularly audit your AWS configuration using AWS Security Hub and AWS Config.",
}

PLACEHOLDER_API_KEYS = {
    "your-gemini-api-key-here",
    "your-openai-api-key-here",
}
_provider_unavailable = False


async def generate_ai_explanation(finding: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI explanation for a finding.
    Tries Gemini → OpenAI → built-in fallback.
    """
    issue_title = finding.get("issue_title", "")
    description = finding.get("description", "")
    service = finding.get("service", "")
    severity = finding.get("severity", "")

    # Try AI providers
    global _provider_unavailable

    if (not _provider_unavailable and settings.AI_PROVIDER == "gemini"
            and settings.GEMINI_API_KEY not in ("", *PLACEHOLDER_API_KEYS)):
        result = await _gemini_explain(issue_title, description, service, severity)
        if result:
            return result
        _provider_unavailable = True

    if (not _provider_unavailable and settings.AI_PROVIDER == "openai"
            and settings.OPENAI_API_KEY not in ("", *PLACEHOLDER_API_KEYS)):
        result = await _openai_explain(issue_title, description, service, severity)
        if result:
            return result
        _provider_unavailable = True

    # Built-in fallback
    return FALLBACK_EXPLANATIONS.get(issue_title, DEFAULT_EXPLANATION)


async def _gemini_explain(title: str, description: str, service: str, severity: str) -> Optional[Dict]:
    """Call Google Gemini API for explanation."""
    try:
        import google.generativeai as genai
        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = _build_prompt(title, description, service, severity)
        response = await asyncio.to_thread(model.generate_content, prompt)
        return _parse_ai_response(response.text)
    except Exception as e:
        print(f"[AI] Gemini error: {e}")
        return None


async def _openai_explain(title: str, description: str, service: str, severity: str) -> Optional[Dict]:
    """Call OpenAI API for explanation."""
    try:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        prompt = _build_prompt(title, description, service, severity)
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a cloud security expert. Respond in JSON format."},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        import json
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"[AI] OpenAI error: {e}")
        return None


def _build_prompt(title: str, description: str, service: str, severity: str) -> str:
    return f"""
You are a cloud security expert. Analyze this AWS security finding and respond with a JSON object.

Finding:
- Title: {title}
- Service: {service.upper()}
- Severity: {severity}
- Description: {description}

Respond with this exact JSON structure:
{{
  "explanation": "Simple 2-3 sentence explanation of what this issue is",
  "why_dangerous": "Why this is dangerous (2-3 sentences)",
  "business_impact": "Business impact if exploited (2-3 sentences)",
  "fix_steps": ["Step 1", "Step 2", "Step 3", "Step 4"],
  "cli_command": "AWS CLI command to fix this issue",
  "best_practice": "AWS best practice recommendation (1-2 sentences)"
}}
"""


def _parse_ai_response(text: str) -> Optional[Dict]:
    """Parse JSON from AI response text."""
    import json
    import re
    try:
        # Try direct parse
        return json.loads(text)
    except Exception:
        # Extract JSON block
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    return None
