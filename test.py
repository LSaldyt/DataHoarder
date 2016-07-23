#!/usr/bin/env python3
import praw
from praw.errors import HTTPException, APIException
import time
import pickle

start   = time.time()
current = start
i = 0

while True:
    try:
        r = praw.Reddit('Simple reddit crawler by /u/bearded_vagina. Contact: lucassaldyt@gmail.com. Application is at github.com/LSaldyt/ (GPL)')
        for submission in praw.helpers.submission_stream(r, 'all'):
            i += 1

            print('Opened submission %s' % submission.title)

            comments = []
            for comment in submission.comments:
                comments.append((comment.author, comment.body))
                for subcomment in comment.replies:
                    comments.append((comment.author, comment.body))
            with open('serialized/%s.pkl' % i, 'wb') as picklefile:
                pickle.dump((submission.author, 
                             submission.title + submission.selftext, 
                             comments), picklefile)
            taken   = time.time() - current # "Current"
            current = time.time()
            print('Wrote submission. Total elapsed: %s. For submission serialization: %s' % (current - start, taken))

    except HTTPException or APIException as e: # Catch what isn't my fault
        print(e)
        time.sleep(1)

