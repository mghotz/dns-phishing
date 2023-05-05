#!/usr/bin/env python3

"""
A URL scanner that generates a list of permutations for a given domain name
and checks if each URL is responsive.

Author: Mahammad Salimov
Email: salimovm.7@gmail.com
"""


import itertools
import tldextract
import aiohttp
import asyncio
from typing import List, Dict
import requests
import argparse
from itertools import permutations

parser = argparse.ArgumentParser(description='URL Scanner')
parser.add_argument('-u', '--url', type=str, required=True, help='URL to scan')

tld_choices = ['all', 'popular']
parser.add_argument('-t', '--tld', type=str, choices=tld_choices, default='popular',
                    help=f'Choose TLDs to use in permutations (default: popular). Options: {tld_choices}')

tld_source_choices = ['iana', 'file']
parser.add_argument('-s', '--tld-source', type=str, choices=tld_source_choices, default='iana',
                    help=f'Source of TLD list (default: iana). Options: {tld_source_choices}')

args = parser.parse_args()

REQUEST_TIMEOUT = 3
REQUEST_RETRIES = 2


class Combinations:
    latin_to_cyrillic = {
        'a': 'а', 'b': 'ь', 'c': 'с', 'd': 'ԁ', 'e': 'е', 'g': 'ԍ', 'h': 'һ',
        'i': 'і', 'j': 'ј', 'k': 'к', 'l': 'ӏ', 'm': 'м', 'o': 'о', 'p': 'р',
        'q': 'ԛ', 's': 'ѕ', 't': 'т', 'v': 'ѵ', 'w': 'ԝ', 'x': 'х', 'y': 'у',
    }

    qwerty = {
        '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4', '6': '7yt5', '7': '8uy6', '8': '9iu7',
        '9': '0oi8', '0': 'po9',
        'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6ygfr5', 'y': '7uhgt6', 'u': '8ijhy7',
        'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
        'a': 'qwsz', 's': 'edxzaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft', 'h': 'ujnbgy', 'j': 'ikmnhu',
        'k': 'olmji', 'l': 'kop',
        'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
    }

    qwertz = {
        '1': '2q', '2': '3wq1', '3': '4ew2', '4': '5re3', '5': '6tr4', '6': '7zt5', '7': '8uz6', '8': '9iu7',
        '9': '0oi8', '0': 'po9',
        'q': '12wa', 'w': '3esaq2', 'e': '4rdsw3', 'r': '5tfde4', 't': '6zgfr5', 'z': '7uhgt6', 'u': '8ijhz7',
        'i': '9okju8', 'o': '0plki9', 'p': 'lo0',
        'a': 'qwsy', 's': 'edxyaw', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'zhbvft', 'h': 'ujnbgz', 'j': 'ikmnhu',
        'k': 'olmji', 'l': 'kop',
        'y': 'asx', 'x': 'ysdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhjm', 'm': 'njk'
    }

    azerty = {
        '1': '2a', '2': '3za1', '3': '4ez2', '4': '5re3', '5': '6tr4', '6': '7yt5', '7': '8uy6', '8': '9iu7',
        '9': '0oi8', '0': 'po9',
        'a': '2zq1', 'z': '3esqa2', 'e': '4rdsz3', 'r': '5tfde4', 't': '6ygfr5', 'y': '7uhgt6', 'u': '8ijhy7',
        'i': '9okju8', 'o': '0plki9', 'p': 'lo0m',
        'q': 'zswa', 's': 'edxwqz', 'd': 'rfcxse', 'f': 'tgvcdr', 'g': 'yhbvft', 'h': 'ujnbgy', 'j': 'iknhu',
        'k': 'olji', 'l': 'kopm', 'm': 'lp',
        'w': 'sxq', 'x': 'wsdc', 'c': 'xdfv', 'v': 'cfgb', 'b': 'vghn', 'n': 'bhj'
    }

    keyboards = [qwerty, qwertz, azerty]

    def __init__(self, domain_name):
        self.pem_list = []
        self.letters_numbers = 'abcdefghijklmnopqrstuvwxyz0123456789'
        self.ext = tldextract.extract(domain_name)
        self.domain = self.ext.domain
        self.tld = self.ext.suffix

    def get_tlds(self, source):
        """
        Get a list of all valid TLDs from the IANA TLD registry or a local file
        """
        if source == 'iana':
            url = 'https://data.iana.org/TLD/tlds-alpha-by-domain.txt'
            response = requests.get(url)
            tlds = response.content.decode('utf-8').split('\n')
            tlds = [tld.lower() for tld in tlds if tld and not tld.startswith('#')]
        else:
            with open('tlds.txt', 'r') as f:
                tlds = f.read().split('\n')
                tlds = [tld.lower() for tld in tlds if tld and not tld.startswith('#')]
        return tlds

    def get_popular_tlds(self):
        """
        Get a list of popular TLDs from a pre-defined list
        """
        tlds = ['com', 'org', 'net', 'edu', 'gov', 'info', 'biz', 'co', 'io', 'me', 'app', 'dev', 'tv', 'fm']
        return tlds if self.tld == 'popular' else []

    def aLetters(self):
        # Check every possibility for every letter
        for i in range(len(self.domain)):
            for letter in self.letters_numbers:
                permutation = self.domain[:i] + letter + self.domain[i + 1:] + '.' + self.tld
                self.pem_list.append(permutation)
        return self.pem_list


    def lLetters(self):
        # Add the letters that make up the word for every position
        for i in range(len(self.domain) + 1):
            for j in list(set(self.domain)):  # Use set to remove duplicates
                permutation = self.domain[:i] + j + self.domain[i:] + '.' + self.tld
                if permutation in self.pem_list:
                    continue
                self.pem_list.append(permutation)
        return self.pem_list

    def tlds(self):
        # Add TLDs to original domain
        for suffix in self.get_popular_tlds():
            permutation = self.domain + '.' + suffix
            self.pem_list.append(permutation)
        return self.pem_list

    def cyrillic(self):
        cdomain = self.domain
        for l, c in self.latin_to_cyrillic.items():
            cdomain = cdomain.replace(l, c)
            self.pem_list.append(cdomain)

        for c, l in zip(cdomain, self.domain):
            if c == l:
                continue

        return self.pem_list

    def swap_adjacent_characters(self):
        for i in range(len(self.domain) - 1):
            swapped_domain = list(self.domain)
            swapped_domain[i], swapped_domain[i + 1] = swapped_domain[i + 1], swapped_domain[i]
            permutation = "".join(swapped_domain) + "." + self.tld
            self.pem_list.append(permutation)
        return self.pem_list

    def replacement(self):
        for i, c in enumerate(self.domain):
            pre = self.domain[:i]
            suf = self.domain[i + 1:] + '.' + self.tld
            for layout in self.keyboards:
                for r in layout.get(c, ''):
                    self.pem_list.append(pre + r + suf)

        return self.pem_list

    def double_characters(self):
        for i in range(len(self.domain)):
            permutation = self.domain[:i] + self.domain[i] * 2 + self.domain[i + 1:] + '.' + self.tld
            self.pem_list.append(permutation)
        return self.pem_list

    def reverse_domain(self):
        reversed_domain = self.domain[::-1]
        permutation = reversed_domain + '.' + self.tld
        self.pem_list.append(permutation)
        return self.pem_list

class Permutation:
    def __init__(self, domain):
        self.domain_name = domain

    def generate_similar_domains(self):
        combinations = Combinations(self.domain_name)
        permutations = []

        permutations += combinations.aLetters()
        permutations += combinations.lLetters()
        permutations += combinations.tlds()
        permutations += combinations.cyrillic()
        permutations += combinations.replacement()
        permutations += combinations.swap_adjacent_characters()
        permutations += combinations.double_characters()
        permutations += combinations.reverse_domain()

        return permutations

class Scanner:
    def __init__(self, urls):
        self.urls = urls

    async def get_response(self, session, url):
        for i in range(REQUEST_RETRIES):
            try:
                async with session.get(url, timeout=REQUEST_TIMEOUT, ssl=False) as response:
                    return url, await response.text()
            except (aiohttp.InvalidURL, aiohttp.ClientConnectorError, asyncio.TimeoutError):
                continue
            except aiohttp.client_exceptions.SSLCertificateError:
                return url, None
        return url, None

    async def scan_urls(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in self.urls:
                tasks.append(asyncio.ensure_future(self.get_response(session, f"https://{url}")))
            responses = await asyncio.gather(*tasks)
            return responses


def main():
    parser = argparse.ArgumentParser(description='URL Scanner')
    parser.add_argument('-u', '--url', type=str, help='URL to scan')
    args = parser.parse_args()

    if not args.url:
        print('Please provide a URL with the -u or --url argument.')
        return

    urls = list(set(Permutation(args.url).generate_similar_domains()))

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