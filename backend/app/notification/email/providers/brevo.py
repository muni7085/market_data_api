from app.notification.email.email_provider import EmailProvider
import os
import brevo_python
from brevo_python.rest import ApiException


class BrevoEmailProvider(EmailProvider):
    def __init__(self):
        self.configuration = brevo_python.Configuration()
        self.configuration.api_key["api-key"] = os.environ.get("BREVO_API_KEY")
        self.sender_name = os.environ.get("BREVO_SENDER_NAME")
        self.sender_email = os.environ.get("BREVO_SENDER_EMAIL")

    def send_notification(
        self, code: str, recipient_email: str, recipient_name: str
    ) -> None:
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
            # Send a transactional email
            api_response = api_instance.send_transac_email(send_smtp_email)
            return api_response

        except ApiException as e:
            print(
                "Exception when calling TransactionalEmailsApi->send_transac_email: %s\n"
                % e
            )
