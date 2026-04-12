"""Email notification service using Resend."""

import logging
from typing import Literal

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

RESEND_API_URL = "https://api.resend.com/emails"


async def send_email(
    to: str,
    subject: str,
    html_body: str,
) -> dict:
    """Send a single email via Resend API. Returns the Resend response dict."""
    settings = get_settings()
    api_key = settings.RESEND_API_KEY

    if not api_key:
        logger.error("RESEND_API_KEY not set — skipping email to %s", to)
        raise RuntimeError("Email service not configured (RESEND_API_KEY missing)")

    payload = {
        "from": settings.EMAIL_FROM,
        "to": [to],
        "subject": subject,
        "html": html_body,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.post(
            RESEND_API_URL,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    if resp.status_code >= 400:
        logger.error("Resend API error %d: %s", resp.status_code, resp.text)
        raise RuntimeError(f"Email delivery failed: {resp.text}")

    data = resp.json()
    logger.info("Email sent to %s — id=%s", to, data.get("id"))
    return data


def build_shortlisted_email(
    candidate_name: str,
    job_title: str,
    custom_message: str | None = None,
) -> tuple[str, str]:
    """Build subject and HTML body for a shortlisted notification."""
    subject = f"Great news! You've been shortlisted — {job_title}"

    greeting = candidate_name or "there"
    message_block = custom_message or (
        "After careful review of your application, we are pleased to inform you that "
        "you have been <strong>shortlisted</strong> for the next stage of our selection process. "
        "A member of our hiring team will be reaching out to you shortly to schedule a conversation."
    )

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 32px 24px; color: #1e293b;">
      <div style="text-align: center; margin-bottom: 24px;">
        <div style="display: inline-block; width: 40px; height: 40px; line-height: 40px; border-radius: 10px; background: #4f46e5; color: white; font-weight: bold; font-size: 18px;">R</div>
      </div>
      <h2 style="color: #1e293b; margin-bottom: 8px;">Congratulations, {greeting}!</h2>
      <p style="color: #475569; line-height: 1.6;">{message_block}</p>
      <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 16px; border-radius: 8px; margin: 24px 0;">
        <strong style="color: #166534;">Position:</strong> {job_title}
      </div>
      <p style="color: #475569; line-height: 1.6;">We look forward to speaking with you soon.</p>
      <p style="color: #94a3b8; font-size: 13px; margin-top: 32px;">— RAX Resume Analysis eXpert</p>
    </div>
    """
    return subject, html


def build_rejected_email(
    candidate_name: str,
    job_title: str,
    gaps: list | None = None,
    strengths: list | None = None,
    custom_message: str | None = None,
) -> tuple[str, str]:
    """Build subject and HTML body for a rejection notification with constructive feedback."""
    subject = f"Update on your application — {job_title}"

    greeting = candidate_name or "there"
    message_block = custom_message or (
        "Thank you for your interest and the time you invested in applying. "
        "After careful evaluation, we have decided to move forward with other candidates "
        "whose experience more closely matches the current requirements."
    )

    # Build feedback sections from analysis data
    gaps_html = ""
    if gaps and len(gaps) > 0:
        top_gaps = gaps[:3]
        items = "".join(f"<li style='margin-bottom: 6px; color: #475569;'>{g}</li>" for g in top_gaps)
        gaps_html = f"""
        <div style="background: #fff7ed; border-left: 4px solid #f97316; padding: 16px; border-radius: 8px; margin: 16px 0;">
          <strong style="color: #9a3412;">Areas for growth:</strong>
          <ul style="margin: 8px 0 0 0; padding-left: 20px;">{items}</ul>
        </div>
        """

    strengths_html = ""
    if strengths and len(strengths) > 0:
        top_strengths = strengths[:3]
        items = "".join(f"<li style='margin-bottom: 6px; color: #475569;'>{s}</li>" for s in top_strengths)
        strengths_html = f"""
        <div style="background: #f0fdf4; border-left: 4px solid #22c55e; padding: 16px; border-radius: 8px; margin: 16px 0;">
          <strong style="color: #166534;">What stood out:</strong>
          <ul style="margin: 8px 0 0 0; padding-left: 20px;">{items}</ul>
        </div>
        """

    html = f"""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 600px; margin: 0 auto; padding: 32px 24px; color: #1e293b;">
      <div style="text-align: center; margin-bottom: 24px;">
        <div style="display: inline-block; width: 40px; height: 40px; line-height: 40px; border-radius: 10px; background: #4f46e5; color: white; font-weight: bold; font-size: 18px;">R</div>
      </div>
      <h2 style="color: #1e293b; margin-bottom: 8px;">Hi {greeting},</h2>
      <p style="color: #475569; line-height: 1.6;">{message_block}</p>
      <div style="background: #f8fafc; border-left: 4px solid #6366f1; padding: 16px; border-radius: 8px; margin: 24px 0;">
        <strong style="color: #4338ca;">Position:</strong> {job_title}
      </div>
      {strengths_html}
      {gaps_html}
      <p style="color: #475569; line-height: 1.6;">
        We encourage you to continue developing in these areas. We wish you the very best in your career journey, 
        and we hope you'll consider applying for future opportunities with us.
      </p>
      <p style="color: #94a3b8; font-size: 13px; margin-top: 32px;">— RAX Resume Analysis eXpert</p>
    </div>
    """
    return subject, html
