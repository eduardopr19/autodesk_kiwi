import os
import imaplib
import email
import ssl
from email.header import decode_header
from typing import List
from fastapi import APIRouter
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

router = APIRouter(prefix="/email", tags=["Email"])

# --- DATA MODELS ---
class EmailItem(BaseModel):
    subject: str
    sender: str
    date: str

class EmailSummary(BaseModel):
    count_unread: int
    emails: List[EmailItem] = []
    error: str = ""

# --- PROTON MAIL ROUTE (VIA BRIDGE) ---

@router.get("/proton/unread", response_model=EmailSummary)
def get_proton_unread():
    """Fetch unread emails via local IMAP (Proton Bridge)"""

    # Use environment variables for credentials
    host = os.getenv("PROTON_BRIDGE_HOST", "127.0.0.1")
    port = int(os.getenv("PROTON_BRIDGE_PORT", "1143"))
    user = os.getenv("PROTON_BRIDGE_USER")
    password = os.getenv("PROTON_BRIDGE_PASS")

    if not all([user, password]):
        return EmailSummary(count_unread=0, error="Incomplete .env configuration (PROTON_BRIDGE_USER/PASS)")

    print(f"DEBUG: Connecting to {host}:{port} with user='{user}'")

    try:
        # 1. Connect to Bridge
        mail = imaplib.IMAP4(host, port)

        # 2. STARTTLS
        try:
            mail.starttls()
        except Exception as e:
            # Continue without STARTTLS if it fails
            pass

        # 3. Authentication
        mail.login(user, password)

        # 4. Select inbox
        mail.select("inbox")

        # 5. Search for unread emails
        status, messages = mail.search(None, "(UNSEEN)")
        
        email_ids = messages[0].split()
        count = len(email_ids)
        
        email_list = []
        
        # Get details of the last 5 unread emails
        # reversed() to get most recent first
        for e_id in reversed(email_ids[-5:]):
            try:
                # Fetch only header (faster)
                _, msg_data = mail.fetch(e_id, "(RFC822.HEADER)")
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decode subject
                        subject_header = msg["Subject"]
                        subject_text = "(No subject)"
                        if subject_header:
                            decoded_list = decode_header(subject_header)
                            subject_text = ""
                            for text, encoding in decoded_list:
                                if isinstance(text, bytes):
                                    subject_text += text.decode(encoding if encoding else "utf-8", errors="ignore")
                                else:
                                    subject_text += str(text)

                        # Decode sender
                        from_header = msg.get("From", "Unknown")
                        
                        # Date
                        date_header = msg.get("Date", "")

                        email_list.append(EmailItem(
                            subject=subject_text,
                            sender=from_header,
                            date=date_header
                        ))
            except Exception as e:
                print(f"Error reading email {e_id}: {e}")
                continue

        mail.close()
        mail.logout()

        return EmailSummary(
            count_unread=count,
            emails=email_list
        )

    except ConnectionRefusedError:
        return EmailSummary(count_unread=0, error="Proton Bridge not running or wrong port")
    except imaplib.IMAP4.error as e:
        return EmailSummary(count_unread=0, error=f"IMAP error (Login?): {str(e)}")
    except Exception as e:
        print(f"Unknown error: {e}")
        return EmailSummary(count_unread=0, error=f"Error: {str(e)}")

# --- PAGINATED HISTORY ROUTE (Lazy Loading) ---

class EmailHistoryResponse(BaseModel):
    total_count: int
    emails: List[EmailItem] = []
    has_more: bool = False
    error: str = ""

@router.get("/proton/history", response_model=EmailHistoryResponse)
def get_proton_history(page: int = 1, per_page: int = 20):
    """Fetch email history with pagination (infinite scroll style)"""
    
    host = os.getenv("PROTON_BRIDGE_HOST", "127.0.0.1")
    port = int(os.getenv("PROTON_BRIDGE_PORT", "1143"))
    user = os.getenv("PROTON_BRIDGE_USER")
    password = os.getenv("PROTON_BRIDGE_PASS")
    
    if not all([user, password]):
        return EmailHistoryResponse(total_count=0, error="Incomplete .env configuration")
    
    try:
        # Connection
        mail = imaplib.IMAP4(host, port)
        try:
            mail.starttls()
        except:
            pass
        mail.login(user, password)
        mail.select("inbox")

        # Search ALL emails (not just UNSEEN)
        status, messages = mail.search(None, "ALL")
        
        if status != "OK":
            return EmailHistoryResponse(total_count=0, error="Email search error")
        
        email_ids = messages[0].split()
        total_count = len(email_ids)
        
        # Pagination: calculate indices
        # IMPORTANT: Keep chronological order (old → recent)
        # No reversed() here to have complete history in order
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_ids = email_ids[start_idx:end_idx]
        
        email_list = []
        
        for e_id in page_ids:
            try:
                _, msg_data = mail.fetch(e_id, "(RFC822.HEADER)")
                
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        # Decode subject
                        subject_header = msg["Subject"]
                        subject_text = "(No subject)"
                        if subject_header:
                            decoded_list = decode_header(subject_header)
                            subject_text = ""
                            for text, encoding in decoded_list:
                                if isinstance(text, bytes):
                                    subject_text += text.decode(encoding if encoding else "utf-8", errors="ignore")
                                else:
                                    subject_text += str(text)
                        
                        from_header = msg.get("From", "Unknown")
                        date_header = msg.get("Date", "")
                        
                        email_list.append(EmailItem(
                            subject=subject_text,
                            sender=from_header,
                            date=date_header
                        ))
            except Exception as e:
                print(f"Error reading email {e_id}: {e}")
                continue
        
        mail.close()
        mail.logout()
        
        has_more = end_idx < total_count
        
        return EmailHistoryResponse(
            total_count=total_count,
            emails=email_list,
            has_more=has_more
        )
        
    except ConnectionRefusedError:
        return EmailHistoryResponse(total_count=0, error="Proton Bridge not running")
    except imaplib.IMAP4.error as e:
        return EmailHistoryResponse(total_count=0, error=f"IMAP error: {str(e)}")
    except Exception as e:
        print(f"History error: {e}")
        return EmailHistoryResponse(total_count=0, error=f"Error: {str(e)}")

# --- SEND EMAIL ROUTE (SMTP) ---

class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str

@router.post("/proton/send")
def send_proton_email(email_data: SendEmailRequest):
    """Send an email via SMTP Proton Bridge"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    smtp_host = os.getenv("PROTON_BRIDGE_SMTP_HOST", "127.0.0.1")
    smtp_port = int(os.getenv("PROTON_BRIDGE_SMTP_PORT", "1025"))
    smtp_user = os.getenv("PROTON_BRIDGE_SMTP_USER")
    smtp_pass = os.getenv("PROTON_BRIDGE_SMTP_PASS")
    
    if not all([smtp_user, smtp_pass]):
        return {"success": False, "error": "Incomplete SMTP configuration"}
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email_data.to
        msg['Subject'] = email_data.subject
        msg.attach(MIMEText(email_data.body, 'plain'))
        
        # SMTP connection
        server = smtplib.SMTP(smtp_host, smtp_port)
        try:
            server.starttls()
        except:
            pass
        server.login(smtp_user, smtp_pass)
        
        # Send
        server.send_message(msg)
        server.quit()

        return {"success": True, "message": "Email sent successfully"}
        
    except Exception as e:
        print(f"Email send error: {e}")
        return {"success": False, "error": str(e)}

# --- GLOBAL SUMMARY ROUTE (For future compatibility) ---
@router.get("/summary")
def get_summary():
    # For now, only return Proton since Outlook is disabled
    proton_data = get_proton_unread()
    return {
        "outlook": 0,
        "proton": proton_data.count_unread,
        "total": proton_data.count_unread
    }