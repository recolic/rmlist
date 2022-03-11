# Functions in this file should not use config, should not be stateful.
# Just static utilities.

from email.header import decode_header
import fnmatch, time
import imaplib, smtplib

# from itertools import chain
# def create_imap_search_string(uid_max = None, criteria = {}):
#     # Produce search string in IMAP format:
#     #   e.g. (FROM "me@gmail.com" SUBJECT "abcde" BODY "123456789" UID 9999:*)
#     c = list(map(lambda t: (t[0], '"'+str(t[1])+'"'), criteria.items()))
#     if uid_max is not None:
#         c += [('UID', '%d:*' % (uid_max+1))]
#     return '(%s)' % ' '.join(chain(*c))
#
#
# def imap_get_max_uid(server):
#     result, data = server.uid('search', None, create_imap_search_string(0, {}))
#     uids = [int(s) for s in data[0].split()]
#     return max(uids) if uids else 0


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


def simplify_addr(s):
    # Simplify "Name <addr@domain.com>" to "addr@domain.com"
    l, r = s.find('<'), s.find('>')
    if l == -1:
        return s
    else:
        return s[l+1:r]


def extract_headers_from_msg(msg_body):
    # Extract 'From' and 'Subject' from mes_body.
    # TODO: try email.message_from_body()['From']
    FROM_FIELD = 'From: '
    SUBJ_FIELD = 'Subject: '
    from_addr, subj = None, None
    for line in msg_body.split(b'\r\n'):
        line = line.decode('utf-8', errors='ignore')  # Unicode should be encoded inside its field
        if line.startswith('From: '):
            from_addr = line[len(FROM_FIELD):]
            from_addr = simplify_addr(from_addr)
        if line.startswith('Subject: '):
            subj, encoding = decode_header(line[len(SUBJ_FIELD):])[0]
            if encoding is not None:
                subj = subj.decode(encoding, errors='ignore')
    if from_addr is None or subj is None:
        raise ValueError("Failed to extract from_addr or subj from message. \nmsg_body first 1KB:" + msg_body[:1024])
    return from_addr, subj


def check_if_sender_allowed(allowed_sender_wildcards, sender_addr):
    for wildcard in allowed_sender_wildcards:
        if fnmatch.fnmatch(sender_addr, wildcard):
            return True
    return False


import email
from email.mime.text import MIMEText
from email.utils import formatdate


def forward_a_email(smtp_server, self_address, to_address, original_body):
    message = email.message_from_bytes(original_body)
    message.replace_header('From', self_address)
    message.replace_header('To', to_address)
    smtp_server.sendmail(self_address, to_address, message.as_string())


def send_a_email(smtp_server, self_address, to_address, subj, text):
    message = MIMEText(text)
    message['Subject'] = subj
    message['From'] = self_address
    message['To'] = to_address
    message['Date'] = formatdate(localtime=True)
    smtp_server.send_message(message)


IMAPDB_HEADER = "Subject: Internal Message DO NOT DELETE\r\n\r\n"
def upload_data_to_imap(imap_server, folder_name, str_msg):
    imap_server.create(folder_name) # Create if not exists
    try:
        stat, data = imap_server.select(folder_name)
        assert(stat == 'OK')

        # 1. Clear the folder
        msg_count = int(data[0].decode())
        if msg_count > 1:
            print("Warning: msg_count > 1 in managed IMAPDB data folder. Someone may touched my DB! ")
        if msg_count > 0:
            for i in range(msg_count):
                imap_server.store(str(i+1).encode(), '+FLAGS', '\\Deleted')
            imap_server.expunge()

        # 2. Append the new message
        imap_server.append(folder_name, (), imaplib.Time2Internaldate(time.time()), (IMAPDB_HEADER + str_msg).encode('utf-8'))
    except:
        raise
    finally:
        imap_server.close()
def download_data_from_imap(imap_server, folder_name):
    # Returns string message
    try:
        stat, data = imap_server.select(folder_name)
        assert(stat == 'OK')
        msg_count = int(data[0].decode())
        if msg_count > 0:
            stat, data = imap_server.fetch(b'1', '(RFC822)')
            assert(stat == 'OK')
            return data[0][1].decode('utf-8', errors='ignore')
        else:
            return ""
    except:
        raise
    finally:
        imap_server.close()

