"""Module defining unit tests for the email-related tasks."""

import smtplib
from unittest import mock

import pytest

from app.account.otp.tasks.email import (
    HTML_TEMPLATE_PATH,
    format_email_html,
    load_html_template,
    send_otp_email,
)
from tests.conftest import settings


def test_load_html_template_success() -> None:
    """Verify that load_html_template correctly loads an HTML file's content."""
    # Arrange
    mock_html = "<p>HTML `p` tag for testing</p>"
    dummy_path = "dummy/path.html"
    with mock.patch(
        "builtins.open", new_callable=mock.mock_open, read_data=mock_html
    ) as mock_open:
        # Act
        actual_result = load_html_template(template_path=dummy_path)

        # Assert
        expected_result = mock_html
        assert actual_result == expected_result

        mock_open.assert_called_once_with(dummy_path)


def test_lod_html_template_exception_raised_failed() -> None:
    """Verify that load_html_template raises FileNotFoundError for a missing file."""
    # Arrange
    dummy_path = "dummy/path.html"
    with mock.patch(
        "builtins.open", side_effect=FileNotFoundError("test error")
    ) as mock_open:
        # Act & Assert
        with pytest.raises(FileNotFoundError, match="test error"):
            load_html_template(dummy_path)

        mock_open.assert_called_once_with(dummy_path)


def test_format_email_html_success() -> None:
    """Verify that format_email_html replaces placeholders with OTP values."""
    # Arrange
    otp = "123456"
    dummy_path = "dummy/path.html"
    mock_html = "<html>{{otp}} expires in {{otp_expiration_time}} minutes</html>"

    with mock.patch(
        "app.account.otp.tasks.email.load_html_template", return_value=mock_html
    ) as mock_load_html_template:
        # Act
        actual_result = format_email_html(template_path=dummy_path, otp=otp)

        # Assert
        expected_result = mock_html.replace("{{otp}}", otp).replace(
            "{{otp_expiration_time}}", str(settings.otp_ttl // 60)
        )
        assert actual_result == expected_result

        mock_load_html_template.assert_called_once_with(template_path=dummy_path)


def test_send_otp_email_success() -> None:
    """Verify that send_otp_email sends an OTP email with formatted HTML content."""
    # Arranges
    mock_html = "<html>Formatted HTML</html>"
    mock_smtp = mock.MagicMock(spec_set=smtplib.SMTP)
    mock_ssl_context = mock.MagicMock()

    email = "test@test.com"
    otp = "123456"

    with mock.patch(
        "app.account.otp.tasks.email.format_email_html", return_value=mock_html
    ) as mock_format_email_html, mock.patch(
        "app.account.otp.tasks.email.smtplib.SMTP", new=mock_smtp
    ), mock.patch("app.account.otp.tasks.email.ssl", autospec=True) as mock_ssl:
        mock_smtp.return_value.__enter__.return_value = mock_smtp
        mock_ssl.create_default_context.return_value = mock_ssl_context

        # Act
        send_otp_email(to_email=email, otp=otp)

        # Assert
        mock_format_email_html.assert_called_once_with(
            template_path=HTML_TEMPLATE_PATH, otp=otp
        )

        mock_smtp.assert_called_once_with(settings.email_host, settings.email_port)
        mock_ssl.create_default_context.assert_called_once_with()
        mock_smtp.starttls.assert_called_once_with(context=mock_ssl_context)
        mock_smtp.login.assert_called_once_with(
            settings.email_username, settings.email_password
        )
        mock_smtp.sendmail.assert_called_once()

        assert mock_smtp.sendmail.call_args[0][0] == settings.email_host
        assert mock_smtp.sendmail.call_args[0][1] == [email]
        assert mock_html in mock_smtp.sendmail.call_args[0][2]


@pytest.mark.parametrize("exc", [smtplib.SMTPException, ConnectionRefusedError])
def test_send_otp_email_retry(
    exc: smtplib.SMTPException | ConnectionRefusedError,
) -> None:
    """Verify retries on `SMTPException` or `ConnectionRefusedError`."""
    # Arranges
    mock_html = "<html>Formatted HTML</html>"
    mock_smtp = mock.MagicMock(spec_set=smtplib.SMTP)
    mock_smtp.sendmail.side_effect = exc
    mock_ssl_context = mock.MagicMock()

    email = "test@test.com"
    otp = "123456"

    with mock.patch(
        "app.account.otp.tasks.email.format_email_html", return_value=mock_html
    ) as mock_format_email_html, mock.patch(
        "app.account.otp.tasks.email.smtplib.SMTP", new=mock_smtp
    ), mock.patch(
        "app.account.otp.tasks.email.ssl", autospec=True
    ) as mock_ssl, mock.patch(
        "app.account.otp.tasks.email.send_otp_email.retry"
    ) as mock_retry:
        mock_smtp.return_value.__enter__.return_value = mock_smtp
        mock_ssl.create_default_context.return_value = mock_ssl_context

        # Act
        send_otp_email(to_email=email, otp=otp)

        # Assert
        mock_format_email_html.assert_called_once_with(
            template_path=HTML_TEMPLATE_PATH, otp=otp
        )

        mock_smtp.assert_called_once_with(settings.email_host, settings.email_port)
        mock_ssl.create_default_context.assert_called_once_with()
        mock_smtp.starttls.assert_called_once_with(context=mock_ssl_context)
        mock_smtp.login.assert_called_once_with(
            settings.email_username, settings.email_password
        )

        mock_retry.assert_called_once_with(exc=mock.ANY, countdown=60)
        actual_exception_class = mock_retry.call_args[1]["exc"].__class__
        expected_exception_class = exc
        assert actual_exception_class == expected_exception_class


def test_send_otp_email_unknown_exception() -> None:
    """Verify that send_otp_email raises an exception for unexpected errors."""
    # Arranges
    mock_html = "<html>Formatted HTML</html>"
    mock_smtp = mock.MagicMock(spec_set=smtplib.SMTP)
    mock_smtp.sendmail.side_effect = Exception("test error")
    mock_ssl_context = mock.MagicMock()

    email = "test@test.com"
    otp = "123456"

    with mock.patch(
        "app.account.otp.tasks.email.format_email_html", return_value=mock_html
    ) as mock_format_email_html, mock.patch(
        "app.account.otp.tasks.email.smtplib.SMTP", new=mock_smtp
    ), mock.patch("app.account.otp.tasks.email.ssl", autospec=True) as mock_ssl:
        mock_smtp.return_value.__enter__.return_value = mock_smtp
        mock_ssl.create_default_context.return_value = mock_ssl_context

        # Act
        with pytest.raises(Exception, match="test error"):
            send_otp_email(to_email=email, otp=otp)

        # Assert
        mock_format_email_html.assert_called_once_with(
            template_path=HTML_TEMPLATE_PATH, otp=otp
        )

        mock_smtp.assert_called_once_with(settings.email_host, settings.email_port)
        mock_ssl.create_default_context.assert_called_once_with()
        mock_smtp.starttls.assert_called_once_with(context=mock_ssl_context)
        mock_smtp.login.assert_called_once_with(
            settings.email_username, settings.email_password
        )
