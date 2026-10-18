# 01 — DNSHE 免费域名注册

DNSHE (https://dnshe.com) 提供免费域名，免费 1 年，无需信用卡。

## 免费后缀（2026-10 实测，共 7 个）

| 后缀 | 说明 |
| --- | --- |
| `cc.cd` | 创意项目类 |
| `us.ci` | CI/CD 与服务类（官网标注推荐） |
| `de5.net` | 技术开发类 |
| `bot.cd` | 机器人与自动化类 |
| `ccwu.cc` | 通用 |
| `l.cd` | 2026-08-01 起开放无限制免费注册 |
| `v.cd` | 免费邮箱服务用域名 |

> 来源：dnshe.com 官网首页、官方 GitHub DNSHE-FreeDomains、官方公告。控制台登录后可能有更多后缀。

## 账号与配额

- 登录方式：Gmail OAuth（无密码，依赖浏览器登录态）
- 地区：选择 Singapore
- 配额：**单账号最多 3 个域名**（2026-10 实测）

## 注册流程（浏览器操作）

1. 打开 https://dnshe.com，用 Gmail 登录
2. 搜索想要的域名（如 `example.cc.cd`）
   - 注意：短域名可能已被注册，换一个再试
3. 点击注册，选择 **1 年免费**
4. 重复直到用完配额或够用为止

### 示例（2026-10-18 注册）

| 域名 | 用途 |
|------|------|
| `example1.cc.cd` | 备用 |
| `example2.cc.cd` | 备用 |
| `example.cc.cd` | 本项目使用 |

## NS 修改（绑定 Cloudflare）

域名注册后默认用 DNSHE 的 NS。要接入 Cloudflare，需把 NS 改为 Cloudflare 分配的：

1. 在 Cloudflare 创建 Zone 后，会分配 2 个 NS（如 `dax.ns.cloudflare.com`）
2. 回到 DNSHE → 域名管理 → 修改 NS
3. 填入 Cloudflare 的 2 个 NS，保存
4. 等待生效（通常几分钟到几小时）

详见 [02-cloudflare-setup.md](02-cloudflare-setup.md)。

## 续期

- 免费 1 年，到期前 **180 天内**可免费续 1 年
- 续期往原到期日累加，不亏时间
- 建议设置定时提醒（如到期前 2 周）

## 验证步骤

- [ ] 3 个域名（或所需数量）注册成功
- [ ] NS 已改为 Cloudflare 分配的 NS
- [ ] DoH 查询 NS 记录返回 Cloudflare 的 NS（见 02 章）
- [ ] 记录每个域名的到期日，设置续期提醒
