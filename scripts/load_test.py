"""Read-only load check against local server; no data mutations."""
import argparse
import json
import statistics
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8000')
    args = parser.parse_args()
    paths = ['/', '/halls/', '/exhibitions/', '/statistics/', '/health/']

    def request(index):
        start = time.perf_counter()
        with urllib.request.urlopen(args.url + paths[index % len(paths)],
                                    timeout=15) as response:
            response.read()
            return response.status, (time.perf_counter() - start) * 1000

    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(request, range(100)))
    elapsed = time.perf_counter() - start
    latencies = sorted(value for _, value in results)
    report = {
        'requests': 100, 'workers': 8,
        'successful': sum(status == 200 for status, _ in results),
        'elapsed_seconds': round(elapsed, 3),
        'requests_per_second': round(100 / elapsed, 2),
        'median_ms': round(statistics.median(latencies), 2),
        'p95_ms': round(latencies[94], 2),
        'scope': 'Local smoke load test, not a production capacity estimate',
    }
    target = Path('docs/evidence/load-test.json')
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2),
                      encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False))
    if report['successful'] != 100:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
