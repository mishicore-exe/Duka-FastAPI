import os,mailtrap

token = os.getenv("MAILTRAP_TOKEN")

def email(to, subject, message):
    if not token:
        raise ValueError("Mailtrap token is missing")

    mail = mailtrap.Mail(
        sender=mailtrap.Address(
            email="hello@demomailtrap.co",
            name="DUKA"
        ),
        to=[mailtrap.Address(email=to)],
        subject=subject,
        text=message,
        category="Payment Confirmation"
    )

    client = mailtrap.MailtrapClient(token=token)
    response = client.send(mail)

    print("Mailtrap response:", response)
    return response