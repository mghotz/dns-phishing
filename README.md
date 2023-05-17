## Permutation.py

Permutation.py is a python script for generating similar domains (also known as permutation domains or domain permutations) for a given domain name. This script is mainly used for security testing purposes. It's a useful tool to identify potential phishing websites or domains that may be trying to impersonate your brand.

Author: Mahammad Salimov
Email: salimovm.7@gmail.com

## Features

- Generate similar domains by altering, adding, or deleting one character.
- Generate similar domains by swapping adjacent characters.
- Generate similar domains by replacing characters with similar-looking characters from different character sets (e.g., Cyrillic).
- Generate similar domains by adding popular TLDs.
- Check the existence of the domains and fetch DNS records.
- Compare the similarity between the original and similar domain webpages.

## Requirements

- Python 3.7+
- It requires the following Python packages: `itertools`, `tldextract`, `aiohttp`, `aiodns`, `dns.resolver`, `requests`, `argparse`, `html_similarity`

## How to use

1. First, install the required Python packages, using pip:

```bash
pip install -r requirements.txt
```

2. Run the script:

```bash
python permutation.py -u <URL> -sim <similarity> -c
```

Replace `<URL>` with the domain you want to scan. Replace `<similarity>` with the type of similarity you want to check. It can be either 'style', 'structural', or 'similarity'. Use `-c` to check the similarity.

Example:

```bash
python permutation.py -u www.example.com -sim style -c
```

This will generate similar domains for 'www.example.com', fetch their DNS records, get their webpage HTML, and check the style similarity with the original domain's webpage.

## Flask Web App

A flask web application is also provided for calling the script. You can run it using the following command:

```bash
flask run
```

Please ensure that you have Flask installed and configured correctly before running the command.

## Disclaimer

This script is for educational and testing purposes only. Always ensure you have proper authorization before running any security testing tools against any domains.

## License

This project is open source under the MIT license. See the [LICENSE](LICENSE) file for details.