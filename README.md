# cf-n — CFnew 一键部署文档项目

整理自 2026-10-18 实际部署全流程。目标：任何没参与过的 Agent 照着文档能独立复现整套部署。

## 架构

```
┌─────────────┐     NS 托管      ┌──────────────────┐
│   DNSHE     │ ──────────────▶ │   Cloudflare     │
│ 免费域名    │                 │  DNS + Workers   │
│ (cc.cd)     │                 └────────┬─────────┘
└─────────────┘                          │
                                         │ Workers Route
                                         ▼
┌─────────────┐                 ┌──────────────────┐
│   Vercel    │                 │  Worker          │
│  管理面板   │ ─── API 调用 ──▶ │  333-lovie       │
│ (cfnew-panel)│                │  代理内核 37KB   │
└─────────────┘                 └──────────────────┘
       ▲                                 ▲
       │ 订阅链接                         │ VLESS/WS 流量
       └─────────────────────────────────┘
                    客户端 (Shadowrocket 等)
```

| 组件 | 作用 | 部署位置 |
|------|------|----------|
| DNSHE 免费域名 | 域名注册 + NS 托管 | dnshe.com |
| Cloudflare Worker `333-lovie` | cfnew 精简内核，实际代理流量 | Cloudflare |
| Vercel Panel | 管理面板：配置、订阅生成 | Vercel |
| Cloudflare KV | 面板在线保存配置 | Cloudflare |

## 目录结构

```
cf-n/
├── README.md                 # 本文件
├── docs/
│   ├── 01-domain-dnshe.md    # DNSHE 免费域名注册
│   ├── 02-cloudflare-setup.md # Cloudflare Token/Zone 配置
│   ├── 03-worker-deploy.md   # Worker 部署
│   ├── 04-panel-deploy.md    # 面板部署（Vercel）
│   └── 05-troubleshooting.md # 故障排查
├── worker/
│   └── _worker.js            # cfnew 精简内核（byJoey/cfnew core-only 分支）
├── panel/
│   └── ...                   # 面板源码（含简洁风 UI）
└── scripts/
    ├── cf-api.py              # Cloudflare API 通用 helper
    ├── deploy-worker.py       # Worker 部署脚本
    └── set-secret.py          # 设置 secret 变量脚本
```

## 快速开始

按顺序阅读执行：

1. [01-domain-dnshe.md](docs/01-domain-dnshe.md) — 注册免费域名（约 10 分钟，需浏览器）
2. [02-cloudflare-setup.md](docs/02-cloudflare-setup.md) — 配置 Cloudflare（约 15 分钟）
3. [03-worker-deploy.md](docs/03-worker-deploy.md) — 部署 Worker（约 10 分钟，纯 API）
4. [04-panel-deploy.md](docs/04-panel-deploy.md) — 部署面板（约 15 分钟，需浏览器+Vercel 账号）
5. [05-troubleshooting.md](docs/05-troubleshooting.md) — 出问题时查

## 核心概念

- **cfnew**：byJoey 开源的 Cloudflare Worker 代理内核，core-only 分支仅 37KB
- **UUID (`u`)**：既是代理认证凭据，也是面板登录凭据，必须换成自己生成的
- **KV (`C`)**：可选，面板在线保存配置用
- **面板**：独立部署，不处理代理流量，只负责配置管理和订阅生成

## 注意事项

- 文档中所有密钥、UUID、Token 均用占位符（`YOUR_UUID`、`YOUR_TOKEN`）表示
- 部署 Worker 和配置 DNS 可用 `scripts/` 中的脚本纯 API 完成
- 注册域名、Vercel 账号需要浏览器人工操作
