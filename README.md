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

## Output

If you were to run it hourly, `inbox_count.log` would look something like this:
```
1428130801	2015-04-04 00:00:01	48
1428134401	2015-04-04 01:00:01	49
1428138001	2015-04-04 02:00:01	49
1428141601	2015-04-04 03:00:01	50
...
```

...and every hour, a JSON file named something like `2015-04-04_00.00.01.json` would be produced:
```
[
  {
    "date": "Mon, 30 Mar 2015 14:06:20 -0700",
    "thread_id": "1497103965428563028",
    "unread": false,
    "from": [
      "Barack Obama <b@whitehouse.gov>"
    ],
    "subject": "Supreme Court nomination"
  },
  ...
]
```

## Notes

I wrote this hastily, for my personal needs, and with the goal of logging as much data as reasonably possible. Eventually I'll update it to log in a saner format and offer options for what gets logged.

Add to my inbox count: mark@warkmilson.com
