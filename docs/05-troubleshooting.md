# 05 — 故障排查

## 面板连不上 Worker（"连接未完成" / "读取配置失败"）

**原因**：`u` 变量未生效。实测通过 multipart metadata 传的普通 vars 有时不被面板识别。

**解决**：改用 secret 方式设置：

```bash
python3 scripts/set-secret.py --script-name YOUR_WORKER_NAME --name u --value YOUR_UUID
```

设置后重新在面板连接。

## Shadowrocket 订阅节点 UUID 错误

**现象**：节点能测出延迟，但打不开任何网站。查看节点详情发现 `uuid` 字段与实际 UUID 不符。

**原因**：Shadowrocket 缓存了旧订阅的 UUID，刷新订阅不会更新该字段。

**解决**：**删除订阅后重新添加**（左滑删除，不要点刷新按钮）。

## workers.dev 返回 `error code: 1042`

**原因**：账号级问题，workers.dev 子域名未正常启用，API 无法修复。

**解决**：改用自定义域名（见 03 章步骤 4）。

## Cloudflare Worker 间经自定义域名互调超时

**现象**：面板部署为 Worker 后，调用代理 Worker 的 API 持续超时（10s+），
而直接 curl 代理 Worker 正常（1s 内）。

**原因**：Cloudflare 平台限制，与代码无关。

**解决**：面板部署到 Vercel（见 04 章）。

## Pages Direct Upload 缺 manifest 报错

**现象**：`8000096` 错误。

**解决**：multipart 上传必须带 `manifest` 字段：

```bash
-F 'manifest={"_worker.js":"<sha256hex>"}'
```

> 注：Direct Upload 的部署不可 retry（`8000055`），失败需重新上传。

## 沙箱 curl 验证不可信

**现象**：沙箱内 curl `pages.dev` 或自定义域返回 nginx 欢迎页（DNS 被解析到 `198.18.253.x`）。

**原因**：沙箱出口经代理，DNS 被劫持。

**解决**：以真实设备（手机/电脑）测试为准，沙箱 curl 仅作参考。

## Token 无法删除自己

**现象**：调用 `DELETE /user/tokens/{id}` 返回 `9109` 错误。

**原因**：API 限制，Token 不能删除自身。

**解决**：手动去 Dashboard → My Profile → API Tokens 删除。

## 验证步骤（通用）

出问题时按此顺序排查：

- [ ] Worker 首页 `curl https://YOUR_DOMAIN/` 返回 `hello`
- [ ] `u` 是用 secret 方式设置的
- [ ] 订阅链接中的 UUID 与 Worker 的 `u` 一致
- [ ] 客户端删除订阅重加（非刷新）
- [ ] 换一个网络环境测试（排除本地网络问题）
