#!/usr/bin/env python3

from fetch           import fetch_reddit
from multiprocessing import Pool, TimeoutError

if __name__ == '__main__':
    pool    = Pool(processes=4)
    futures = []
    futures.append(pool.apply_async(fetch_reddit))
    for future in futures:
        future.get()


