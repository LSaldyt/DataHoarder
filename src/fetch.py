#!/usr/bin/env python3
from settings      import submission_attrs, comment_attrs, group_size
from serialization import serialize, concatenate
from contextlib    import contextmanager

import time, sys

# Helper function for taking attributes from readable reddit objects
def collect_attrs(item, attributes):
    return tuple(getattr(item, attribute) for attribute in attributes)

# Get the description of our crawler
def get_UA():
    with open('../etc/user-agent.txt') as UAFile:
        return UAFile.read()

@contextmanager
def redirect(filename=None):
    if filename is not None:
        with open(filename, 'w') as output:
            sys.stdout = output
            try:
                yield
            finally:
                sys.stdout = sys.__stdout__
    else:
        yield

# Indefinitely read stuff off of reddit
def fetch_reddit(filename=None):
    from praw.errors   import HTTPException, APIException, ClientException
    import praw
    import time

    start   = time.time()
    current = start
    i = 0

    with redirect(filename):
        while True:
            try:
                r = praw.Reddit(get_UA()) # Read the file in etc/user-agent
                submissions = []
                for submission in praw.helpers.submission_stream(r, 'all'):
                    i += 1

                    print('Opened submission %s' % submission.title)
                    comments = []
                    for comment in submission.comments:
                        comments.append(collect_attrs(comment, comment_attrs))
                        for subcomment in comment.replies:
                            comments.append(collect_attrs(comment, comment_attrs))

                    if i % group_size == 0: # Save submissions every `group_size` (ex 25th) submission
                        print('Writing submission group for reddit')
                        serialize(submissions, '../serialized/reddit%s' % (i/group_size))
                        submissions = []
                        print('Wrote submission group. Time so far: %s' % (time.time() - start))
                        concatenate('reddit')
                        i = 0

                    submissions.append(collect_attrs(submission, submission_attrs))
                    taken   = time.time() - current # "Current"
                    current = time.time()
                    print('Finished processing submission. Total elapsed: %s. For submission: %s' % (current - start, taken))

            except HTTPException or APIException as e: # Catch what isn't my fault
                print(e)
                print('Retrying...')
                time.sleep(1)

            except ClientException as e: # Catch what is
                print(e)
                break

            except KeyboardInterrupt:
                concatenate('reddit')
                sys.exit(0)

# Download popular corpuses (corpi?) from gutenberg website
def fetch_gutenberg(filename=None):
    from gutenberg.acquire import load_etext
    from gutenberg.cleanup import strip_headers
    from gutenbergsettings import popularTitles, saveInterval

    start    = time.time()
    lastsave = start

    with redirect(filename):
        try:
            for title in popularTitles:
                text = strip_headers(load_etext(title)).strip()
                serialize([(title, text)], '../serialized/guten%s' % title)
                sinceLast = time.time() - lastsave
                print('%s since last save' % sinceLast)
                if sinceLast > saveInterval:
                    concatenate('guten')
                    lastsave = time.time()
        except KeyboardInterrupt:
            concatenate('guten')
            sys.exit(0)


def fetch_template(crawl):
    def template(remaining, filename=None):
        seen = set()
        with redirect(filename):
            while True:
                next_remaining = set()
                for item in remaining:
                    next_remaining.update(crawl(item, seen))
                remaining = next_remaining
    return template


def crawl_template(source, get, exceptions, silent=True, interval=10, defaultval=set()):
    def template(item, seen):
        print('Crawling %s' % item)
        if len(seen) % interval == 0:
            print('Saving')
            concatenate(source)
        try:
            seen.add(item)
            content, remaining = get(item, seen)
            serialize(content, '../serialized/%s%s' % (source, len(seen)))
            return remaining 
        # If something goes wrong (on API side), throw away everything from this section of the crawl
        except exceptions as e: 
            print(repr(e))
            return defaultval
        except KeyboardInterrupt:
            concatenate(source)
            sys.exit(0)
    return template


def get_google(url, seen):
    from bs4    import BeautifulSoup
    from google import search, get_page
    soup      = BeautifulSoup(get_page(url), 'lxml')
    content   = { url : [str(s) for paragraph in soup.find_all('p') for s in paragraph.strings] }
    remaining = { link.get('href') for link in soup.find_all('a') if link.get('href') not in seen }
    return content, remaining

from urllib.error import HTTPError, URLError, ContentTooShortError
crawl_google = crawl_template('google', get_google, (HTTPError, URLError, ContentTooShortError, ValueError))
fetch_google = fetch_template(crawl_google)

def get_wikipedia(term, seen):
    import wikipedia
    content   = dict()
    remaining = set()
    for item in wikipedia.search(term, results=10):
        if item not in seen:
            content[item] = wikipedia.summary(item)
        remaining = { word for summary in content.values() for word in summary.split() if word not in seen}
    return content, remaining

from wikipedia.exceptions import WikipediaException
crawl_wikipedia = crawl_template('wiki', get_wikipedia, (WikipediaException,))
fetch_wikipedia = fetch_template(crawl_wikipedia)

if __name__ == '__main__':
    fetch_wikipedia({'spider'})
