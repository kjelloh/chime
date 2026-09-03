# chime

## from_mail.py

This script reads an IMAP mailbox and filters out mails that are 'chimes'.

It requires the local shell environment to be populated with the environment variables to identify the IMAP host, the user and the credentials (password) för SSH access

```sh
> export IMAP_HOST="imap.example.com"
> export IMAP_USER="me@example.com"
> export IMAP_PASSWORD="secret"
> python3 from_mail.py
```