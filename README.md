# 飞书扣子智能体机器人

将扣子(Coze)智能体接入飞书，实现通过飞书机器人与AI对话。

## 功能特性

- 接收飞书消息并转发给扣子智能体
- 将扣子智能体的回复发送回飞书
- 支持流式响应（非流式模式）
- 健康检查接口

## 部署到 Railway

### 方式一：通过 Railway 按钮一键部署

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### 方式二：手动部署

1. Fork 此仓库
2. 在 [Railway](https://railway.app) 注册账号
3. 点击 "New Project" → "Deploy from GitHub"
4. 选择此仓库
5. 在 Environment Variables 中添加以下变量：
   - `COZE_API_URL`: 扣子 API 地址
   - `COZE_API_TOKEN`: 扣子 API Token
   - `FEISHU_APP_ID`: 飞书应用 App ID
   - `FEISHU_APP_SECRET`: 飞书应用 App Secret

## 部署到 Render

1. Fork 此仓库
2. 在 [Render](https://render.com) 注册账号
3. 点击 "New" → "Web Service"
4. 连接 GitHub 仓库
5. 设置构建命令: `pip install -r requirements.txt`
6. 设置启动命令: `python app.py`
7. 添加环境变量（同上）

## 飞书应用配置

### 1. 创建飞书应用
1. 打开 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 App ID 和 App Secret

### 2. 启用机器人能力
1. 在应用管理页面添加「机器人」能力
2. 配置事件订阅：
   - 订阅 `im.message.receive_v1` 事件
   - 回调地址填写: `https://你的Railway地址.railway.app/webhook`

### 3. 发布应用
1. 创建版本并提交审核
2. 审核通过后即可使用

## 本地开发

```bash
# 克隆仓库
git clone https://github.com/你的用户名/feishu-coze-bot.git
cd feishu-coze-bot

# 安装依赖
pip install -r requirements.txt

# 复制环境变量文件
cp .env.example .env

# 编辑 .env 填入配置
# COZE_API_URL=你的扣子API地址
# COZE_API_TOKEN=你的扣子API Token
# FEISHU_APP_ID=你的飞书App ID
# FEISHU_APP_SECRET=你的飞书App Secret

# 启动服务
python app.py
```

## 项目结构

```
feishu-coze-bot/
├── app.py              # Flask 应用主文件
├── requirements.txt    # Python 依赖
├── Procfile           # Railway 部署配置
├── .env.example       # 环境变量示例
├── .gitignore         # Git 忽略文件
└── README.md          # 项目说明
```

## 环境变量说明

| 变量名 | 必填 | 说明 |
|--------|------|------|
| COZE_API_URL | 是 | 扣子 API 地址 |
| COZE_API_TOKEN | 是 | 扣子 API Token |
| FEISHU_APP_ID | 是 | 飞书应用 App ID |
| FEISHU_APP_SECRET | 是 | 飞书应用 App Secret |
| PORT | 否 | 服务端口，默认 5000 |

## 注意事项

1. 确保飞书应用已正确配置事件订阅
2. 确保回调地址可以被飞书访问（需要公网地址）
3. 扣子 API Token 请妥善保管，不要泄露
