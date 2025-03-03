"""Module defining celery tasks related to email sending."""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import TYPE_CHECKING, Any

from celery import Task

if TYPE_CHECKING:
    AnyTask = Task[Any, Any]
else:
    AnyTask = Task

from config.base import celery_app, logger, settings

HTML_TEMPLATE_PATH = "app/account/otp/templates/otp_email.html"


def load_html_template(template_path: str) -> str:
    """
    Load an HTML template from a file.

    Parameters
    ----------
    template_path : str
        Path to the HTML template file.

    Returns
    -------
    str
        The content of the HTML template as a string.

    Raises
    ------
    Exception
        If an error occurs while reading the file.
    """
    try:
        with open(template_path) as template_file:
            return template_file.read()
    except Exception:
        logger.error(
            "Unexpected error while loading html template at: %s", template_path
        )
        raise


def format_email_html(template_path: str, otp: str) -> str:
    """
    Format an HTML email template by inserting the OTP and expiration time.

    Parameters
    ----------
    template_path : str
        Path to the HTML template file.
    otp : str
        One-time password (OTP) to be inserted into the template.

    Returns
    -------
    str
        The formatted HTML content with the OTP and expiration time replaced.
    """
    unformatted_html = load_html_template(template_path=template_path)
    formatted_html = unformatted_html.replace("{{otp}}", otp).replace(
        "{{otp_expiration_time}}", str(settings.otp_ttl // 60)
    )
    return formatted_html


@celery_app.task(
    bind=True,
    max_retries=2,
    default_retry_delay=180,
    ignore_result=True,
    rate_limit="500/m",
)
def send_otp_email(self: AnyTask, to_email: str, otp: str) -> None:
    """
    Send an OTP email using an SMTP server.

    Parameters
    ----------
    self : Task
        The Celery task instance.
    to_email : str
        Recipient's email address.
    otp : str
        One-time password (OTP) to be sent in the email.

    Raises
    ------
    Exception
        If an unexpected error occurs while sending the email.
    """
    task_id = self.request.id

    subject = "Your verification code (Rental House FastAPI)"
    plain_text = f"Your verification code is: {otp}"

    email_html = format_email_html(template_path=HTML_TEMPLATE_PATH, otp=otp)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = settings.email_host
    msg["To"] = to_email
    part1 = MIMEText(plain_text, "plain")
    part2 = MIMEText(email_html, "html")
    msg.attach(part1)
    msg.attach(part2)

    try:
        with smtplib.SMTP(settings.email_host, settings.email_port) as smtp_server:
            context = ssl.create_default_context()
            smtp_server.starttls(context=context)
            smtp_server.login(settings.email_username, settings.email_password)

            logger.debug(
                "Task %s: sending email subject: %s to: %s", task_id, subject, to_email
            )
            smtp_server.sendmail(msg["From"], [to_email], msg.as_string())
    except (smtplib.SMTPException, ConnectionRefusedError) as exc:
        max_retries = self.max_retries if self.max_retries is not None else 0
        logger.warning(
            "Task %s: failed to send email to %s. Attempt %s of %s. Error: %s",
            task_id,
            to_email,
            self.request.retries + 1,
            max_retries,
            str(exc),
        )
        self.retry(exc=exc, countdown=60 * (2**self.request.retries))
    except Exception:
        logger.error(
            "Task %s: unexpected error occurred sending email to: %s", task_id, to_email
        )
        raise
