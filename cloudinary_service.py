import cloudinary
import cloudinary.uploader
import os
from dotenv import load_dotenv
from send_email import email

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

print("Cloudinary configuration successful")

def upload_pdf(transaction_code, customer_email=None):
    try:
        file_path = f"receipts/{transaction_code}.pdf"

        if not os.path.exists(file_path):
            raise FileNotFoundError("Receipt PDF not found")

        upload = cloudinary.uploader.upload(
            file_path,
            resource_type="raw"
        )

        receipt_url = upload["secure_url"]

        print("Successful Cloudinary upload")
        print(receipt_url)

        if customer_email:
            try:
                email(
                    customer_email,
                    "Successful Payment",
                    f"Thank you, we have received your payment.\n\nReceipt: {receipt_url}"
                )
            except Exception as e:
                print("EMAIL ERROR:", str(e))

        return receipt_url

    except Exception as e:
        print("Upload failed:", str(e))
        return None