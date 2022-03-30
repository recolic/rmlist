# RMlist Configuration file

# Mailing list introduction
list_name = 'Hutao Cloud Mailing List'

# Mail account attached to this list
# - server protocol could be PLAIN, SSL or STARTTLS.
list_address = 'hutao-news@recolic.net'

imap_server = 'SSL:imap.recolic.net:993'
imap_username = list_address
imap_password = '...'

smtp_server = 'STARTTLS:smtp.recolic.net:587'
smtp_username = imap_username
smtp_password = imap_password

# Who is allowed to broadcast to this mailing list? Accepting wildcard matching (fnmatch syntax, case insensitive).
allowed_senders = ['root@recolic.net', '*@hutao.cloud', '*@recolic.net']

# Blacklist: ignore all email from blacklist. 
# Usually you need to block yourself to avoid infinite loop, and block service provider to avoid junk mail from them. 
blocked_users = [list_address, '*@google.com']

#########################################################
# You usually don't need to modify the following settings
# Just leave it as-is, and it should be working fine.

# This additional message would be appended to the help message that delivered to subscribers.
# Leave it empty if you have nothing to say.
additional_help_msg = 'If you still have question, please contact support team. '

# It checks latest email every 30 seconds
poll_interval = 10

# rmlist will create these IMAP folders, to store processed mails, and subscriber info.
archive_folder_name = 'rmlist_archived'
data_folder_name = 'rmlist_data'

