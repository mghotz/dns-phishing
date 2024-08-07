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
import aiodns
import dns.resolver
from typing import List, Dict
import json
import requests
import argparse
from itertools import permutations
from html_similarity import style_similarity, structural_similarity, similarity


REQUEST_TIMEOUT = 3
REQUEST_RETRIES = 2


class Combinations:
    latin_to_cyrillic = {
        'a': 'а', 'b': 'ь', 'c': 'с', 'd': 'ԁ', 'e': 'е', 'g': 'ԍ', 'h': 'һ',
        'i': 'і', 'j': 'ј', 'k': 'к', 'l': 'ӏ', 'm': 'м', 'o': 'о', 'p': 'р',
        'q': 'ԛ', 's': 'ѕ', 't': 'т', 'v': 'ѵ', 'w': 'ԝ', 'x': 'х', 'y': 'у',
    }

    glyphs_idn_by_tld = {
        **dict.fromkeys(['ad', 'cz', 'sk', 'uk', 'co.uk', 'nl', 'edu', 'us'], {}),
        **dict.fromkeys(['jp', 'co.jp', 'ad.jp', 'ne.jp'], {}),
        **dict.fromkeys(['cn', 'com.cn', 'tw', 'com.tw', 'net.tw'], {}),
        **dict.fromkeys(['info'], {
            'a': ('á', 'ä', 'å', 'ą'),
            'c': ('ć', 'č'),
            'e': ('é', 'ė', 'ę'),
            'i': ('í', 'į'),
            'l': ('ł',),
            'n': ('ñ', 'ń'),
            'o': ('ó', 'ö', 'ø', 'ő'),
            's': ('ś', 'š'),
            'u': ('ú', 'ü', 'ū', 'ű', 'ų'),
            'z': ('ź', 'ż', 'ž'),
            'ae': ('æ',),
        }),
        **dict.fromkeys(['br', 'com.br'], {
            'a': ('à', 'á', 'â', 'ã'),
            'c': ('ç',),
            'e': ('é', 'ê'),
            'i': ('í',),
            'o': ('ó', 'ô', 'õ'),
            'u': ('ú', 'ü'),
            'y': ('ý', 'ÿ'),
        }),
        **dict.fromkeys(['dk'], {
            'a': ('ä', 'å'),
            'e': ('é',),
            'o': ('ö', 'ø'),
            'u': ('ü',),
            'ae': ('æ',),
        }),
        **dict.fromkeys(['eu', 'de', 'pl'], {
            'a': ('á', 'à', 'ă', 'â', 'å', 'ä', 'ã', 'ą', 'ā'),
            'c': ('ć', 'ĉ', 'č', 'ċ', 'ç'),
            'd': ('ď', 'đ'),
            'e': ('é', 'è', 'ĕ', 'ê', 'ě', 'ë', 'ė', 'ę', 'ē'),
            'g': ('ğ', 'ĝ', 'ġ', 'ģ'),
            'h': ('ĥ', 'ħ'),
            'i': ('í', 'ì', 'ĭ', 'î', 'ï', 'ĩ', 'į', 'ī'),
            'j': ('ĵ',),
            'k': ('ķ', 'ĸ'),
            'l': ('ĺ', 'ľ', 'ļ', 'ł'),
            'n': ('ń', 'ň', 'ñ', 'ņ'),
            'o': ('ó', 'ò', 'ŏ', 'ô', 'ö', 'ő', 'õ', 'ø', 'ō'),
            'r': ('ŕ', 'ř', 'ŗ'),
            's': ('ś', 'ŝ', 'š', 'ş'),
            't': ('ť', 'ţ', 'ŧ'),
            'u': ('ú', 'ù', 'ŭ', 'û', 'ů', 'ü', 'ű', 'ũ', 'ų', 'ū'),
            'w': ('ŵ',),
            'y': ('ý', 'ŷ', 'ÿ'),
            'z': ('ź', 'ž', 'ż'),
            'ae': ('æ',),
            'oe': ('œ',),
        }),
        **dict.fromkeys(['fi'], {
            '3': ('ʒ',),
            'a': ('á', 'ä', 'å', 'â'),
            'c': ('č',),
            'd': ('đ',),
            'g': ('ǧ', 'ǥ'),
            'k': ('ǩ',),
            'n': ('ŋ',),
            'o': ('õ', 'ö'),
            's': ('š',),
            't': ('ŧ',),
            'z': ('ž',),
        }),
        **dict.fromkeys(['no'], {
            'a': ('á', 'à', 'ä', 'å'),
            'c': ('č', 'ç'),
            'e': ('é', 'è', 'ê'),
            'i': ('ï',),
            'n': ('ŋ', 'ń', 'ñ'),
            'o': ('ó', 'ò', 'ô', 'ö', 'ø'),
            's': ('š',),
            't': ('ŧ',),
            'u': ('ü',),
            'z': ('ž',),
            'ae': ('æ',),
        }),
        **dict.fromkeys(['be', 'fr', 're', 'yt', 'pm', 'wf', 'tf', 'ch', 'li'], {
            'a': ('à', 'á', 'â', 'ã', 'ä', 'å'),
            'c': ('ç',),
            'e': ('è', 'é', 'ê', 'ë'),
            'i': ('ì', 'í', 'î', 'ï'),
            'n': ('ñ',),
            'o': ('ò', 'ó', 'ô', 'õ', 'ö'),
            'u': ('ù', 'ú', 'û', 'ü'),
            'y': ('ý', 'ÿ'),
            'ae': ('æ',),
            'oe': ('œ',),
        }),
        **dict.fromkeys(['ca'], {
            'a': ('à', 'â'),
            'c': ('ç',),
            'e': ('è', 'é', 'ê', 'ë'),
            'i': ('î', 'ï'),
            'o': ('ô',),
            'u': ('ù', 'û', 'ü'),
            'y': ('ÿ',),
            'ae': ('æ',),
            'oe': ('œ',),
        }),
    }

    glyphs_unicode = {
        '2': ('ƻ',),
        '3': ('ʒ',),
        '5': ('ƽ',),
        'a': ('ạ', 'ă', 'ȧ', 'ɑ', 'å', 'ą', 'â', 'ǎ', 'á', 'ə', 'ä', 'ã', 'ā', 'à'),
        'b': ('ḃ', 'ḅ', 'ƅ', 'ʙ', 'ḇ', 'ɓ'),
        'c': ('č', 'ᴄ', 'ċ', 'ç', 'ć', 'ĉ', 'ƈ'),
        'd': ('ď', 'ḍ', 'ḋ', 'ɖ', 'ḏ', 'ɗ', 'ḓ', 'ḑ', 'đ'),
        'e': ('ê', 'ẹ', 'ę', 'è', 'ḛ', 'ě', 'ɇ', 'ė', 'ĕ', 'é', 'ë', 'ē', 'ȩ'),
        'f': ('ḟ', 'ƒ'),
        'g': ('ǧ', 'ġ', 'ǵ', 'ğ', 'ɡ', 'ǥ', 'ĝ', 'ģ', 'ɢ'),
        'h': ('ȟ', 'ḫ', 'ḩ', 'ḣ', 'ɦ', 'ḥ', 'ḧ', 'ħ', 'ẖ', 'ⱨ', 'ĥ'),
        'i': ('ɩ', 'ǐ', 'í', 'ɪ', 'ỉ', 'ȋ', 'ɨ', 'ï', 'ī', 'ĩ', 'ị', 'î', 'ı', 'ĭ', 'į', 'ì'),
        'j': ('ǰ', 'ĵ', 'ʝ', 'ɉ'),
        'k': ('ĸ', 'ǩ', 'ⱪ', 'ḵ', 'ķ', 'ᴋ', 'ḳ'),
        'l': ('ĺ', 'ł', 'ɫ', 'ļ', 'ľ'),
        'm': ('ᴍ', 'ṁ', 'ḿ', 'ṃ', 'ɱ'),
        'n': ('ņ', 'ǹ', 'ń', 'ň', 'ṅ', 'ṉ', 'ṇ', 'ꞑ', 'ñ', 'ŋ'),
        'o': ('ö', 'ó', 'ȯ', 'ỏ', 'ô', 'ᴏ', 'ō', 'ò', 'ŏ', 'ơ', 'ő', 'õ', 'ọ', 'ø'),
        'p': ('ṗ', 'ƿ', 'ƥ', 'ṕ'),
        'q': ('ʠ',),
        'r': ('ʀ', 'ȓ', 'ɍ', 'ɾ', 'ř', 'ṛ', 'ɽ', 'ȑ', 'ṙ', 'ŗ', 'ŕ', 'ɼ', 'ṟ'),
        's': ('ṡ', 'ș', 'ŝ', 'ꜱ', 'ʂ', 'š', 'ś', 'ṣ', 'ş'),
        't': ('ť', 'ƫ', 'ţ', 'ṭ', 'ṫ', 'ț', 'ŧ'),
        'u': ('ᴜ', 'ų', 'ŭ', 'ū', 'ű', 'ǔ', 'ȕ', 'ư', 'ù', 'ů', 'ʉ', 'ú', 'ȗ', 'ü', 'û', 'ũ', 'ụ'),
        'v': ('ᶌ', 'ṿ', 'ᴠ', 'ⱴ', 'ⱱ', 'ṽ'),
        'w': ('ᴡ', 'ẇ', 'ẅ', 'ẃ', 'ẘ', 'ẉ', 'ⱳ', 'ŵ', 'ẁ'),
        'x': ('ẋ', 'ẍ'),
        'y': ('ŷ', 'ÿ', 'ʏ', 'ẏ', 'ɏ', 'ƴ', 'ȳ', 'ý', 'ỿ', 'ỵ'),
        'z': ('ž', 'ƶ', 'ẓ', 'ẕ', 'ⱬ', 'ᴢ', 'ż', 'ź', 'ʐ'),
        'ae': ('æ',),
        'oe': ('œ',),
    }

    glyphs_ascii = {
        '0': ('o',),
        '1': ('l', 'i'),
        '3': ('8',),
        '6': ('9',),
        '8': ('3',),
        '9': ('6',),
        'b': ('d', 'lb'),
        'c': ('e',),
        'd': ('b', 'cl', 'dl'),
        'e': ('c',),
        'g': ('q',),
        'h': ('lh'),
        'i': ('1', 'l'),
        'k': ('lc'),
        'l': ('1', 'i'),
        'm': ('n', 'nn', 'rn'),
        'n': ('m', 'r'),
        'o': ('0',),
        'q': ('g',),
        'w': ('vv',),
        'rn': ('m',),
        'cl': ('d',),
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
        tlds = ['com', 'org', 'net', 'edu', 'gov', 'info', 'biz', 'co', 'io', 'me', 'app', 'dev', 'tv', 'fm', 'am', 'de', 'ru', 'ag', 'cn', 'br', 'uk', 'it', 'tk', 'cf', 'az', 'xyz', 'sh']
        return tlds

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
        # for suffix in self.get_tlds('iana'):
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

    def missed_character(self):
        for i in range(len(self.domain)):
            new_domain = self.domain[:i] + self.domain[i+1:] + '.' + self.tld
            self.pem_list.append(new_domain)
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

    def insertion(self):
        for i in range(1, len(self.domain)-1):
            prefix, orig_c = self.domain[:i], self.domain[i]
            for c in (c for keys in self.keyboards for c in keys.get(orig_c, [])):
                self.pem_list.append(prefix + c + orig_c + self.tld)
                self.pem_list.append(prefix + orig_c + c + self.tld)
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

    def glyphs_idn(self):
        tld_glyphs = self.glyphs_idn_by_tld.get(self.tld, {})
        for i, c in enumerate(self.domain):
            pre = self.domain[:i]
            suf = self.domain[i + 1:] + '.' + self.tld
            for g in tld_glyphs.get(c, ()):
                self.pem_list.append(pre + g + suf)
        return self.pem_list

    def glyphs_unicodes(self):
        for i, c in enumerate(self.domain):
            pre = self.domain[:i]
            suf = self.domain[i + 1:] + '.' + self.tld
            for g in self.glyphs_unicode.get(c, ()):
                self.pem_list.append(pre + g + suf)
        return self.pem_list

    def glyphs_asciis(self):
        for i, c in enumerate(self.domain):
            pre = self.domain[:i]
            suf = self.domain[i + 1:] + '.' + self.tld
            for g in self.glyphs_ascii.get(c, ()):
                self.pem_list.append(pre + g + suf)
        return self.pem_list


class Permutation:
    def __init__(self, domain):
        self.domain_name = domain

    def generate_similar_domains(self):
        combinations = Combinations(self.domain_name)
        permutations = []

        permutations += combinations.cyrillic()
        permutations += combinations.aLetters()
        permutations += combinations.lLetters()
        permutations += combinations.tlds()
        permutations += combinations.replacement()
        permutations += combinations.swap_adjacent_characters()
        permutations += combinations.double_characters()
        permutations += combinations.reverse_domain()
        permutations += combinations.missed_character()
        permutations += combinations.insertion()
        permutations += combinations.glyphs_idn()
        permutations += combinations.glyphs_unicodes()
        permutations += combinations.glyphs_asciis()
        
        return permutations


class Scanner:
    def __init__(self, urls):
        self.urls = urls
        self.resolver = aiodns.DNSResolver(timeout=0.1)

    async def get_dns_records(self, domain, record_type):
        try:
            result = await self.resolver.query(domain, record_type)
            return domain, result
        except Exception as e:
            return domain, None

    async def get_response(self, session, url):
        for i in range(REQUEST_RETRIES):
            try:
                async with session.get(f"https://{url}", timeout=REQUEST_TIMEOUT, ssl=False) as response:
                    return url, await response.text()
            except (aiohttp.InvalidURL, aiohttp.ClientConnectorError, asyncio.TimeoutError):
                continue
            except aiohttp.client_exceptions.SSLCertificateError:
                return url, None
        return url, None

    async def scan_domains(self):
        tasks = []
        for url in self.urls:
            tasks.append(asyncio.ensure_future(self.get_dns_records(url, 'A')))
        dns_records = await asyncio.gather(*tasks)
        
        existed_urls = [{'url': e_url[0], 'A': e_url[1]} for e_url in dns_records if e_url[1]]
        async with aiohttp.ClientSession() as session:
            tasks = []
            for url in existed_urls:
                tasks.append(asyncio.ensure_future(self.get_response(session, url['url'])))
            responses = await asyncio.gather(*tasks)
            return responses, existed_urls


def main(original_domain=False, original_similarity=False, original_similarity_check=False):
    if not original_domain:
        parser = argparse.ArgumentParser(description='URL Scanner')
        parser.add_argument('-u', '--url', type=str, help='URL to scan')

        similarity_choices = ['style', 'structural', 'similarity']
        parser.add_argument('-sim', '--similarity', type=str, choices=similarity_choices, default='style')

        parser.add_argument('-c', '--similaritycheck', action="store_true", help='Check similarity')

        args = parser.parse_args()

    original_domain = original_domain or args.url
    original_similarity = original_similarity or args.similarity
    original_similarity_check = original_similarity_check or args.similaritycheck

    if not original_domain:
        print('Please provide a URL with the -u or --url argument.')
        return

    urls = Permutation(original_domain).generate_similar_domains()
    
    urls = list(set(urls))
    scanner = Scanner(urls)
    loop = asyncio.get_event_loop()
    responses = loop.run_until_complete(scanner.scan_domains())
    original_domain_html = requests.get("https://{}".format(original_domain)).text
    response = []
    records  = responses[1]
    htmls = responses[0]
    
    for record in records:
        if record['url'] != original_domain:
            f_domain = record['url']
            a_records = []
            mx_records = []
            ns_records = []
            for a in record['A']:
                a_records.append(a.host)
            
            try:
                for mx in dns.resolver.resolve(f_domain, 'MX'):
                    mx_records.append(mx.to_text())
            except:
                pass
            try:
                for ns in dns.resolver.resolve(f_domain, 'NS'):
                    ns_records.append(ns.to_text())
            except:
                pass
            
            sim = False
            if original_similarity_check:
                f_html = [i[1] for i in htmls if i[0] == f_domain]
                if len(f_html) > 0 and f_html[0]:
                    get_html = f_html[0]
                    if original_similarity == 'style':
                        sim = style_similarity(original_domain_html, get_html)
                    elif original_similarity == 'structural':
                        sim = structural_similarity(original_domain_html, get_html)
                    else:
                        sim_style = style_similarity(original_domain_html, get_html)
                        sim_structural = structural_similarity(original_domain_html, get_html)
                        sim = (sim_style + sim_structural) / 2

                    sim = round((sim * 100), 2)

            response.append({
                'domain': f_domain,
                'a_records': a_records,
                'mx_records': mx_records,
                'ns_records': ns_records,
                'similarity': sim
            })

    return response


if __name__ == '__main__':
    main()
