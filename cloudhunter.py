```python
import requests
import argparse
from urllib3.exceptions import InsecureRequestWarning
import random
import time

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

COMMON_BUCKET_PATTERNS = [
    "{}",
    "{}-assets",
    "{}cdn",
    "{}-static",
    "{}backup",
    "{}-files",
    "cdn-{}",
    "{}-media",
    "{}-test",
    "{}-dev"
]

HEADERS = {
    "User-Agent": "cloudhunter/1.0 (+https://github.com/ethanfrostsec)"
}

def generate_buckets(domain):
    base = domain.replace("www.", "").split('.')[0]
    return [pattern.format(base) for pattern in COMMON_BUCKET_PATTERNS]

def check_bucket(bucket_name):
    services = {
        "AWS S3": f"http://{bucket_name}.s3.amazonaws.com",
        "Azure Blob": f"http://{bucket_name}.blob.core.windows.net",
        "Google GCS": f"http://storage.googleapis.com/{bucket_name}"
    }

    for provider, url in services.items():
        try:
            resp = requests.get(url, headers=HEADERS, timeout=8, verify=False)
            if resp.status_code in [200, 403]: # 200 = public, 403 = exists but denied
                return (provider, url, resp.status_code)
        except requests.exceptions.RequestException:
            pass
    return None

def hunt(domain, output=None):
    buckets = generate_buckets(domain)
    found = []

    print(f"\n[+] Hunting cloud buckets for: {domain}")
    for bucket in buckets:
        result = check_bucket(bucket)
        if result:
            provider, url, code = result
            print(f"[✓] {provider}: {url} ({code})")
            found.append(f"{provider}: {url} ({code})")
        else:
            print(f"[x] Not Found: {bucket}")
        time.sleep(random.uniform(0.5, 1.5)) # stealth mode

    if output:
        with open(output, 'w') as f:
            f.write('\n'.join(found))
        print(f"\n[+] Results saved to {output}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cloud Storage Bucket Hunter")
    parser.add_argument("domain", help="Target base domain (e.g. example.com)")
    parser.add_argument("-o", "--output", help="Save found results to file")
    args = parser.parse_args()

    hunt(args.domain, args.output)
```
