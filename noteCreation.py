import sqlite3
import imaplib
import email
from email.header import decode_header
import re

#site notes will be enclosed within "=================="


#email account credentials
username = ""
passwd = ""


#connect to db
conn = sqlite3.connect("databaseFile.db")
cursor = conn.cursor()

#function to add a note
#TODO look into execute prompt. ''' is throwing errors
def add_note(client_name, note):
    cursor.execute('''
        INSERT INTO Notes (client_name, note)
        VALUES (?,?))
    ''',(client_name, note))
    conn.commit()
    conn.close()

#function to extract plain text from email body
def get_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            #ignore attachments and HTML
            if part.get_content_type() == "text/plain":
                return part.get_payload(decode=True).decode()
    else:
        return msg.get_payload(decode=True).decode()

#parse email
def parse_email(email_message):
    
    body = get_body(email_message)
    if body:
        #parse email body for "Client:" and anything after the colon until newline character
        found_client = re.search(r'Client:\s*(.*?)(?=Project:|$)', body)
        
        #parse email body for 18 "=" operators as notes are contained within
        found_note = re.search(r'={18}\n?(.*?)(?={This email notification|\$)', body, re.DOTALL)

        #debugging start
        if found_client:
            print(f"Client found: {found_client.group(1).strip()}")
        else:
            print("NO client found")
        
        if found_note:
            print(f"Notes found: {found_note.group(1).strip()}")
        else:
            print("No notes found")

        if found_client and found_note:
            client_name = found_client.group(1).strip()
            note = found_note.group(1).strip()
            add_note(client_name, note)
        else:
            print("ERROR: Client or note not found")
    else:
        print("ERROR: No email body found")


#connect to mail server
mail = imaplib.IMAP4_SSL("imap.gmail.com")
mail.login(username, passwd)
mail.select("inbox")

#search for unseen emails
status, messages = mail.search(None, "(UNSEEN)")

#Process unseen emails
for num in messages[0].split():
    status, msg_data = mail.fetch(num, "(RFC822)")
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(response_part[1])
            parse_email(msg)

#close connections
mail.close()
mail.logout()
conn.close()
