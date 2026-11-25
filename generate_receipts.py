import os
from fpdf import FPDF
from cloudinary_service import upload_pdf

def create_pdf(payment_data, transaction_code):
    try:
        os.makedirs("receipts", exist_ok=True)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, txt=payment_data, align="C")

        file_path = f"receipts/{transaction_code}.pdf"
        pdf.output(file_path)

        print("Receipt created successfully")

        receipt_url = upload_pdf(transaction_code)

        return receipt_url

    except Exception as e:
        print("Receipt generation failed:", str(e))
        return None