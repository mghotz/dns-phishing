# URL Scanner

This is a Python script for scanning a URL and its permutations to see if they return a response. It uses the aiohttp library for making asynchronous HTTP requests.

## Getting started

### Prerequisites

- Python 3.x
- aiohttp library
- requests library

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/<username>/url-scanner.git
   ```
2. Install the required libraries:
   ```sh
   pip install aiohttp requests
   ```

### Usage

To scan a URL, run the `scanner.py` script with the `-u` or `--url` argument followed by the URL you want to scan:
```sh
python scanner.py -u https://example.com
```

The script will generate permutations of the URL and scan each permutation to see if it returns a response. If a response is returned, the script will print the URL and the first 50 characters of the response. If no response is returned, the script will print the URL and a message indicating that no response was returned.

### Options

The following options are available:

- `-u`, `--url`: The URL to scan (required).
- `-t`, `--tlds`: The top-level domains to use for generating permutations (comma-separated).
- `-a`, `--all-tlds`: Use all valid TLDs for generating permutations.
- `-r`, `--retries`: The number of times to retry failed requests (default is 2).
- `-T`, `--timeout`: The timeout for each request (default is 3 seconds).

### Examples

Scan a URL with the default options:
```sh
python scanner.py -u https://example.com
```

Scan a URL with all valid TLDs:
```sh
python scanner.py -u https://example.com -a
```

Scan a URL with a specific set of TLDs:
```sh
python scanner.py -u https://example.com -t com,net,org
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

- Name: Mahammad Salimov
- Email: salimovm.7@gmail.com

If you have any questions or feedback, please feel free to contact me.