from typing import Optional
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from permutation import Permutation, Scanner
import asyncio
import dns.resolver
import requests
import nest_asyncio
import aiohttp
from loguru import logger
import sys
from html_similarity import style_similarity, structural_similarity, similarity
import json
nest_asyncio.apply()


logger.remove()
logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | {level} | <level>{message}</level>")

app = FastAPI()

class Domain(BaseModel):
    domain: str
    callback_url: str
    style: Optional[str] = 'style'
    style_check: Optional[bool] = False


async def process(scanner, original_domain, original_similarity, original_similarity_check, callback_url):
    tasks = []
    response = []
    # Push urls to resolve A record of DNS
    for url in scanner.urls:
        tasks.append(asyncio.ensure_future(scanner.get_dns_records(url, 'A')))

    dns_records = await asyncio.gather(*tasks)
    records = [{'url': e_url[0], 'A': e_url[1]} for e_url in dns_records if e_url[1]]

    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in records:
            tasks.append(asyncio.ensure_future(scanner.get_response(session, url['url'])))
        htmls  = await asyncio.gather(*tasks)

    original_domain_html = requests.get("https://{}".format(original_domain)).text
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
            logger.info(response)
    
    requests.post(callback_url, json=response)
    return json.dumps(response)

@app.post("/scan/")
async def scan_domains(background_tasks: BackgroundTasks, domain: Domain):
    original_domain = domain.domain
    original_similarity = domain.style 
    original_similarity_check = domain.style_check or True
    callback_url = domain.callback_url
    urls = Permutation(original_domain).generate_similar_domains()
    urls = list(set(urls))
    scanner = Scanner(urls)
    background_tasks.add_task(process, scanner, original_domain, original_similarity, original_similarity_check, callback_url)

    return {"result": "Success"}
