# gmail-logger

Log metadata about your Gmail inbox.

## Quick start

* Add a file called `secret.py` which looks like this. If your Google account has 2-step verification, create a new app-specific password for this.
```
email = 'your-email@gmail.com'
password = 'your-password'
```

* Make sure you have pip and virtualenv.

* Set up a virtualenv, activate it, and install requirements:
```
virtualenv venv
. venv/bin/activate
pip install -r requirements.txt
```

* Test it out:
```
python log_inbox.py
```

* Schedule it to run regularly. This is the line from my `crontab` which schedules it at the top of every hour:
```
0 * * * * cd /path/to/log/to; /path/to/gmail-logger/venv/bin/python /path/to/gmail-logger/log_inbox.py >/dev/null
```

## Notes

I wrote this hastily, for my personal needs, and with the goal of logging as much data as reasonably possible. Eventually I'll update it to log in a saner format and offer options for what gets logged.

Add to my inbox count: mark@warkmilson.com
