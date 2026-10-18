# 04 — 面板部署（Vercel）

## 项目介绍

- 仓库：https://github.com/byJoey/cfnew-panel
- 官方推荐部署到 **Vercel**（Node.js 应用，非纯静态站）
- 本项目 `panel/` 即该仓库源码，UI 已改为简洁风
- 面板不处理代理流量，只负责配置管理和订阅生成

## 简洁风 UI 改动说明

相对原版的改动（仅视觉层，未动后端逻辑）：

1. **`src/theme.css` 完全重写**（973 行 → 约 430 行）
   - 配色：白底 `#ffffff` + 浅灰页面底 `#f6f7f9`，深灰文字 `#1e293b`，单一蓝色强调 `#2563eb`
   - 系统字体栈，隐藏所有赛博朋克装饰（矩阵雨、霓虹网格、扫描线、glitch）
   - 卡片式布局，移动端适配
2. **`src/engine.mjs`**：159 处霓虹青 `#00f0ff` → 深灰，删除全部 `text-shadow` 发光效果，
   深色背景 → 浅灰/白色，成功/警告/错误色改为浅底可读版本
3. **`src/index.html`**：未改动（新 CSS 直接生效）

## Vercel 部署（浏览器操作）

1. 注册 Vercel：https://vercel.com/signup（可用 GitHub OAuth）
2. 打开一键部署：
   `https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2FbyJoey%2Fcfnew-panel&project-name=cfnew-panel&repository-name=cfnew-panel`
3. 按提示连接 GitHub（会 fork 一份到你自己的账号），Framework Preset 选 **Other**
4. 点击 Deploy，等待完成，记下分配的域名（如 `xxx.vercel.app`）

### 使用自己的简洁风代码

一键部署拉的是原版代码。要换简洁风：

1. 把本项目 `panel/` 的 `src/theme.css` 和 `src/engine.mjs` 覆盖到你 fork 的仓库对应位置
2. `git push` 后 Vercel 自动重新部署
3. 如样式未更新，在 Vercel → Deployments → 最新部署 → Redeploy（**不勾选** Use existing Build Cache）

## Deployment Protection（必须关闭）

新部署默认开启 Vercel Authentication，外部无法访问：

1. Vercel → 项目 → Settings → Deployment Protection
2. 关闭 **Vercel Authentication**（确认框输入 `disable vercel authentication`）
3. 保存后面板可公开访问

## 自定义域名

1. Vercel → 项目 → Settings → Domains → Add `panel.YOUR_DOMAIN`
2. Vercel 会给出 CNAME 目标（如 `xxx.vercel-dns-017.com`）
3. 在 Cloudflare 加 DNS 记录：

```bash
python3 scripts/cf-api.py POST /zones/YOUR_ZONE_ID/dns_records \
  '{"type":"CNAME","name":"panel","content":"YOUR_VERCEL_CNAME","proxied":false}'
```

> **CNAME 必须 DNS only（`proxied: false`）**，不能走 Cloudflare 代理。

4. 等 DNS 生效后 Vercel 会自动签发证书

## 重要限制

> **不要把面板部署为 Cloudflare Worker。**
> 实测：Worker A（面板）经自定义域名调用 Worker B（代理内核）时请求持续超时，
> 这是 Cloudflare 平台限制（Worker 间经自定义域名互调），与代码无关。
> 面板必须部署在 Cloudflare 之外（Vercel 官方推荐）。

## 验证步骤

- [ ] 面板首页可公开访问（无登录墙），为简洁风白底 UI
- [ ] 填入 Worker 域名 + UUID 能进入控制台
- [ ] 控制台显示 Worker 地区、ProxyIP 状态、KV 状态
- [ ] 生成的订阅链接可导入客户端
- [ ] 自定义域名 `panel.YOUR_DOMAIN` 可访问
