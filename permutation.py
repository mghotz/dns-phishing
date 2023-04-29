import itertools
import tldextract
import aiohttp
import asyncio
from typing import List, Dict
import requests
import argparse
from itertools import permutations

# create parser object
parser = argparse.ArgumentParser(description='URL Scanner')

# add arguments to the parser
parser.add_argument('-u', '--url', type=str, required=True, help='URL to scan')

# parse the arguments
args = parser.parse_args()

REQUEST_TIMEOUT = 3
REQUEST_RETRIES = 2


class Permutation:
    def __init__(self, domain):
        self.domain_name = domain

    def get_tlds(self):
        """
        Get a list of all valid TLDs from the IANA TLD registry
        """
        url = 'https://data.iana.org/TLD/tlds-alpha-by-domain.txt'
        response = requests.get(url)
        tlds = response.content.decode('utf-8').split('\n')
        tlds = [tld.lower() for tld in tlds if tld and not tld.startswith('#')]
        return tlds

    def get_popular_tlds(self):
        """
        Get a list of popular TLDs from a pre-defined list
        """
        tlds = ['com', 'org', 'net', 'edu', 'gov', 'info', 'biz', 'co', 'io', 'me', 'app', 'dev', 'tv', 'fm']
        return tlds

    def generate_similar_domains(self):
        # Get the original domain and suffix
        ext = tldextract.extract(self.domain_name)
        domain, tld = ext.domain, ext.suffix

        letters_numbers = 'abcdefghijklmnopqrstuvwxyz0123456789'
        permutations = []

        for i in range(len(domain)):
            for letter in letters_numbers:
                permutation = domain[:i] + letter + domain[i + 1:] + '.' + tld
                permutations.append(permutation)

        for suffix in self.get_popular_tlds():
            permutation = domain + '.' + suffix
            permutations.append(permutation)

        return permutations

class Scanner:
    def __init__(self, urls):
        self.urls = urls

    async def get_response(self, session, url):
        try:
            async with session.get(url, timeout=REQUEST_TIMEOUT) as response:
                return url, await response.text()
        except (aiohttp.InvalidURL, aiohttp.ClientConnectorError, asyncio.TimeoutError):
            return url, None

    async def scan_urls(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in self.urls:
                tasks.append(asyncio.ensure_future(self.get_response(session, url)))
            responses = await asyncio.gather(*tasks)
            return responses


def main():
    parser = argparse.ArgumentParser(description='URL Scanner')
    parser.add_argument('-u', '--url', type=str, help='URL to scan')
    args = parser.parse_args()

    if not args.url:
        print('Please provide a URL with the -u or --url argument.')
        return

    urls = Permutation(args.url).generate_similar_domains()

    scanner = Scanner(urls)
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(scanner.scan_urls())

    for url, response in responses:
        if response:
            print(f'{url} returned response: {response[:50]}...')
        else:
            print(f'{url} did not return a response.')


if __name__ == '__main__':
    main()