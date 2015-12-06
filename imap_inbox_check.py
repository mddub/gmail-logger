"""Get metadata about messages in a Gmail inbox, grouped by thread.

This example was helpful:
http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/

"""
import imaplib
import re
from collections import defaultdict
from dateutil.parser import parser
from dateutil.tz import tzlocal
from email.parser import HeaderParser
from functools import partial

message_index_re = re.compile('^(\d+) \(')
thread_id_re = re.compile('X-GM-THRID (\d+)')

date_parser = parser()
header_parser = HeaderParser()

def message_info_from_tuple(unread_indices, m):
    parsed = dict(header_parser.parsestr(m[1]).items())
    return {
        'thread_id': thread_id_re.search(m[0]).group(1),
        'unread': message_index_re.search(m[0]).group(1) in unread_indices,
        'date': parsed['Date'],
        'subject': parsed.get('Subject', ''),
        'from': parsed.get('From', ''),
    }

def parse_date_from_message_dict(info):
    date = info['date']

    parsed = date_parser.parse(date)

    if parsed.tzinfo is None:
        # dateutil doesn't understand these...
        unfortunate_tz_strings = [('EST', '-0500'), ('EDT', '-0400'), ('(GMT+00:00)', '(GMT)')]
        for tz_str, offset in unfortunate_tz_strings:
            date = date.replace(tz_str, offset)
        parsed = date_parser.parse(date)

    # Parsed dates are used for sorting, but not in the output,
    # so we can afford to be lenient with bad timezones.
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tzlocal())

    return parsed


def gmail_thread_info(email, password):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email, password)

    mail.select('INBOX')

    _, (uid_list,) = mail.uid('search', None, 'ALL')

    if uid_list == '':
        return []

    uids = uid_list.split(' ')
    _, inbox = mail.uid('fetch', ','.join(uids), '(X-GM-THRID BODY.PEEK[HEADER])')

    _, (unread_indices,) = mail.search(None, '(UNSEEN)')
    unread_indices = unread_indices.split(' ')

    # every other "message" is the string ")"
    actual_messages = [inbox[i] for i in xrange(0, len(inbox), 2)]
    thread_infos = map(partial(message_info_from_tuple, unread_indices), actual_messages)

    # Group messages into Gmail threads
    thread_id_to_messages = defaultdict(list)
    for m in thread_infos:
        thread_id_to_messages[m['thread_id']].append(m)

    # Summarize each thread
    summarized_threads = []
    for thread_id, messages in thread_id_to_messages.iteritems():
        sorted_by_date = list(sorted(messages, key=parse_date_from_message_dict))
        summarized_threads.append({
            # Take subject from the earliest message, which is least likely to have "Re:" in it
            'subject': sorted_by_date[0]['subject'],
            # Take date from the latest message
            'date': sorted_by_date[-1]['date'],
            'from': list(set(m['from'] for m in sorted_by_date)),
            'unread': any(m['unread'] for m in sorted_by_date),
            'thread_id': thread_id,
        })

    # Sort by timestamp
    return list(sorted(summarized_threads, key=parse_date_from_message_dict, reverse=True))
