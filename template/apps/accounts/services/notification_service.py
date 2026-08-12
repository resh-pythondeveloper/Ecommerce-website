from utils.email.smtp import send_otp_email

class NotificationService:

    @staticmethod
    def send_email_otp(
        *,
        email: str,
        otp: str,
    ) -> None:

        send_otp_email(
            email=email,
            otp=otp,
        )
