import smtplib
import os
from email.mime.text import MIMEText
from datetime import datetime
from pymongo import MongoClient


EMAIL_PASSWORD = os.environ.get("LIBRARY_APP_PASSWORD")

client = MongoClient("mongodb://localhost:27017/")
db = client["library_db"]
trans_col = db["transactions"]


def send_overdue_emails():
    now = datetime.utcnow()
    # Find all borrow transactions that are overdue and not yet returned
    overdue = trans_col.find({
        "action": "borrow",
        "due_date": {"$lt": now}
    })

    for rec in overdue:
        # Check that there is no matching 'return' action for the same book & user
        returned = trans_col.find_one({
            "action": "return",
            "book_id": rec["book_id"],
            "library_id": rec["library_id"],
            "user": rec["user"],
            "_id": {"$gt": rec["_id"]}   # a later record
        })
        if returned:
            continue  # Already returned

        # Compose the email
        subject = f"Library Reminder: '{rec['title']}' is overdue"
        body = (
            f"Dear {rec['user']},\n\n"
            f"Our records show that the book '{rec['title']}' "
            f"(Book ID {rec['book_id']}) was due on {rec['due_date'].date()}.\n"
            f"Please return it as soon as possible.\n\n"
            "Thank you,\nLibrary Team"
        )
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = "poorvikulshrestha0105@gmail.com"
        msg["To"] = rec["email"]

        # Send the email
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login("poorvikulshrestha0105@gmail.com", "Poorvi011205")  # use an app password!
                server.send_message(msg)
            print(f"Email sent to {rec['email']} for {rec['title']}")
        except Exception as e:
            print(f"Failed to send email to {rec['email']}: {e}")
