# ResultsNotifier

This is a little program for University of Sydney students -- But I would image could be easily modified for any purpose. It logs in to the sydneystudent.sydney.edu.au website with your credentials and then checks if your course results have been posted for subjects you have requested.

## Usage
```
usage: main.py [-h] --username USERNAME --subjects SUBJECTS [SUBJECTS ...]
               --email EMAIL

Get notified when results are posted

optional arguments:
  -h, --help            show this help message and exit
  --username USERNAME
  --subjects SUBJECTS [SUBJECTS ...]
  --email EMAIL

```


## Minimal Installation and Setup

I recommend setting this up on a server or somewhere. You'll also need to provide an account to send e-mails from. I use mail.com here, but it also works with g-mail accounts.

```
git clone ...
cd ResultsNotifier
```

### Setup Virtualenv
Setup the virtual environment:

```
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Modify Email Account
At the time of writing, the email account is provided to the `conn.login` function. This is the e-mail account that will send you an e-mail notification.

### Run
I'd recommend running in screen or tmux, it isn't a daemon process or a service. Therefore you will need something like screen/tmux. I prefer tmux:

```
tmux
./main.py --username unikey --subjects INFO1003 --email youremailaddress@hotmail.com
```
