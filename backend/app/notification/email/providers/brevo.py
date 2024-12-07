""" 
BrevoEmailProvider is used to send email notifications using the Brevo API.
"""

import os
from pathlib import Path

import brevo_python
from brevo_python.rest import ApiException
from omegaconf import DictConfig

from app.notification.email.email_provider import EmailProvider
from app.notification.provider import NotificationProvider
from app.utils.common.logger import get_logger

logger = get_logger(Path(__file__).name)


@NotificationProvider.register("brevo")
class BrevoEmailProvider(EmailProvider):
    """
    This class used to send verification code to the user's email using the Brevo API.

    Attributes:
    ----------
    sender_name: ``str``
        The name of the sender
    sender_email: ``str``
        The email of the sender
    brevo_api_key_name: ``str``
        The name of the environment variable that contains the Brevo API key
    """

    def __init__(self, sender_name: str, sender_email: str, brevo_api_key_name) -> None:

        self.configuration = brevo_python.Configuration()
        self.configuration.api_key["api-key"] = os.environ.get(brevo_api_key_name)
        self.sender_name = sender_name
        self.sender_email = sender_email

    def send_notification(
        self, code: str, recipient_email: str, recipient_name: str
    ) -> None:
        """
        This method is used to send the verification code to the user's email.

        Parameters:
        ----------
        code: ``str``
            The verification code that will be sent to the user's email
        recipient_email: ``str``
            The email address to which the verification code will be sent
        recipient_name: ``str``
            The name of the receiver
        """
        subject = "Verify your email"
        sender = {"name": self.sender_name, "email": self.sender_email}
        to = [{"email": recipient_email, "name": recipient_name}]
        html_content = f"<p>Your verification code is: <strong>{code}</strong></p>"

        api_instance = brevo_python.TransactionalEmailsApi(
            brevo_python.ApiClient(self.configuration)
        )
        send_smtp_email = brevo_python.SendSmtpEmail(
            sender=sender, to=to, subject=subject, html_content=html_content
        )

        try:
            api_instance.send_transac_email(send_smtp_email)

        except ApiException as e:
            logger.error(
                "Exception when calling TransactionalEmailsApi->send_transac_email: %s\n",
                e,
            )

    @classmethod
    def from_cfg(cls, cfg: DictConfig) -> "BrevoEmailProvider":
        """
        Initialize the BrevoEmailProvider from the configuration.
        """
        if cfg.get("sender_name") is None:
            raise ValueError("sender_name is required")

        if cfg.get("sender_email") is None:
            raise ValueError("sender_email is required")

        if cfg.get("brevo_api_key_name") is None:
            raise ValueError("brevo_api_key_name is required")

        return cls(
            sender_name=cfg.sender_name,
            sender_email=cfg.sender_email,
            brevo_api_key_name=cfg.brevo_api_key_name,
        )
