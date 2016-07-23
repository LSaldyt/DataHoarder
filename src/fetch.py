#!/usr/bin/env python3
from praw.errors   import HTTPException, APIException, ClientException
from settings      import submission_attrs, comment_attrs, group_size
from serialization import serialize, concatenate

import praw, time

# Helper function for taking attributes from readable reddit objects
def collect_attrs(item, attributes):
    return tuple(getattr(item, attribute) for attribute in attributes)

# Get the description of our crawler
def get_UA():
    with open('../etc/user-agent.txt') as UAFile:
        return UAFile.read()

# Indefinitely read stuff off of reddit
def fetch_reddit(silent=False):
    def log(*args, **kwargs):
        if not silent:
            print(*args, **kwargs)

    start   = time.time()
    current = start
    i = 0

    while True:
        try:
            r = praw.Reddit(get_UA()) # Read the file in etc/user-agent
            submissions = []
            for submission in praw.helpers.submission_stream(r, 'all'):
                i += 1

                log('Opened submission %s' % submission.title)
                comments = []
                for comment in submission.comments:
                    comments.append(collect_attrs(comment, comment_attrs))
                    for subcomment in comment.replies:
                        comments.append(collect_attrs(comment, comment_attrs))

                if i % group_size == 0: # Save submissions every `group_size` (ex 25th) submission
                    log('Writing submission group')
                    serialize(submissions, '../serialized/reddit%s' % (i/group_size))
                    submissions = []
                    log('Wrote submission group. Time so far: %s' % (time.time() - start))
                    concatenate('reddit')

                submissions.append(collect_attrs(submission, submission_attrs))
                taken   = time.time() - current # "Current"
                current = time.time()
                log('Finished processing submission. Total elapsed: %s. For submission: %s' % (current - start, taken))

        except HTTPException or APIException as e: # Catch what isn't my fault
            print(e)
            log('Retrying...')
            time.sleep(1)

        except ClientException as e: # Catch what is
            print(e)
            break

if __name__ == '__main__':
    fetch_reddit()
