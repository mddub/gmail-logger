"""Check the state of a Gmail inbox, then log the number of threads to a
tab-separated file, and summary information about the threads to a JSON file.
"""
from datetime import datetime

import simplejson as json

import secret
from imap_inbox_check import gmail_thread_info

LOG_FILE = 'inbox_count.log'

log_date = lambda d: d.strftime('%Y-%m-%d %H:%M:%S')
json_file_date = lambda d: d.strftime('%Y-%m-%d_%H.%M.%S')
unix_date = lambda d: d.strftime('%s')

now = datetime.now()
info = gmail_thread_info(secret.email, secret.password)
log_line = '%s\t%s\t%s' % (unix_date(now), log_date(now), len(info))
print log_line

with open(LOG_FILE, 'a') as f:
    f.write(log_line + '\n')

with open(json_file_date(now) + '.json', 'w') as f:
    f.write(json.dumps(info))
