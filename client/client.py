"""Send each request over a new connection to the Kubernetes Service DNS name."""

import argparse
from collections import Counter
import json
import os
import time
import urllib.error
import urllib.request


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=0, help="0 means run continuously")
    parser.add_argument("--interval", type=float, default=1)
    parser.add_argument("--expect", nargs="*", default=[])
    parser.add_argument("--exclude", nargs="*", default=[])
    parser.add_argument("--allow-errors", action="store_true")
    args = parser.parse_args()
    if args.count < 0 or args.interval < 0:
        parser.error("count and interval must be nonnegative")
    url = os.environ.get("INVENTORY_URL", "http://inventory:5001").rstrip("/")
    url += "/v1/items/sku-123"
    # Ignore host HTTP proxy settings for cluster-local DNS.
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    counts = Counter()
    errors = 0
    sequence = 0
    while args.count == 0 or sequence < args.count:
        sequence += 1
        try:
            request = urllib.request.Request(url, headers={"Connection": "close"})
            with opener.open(request, timeout=3) as response:
                item = json.load(response)
            counts[item["pod"]] += 1
            print(json.dumps({"request": sequence, "url": url, **item}), flush=True)
        except (urllib.error.URLError, OSError, ValueError, KeyError) as error:
            errors += 1
            print(json.dumps({"request": sequence, "url": url, "error": str(error)}), flush=True)
        if args.count == 0 or sequence < args.count:
            time.sleep(args.interval)
    print(json.dumps({"summary": dict(counts), "errors": errors}), flush=True)
    missing = set(args.expect) - counts.keys()
    excluded = set(args.exclude) & counts.keys()
    if not counts or missing or excluded or (errors and not args.allow_errors):
        raise SystemExit(f"FAIL: missing={sorted(missing)}, excluded={sorted(excluded)}, errors={errors}")


if __name__ == "__main__":
    main()
