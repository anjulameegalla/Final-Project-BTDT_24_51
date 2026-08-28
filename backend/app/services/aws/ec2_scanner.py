"""
CloudGuard AI – EC2 Security Scanner
Detects: SSH/RDP open to world, unrestricted inbound, public instances.
"""

from typing import List, Dict, Any
import boto3
from botocore.exceptions import ClientError


DEMO_FINDINGS = [
    {
        "service": "ec2",
        "resource_id": "sg-0abc123def456",
        "issue_title": "SSH Port 22 Open to the Internet",
        "severity": "High",
        "description": "Security group 'sg-0abc123def456' allows inbound SSH (port 22) from 0.0.0.0/0.",
    },
    {
        "service": "ec2",
        "resource_id": "sg-0xyz789ghi012",
        "issue_title": "RDP Port 3389 Open to the Internet",
        "severity": "High",
        "description": "Security group 'sg-0xyz789ghi012' allows inbound RDP (port 3389) from 0.0.0.0/0.",
    },
    {
        "service": "ec2",
        "resource_id": "sg-0all000traffic",
        "issue_title": "All Traffic Allowed From Internet",
        "severity": "Critical",
        "description": "Security group 'sg-0all000traffic' allows all inbound traffic from 0.0.0.0/0.",
    },
    {
        "service": "ec2",
        "resource_id": "i-0abc123456789def0",
        "issue_title": "EC2 Instance Has Public IP Address",
        "severity": "Medium",
        "description": "Instance 'i-0abc123456789def0' has a public IP address and may be directly reachable.",
    },
]


class EC2Scanner:
    def __init__(self, session: boto3.Session):
        self.ec2 = session.client("ec2")

    def scan(self) -> List[Dict[str, Any]]:
        findings = []
        findings.extend(self._check_security_groups())
        findings.extend(self._check_public_instances())
        return findings

    # ── Security Groups ──────────────────────────────────────────────────────
    def _check_security_groups(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            paginator = self.ec2.get_paginator("describe_security_groups")
            for page in paginator.paginate():
                for sg in page["SecurityGroups"]:
                    sg_id = sg["GroupId"]
                    sg_name = sg.get("GroupName", sg_id)
                    for rule in sg.get("IpPermissions", []):
                        from_port = rule.get("FromPort", -1)
                        to_port = rule.get("ToPort", -1)
                        ip_protocol = rule.get("IpProtocol", "")

                        for ip_range in rule.get("IpRanges", []) + rule.get("Ipv6Ranges", []):
                            cidr = ip_range.get("CidrIp") or ip_range.get("CidrIpv6", "")
                            if cidr not in ("0.0.0.0/0", "::/0"):
                                continue

                            # All traffic
                            if ip_protocol == "-1":
                                findings.append({
                                    "service": "ec2",
                                    "resource_id": sg_id,
                                    "issue_title": "All Traffic Allowed From Internet",
                                    "severity": "Critical",
                                    "description": f"Security group '{sg_name}' allows all inbound traffic from {cidr}.",
                                })
                            # SSH
                            elif from_port <= 22 <= to_port:
                                findings.append({
                                    "service": "ec2",
                                    "resource_id": sg_id,
                                    "issue_title": "SSH Port 22 Open to the Internet",
                                    "severity": "High",
                                    "description": f"Security group '{sg_name}' allows SSH (port 22) from {cidr}.",
                                })
                            # RDP
                            elif from_port <= 3389 <= to_port:
                                findings.append({
                                    "service": "ec2",
                                    "resource_id": sg_id,
                                    "issue_title": "RDP Port 3389 Open to the Internet",
                                    "severity": "High",
                                    "description": f"Security group '{sg_name}' allows RDP (port 3389) from {cidr}.",
                                })
                            # Any other wide-open port
                            elif from_port == 0 and to_port == 65535:
                                findings.append({
                                    "service": "ec2",
                                    "resource_id": sg_id,
                                    "issue_title": "Unrestricted Inbound Rule Detected",
                                    "severity": "High",
                                    "description": f"Security group '{sg_name}' allows all ports from {cidr}.",
                                })
        except ClientError as e:
            print(f"[EC2] Security group check error: {e}")
        return findings

    # ── Public Instances ─────────────────────────────────────────────────────
    def _check_public_instances(self) -> List[Dict[str, Any]]:
        findings = []
        try:
            paginator = self.ec2.get_paginator("describe_instances")
            for page in paginator.paginate():
                for reservation in page["Reservations"]:
                    for instance in reservation["Instances"]:
                        if instance.get("State", {}).get("Name") != "running":
                            continue
                        if instance.get("PublicIpAddress"):
                            instance_id = instance["InstanceId"]
                            findings.append({
                                "service": "ec2",
                                "resource_id": instance_id,
                                "issue_title": "EC2 Instance Has Public IP Address",
                                "severity": "Medium",
                                "description": f"Instance '{instance_id}' has public IP "
                                               f"{instance['PublicIpAddress']} and may be internet-reachable.",
                            })
        except ClientError as e:
            print(f"[EC2] Instance check error: {e}")
        return findings


def run_ec2_scan(session: boto3.Session, demo: bool = False) -> List[Dict[str, Any]]:
    """Entry point: run EC2 scan or return demo data."""
    if demo:
        return DEMO_FINDINGS
    scanner = EC2Scanner(session)
    return scanner.scan()
