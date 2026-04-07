import smtplib
import os
from dotenv import load_dotenv
from email.message import EmailMessage

def sendEmail(pdf_path):
  
    load_dotenv()
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")

    recipients = ["vaihing00@gmail.com", "vgsk1504@gmail.com"]


    msg = EmailMessage()
    msg['From'] = EMAIL_USER
    msg['To'] = ", ".join(recipients)
    msg['Subject'] = "Monthly Sales Report"


    body_text = "Hello,\n\nPlease find attached the monthly sales report.\n\nBest regards,"
    msg.set_content(body_text)

  
    with open(pdf_path, "rb") as f:
        file_data = f.read()
        file_name = os.path.basename(pdf_path)
        msg.add_attachment(file_data, maintype='application', subtype='pdf', filename=file_name)

  
    print("Sending Email.............")
    print("Email will be sent to:", ", ".join(recipients))
    print("Email subject:", msg['Subject'])
    print("Email attachment:", file_name)


    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print("✅ Email sent successfully with PDF attachment!")
    except Exception as e:
        print("❌ Error sending email:", e)