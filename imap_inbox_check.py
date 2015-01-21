"""Count the number of unique message threads in a Gmail inbox, by logging
in with IMAP and checking the count of unique values of the X-GM-THRID header.

This example was helpful:
http://yuji.wordpress.com/2011/06/22/python-imaplib-imap-example-with-gmail/

"""
import imaplib
import re
from collections import defaultdict
from dateutil.parser import parser
from operator import itemgetter

# messages fetched with query '(ENVELOPE X-GM-THRID)' look like:
# 145 (X-GM-THRID 1490479738467641057 UID 63980 ENVELOPE ("Fri, 16 Jan 2015 18:17:21 +0000 (UTC)" "Mark, please add me to your LinkedIn network" (("Terry Kim" NIL "member" "linkedin.com")) (("Terry Kim" NIL "member" "linkedin.com")) ((NIL NIL "terry" "yelp.com")) (("Mark Wilson" NIL "mark.wilson" "aya.yale.edu")) NIL NIL NIL "<979753161.7821475.1421432241882.JavaMail.app@lva1-app1733.prod>"))
# apparently they can also look like:
# 29 (X-GM-THRID 1490862160724952480 UID 64181 ENVELOPE ("Tue, 20 Jan 2015 23:35:51 +0000" "New PadMapper Listing Alert" ((NIL NIL "noreply" "padmapper.com")) ((NIL NIL "noreply" "padmapper.com")) ((NIL NIL "noreply" "padmapper.com")) ((NIL NIL "secretchinamark+sunset-1br-2500" "gmail.com")) NIL NIL NIL "<0000014b09b3c3fd-f698d656-9b38-4d90-86dd-91d81ed9f1bd-000000@us-west-2.amazonses.com>"))
# or:
# 31 (X-GM-THRID 1490880451527408411 UID 64194 ENVELOPE ("Tue, 20 Jan 2015 23:26:35 -0500" "Monday: Join 35 Chinese Speakers at \\"Monthly Mega Meetup\\"" (("Mandarin Mixer Meetup (SF Bay Area)" NIL "info" "meetup.com")) ((NIL NIL "info" "meetup.com")) (("Mandarin Mixer Meetup (SF Bay Area)" NIL "info" "meetup.com")) ((NIL NIL "secretchinamark" "gmail.com")) NIL NIL NIL "<1562012193.1421814395162.JavaMail.root@jobs0.meetup.com>"))

thread_id_re = re.compile('X-GM-THRID (\d+)')
date_re = re.compile('ENVELOPE \("([^"]+)"')
subject_re = re.compile('ENVELOPE \("[^"]+" "(.+)" \(\(("|NIL)')
from_re = re.compile('ENVELOPE \("[^"]+" "(.+)" \(\(("([^"]*)"|NIL) NIL "([^"]*)" "([^"]*)"')

date_parser = parser()

def re_partial(regex):
    return lambda envelope: regex.search(envelope).group(1)

def date_str_to_timestamp(date_str):
    return int(date_parser.parse(date_str).strftime('%s'))

def get_subject(envelope):
    result = subject_re.search(envelope)
    return result.group(1).replace('\\"', '"')

def get_from(envelope):
    result = from_re.search(envelope)
    _, _, name, email1, email2 = [result.group(i) for i in range(5)]
    email = '%s@%s' % (email1, email2)
    return [name if name is not None else email, email]

def gmail_thread_info(email, password):
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email, password)

    mail.select('INBOX')

    _, (uid_list,) = mail.uid('search', None, 'ALL')
    uids = uid_list.split(' ')

    _, inbox = mail.uid('fetch', ','.join(uids), '(ENVELOPE X-GM-THRID)')

    # Group messages into Gmail threads
    thread_id_to_messages = defaultdict(list)
    for m in inbox:
        thread_id_to_messages[re_partial(thread_id_re)(m)] += [m]

    # Pick the one whose subject doesn't start with "Re:"
    thread_id_to_single_message = {}
    for thread_id, messages in thread_id_to_messages.iteritems():
        if len(messages) == 1:
            thread_id_to_single_message[thread_id] = messages[0]
        else:
            subjects_without_reply = [ m for m in messages if not get_subject(m).startswith('Re: ') ]
            if subjects_without_reply:
                thread_id_to_single_message[thread_id] = subjects_without_reply[0]
            else:
                thread_id_to_single_message[thread_id] = messages[0]

    out = []

    # Pull out the important stuff
    for message in thread_id_to_single_message.itervalues():
        date = re_partial(date_re)(message)
        out.append({
            'thread_id': re_partial(thread_id_re)(message),
            'date': date,
            'date_ts': date_str_to_timestamp(date),
            'subject': get_subject(message),
            'from': get_from(message),
        })

    # Sort by timestamp
    out = list(sorted(out, key=itemgetter('date_ts'), reverse=True))

    return out
