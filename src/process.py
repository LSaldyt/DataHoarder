#!/usr/bin/env python3

from fetch        import fetch_reddit, fetch_gutenberg, fetch_google, fetch_wikipedia
from multiprocess import Pool, TimeoutError
    #fetch_google({'https://en.wikipedia.org/wiki/Spider'})
    #fetch_wikipedia({'spiders'})

if __name__ == '__main__':
    pool    = Pool(processes=4)
    futures = []
    launch = lambda f, args=() : futures.append(pool.apply_async(f, args))
    launch(fetch_google, ({'https://en.wikipedia.org/wiki/Spider'},))
    launch(fetch_reddit, (True, ))
    launch(fetch_wikipedia, ('spiders'))
    for future in futures:
        future.get()


