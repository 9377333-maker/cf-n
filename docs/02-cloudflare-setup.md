# 02 — Cloudflare 账号 / Token / Zone 配置

## API Token 权限

在 Cloudflare Dashboard → My Profile → API Tokens → Create Token，所需权限：

| 权限组 | 权限 | 用途 |
|--------|------|------|
| Zone | Zone:Edit | 创建 Zone、管理 DNS |
| Zone | DNS:Edit | 添加/删除 DNS 记录 |
| Account | Workers Scripts:Edit | 部署 Worker |
| Account | Workers KV Storage:Edit | 创建 KV |
| Account | Pages:Edit | （如用 Pages，可选） |

> **注意**：Token 自身**没有删除自己的权限**（API 返回 9109 错误）。
> 用完后需手动去 Dashboard → API Tokens 删除。

## 创建 Zone

```bash
export CLOUDFLARE_TOKEN="YOUR_TOKEN"

# 创建 zone（以 bssq.cc.cd 为例）
python3 scripts/cf-api.py POST /zones '{"name":"YOUR_DOMAIN","account":{"id":"YOUR_ACCOUNT_ID"}}'
```

返回中记录：
- `zone_id`（如 `c53cf3418e824dd5dba7472b88f97ff9`）
- `name_servers`（如 `dax.ns.cloudflare.com`、`kehlani.ns.cloudflare.com`）

## 获取 Account ID

```bash
python3 scripts/cf-api.py GET /accounts
```

## NS 回填与验证

1. 把 Cloudflare 分配的 2 个 NS 填回 DNSHE（见 01 章）
2. 等待几分钟后验证：

```bash
# DoH 查询 NS 是否生效
curl -s "https://cloudflare-dns.com/dns-query?name=YOUR_DOMAIN&type=NS" \
  -H "accept: application/dns-json" | python3 -c "
import sys, json
d = json.load(sys.stdin)
for a in d.get('Answer', []):
    print(a['data'])
"
```

3. 查 Zone 状态：

```bash
python3 scripts/cf-api.py GET /zones/YOUR_ZONE_ID
# status 应为 "active"
```

> Zone 为 `pending` 时是正常的，等 Cloudflare 验证 NS，无需人工操作。

## 验证步骤

- [ ] Token 创建成功，权限包含上表 5 项
- [ ] Zone 创建成功，拿到 `zone_id`
- [ ] DNSHE 的 NS 已改为 Cloudflare 分配的 NS
- [ ] DoH 查询返回 Cloudflare NS
- [ ] Zone 状态为 `active`
- [ ] （部署完成后）手动删除临时 Token
