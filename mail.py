#from email import encoders
#from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# from os import login_tty
import smtplib
from jinja2 import Template

SMTP_SERVER_HOST= "localhost"
SMTP_SERVER_PORT= 1025
SENDER_ADDRESS = "rishikasingh@gmail.com"
SENDER_PASSWORD = "pass"

def send_email(to_address, subject, message):
    msg=MIMEMultipart()
    msg["From"] = SENDER_ADDRESS
    msg["To"] = to_address
    msg["Subject"] = subject
    msg.attach(MIMEText(message,"html"))
    
    s = smtplib.SMTP(host=SMTP_SERVER_HOST, port=SMTP_SERVER_PORT)
    # s.starttls()
    s.login(SENDER_ADDRESS,SENDER_PASSWORD)
    s.send_message(msg)
    s.quit()
    return True 

    
def main():
    # name = "Aditya"
    # with open("c:/Users/Upender Singh/Desktop/kanban/project/public/mail.html") as temp:
    #     template=Template(temp.read())
    #     message = template.render(data= name)
    #for user in new_users:
        #send_email(user["email"])
        send_email("sample@gmail.com", subject="Test mail", message = "hi")


if __name__=="__main__":
    main()

