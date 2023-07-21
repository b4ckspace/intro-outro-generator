#!/usr/bin/env python3

from bs4 import BeautifulSoup
from sys import argv, exit, stderr

if __name__ == '__main__':
    if len(argv) < 2:
        print(f'usage: {argv[0]} <svg>', file=stderr)
        exit(1)

    with open(argv[1]) as f:
        soup = BeautifulSoup(f.read(), 'xml')

    for orbit in soup.find_all(lambda t: t.has_attr('id') and t['id'].startswith('orbit')):
        container = soup.new_tag('g', transform=f"translate({orbit['cx']} {orbit['cy']})")
        del orbit['cx']
        del orbit['cy']
        orbit.wrap(container)

    with open(argv[1], 'w') as f:
        f.write(str(soup))
