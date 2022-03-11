# rmlist [Work-In-Progress]

> Turn any mailbox into mailing list. 

This is an extremely-simple, lightweight, stateless mailing list. No setup, no deployment, no database, no hook. Just run it! 

## Usage

### How to run this service

1. Download this repository. 
2. Edit `config.py` to set your mailing account information. 
3. Run `main.py` and you are all set! 

### How to subscribe & unsubscribe

Anyone can send an email with title `subscribe`, to subscribe a mailing list. It will reply a confirmation email.

Anyone can send an email with title `unsubscribe`, to unsubscribe a mailing list. It will reply a confirmation email. 
