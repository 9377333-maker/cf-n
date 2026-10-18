#!/usr/bin/env python3
"""
Cloudflare API 通用 helper。

用法：
    export CLOUDFLARE_TOKEN="YOUR_TOKEN"
    python3 cf-api.py GET /accounts
    python3 cf-api.py POST /zones '{"name":"example.com","account":{"id":"..."}}'
    python3 cf-api.py DELETE /zones/ZONE_ID/dns_records/RECORD_ID

Token 从环境变量 CLOUDFLARE_TOKEN 读取，不依赖任何特定连接器。
"""
import json
import os
import sys
import urllib.request
import urllib.error


API_BASE = "https://api.cloudflare.com/client/v4"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def api(method, path, data=None):
    token = os.environ.get("CLOUDFLARE_TOKEN")
    if not token:
        print("ERROR: 环境变量 CLOUDFLARE_TOKEN 未设置", file=sys.stderr)
        sys.exit(1)
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(
        API_BASE + path,
        data=body,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:1000]}", file=sys.stderr)
        sys.exit(1)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    method = sys.argv[1].upper()
    path = sys.argv[2]
    data = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
    print(json.dumps(api(method, path, data), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
