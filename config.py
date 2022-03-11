# RMlist Configuration file

# Mailing list introduction
list_name = 'Hutao Cloud Mailing List'
list_desc = 'This is a powerful breakwall service, and cloud hosting service provider. '

# Who is allowed to send to this mailing list? Accepting whidcard matching (fnmatch syntax). 
allowed_sender = ['root@recolic.net', '*@hutao.cloud']

# Mail account attached to this list
#   server protocol could be PLAIN, SSL or STARTTLS. 
list_address = 'hutao-list@recolic.net'

imap_server = 'SSL:imap.recolic.net:993'
imap_username = list_address
imap_password = 'P@ssw0rd'

smtp_server = 'STARTTLS:smtp.recolic.net:587'
smtp_username = imap_username
smtp_password = imap_password

# It checks latest email every 30 seconds
poll_interval = 30



