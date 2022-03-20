#!/usr/bin/python3 -u

import traceback, time
import config
import utils
import imaplib

user_help_msg = "To subscribe {0}, you could send a email with subject 'subscribe' to '{1}'. You will receive a confirmation email if everything is going well. \r\n" \
                "To unsubscribe, you could send a email with subject 'unsubscribe' to '{1}'. You will also receive a confirmation email if it's success. \r\n" \
                "To broadcast a message to this list, you must be in the 'allow list'. You just send whatever you want, and it will be forwarded to everyone. \r\n" \
                "{2}".format(config.list_name, config.list_address, config.additional_help_msg)
subscribed_msg_subj = "You have subscribed {}".format(config.list_name)
subscribed_msg_text = "Welcome to subscribe {0}. You will receive all future messages in {0}, which will be sent from {1}. \r\n\r\n".format(config.list_name, config.list_address) + user_help_msg
unsubscribed_msg_subj = "You have unsubscribed {}".format(config.list_name)
unsubscribed_msg_text = "You have successfully unsubscribe {0}. \r\n\r\n".format(config.list_name) + user_help_msg
rejected_broadcast_msg_subj = "You are not allowed to broadcast at {}".format(config.list_name)
rejected_broadcast_msg_text = "You are not allowed to broadcast at {}, because you are not in the allow list. \r\n\r\n".format(config.list_name) + user_help_msg
dup_subscribed_msg_subj = "You have already subscribed {}".format(config.list_name)
dup_subscribed_msg_text = "It seems that you have already subscribed to {0}. This request would be ignored. \r\n\r\n".format(config.list_name, config.list_address) + user_help_msg
dup_unsubscribed_msg_subj = "You are not subscribing {}".format(config.list_name)
dup_unsubscribed_msg_text = "It seems that you are not subscribing to {0} at all. This request would be ignored. \r\n\r\n".format(config.list_name) + user_help_msg

# This is a cache, and it must be written-back to server on change.
# All email addresses in database must in lower-case.
subscribers_cache = []


def broadcast_a_email(msg_body, smtp_server):
    for subscriber_addr in subscribers_cache:
        utils.forward_a_email(smtp_server, config.list_address, subscriber_addr, msg_body)

def on_new_message(msg_body, imap_server, smtp_server):
    from_addr, subj = utils.extract_headers_from_msg(msg_body)
    if utils.check_if_addr_in_list(config.blocked_users, from_addr):
        print("Ignoring blocked sender: ", from_addr, subj)
        return
    print("DEBUG: on_new_message, ", from_addr, subj)
    if subj.strip().lower() == 'subscribe':
        if from_addr.lower() not in subscribers_cache:
            # Subscribe this guy
            subscribers_cache.append(from_addr.lower())
            utils.upload_strarr_to_imap(imap_server, config.data_folder_name, subscribers_cache)
            utils.send_a_email(smtp_server, config.list_address, from_addr, subscribed_msg_subj, subscribed_msg_text)
        else:
            utils.send_a_email(smtp_server, config.list_address, from_addr, dup_subscribed_msg_subj, dup_subscribed_msg_text)
    elif subj.strip().lower() == 'unsubscribe':
        if from_addr.lower() in subscribers_cache:
            # Unsubscribe this guy.
            subscribers_cache.remove(from_addr.lower())
            utils.upload_strarr_to_imap(imap_server, config.data_folder_name, subscribers_cache)
            utils.send_a_email(smtp_server, config.list_address, from_addr, unsubscribed_msg_subj, unsubscribed_msg_text)
        else:
            utils.send_a_email(smtp_server, config.list_address, from_addr, dup_unsubscribed_msg_subj, dup_unsubscribed_msg_text)
    else:
        # This is a broadcast request
        if utils.check_if_addr_in_list(config.allowed_senders, from_addr):
            print("Accepted broadcast '{}' from sender {}. ".format(subj, from_addr))
            broadcast_a_email(msg_body, smtp_server)
        else:
            print("Rejected broadcast '{}' from sender {}, this sender is not allowed. ".format(subj, from_addr))
            utils.send_a_email(smtp_server, config.list_address, from_addr, rejected_broadcast_msg_subj, rejected_broadcast_msg_text)


def mailbox_monitor_forever(imap_server, smtp_server):
    imap_server.create(config.archive_folder_name)

    while True:
        need_expunge = False
        try:
            imap_server.select('INBOX')
            stat, data = imap_server.search(None, '(ALL)')
            assert(stat == 'OK')

            # For every message in INBOX
            for msg_id in data[0].split():
                stat, data = imap_server.fetch(msg_id, '(RFC822)')
                assert(stat == 'OK')
                msg_body = data[0][1]

                on_new_message(msg_body, imap_server, smtp_server)

                # After processing the message, move it to archived folder.
                imap_server.copy(msg_id, config.archive_folder_name)
                imap_server.store(msg_id, '+FLAGS', '\\Deleted')
                need_expunge = True
        except imaplib.IMAP4.abort:
            print("IMAP connection broken... reconnecting... ")
            imap_server = utils.connect_to_server(True, config.imap_server)
            smtp_server = utils.connect_to_server(False, config.smtp_server)
            imap_server.login(config.imap_username, config.imap_password)
            smtp_server.login(config.smtp_username, config.smtp_password)
        except:
            print("Exception caught in mailbox_monitor_forever main loop: ")
            traceback.print_exc()
        finally:
            # Actually perform the DELETE operations. It will invalidate most msg_id.
            if need_expunge:
                imap_server.expunge()
        time.sleep(config.poll_interval)


def main():
    global subscribers_cache
    print('Connecting to IMAP and SMTP servers...')
    imap_server = utils.connect_to_server(True, config.imap_server)
    smtp_server = utils.connect_to_server(False, config.smtp_server)
    imap_server.login(config.imap_username, config.imap_password)
    smtp_server.login(config.smtp_username, config.smtp_password)
    print('Successfully logged into IMAP and SMTP server. ')
    subscribers_cache = utils.download_strarr_from_imap(imap_server, config.data_folder_name)
    print('Subscribers:', subscribers_cache)
    mailbox_monitor_forever(imap_server, smtp_server)


main()
