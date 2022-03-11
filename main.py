#!/usr/bin/python3

import imaplib, smtplib
import utils
import email

def connect_to_server(isImap, server_string):
    protocol, addr, port = server_string.split(':')
    port = int(port)

    if protocol == 'PLAIN' or protocol == 'STARTTLS':
        server = imaplib.IMAP4(addr, port) if isImap else smtplib.SMTP(addr, port)
    elif protocol == 'SSL':
        server = imaplib.IMAP4_SSL(addr, port) if isImap else smtplib.SMTP_SSL(addr, port)
    else:
        raise ValueError("Invalid protocol in server setting: " + server_string)
    if protocol == 'STARTTLS':
        server.starttls()
    return server


def send_a_email(smtp_server, to_address, TODO):
    pass


def broadcast_a_email():
    pass


def mailbox_monitor_forever(imap_server, smtp_server, poll_interval):
    def check_stat(stat_str):
        if stat_str != 'OK':
            print("Warning: IMAP request error, server says ", stat_str)

    imap_server.select('INBOX')
    while True:
        stat, data = imap_server.search(None, '(ALL)')
        check_stat(stat)
        # For every message in INBOX
        for msg_id in data[0].split():
            stat, data = imap_server.fetch(msg_id, '(RFC822)')
            check_stat(stat)
            msg_body = data[0][1]
            if msg_id == '4':
                print("DELETING MSG 4, body=", msg_body)
                imap_server.store(msg_id, '+FLAGS', '\\Deleted')
                imap_server.expunge()
        break



def main():
    import config
    imap_server = connect_to_server(True, config.imap_server)
    smtp_server = connect_to_server(False, config.smtp_server)
    imap_server.login(config.imap_username, config.imap_password)
    smtp_server.login(config.smtp_username, config.smtp_password)
    mailbox_monitor_forever(imap_server, smtp_server, config.poll_interval)

main()
