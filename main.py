#!/usr/bin/python3

import traceback, time
import config
import utils


def broadcast_a_email(msg_body, smtp_server):
    print("Broadcasting a email (not implemented yet)")
    utils.forward_a_email(smtp_server, config.list_address, "root+ms@recolic.net", msg_body)


def on_new_message(msg_body, smtp_server):
    from_addr, subj = utils.extract_headers_from_msg(msg_body)
    print("DEBUG: on_new_message, ", from_addr, subj)
    if subj.strip().lower() == 'subscribe':
        # Add this user to 'subscribed' list
        utils.send_a_email(smtp_server, config.list_address, from_addr, "You have subscribed {}", "Welcome! ...")
        # if already subscribed, send error mail
        pass
    elif subj.strip().lower() == 'unsubscribe':
        # Send unsubscribe email or error mail
        # Remove this user from list
        pass
    else:
        # This is a broadcast request
        if utils.check_if_sender_allowed(config.allowed_senders, from_addr):
            broadcast_a_email(msg_body, smtp_server)
        else:
            print("Ignored message '{}' from sender {}, because sender not allowed. ".format(subj, from_addr))


def mailbox_monitor_forever(imap_server, smtp_server):
    imap_server.select('INBOX')
    imap_server.create(config.archive_folder_name)

    while True:
        need_expunge = False
        try:
            stat, data = imap_server.search(None, '(ALL)')
            assert(stat == 'OK')

            # For every message in INBOX
            for msg_id in data[0].split():
                stat, data = imap_server.fetch(msg_id, '(RFC822)')
                assert(stat == 'OK')
                msg_body = data[0][1]

                on_new_message(msg_body, smtp_server)

                # After processing the message, move it to archived folder.
                imap_server.copy(msg_id, config.archive_folder_name)
                imap_server.store(msg_id, '+FLAGS', '\\Deleted')
                need_expunge = True
        except:
            print("Exception caught in mailbox_monitor_forever main loop: ")
            traceback.print_exc()
        finally:
            # Actually perform the DELETE operations. It will invalidate most msg_id.
            if need_expunge:
                imap_server.expunge()

        time.sleep(config.poll_interval)


def main():
    imap_server = utils.connect_to_server(True, config.imap_server)
    smtp_server = utils.connect_to_server(False, config.smtp_server)
    imap_server.login(config.imap_username, config.imap_password)
    smtp_server.login(config.smtp_username, config.smtp_password)
    print('Successfully logged into IMAP and SMTP server. ')
    mailbox_monitor_forever(imap_server, smtp_server)


main()
