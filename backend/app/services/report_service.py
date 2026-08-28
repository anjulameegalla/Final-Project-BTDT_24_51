"""
CloudGuard AI – PDF Report Generator
Generates professional security audit reports using ReportLab.
"""

import os
import io
from datetime import datetime
from typing import Dict, Any, List

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, PageBreak,
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from app.config import settings

# ── Color Palette ─────────────────────────────────────────────────────────────
DARK_BLUE   = colors.HexColor("#1e293b")
ACCENT_BLUE = colors.HexColor("#3b82f6")
CRITICAL    = colors.HexColor("#dc2626")
HIGH        = colors.HexColor("#ea580c")
MEDIUM      = colors.HexColor("#d97706")
LOW         = colors.HexColor("#16a34a")
LIGHT_GRAY  = colors.HexColor("#f1f5f9")
MID_GRAY    = colors.HexColor("#94a3b8")

SEVERITY_COLORS = {
    "Critical": CRITICAL,
    "High": HIGH,
    "Medium": MEDIUM,
    "Low": LOW,
}


def _severity_color(sev: str):
    return SEVERITY_COLORS.get(sev, MID_GRAY)


def generate_pdf_report(scan_data: Dict[str, Any], user_name: str = "User") -> bytes:
    """
    Generate a PDF security report from scan data.
    Returns PDF bytes.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title="CloudGuard AI Security Report",
    )

    styles = getSampleStyleSheet()
    story = []

    # ── Custom Styles ─────────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=26,
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=12,
        textColor=MID_GRAY,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading1"],
        fontSize=14,
        textColor=DARK_BLUE,
        spaceBefore=16,
        spaceAfter=8,
        borderPad=4,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        textColor=colors.HexColor("#334155"),
        spaceAfter=6,
        leading=16,
    )
    finding_title_style = ParagraphStyle(
        "FindingTitle",
        parent=styles["Normal"],
        fontSize=11,
        textColor=DARK_BLUE,
        fontName="Helvetica-Bold",
        spaceAfter=4,
    )

    # ── Cover Page ────────────────────────────────────────────────────────────
    # Header banner
    header_data = [[Paragraph("🛡️ CloudGuard AI", title_style)]]
    header_table = Table(header_data, colWidths=[17 * cm])
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), DARK_BLUE),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("ROUNDEDCORNERS", [8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("AWS Cloud Security Audit Report", subtitle_style))
    story.append(Spacer(1, 0.3 * cm))

    # Meta info table
    scan_date = scan_data.get("scan_date", datetime.utcnow())
    if isinstance(scan_date, str):
        scan_date = datetime.fromisoformat(scan_date.replace("Z", "+00:00"))

    meta_data = [
        ["Account / Project", scan_data.get("account_name", "CloudGuard Demo")],
        ["Report Generated", datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")],
        ["Scan Date", scan_date.strftime("%B %d, %Y at %H:%M UTC")],
        ["Prepared For", user_name],
        ["Scan ID", str(scan_data.get("id", "N/A"))],
    ]
    meta_table = Table(meta_data, colWidths=[5 * cm, 12 * cm])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT_GRAY]),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 0.8 * cm))

    # ── Security Score Card ───────────────────────────────────────────────────
    score = scan_data.get("overall_score", 0)
    risk_level = scan_data.get("risk_level", "Unknown")
    score_color = (
        LOW if score >= 90 else
        MEDIUM if score >= 70 else
        HIGH if score >= 40 else
        CRITICAL
    )

    story.append(Paragraph("Overall Security Score", section_style))
    score_data = [[
        Paragraph(f'<font size="36" color="{score_color.hexval()}">{score}</font><font size="14">/100</font>', ParagraphStyle("Score", alignment=TA_CENTER)),
        Paragraph(f'<font size="16" color="{score_color.hexval()}"><b>{risk_level}</b></font>', ParagraphStyle("Risk", alignment=TA_CENTER)),
    ]]
    score_table = Table(score_data, colWidths=[8.5 * cm, 8.5 * cm])
    score_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 20),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 20),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("ROUNDEDCORNERS", [6]),
    ]))
    story.append(score_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Summary Statistics ────────────────────────────────────────────────────
    story.append(Paragraph("Findings Summary", section_style))
    summary_data = [
        ["Total Issues", "Critical", "High", "Medium", "Low"],
        [
            str(scan_data.get("total_issues", 0)),
            str(scan_data.get("critical_count", 0)),
            str(scan_data.get("high_count", 0)),
            str(scan_data.get("medium_count", 0)),
            str(scan_data.get("low_count", 0)),
        ],
    ]
    summary_table = Table(summary_data, colWidths=[3.4 * cm] * 5)
    summary_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (1, 1), (1, 1), colors.HexColor("#fee2e2")),
        ("BACKGROUND", (2, 1), (2, 1), colors.HexColor("#ffedd5")),
        ("BACKGROUND", (3, 1), (3, 1), colors.HexColor("#fef9c3")),
        ("BACKGROUND", (4, 1), (4, 1), colors.HexColor("#dcfce7")),
        ("TEXTCOLOR", (1, 1), (1, 1), CRITICAL),
        ("TEXTCOLOR", (2, 1), (2, 1), HIGH),
        ("TEXTCOLOR", (3, 1), (3, 1), MEDIUM),
        ("TEXTCOLOR", (4, 1), (4, 1), LOW),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 1), (-1, 1), 16),
        ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
    ]))
    story.append(summary_table)
    story.append(Spacer(1, 0.5 * cm))

    # ── Service Scores ────────────────────────────────────────────────────────
    service_scores = scan_data.get("service_scores", {})
    if service_scores:
        story.append(Paragraph("Service-wise Security Scores", section_style))
        svc_data = [["Service", "Score", "Status"]]
        for svc, svc_score in service_scores.items():
            status = "Secure" if svc_score >= 90 else "Moderate" if svc_score >= 70 else "High Risk" if svc_score >= 40 else "Critical"
            svc_data.append([svc.upper(), f"{svc_score}/100", status])
        svc_table = Table(svc_data, colWidths=[5 * cm, 4 * cm, 8 * cm])
        svc_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 0), (1, -1), "CENTER"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_GRAY]),
            ("GRID", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ]))
        story.append(svc_table)
        story.append(Spacer(1, 0.5 * cm))

    # ── Detailed Findings ─────────────────────────────────────────────────────
    findings = scan_data.get("findings", [])
    if findings:
        story.append(PageBreak())
        story.append(Paragraph("Detailed Security Findings", section_style))
        story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE))
        story.append(Spacer(1, 0.3 * cm))

        for i, finding in enumerate(findings, 1):
            sev = finding.get("severity", "Low")
            sev_color = _severity_color(sev)

            # Finding header
            header_row = [[
                Paragraph(f'<b>{i}. {finding.get("issue_title", "")}</b>', finding_title_style),
                Paragraph(
                    f'<font color="{sev_color.hexval()}"><b>{sev}</b></font>',
                    ParagraphStyle("SevBadge", alignment=TA_RIGHT, fontSize=11),
                ),
            ]]
            hdr_table = Table(header_row, colWidths=[13 * cm, 4 * cm])
            hdr_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GRAY),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (0, -1), 10),
                ("RIGHTPADDING", (-1, 0), (-1, -1), 10),
                ("LINEBELOW", (0, 0), (-1, -1), 2, sev_color),
            ]))
            story.append(hdr_table)

            # Details
            detail_data = [
                ["Service", finding.get("service", "").upper()],
                ["Resource", finding.get("resource_id", "")],
                ["Description", finding.get("description", "")],
            ]
            if finding.get("ai_explanation"):
                detail_data.append(["AI Explanation", finding["ai_explanation"]])
            if finding.get("recommendation"):
                detail_data.append(["Recommendation", finding["recommendation"]])

            detail_table = Table(
                [[Paragraph(k, ParagraphStyle("Key", fontName="Helvetica-Bold", fontSize=9, textColor=DARK_BLUE)),
                  Paragraph(str(v), body_style)] for k, v in detail_data],
                colWidths=[3.5 * cm, 13.5 * cm],
            )
            detail_table.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [colors.white, LIGHT_GRAY]),
                ("GRID", (0, 0), (-1, -1), 0.3, MID_GRAY),
            ]))
            story.append(detail_table)

            # Fix steps
            fix_steps = finding.get("fix_steps", [])
            if fix_steps:
                story.append(Paragraph("Remediation Steps:", ParagraphStyle(
                    "FixHeader", fontName="Helvetica-Bold", fontSize=10,
                    textColor=ACCENT_BLUE, spaceBefore=6, spaceAfter=4,
                )))
                for step_num, step in enumerate(fix_steps, 1):
                    story.append(Paragraph(
                        f"  {step_num}. {step}",
                        ParagraphStyle("Step", fontSize=9, textColor=colors.HexColor("#334155"),
                                       leftIndent=10, spaceAfter=3),
                    ))

            story.append(Spacer(1, 0.4 * cm))

    # ── Conclusion ────────────────────────────────────────────────────────────
    story.append(PageBreak())
    story.append(Paragraph("Conclusion & Recommendations", section_style))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE))
    story.append(Spacer(1, 0.3 * cm))

    conclusion_text = f"""
    This security audit identified <b>{scan_data.get('total_issues', 0)} issues</b> across your AWS environment,
    resulting in an overall security score of <b>{score}/100</b> ({risk_level}).
    <br/><br/>
    <b>Immediate Actions Required:</b><br/>
    • Remediate all Critical severity findings immediately<br/>
    • Address High severity findings within 24-48 hours<br/>
    • Plan remediation for Medium findings within 1-2 weeks<br/>
    • Schedule Low severity fixes in the next sprint<br/>
    <br/>
    <b>Long-term Recommendations:</b><br/>
    • Enable AWS Security Hub for continuous compliance monitoring<br/>
    • Implement AWS Config rules for automated compliance checks<br/>
    • Set up CloudWatch alarms for security-relevant events<br/>
    • Conduct quarterly security reviews<br/>
    • Train development teams on AWS security best practices<br/>
    • Implement Infrastructure as Code (IaC) security scanning<br/>
    """
    story.append(Paragraph(conclusion_text, body_style))

    # ── Footer ────────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1 * cm))
    footer_data = [[Paragraph(
        f'Generated by CloudGuard AI | {datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")} | Confidential',
        ParagraphStyle("Footer", fontSize=8, textColor=MID_GRAY, alignment=TA_CENTER),
    )]]
    footer_table = Table(footer_data, colWidths=[17 * cm])
    footer_table.setStyle(TableStyle([
        ("LINEABOVE", (0, 0), (-1, -1), 0.5, MID_GRAY),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(footer_table)

    # Build PDF
    doc.build(story)
    return buffer.getvalue()


async def save_report_to_disk(pdf_bytes: bytes, scan_id: str) -> str:
    """Save PDF to local reports directory. Returns file path."""
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)
    filename = f"cloudguard_report_{scan_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(reports_dir, filename)
    with open(filepath, "wb") as f:
        f.write(pdf_bytes)
    return filepath


async def upload_report_to_s3(pdf_bytes: bytes, filename: str) -> str:
    """Upload PDF to S3 and return the S3 URL."""
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError

    if settings.DEMO_MODE or not settings.REPORTS_S3_BUCKET:
        return ""

    try:
        from app.config import settings as cfg
        s3 = boto3.client("s3")
        key = f"reports/{filename}"
        s3.put_object(
            Bucket=cfg.REPORTS_S3_BUCKET,
            Key=key,
            Body=pdf_bytes,
            ContentType="application/pdf",
        )
        return f"https://{cfg.REPORTS_S3_BUCKET}.s3.amazonaws.com/{key}"
    except (ClientError, NoCredentialsError) as e:
        print(f"[Report] S3 upload error: {e}")
        return ""
