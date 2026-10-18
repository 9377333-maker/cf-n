# 03 — cfnew Worker 部署

## 项目介绍

- 仓库：https://github.com/byJoey/cfnew
- 分支：`core-only`（精简内核，仅 37KB）
- 功能：VLESS over WebSocket / Trojan over WebSocket / VLESS XHTTP 代理
- 本项目 `worker/_worker.js` 即该分支最新版

## 关键配置

| 项 | 值 | 说明 |
|----|-----|------|
| 兼容日期 | `2026-01-20` | 必须，否则部分 API 不可用 |
| 变量 `u` | `YOUR_UUID` | **必填**，标准 8-4-4-4-12 格式 UUID；既是代理认证凭据，也是面板登录凭据 |
| KV 绑定 | 绑定名 `C` | 必选，面板在线保存配置用 |

> **重要**：`u` 建议用 **secret 方式**设置。用普通 vars 方式时，面板可能连接失败（实测）。
> 生成 UUID：`python3 -c "import uuid; print(uuid.uuid4())"`

## 部署步骤（纯 API）

### 1. 上传 Worker（含 vars、KV、兼容日期）

```bash
export CLOUDFLARE_TOKEN="YOUR_TOKEN"
export CF_ACCOUNT_ID="YOUR_ACCOUNT_ID"

python3 scripts/deploy-worker.py \
  --script-name YOUR_WORKER_NAME \
  --worker-file worker/_worker.js \
  --uuid YOUR_UUID \
  --kv-id YOUR_KV_ID \          # 必选
  --compatibility-date 2026-01-20
```

脚本使用 `PUT /accounts/{id}/workers/scripts/{name}`，multipart 上传，
metadata 中包含 `main_module`、`compatibility_date`、`vars`、`bindings`。

### 2. 用 secret 方式设置 UUID（推荐）

```bash
python3 scripts/set-secret.py \
  --script-name YOUR_WORKER_NAME \
  --name u \
  --value YOUR_UUID
```

调用 `PUT /accounts/{id}/workers/scripts/{name}/secrets`。

### 3. 创建 KV（必选）

```bash
# 创建
python3 scripts/cf-api.py POST /accounts/YOUR_ACCOUNT_ID/storage/kv/namespaces \
  '{"title":"YOUR_KV_NAME"}'
# 记录返回的 id，部署时作为 --kv-id 传入（绑定名固定为 C）
```

### 4. 绑定自定义域名

```bash
# 4a. 添加 Workers Route
python3 scripts/cf-api.py POST /zones/YOUR_ZONE_ID/workers/routes \
  '{"pattern":"YOUR_DOMAIN/*","script":"YOUR_WORKER_NAME"}'

# 4b. 添加 DNS A 记录（占位 IP，必须 proxied）
python3 scripts/cf-api.py POST /zones/YOUR_ZONE_ID/dns_records \
  '{"type":"A","name":"YOUR_SUBDOMAIN","content":"192.0.2.1","proxied":true}'
```

> `192.0.2.1` 是占位 IP，实际流量由 Workers Route 接管。`proxied` 必须为 `true`。

## 验证步骤

- [ ] `curl https://YOUR_DOMAIN/` 返回 `hello`
- [ ] 面板能用域名 + UUID 正常连接（见 04 章）
- [ ] `GET /accounts/{id}/workers/scripts/{name}/settings` 显示 KV 绑定（`bindings` 非空）
- [ ] 兼容日期为 `2026-01-20`
