import smtplib
import logging
from email.mime.text import MIMEText

from config.settings import settings
from models.schemas import ReplenishmentAction, MaterialHealth

logger = logging.getLogger(__name__)

def should_notify(health_status: str) -> bool:
    return health_status in settings.notify_statuses

def _send_email(to_email: str, subject: str, body_text: str, is_html: bool = False) -> bool:
    msg = MIMEText(body_text, "html" if is_html else "plain")
    msg["Subject"] = subject
    msg["From"] = settings.notify_email_from
    msg["To"] = to_email

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.starttls()
        server.login(settings.smtp_username, settings.smtp_password)
        server.sendmail(settings.notify_email_from, [to_email], msg.as_string())
    return True

def send_replenishment_notification(action: ReplenishmentAction, material_health: MaterialHealth) -> bool:
    if not all([settings.notify_email_to, settings.notify_email_from, settings.smtp_username, settings.smtp_password]):
        logger.warning("SMTP configuration is incomplete. Skipping email notification.")
        return False

    approve_link = f"{settings.api_base_url}/api/replenishment/actions/{action.action_id}/approve?token={action.approval_token}"
    reject_link = f"{settings.api_base_url}/api/replenishment/actions/{action.action_id}/reject?token={action.approval_token}"

    subject = f"[{action.material_id}] [{action.plant_id}] ACTION REQUIRED: Material Shortage"
    
    html_body = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <h2>Replenishment Action Required</h2>
        <p>A material shortage has been detected and an automated action has been proposed.</p>
        
        <table style="border-collapse: collapse; width: 100%; max-width: 600px; margin-bottom: 20px;">
          <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Action ID:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{action.action_id}</td></tr>
          <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Material ID:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{action.material_id}</td></tr>
          <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Plant ID:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{action.plant_id}</td></tr>
          <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Recommended Action:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{action.recommended_action}</td></tr>
          <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Recommended Qty:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{action.recommended_qty}</td></tr>
          <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Suggested Supplier:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{action.suggested_supplier_id}</td></tr>
          <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Rationale:</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{action.rationale}</td></tr>
        </table>

        <div style="margin-top: 30px; margin-bottom: 30px;">
          <a href="{approve_link}" style="background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; margin-right: 15px; display: inline-block;">Approve Action</a>
          <a href="{reject_link}" style="background-color: #ef4444; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold; display: inline-block;">Reject Action</a>
        </div>
        
        <p style="font-size: 13px; color: #666; border-top: 1px solid #eee; padding-top: 15px;">
          Clicking a button above will instantly process your decision and redirect you to the Actions Workflow dashboard.<br/>
          You can also <a href="{settings.frontend_base_url}/actions">view this directly in the portal</a>.
        </p>
      </body>
    </html>
    """

    try:
        _send_email(settings.notify_email_to, subject, html_body, is_html=True)
        logger.info(f"Successfully sent notification for action {action.action_id}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email notification for action {action.action_id}", exc_info=True)
        raise e
