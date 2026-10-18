#!/usr/bin/env python3
"""
以 secret 方式设置 Worker 变量（推荐用于 UUID）。

用法：
    export CLOUDFLARE_TOKEN="YOUR_TOKEN"
    python3 set-secret.py --script-name YOUR_WORKER_NAME --name u --value YOUR_UUID

背景：通过 multipart metadata 传的普通 vars 有时不被面板识别（见 docs/05-troubleshooting.md），
secret 方式优先级更高、更可靠。
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

API_BASE = "https://api.cloudflare.com/client/v4"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args):
        raise RuntimeError("redirect refused, verify the endpoint")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script-name", required=True)
    ap.add_argument("--name", required=True, help="变量名，如 u")
    ap.add_argument("--value", required=True, help="变量值")
    ap.add_argument("--account-id", default=os.environ.get("CF_ACCOUNT_ID"),
                    help="也可用环境变量 CF_ACCOUNT_ID")
    args = ap.parse_args()

    token = os.environ.get("CLOUDFLARE_TOKEN")
    if not token:
        print("ERROR: 环境变量 CLOUDFLARE_TOKEN 未设置", file=sys.stderr)
        sys.exit(1)
    if not args.account_id:
        print("ERROR: 需提供 --account-id 或环境变量 CF_ACCOUNT_ID", file=sys.stderr)
        sys.exit(1)

    body = json.dumps({
        "name": args.name,
        "text": args.value,
        "type": "secret_text",
    }).encode()
    req = urllib.request.Request(
        f"{API_BASE}/accounts/{args.account_id}/workers/scripts/{args.script_name}/secrets",
        data=body,
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=30) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:1000]}", file=sys.stderr)
        sys.exit(1)

    if result.get("success"):
        print(f"secret 设置成功: {args.name} -> {args.script_name}")
    else:
        print("设置失败:", json.dumps(result.get("errors"), ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
