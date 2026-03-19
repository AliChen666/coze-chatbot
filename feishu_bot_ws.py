#!/usr/bin/env python3
"""
飞书机器人 - 使用官方长连接 SDK
无需公网服务器，本地运行即可
"""

import os
import json
import requests
from larksuiteoapi import Config, Context, DOMAIN_FEISHU, LEVEL_DEBUG
from larksuiteoapi.ws import Client as WsClient

# ============ 配置 ============
# 飞书应用凭证
FEISHU_APP_ID = "cli_a931077c75795cd6"
FEISHU_APP_SECRET = "SliJT8UmoU3QIQaSpb0NRHgOkCIljgQY"

# 扣子 API 配置
COZE_API_URL = "https://xqnw9jyc73.coze.site/stream_run"
COZE_API_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjYwODNiZjA2LTljNmMtNDFhOS04MmI2LWZmNzY5NzM1NjM0MiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImVBek9RNnhuT2laZXF4SGY3VTltTlljdDY4elpvaWJPIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczOTA3Mjk1LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE4NzczNDcxMzQ2MDMyNjc4Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE4ODczODE4NDM3NjQ4NDEwIn0.gaeukygroD2rZbln2oo5xjHzo_gBZ_nKSuHI4oE6jvFHFZ8Z-ov1mAgLQ8qxIaVpFdcPdnQMCMPWfLKyojhdhGHCwaBLkz1mSFFc7K0twNRUUhxoBVIm8Mn3SdmHYQgiKzNZCCv6EbbCEn2jR5HYAzkSMzU1fHxRauXcXxUXVF2fraGnCMyCpb6fBdulg51WnXJIMPc9ez8u2g6wHe4ZkHY5LKFrIrF8dvmwyxUjI7djF9Y0BlpPyT8Ccpoq3_Ewuv04h4XOtuLf7g34rzEDH9gFrwUSGhtpl4e7An1SMxhUyX0VLpZWmtaitL7h-Jq4SY5yPLTD0-hoPkvqnLmTBw"


def get_feishu_access_token():
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    return result.get("tenant_access_token")


def send_feishu_message(access_token, receive_id, content):
    """发送消息给用户"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    params = {"receive_id_type": "open_id"}
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
        response = requests.post(COZE_API_URL, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def handle_message(event_data):
    """处理接收到的消息"""
    try:
        message = event_data.get("message", {})
        sender = event_data.get("sender", {})
        
        # 获取消息内容
        content = json.loads(message.get("content", "{}"))
        user_message = content.get("text", "")
        
        # 获取发送者 open_id
        sender_id = sender.get("sender_id", {})
        open_id = sender_id.get("open_id", "")
        
        # 忽略机器人自身消息
        if sender.get("sender_type") == "bot":
            return
        
        print(f"收到消息: {user_message}")
        
        # 调用扣子 API
        coze_response = call_coze_api(user_message)
        print(f"扣子回复: {coze_response}")
        
        # 解析回复
        if "error" in coze_response:
            reply_text = f"抱歉，发生了错误：{coze_response['error']}"
        else:
            reply_text = coze_response.get("result", coze_response.get("data", "抱歉，我暂时无法回答这个问题。"))
            if isinstance(reply_text, dict):
                reply_text = reply_text.get("content", "抱歉，我暂时无法回答这个问题。")
        
        # 获取访问令牌并发送回复
        access_token = get_feishu_access_token()
        if access_token:
            send_feishu_message(access_token, open_id, reply_text)
            print(f"已回复: {reply_text[:50]}...")
        
    except Exception as e:
        print(f"处理消息出错: {str(e)}")


def main():
    """主函数 - 启动长连接客户端"""
    print("=" * 50)
    print("飞书扣子机器人 - 长连接模式")
    print("=" * 50)
    print(f"App ID: {FEISHU_APP_ID}")
    print("正在连接飞书服务器...")
    print("提示：请确保已在飞书后台开启「长连接接收事件」")
    print("=" * 50)
    
    # 配置
    config = Config(
        domain=DOMAIN_FEISHU,
        app_settings=Config.AppSettings(
            app_id=FEISHU_APP_ID,
            app_secret=FEISHU_APP_SECRET,
            encrypt_key="",
            verification_token="",
        ),
        log_level=LEVEL_DEBUG,
    )
    
    # 创建 WebSocket 客户端
    def message_handler(ctx: Context, event):
        """消息处理器"""
        event_data = json.loads(event.event)
        handle_message(event_data)
    
    client = WsClient(config, message_handler)
    
    # 启动客户端
    print("\n机器人已启动！")
    print("在飞书中搜索你的应用，开始对话测试。")
    print("按 Ctrl+C 停止运行\n")
    
    client.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n机器人已停止")