#!/usr/bin/env python3
import praw
import time

from pprint import pprint
r = praw.Reddit('Simple reddit crawler by /u/bearded_vagina. Contact: lucassaldyt@gmail.com. Application is at github.com/LSaldyt/ (GPL)')


all_comments = r.get_comments('all', limit=10)

nice_format = \
'''
%s/%s (%s):
%s
'''

for c in all_comments:
    comment = (nice_format %( 
            c.subreddit,
            c.author,
            c.score,
            c.body)
            )
    print(comment)
    time.sleep(1)
