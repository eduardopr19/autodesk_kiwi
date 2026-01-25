import contextlib
import email
import imaplib
import os
from email.header import decode_header

from dotenv import load_dotenv
from fastapi import APIRouter
from pydantic import BaseModel

load_dotenv()

router = APIRouter(prefix="/email", tags=["Email"])


class EmailItem(BaseModel):
    id: str
    subject: str
    sender: str
    date: str

class EmailSummary(BaseModel):
    count_unread: int
    emails: list[EmailItem] = []
    error: str = ""

class EmailDetail(BaseModel):
    id: str
    subject: str
    sender: str
    date: str
    body: str
    html_body: str | None = None
    error: str = ""


def decode_email_header(header):
    if not header:
        return "(No subject)"
    decoded_list = decode_header(header)
    result = ""
    for text, encoding in decoded_list:
        if isinstance(text, bytes):
            result += text.decode(encoding if encoding else "utf-8", errors="ignore")
        else:
            result += str(text)
    return result


def get_email_body(msg):
    body = ""
    html_body = None

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))

            if "attachment" in content_disposition:
                continue

            if content_type == "text/plain":
                try:
                    charset = part.get_content_charset() or "utf-8"
                    body = part.get_payload(decode=True).decode(charset, errors="ignore")
                except Exception:
                    body = str(part.get_payload())
            elif content_type == "text/html" and not html_body:
                try:
                    charset = part.get_content_charset() or "utf-8"
                    html_body = part.get_payload(decode=True).decode(charset, errors="ignore")
                except Exception:
                    html_body = str(part.get_payload())
    else:
        content_type = msg.get_content_type()
        try:
            charset = msg.get_content_charset() or "utf-8"
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode(charset, errors="ignore")
        except Exception:
            body = str(msg.get_payload())

        if content_type == "text/html":
            html_body = body
            body = ""

    return body, html_body


def connect_to_mail():
    host = os.getenv("PROTON_BRIDGE_HOST", "127.0.0.1")
    port = int(os.getenv("PROTON_BRIDGE_PORT", "1143"))
    user = os.getenv("PROTON_BRIDGE_USER")
    password = os.getenv("PROTON_BRIDGE_PASS")

    if not all([user, password]):
        return None, "Incomplete .env configuration"

    try:
        mail = imaplib.IMAP4(host, port)
        with contextlib.suppress(Exception):
            mail.starttls()
        mail.login(user, password)
        return mail, None
    except ConnectionRefusedError:
        return None, "Proton Bridge not running or wrong port"
    except imaplib.IMAP4.error as e:
        return None, f"IMAP error: {str(e)}"
    except Exception as e:
        return None, f"Error: {str(e)}"


@router.get("/proton/unread", response_model=EmailSummary)
def get_proton_unread():
    mail, error = connect_to_mail()
    if error:
        return EmailSummary(count_unread=0, error=error)

    try:
        mail.select("inbox")
        status, messages = mail.search(None, "(UNSEEN)")

        email_ids = messages[0].split()
        count = len(email_ids)
        email_list = []

        for e_id in reversed(email_ids[-5:]):
            try:
                _, msg_data = mail.fetch(e_id, "(RFC822.HEADER)")

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        email_list.append(EmailItem(
                            id=e_id.decode(),
                            subject=decode_email_header(msg["Subject"]),
                            sender=msg.get("From", "Unknown"),
                            date=msg.get("Date", "")
                        ))
            except Exception as e:
                print(f"Error reading email {e_id}: {e}")
                continue

        mail.close()
        mail.logout()

        return EmailSummary(count_unread=count, emails=email_list)

    except Exception as e:
        print(f"Unknown error: {e}")
        return EmailSummary(count_unread=0, error=f"Error: {str(e)}")


@router.get("/proton/message/{email_id}", response_model=EmailDetail)
def get_email_detail(email_id: str):
    mail, error = connect_to_mail()
    if error:
        return EmailDetail(id=email_id, subject="", sender="", date="", body="", error=error)

    try:
        mail.select("inbox")
        _, msg_data = mail.fetch(email_id.encode(), "(RFC822)")

        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                body, html_body = get_email_body(msg)

                mail.close()
                mail.logout()

                return EmailDetail(
                    id=email_id,
                    subject=decode_email_header(msg["Subject"]),
                    sender=msg.get("From", "Unknown"),
                    date=msg.get("Date", ""),
                    body=body,
                    html_body=html_body
                )

        mail.close()
        mail.logout()
        return EmailDetail(id=email_id, subject="", sender="", date="", body="", error="Email not found")

    except Exception as e:
        print(f"Error fetching email {email_id}: {e}")
        return EmailDetail(id=email_id, subject="", sender="", date="", body="", error=str(e))


class EmailHistoryResponse(BaseModel):
    total_count: int
    emails: list[EmailItem] = []
    has_more: bool = False
    error: str = ""

@router.get("/proton/history", response_model=EmailHistoryResponse)
def get_proton_history(page: int = 1, per_page: int = 20):
    mail, error = connect_to_mail()
    if error:
        return EmailHistoryResponse(total_count=0, error=error)

    try:
        mail.select("inbox")
        status, messages = mail.search(None, "ALL")

        if status != "OK":
            return EmailHistoryResponse(total_count=0, error="Email search error")

        email_ids = messages[0].split()
        total_count = len(email_ids)

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

                        email_list.append(EmailItem(
                            id=e_id.decode(),
                            subject=decode_email_header(msg["Subject"]),
                            sender=msg.get("From", "Unknown"),
                            date=msg.get("Date", "")
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

    except Exception as e:
        print(f"History error: {e}")
        return EmailHistoryResponse(total_count=0, error=f"Error: {str(e)}")


class SendEmailRequest(BaseModel):
    to: str
    subject: str
    body: str

@router.post("/proton/send")
def send_proton_email(email_data: SendEmailRequest):
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    smtp_host = os.getenv("PROTON_BRIDGE_SMTP_HOST", "127.0.0.1")
    smtp_port = int(os.getenv("PROTON_BRIDGE_SMTP_PORT", "1025"))
    smtp_user = os.getenv("PROTON_BRIDGE_SMTP_USER")
    smtp_pass = os.getenv("PROTON_BRIDGE_SMTP_PASS")

    if not all([smtp_user, smtp_pass]):
        return {"success": False, "error": "Incomplete SMTP configuration"}

    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_user
        msg['To'] = email_data.to
        msg['Subject'] = email_data.subject
        msg.attach(MIMEText(email_data.body, 'plain'))

        server = smtplib.SMTP(smtp_host, smtp_port)
        with contextlib.suppress(Exception):
            server.starttls()
        server.login(smtp_user, smtp_pass)

        server.send_message(msg)
        server.quit()

        return {"success": True, "message": "Email sent successfully"}

    except Exception as e:
        print(f"Email send error: {e}")
        return {"success": False, "error": str(e)}


@router.get("/summary")
def get_summary():
    proton_data = get_proton_unread()
    return {
        "outlook": 0,
        "proton": proton_data.count_unread,
        "total": proton_data.count_unread
    }
