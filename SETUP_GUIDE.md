# 飞书机器人部署指南

## 前提条件

在开始之前，请确保你已完成以下步骤：

### 1. 飞书应用创建
1. 打开 https://open.feishu.cn/app/create
2. 创建企业自建应用
3. 获取 App ID 和 App Secret

### 2. Railway 账号
1. 打开 https://railway.app
2. 使用 GitHub 账号登录

---

## 快速部署到 Railway

### 方式一：一键部署（推荐）

点击下方按钮：

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

然后选择 "Deploy from GitHub repo"，选择 `AliChen666/coze-chatbot` 仓库。

### 方式二：手动部署

1. 登录 Railway
2. 点击 "New Project" → "Deploy from GitHub"
3. 选择仓库：`AliChen666/coze-chatbot`
4. Railway 会自动检测为 Python 项目

---

## 配置环境变量

在 Railway 项目中，点击 "Variables"，添加以下变量：

### 必需变量

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `COZE_API_URL` | `https://xqnw9jyc73.coze.site/stream_run` | 扣子 API 地址 |
| `COZE_API_TOKEN` | `你的扣子API Token` | 从扣子平台获取 |
| `FEISHU_APP_ID` | `cli_xxxxxxxx` | 飞书 App ID |
| `FEISHU_APP_SECRET` | `xxxxxxxx` | 飞书 App Secret |

### 部署完成后

1. 复制 Railway 给你的域名，格式类似：
   ```
   https://coze-feishu-bot.up.railway.app
   ```

2. 这个域名就是你的机器人服务地址

---

## 飞书应用配置

### 1. 启用机器人能力

1. 打开 https://open.feishu.cn/app
2. 进入你的应用
3. 点击「添加应用能力」
4. 启用「机器人」

### 2. 配置事件订阅

1. 进入应用 →「事件与回调」
2. 点击「添加事件」
3. 搜索并添加：`im.message.receive_v1`（接收消息）
4. 在「请求地址 URL」中填入：
   ```
   https://你的Railway域名.up.railway.app/webhook
   ```
5. 保存

### 3. 发布应用

1. 点击「版本管理与发布」
2. 创建新版本
3. 提交审核
4. 审核通过后即可使用

---

## 测试机器人

1. 在飞书中搜索你的应用名称
2. 点击「开始聊天」
3. 发送一条消息测试

---

## 常见问题

### Q: 机器人没有回复？
- 检查 Railway 日志是否有错误
- 确认环境变量是否正确配置
- 确认飞书事件订阅是否成功

### Q: 提示 "Failed to get access token"？
- 检查 FEISHU_APP_ID 和 FEISHU_APP_SECRET 是否正确
- 确认飞书应用已启用机器人能力

### Q: 扣子 API 调用失败？
- 检查 COZE_API_TOKEN 是否过期
- 确认 COZE_API_URL 是否正确

---

## 项目结构

```
coze-chatbot/
├── app.py              # Flask 后端应用
├── index.html          # 网页版界面
├── requirements.txt    # Python 依赖
├── Procfile           # Railway 部署配置
├── .env.example       # 环境变量示例
└── .github/
    └── workflows/
        └── deploy.yml  # GitHub Pages 部署
```

---

## 获取帮助

如果遇到问题，请检查：
1. Railway 部署日志
2. 飞书开放平台配置
3. 扣子平台 API 状态
