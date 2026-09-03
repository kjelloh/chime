#!/usr/bin/env python3

import argparse
import email
import imaplib
import os
from email.header import decode_header
from email.utils import parsedate_to_datetime


def decode_mime_header(value):
    """Decode an RFC 2047 email header into readable text."""
    if not value:
        return ""

    parts = decode_header(value)
    result = []

    for text, encoding in parts:
        if isinstance(text, bytes):
            result.append(text.decode(encoding or "utf-8", errors="replace"))
        else:
            result.append(text)

    return "".join(result)


def connect():
    host = os.environ["IMAP_HOST"]
    user = os.environ["IMAP_USER"]
    password = os.environ["IMAP_PASSWORD"]

    mail = imaplib.IMAP4_SSL(host)
    mail.login(user, password)
    return mail


def find_todo_messages(mail, mailbox="INBOX"):
    status, _ = mail.select(mailbox, readonly=True)

    if status != "OK":
        raise RuntimeError(f"Could not select mailbox: {mailbox}")

    # Fetch all message IDs. We inspect Subject ourselves because
    # IMAP's SUBJECT search does not reliably express "starts with".
    status, data = mail.uid("search", None, "ALL")

    if status != "OK":
        raise RuntimeError("IMAP search failed")

    uids = data[0].split()

    for index, uid in enumerate(uids, start=1):

      if index == 1 or index % 100 == 0:
        print(
            f"Scanning message {index}/{len(uids)} "
            f"(UID {uid.decode()})...",
            flush=True,
        )    

        status, msg_data = mail.uid(
            "fetch",
            uid,
            "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])"
        )

        if status != "OK":
            continue

        raw_header = b"".join(
            part[1] for part in msg_data
            if isinstance(part, tuple)
        )

        msg = email.message_from_bytes(raw_header)

        subject = decode_mime_header(msg.get("Subject", ""))

        if not subject.lstrip().upper().startswith("TODO:"):
            continue

        sender = decode_mime_header(msg.get("From", ""))
        date_string = msg.get("Date", "")

        try:
            date = parsedate_to_datetime(date_string)
            date_string = date.isoformat()
        except (TypeError, ValueError):
            pass

        yield {
            "uid": uid.decode(),
            "subject": subject,
            "from": sender,
            "date": date_string,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Find emails whose Subject starts with TODO:"
    )
    parser.add_argument(
        "--mailbox",
        default="INBOX",
        help="IMAP mailbox to inspect (default: INBOX)",
    )

    args = parser.parse_args()

    mail = connect()

    try:
        found = False

        for message in find_todo_messages(mail, args.mailbox):
            found = True
            print(
                f"{message['date']}  "
                f"{message['from']}  "
                f"{message['subject']}  "
                f"(UID {message['uid']})"
            )

        if not found:
            print("No TODO: messages found.")

    finally:
        try:
            mail.close()
        except Exception:
            pass

        mail.logout()


if __name__ == "__main__":
    main()