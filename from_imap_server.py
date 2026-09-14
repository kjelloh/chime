#!/usr/bin/env python3

import argparse
import email
import imaplib
import os
import sys # sys.stderr,...
from email.header import decode_header
from email.utils import parsedate_to_datetime

def progress(message):
    print(message, file=sys.stderr, flush=True)

def decode_mime_header(value):
    """Decode an RFC 2047 email header into readable text."""
    if not value:
        return ""

    parts = decode_header(value)
    result = []

    for text, encoding in parts:

        decoded_text = text

        if isinstance(text, bytes):
            # try to decode bytes to string
            for encoding_candidate in (encoding, "utf-8", "latin-1"):

              try :
                  decoded_text = text.decode(encoding_candidate)
                  break
              except (UnicodeDecodeError, LookupError,TypeError):
                  # TypeError swallows e.g., encoding_candidate None
                  # LookupError swallows e.g., encoding_candidate 'unknown-8-bit'
                  # Both which seems to happen in testing on Swedish IMAP mailbox...
                  continue

              # decode to ascii with hex values for unknowns and non-printables
              # Note: latin-1 above maps all bytes to a code point so we should never end up here?
              decoded_text = "".join(
                  chr(b) if (0x20 <= b <= 0x7e) else f"\\x{b:02x}"
                  for b in text
              )
              break     

        result.append(decoded_text)

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

      progress_scope = 100
      if index == 1 or index % progress_scope == 0:
        progress(
            f"Scanning messages {index}..{index + progress_scope -1} of {len(uids)} "
            f"(UID {uid.decode()})...",
        )    

      status, msg_data = mail.uid(
          "fetch",
          uid,
          "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)])"
      )

      if status != "OK":
        print(f"Failed to fetch message UID {uid.decode()}", flush=True)
        continue

      raw_header = b"".join(
          part[1] for part in msg_data
          if isinstance(part, tuple)
      )

      msg = email.message_from_bytes(raw_header)

      subject = decode_mime_header(msg.get("Subject", ""))
      sender = decode_mime_header(msg.get("From", ""))

      date_string = msg.get("Date", "")

      try:
          date = parsedate_to_datetime(date_string)
          date_string = date.isoformat()
      except (TypeError, ValueError,AttributeError):
          date_string = str(date_string)
          pass

      # print(f"{index}: {date_string} {sender} -> '{subject}'",flush=True)

      if not subject.lstrip().upper().startswith("TODO:"):
          continue

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
        help="IMAP mailbox to inspect (default: Inbox)",
    )

    args = parser.parse_args()

    mail = connect()

    try:
        todo_messages = []

        for message in find_todo_messages(mail, args.mailbox):
            todo_messages.append(message)

        if not todo_messages:
            print("No TODO: messages found.")
        else:
            print(f"Found {len(todo_messages)} TODO: messages:")
            for message in todo_messages:
                print(
                    f"UID: {message['uid']}, "
                    f"From: {message['from']}, "
                    f"Date: {message['date']}, "
                    f"Subject: {message['subject']}"
                )
            print(f"Total count: {len(todo_messages)}")

    finally:
        try:
            mail.close()
        except Exception:
            pass

        mail.logout()


if __name__ == "__main__":
    main()