FROM python:3.9

WORKDIR /dnsphishing

RUN python -m pip install --upgrade pip

RUN pip install fastapi pydantic asyncio dnspython requests loguru aiohttp html_similarity

RUN pip install tldextract aiodns uvicorn

COPY ./ /dnsphishing/

EXPOSE 8081

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8081"]
