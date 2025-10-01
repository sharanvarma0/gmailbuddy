import email
from loguru import logger
from email.utils import parsedate_to_datetime


def parse_received_datetime(received_entry_raw):
    parsed_date = None
    try:
        logger.debug(f"Input for parsing received entry: {received_entry_raw}")
        date_str = received_entry_raw
        if ';' in received_entry_raw:
            date_str = received_entry_raw.split(';')[1]
        parsed_date = parsedate_to_datetime(date_str).date()
        logger.debug(f"Parsed DateTime: {parsed_date}")
        if not parsed_date:
            parsed_date = datetime.strptime(date_str, "%a, %d %b %Y %H:%M:%S %z").date()
        logger.debug(f"Parsed DateTime: {parsed_date}")
    except Exception as date_time_parsing_exc:
        logger.error(f"Exception when attempting to parse datetime in received header: {date_time_parsing_exc}")
    return parsed_date.isoformat()
        

def get_header(name, headers):
    return next((h['value'] for h in headers if h['name'].lower() == name.lower()), None)

def get_mailbox_and_read_status(labels):
    valid_mailboxes = ['INBOX', 'IMPORTANT', 'CATEGORY_PROMOTIONS']
    valid_read_status = ['READ', 'UNREAD']
    mailbox, is_read = None, None

    for mailbox_iter in valid_mailboxes:
        if mailbox_iter in labels:
            mailbox = mailbox_iter 
            break

    for read_status_iter in valid_read_status:
        if read_status_iter in labels:
            is_read = read_status_iter
            break
    return mailbox, is_read


def parse_email(raw_email_item, headers):
    parsed_email = {}
    try:
        label_ids = raw_email_item.get("labelIds", [])
        mailbox, is_read = get_mailbox_and_read_status(label_ids)
        logger.debug(f"{mailbox}, {is_read}")
        if is_read == 'UNREAD':
            is_read = False
        else:
            is_read = True
        parsed_email["sender"] = get_header("From", headers)
        parsed_email["receiver"] = get_header("To", headers)
        parsed_email["sent_timestamp"] = parse_received_datetime(get_header("Date", headers))
        parsed_email["received_timestamp"] = parse_received_datetime(get_header("Received", headers))
        parsed_email["subject"] = get_header("Subject", headers)
        parsed_email["cc"] = get_header("Cc", headers)
        parsed_email["bcc"] = get_header("Bcc", headers)
        parsed_email["mailbox"] = mailbox
        parsed_email["is_read"] = is_read
        logger.debug(f"Parsed Email: {parsed_email}")
    except Exception as exc:
        logger.error(f"Exception when parsing email: {exc}")
    return parsed_email


def get_list_of_emails(service_obj, number_of_results=10):
    messages = []
    parsed_messages = []
    try:
        results = service_obj.users().messages().list(userId="me", maxResults=number_of_results).execute()
        messages = results.get("messages", [])
    except Exception as email_list_exc:
        logger.error(f"Error when attempting to list emails in Gmail: {email_list_exc}")

    if messages:
        try:
            for msg in messages:
                m = service_obj.users().messages().get(userId='me', id=msg['id']).execute()
                headers = m['payload']['headers']
                parsed_email = parse_email(m, headers)
                parsed_messages.append(parsed_email)
        except Exception as exc:
            logger.error(f"Error when describing emails by id: {exc}")
    logger.debug(f"Messages obtained: {len(parsed_messages)}")
    return parsed_messages
