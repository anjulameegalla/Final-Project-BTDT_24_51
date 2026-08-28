"""
CloudGuard AI – Risk Scoring Service
Calculates overall and per-service security scores based on finding severities.
"""

from typing import List, Dict, Any, Tuple

# Deduction points per severity
SEVERITY_DEDUCTIONS = {
    "Critical": 20,
    "High": 10,
    "Medium": 5,
    "Low": 2,
}

# Risk level thresholds
RISK_LEVELS = [
    (90, "Secure"),
    (70, "Moderate"),
    (40, "High Risk"),
    (0,  "Critical"),
]


def calculate_score(findings: List[Dict[str, Any]]) -> Tuple[int, str]:
    """
    Calculate overall security score (0-100) and risk level.
    Returns (score, risk_level).
    """
    score = 100
    for finding in findings:
        severity = finding.get("severity", "Low")
        score -= SEVERITY_DEDUCTIONS.get(severity, 0)
    score = max(0, score)

    risk_level = "Critical"
    for threshold, label in RISK_LEVELS:
        if score >= threshold:
            risk_level = label
            break

    return score, risk_level


def calculate_service_scores(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculate per-service scores (IAM, S3, EC2, CloudTrail).
    Each service starts at 100 and deductions are applied independently.
    """
    services = ["iam", "s3", "ec2", "cloudtrail"]
    service_findings: Dict[str, List] = {s: [] for s in services}

    for finding in findings:
        svc = finding.get("service", "").lower()
        if svc in service_findings:
            service_findings[svc].append(finding)

    scores = {}
    for svc, svc_findings in service_findings.items():
        score, _ = calculate_score(svc_findings)
        scores[svc] = score

    return scores


def count_by_severity(findings: List[Dict[str, Any]]) -> Dict[str, int]:
    """Return counts grouped by severity."""
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for finding in findings:
        sev = finding.get("severity", "Low")
        if sev in counts:
            counts[sev] += 1
    return counts
