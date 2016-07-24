#!/usr/bin/env python3
from settings      import submission_attrs, comment_attrs, group_size
from serialization import serialize, concatenate

import time

# Helper function for taking attributes from readable reddit objects
def collect_attrs(item, attributes):
    return tuple(getattr(item, attribute) for attribute in attributes)

# Get the description of our crawler
def get_UA():
    with open('../etc/user-agent.txt') as UAFile:
        return UAFile.read()

def make_log(silent):
    def log(*args, **kwargs):
        if not silent:
            print(*args, **kwargs)
    return log

# Indefinitely read stuff off of reddit
def fetch_reddit(silent=False):
    from praw.errors   import HTTPException, APIException, ClientException
    import time
    log = make_log(silent)

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
                    i = 0

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

# Download popular corpuses (corpi?) from gutenberg website
def fetch_gutenberg():
    from gutenberg.acquire import load_etext
    from gutenberg.cleanup import strip_headers
    from gutenbergsettings import popularTitles, saveInterval

    start    = time.time()
    lastsave = start

    for title in popularTitles:
        text = strip_headers(load_etext(title)).strip()
        serialize([(title, text)], '../serialized/guten%s' % title)
        sinceLast = time.time() - lastsave
        print('%s since last save' % sinceLast)
        if sinceLast > saveInterval:
            concatenate('guten')
            lastsave = time.time()

def fetch_google(begin='spiders', save_interval=10): # Start crawling from here
    from bs4    import BeautifulSoup
    from google import search, get_page
    from urllib.error import HTTPError, URLError, ContentTooShortError

    searched  = set()
    remaining = set()
    content   = dict()

    def crawl(page):
        print('Crawling %s' % page)
        if int(time.time()) % save_interval == 0:
            print('Saving')
            concatenate('google')

        try:
            searched.add(page)
            soup = BeautifulSoup(get_page(page), 'lxml')
            for paragraph in soup.find_all('p'):
                content[page] = [str(s) for s in paragraph.strings]
            serialize(content, '../serialized/google%s' % len(searched))
            content.clear()
        # If something goes wrong (on API side), throw away everything from this section of the crawl
        except HTTPError or URLError or ContentTooShortError as e: 
            print(e)
            content.clear()
            return [] # There will be plenty of other links, hopefully!
        except Exception as e:
            print('Unknown exception occurred, but we want to continue anyways, right?')
            print(e)
            content.clear()
            return []

        return [link.get('href') for link in soup.find_all('a')]

    remaining = search(begin)

    while True:
        next_remaining = set()
        for page in remaining:
            next_remaining.update(set(crawl(page)))
        remaining = next_remaining

def fetch_wikipedia(begin='spiders', save_interval=10):
    import wikipedia
    from wikipedia.exceptions import WikipediaException
    content = dict()
    seen    = set()

    def crawl(term):
        print('Crawling for %s' % term)
        seen.add(term)
        to_lookup = set()
        try:
            for item in wikipedia.search(term, results=10):
                print('Getting summary on %s' % item)
                info          = wikipedia.summary(item)
                content[item] = info
                to_lookup.update(set([word for word in info if word not in seen]))
            serialize(content, '../serialized/wiki%s' % len(seen))
            if int(time.time()) % save_interval == 0:
                print('Saving')
                concatenate('wiki')
        except WikipediaException as e:
            print(e)
        return to_lookup

    remaining = crawl(begin)
    while True:
        next_remaining = set()
        for item in remaining:
            next_remaining.update(crawl(item))
        remaining = next_remaining
        

if __name__ == '__main__':
    fetch_wikipedia()
