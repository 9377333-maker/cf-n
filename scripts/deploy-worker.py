#!/usr/bin/env python3
"""
部署 cfnew Worker（multipart 上传，含 metadata）。

用法：
    export CLOUDFLARE_TOKEN="YOUR_TOKEN"
    python3 deploy-worker.py \
        --script-name YOUR_WORKER_NAME \
        --worker-file worker/_worker.js \
        --uuid YOUR_UUID \
        [--kv-id YOUR_KV_ID] \
        [--kv-binding C] \
        [--compatibility-date 2026-01-20]

说明：
- metadata 包含 main_module、compatibility_date、bindings（KV）
- UUID 建议随后用 set-secret.py 以 secret 方式再设置一次（见 docs/05-troubleshooting.md）
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
    ap.add_argument("--worker-file", required=True)
    ap.add_argument("--uuid", required=True, help="UUID，写入 vars.u")
    ap.add_argument("--kv-id", default=None, help="KV namespace id（可选）")
    ap.add_argument("--kv-binding", default="C", help="KV 绑定名，默认 C")
    ap.add_argument("--compatibility-date", default="2026-01-20")
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

    with open(args.worker_file, "rb") as f:
        worker_code = f.read()

    metadata = {
        "main_module": "_worker.js",
        "compatibility_date": args.compatibility_date,
        "vars": {"u": args.uuid},
    }
    if args.kv_id:
        metadata["bindings"] = [
            {"type": "kv_namespace", "name": args.kv_binding, "namespace_id": args.kv_id}
        ]

    boundary = "----cfnBoundary7MA4YWxkTrZu0gW"
    parts = []
    parts.append(
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="metadata"\r\n'
        "Content-Type: application/json\r\n\r\n"
        f"{json.dumps(metadata)}\r\n".encode()
    )
    parts.append(
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="_worker.js"; filename="_worker.js"\r\n'
        "Content-Type: application/javascript+module\r\n\r\n".encode()
        + worker_code + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    body = b"".join(parts)

    req = urllib.request.Request(
        f"{API_BASE}/accounts/{args.account_id}/workers/scripts/{args.script_name}",
        data=body,
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
    )
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=60) as resp:
            result = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:1000]}", file=sys.stderr)
        sys.exit(1)

    if result.get("success"):
        print(f"部署成功: {args.script_name}")
        print(f"  deployment_id: {result['result'].get('deployment_id')}")
        print(f"  compatibility_date: {result['result'].get('compatibility_date')}")
    else:
        print("部署失败:", json.dumps(result.get("errors"), ensure_ascii=False, indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
