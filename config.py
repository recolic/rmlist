# RMlist Configuration file

# Mailing list introduction
list_name = 'Hutao Cloud Mailing List'
list_desc = 'This is a powerful breakwall service, and cloud hosting service provider. '

# Who is allowed to send to this mailing list? Accepting wildcard matching (fnmatch syntax, case insensitive).
allowed_senders = ['root@recolic.net', '*@hutao.cloud', '*@recolic.net']

# Mail account attached to this list
#   server protocol could be PLAIN, SSL or STARTTLS. 
list_address = 'tmp1@recolic.net'

imap_server = 'SSL:imap.recolic.net:993'
imap_username = list_address
imap_password = '....'

smtp_server = 'STARTTLS:smtp.recolic.net:587'
smtp_username = imap_username
smtp_password = imap_password

#########################################################
# You usually don't want to modify the following settings
# Just leave it as-is, ans it should be working fine.

# It checks latest email every 30 seconds
poll_interval = 10

archive_folder_name = 'rmlist_archived'

