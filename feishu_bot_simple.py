#!/usr/bin/env python3
"""
飞书机器人 - 使用飞书开放平台长连接
无需公网服务器，本地运行即可
"""

import json
import requests
import websocket
import threading
import time

# ============ 配置 ============
FEISHU_APP_ID = "cli_a931077c75795cd6"
FEISHU_APP_SECRET = "SliJT8UmoU3QIQaSpb0NRHgOkCIljgQY"
COZE_API_URL = "https://xqnw9jyc73.coze.site/stream_run"
COZE_API_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjYwODNiZjA2LTljNmMtNDFhOS04MmI2LWZmNzY5NzM1NjM0MiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImVBek9RNnhuT2laZXF4SGY3VTltTlljdDY4elpvaWJPIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczOTA3Mjk1LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE4NzczNDcxMzQ2MDMyNjc4Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE4ODczODE4NDM3NjQ4NDEwIn0.gaeukygroD2rZbln2oo5xjHzo_gBZ_nKSuHI4oE6jvFHFZ8Z-ov1mAgLQ8qxIaVpFdcPdnQMCMPWfLKyojhdhGHCwaBLkz1mSFFc7K0twNRUUhxoBVIm8Mn3SdmHYQgiKzNZCCv6EbbCEn2jR5HYAzkSMzU1fHxRauXcXxUXVF2fraGnCMyCpb6fBdulg51WnXJIMPc9ez8u2g6wHe4ZkHY5LKFrIrF8dvmwyxUjI7djF9Y0BlpPyT8Ccpoq3_Ewuv04h4XOtuLf7g34rzEDH9gFrwUSGhtpl4e7An1SMxhUyX0VLpZWmtaitL7h-Jq4SY5yPLTD0-hoPkvqnLmTBw"


def get_feishu_token():
    """获取飞书访问令牌"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    headers = {"Content-Type": "application/json"}
    data = {"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
    resp = requests.post(url, headers=headers, json=data)
    return resp.json().get("tenant_access_token")


def send_message(token, open_id, text):
    """发送消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    data = {
        "receive_id": open_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    resp = requests.post(url, headers=headers, json=data, params={"receive_id_type": "open_id"})
    return resp.json()


def call_coze(message):
    """调用扣子"""
    headers = {
        "Authorization": f"Bearer {COZE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {"query": message, "stream": False}
    try:
        resp = requests.post(COZE_API_URL, headers=headers, json=data, timeout=60)
        result = resp.json()
        return result.get("result", result.get("data", "抱歉，我无法回答。"))
    except Exception as e:
        return f"出错了: {str(e)}"


def on_message(ws, message):
    """收到消息"""
    try:
        data = json.loads(message)
        print(f"收到: {data.get('type', 'unknown')}")
        
        if data.get("type") == "im.message.receive_v1":
            event = data.get("event", {})
            msg = event.get("message", {})
            sender = event.get("sender", {})
            
            content = json.loads(msg.get("content", "{}"))
            user_msg = content.get("text", "")
            open_id = sender.get("sender_id", {}).get("open_id", "")
            
            if user_msg and open_id:
                print(f"用户: {user_msg}")
                reply = call_coze(user_msg)
                token = get_feishu_token()
                send_message(token, open_id, reply)
                print(f"回复: {reply[:50]}...")
    except Exception as e:
        print(f"处理错误: {e}")


def on_open(ws):
    """连接成功"""
    print("✓ 已连接到飞书服务器！")
    print("现在可以回到飞书后台点击「保存」了")
    print("在飞书中搜索应用，开始对话测试")


def on_error(ws, error):
    """连接错误"""
    print(f"错误: {error}")


def on_close(ws, close_status_code, close_msg):
    """连接关闭"""
    print("连接已关闭，正在重连...")
    time.sleep(5)
    start_bot()


def start_bot():
    """启动机器人"""
    print("=" * 50)
    print("  飞书扣子机器人")
    print("=" * 50)
    print("正在连接飞书服务器...")
    
    # 获取 WebSocket 地址
    token = get_feishu_token()
    url = "https://open.feishu.cn/open-apis/event/v1/subscription/subscribe"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {
        "app_id": FEISHU_APP_ID,
        "subscription_type": "websocket"
    }
    resp = requests.post(url, headers=headers, json=data)
    result = resp.json()
    
    if result.get("code") != 0:
        print(f"获取连接地址失败: {result}")
        return
    
    ws_url = result.get("data", {}).get("url")
    if not ws_url:
        print("未获取到 WebSocket 地址")
        return
    
    # 连接 WebSocket
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    
    ws.run_forever()


if __name__ == "__main__":
    try:
        start_bot()
    except KeyboardInterrupt:
        print("\n机器人已停止")