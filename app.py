"""
飞书机器人 - 对接扣子智能体
用于接收飞书消息，调用扣子API，并将回复发送回飞书
"""

from flask import Flask, request, jsonify
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# 扣子 API 配置
COZE_API_URL = os.getenv("COZE_API_URL", "https://xqnw9jyc73.coze.site/stream_run")
COZE_API_TOKEN = os.getenv("COZE_API_TOKEN", "")

# 飞书配置
FEISHU_APP_ID = os.getenv("FEISHU_APP_ID", "")
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")


def get_feishu_access_token():
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result.get("tenant_access_token")


def send_feishu_message(access_token, receive_id, receive_id_type, content):
    """发送消息给用户"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": receive_id_type}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = {
        "receive_id": receive_id,
        "msg_type": "text",
        "content": json.dumps({"text": content})
    }
    response = requests.post(url, headers=headers, json=data, params=params)
    return response.json()


def call_coze_api(user_message):
    """调用扣子 API"""
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "query": user_message,
        "stream": False
    }

    try:
        response = requests.post(COZE_API_URL, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


@app.route("/webhook", methods=["POST"])
def webhook():
    """接收飞书消息并处理"""
    event = request.json
    print(f"Received event: {json.dumps(event, ensure_ascii=False)}")

    # 获取访问令牌
    access_token = get_feishu_access_token()
    if not access_token:
        return jsonify({"code": 1, "msg": "Failed to get access token"})

    # 解析消息内容
    try:
        message = event.get("event", {}).get("message", {})
        msg_type = message.get("msg_type", "")
        content = json.loads(message.get("content", "{}"))
        user_message = content.get("text", "")

        # 获取发送者信息
        sender = event.get("event", {}).get("sender", {})
        sender_id = sender.get("sender_id", {})
        open_id = sender_id.get("open_id", "")

        # 忽略机器人自身消息
        if sender.get("sender_type") == "bot":
            return jsonify({"code": 0, "msg": "bot message ignored"})

        # 调用扣子 API 获取回复
        coze_response = call_coze_api(user_message)
        print(f"Coze response: {json.dumps(coze_response, ensure_ascii=False)}")

        # 解析扣子回复
        if "error" in coze_response:
            reply_text = f"抱歉，发生了错误：{coze_response['error']}"
        else:
            # 根据扣子API返回格式调整
            reply_text = coze_response.get("result", coze_response.get("data", "抱歉，我暂时无法回答这个问题。"))
            if isinstance(reply_text, dict):
                reply_text = reply_text.get("content", "抱歉，我暂时无法回答这个问题。")

        # 发送回复给用户
        send_feishu_message(access_token, open_id, "open_id", reply_text)

        return jsonify({"code": 0, "msg": "success"})
    except Exception as e:
        print(f"Error processing message: {str(e)}")
        return jsonify({"code": 1, "msg": str(e)})


@app.route("/health", methods=["GET"])
def health():
    """健康检查接口"""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))