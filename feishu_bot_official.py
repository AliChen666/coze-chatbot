#!/usr/bin/env python3
"""
飞书机器人 - 使用官方 lark-oapi 长连接 WebSocket SDK
"""

import os
import json
import requests
from lark_oapi import ws


# ============ 配置 ============
FEISHU_APP_ID = "cli_a931077c75795cd6"
FEISHU_APP_SECRET = "SliJT8UmoU3QIQaSpb0NRHgOkCIljgQY"
COZE_API_URL = "https://xqnw9jyc73.coze.site/stream_run"
COZE_API_TOKEN = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjYwODNiZjA2LTljNmMtNDFhOS04MmI2LWZmNzY5NzM1NjM0MiJ9.eyJpc3MiOiJodHRwczovL2FwaS5jb3plLmNuIiwiYXVkIjpbImVBek9RNnhuT2laZXF4SGY3VTltTlljdDY4elpvaWJPIl0sImV4cCI6ODIxMDI2Njg3Njc5OSwiaWF0IjoxNzczOTA3Mjk1LCJzdWIiOiJzcGlmZmU6Ly9hcGkuY296ZS5jbi93b3JrbG9hZF9pZGVudGl0eS9pZDo3NjE4NzczNDcxMzQ2MDMyNjc4Iiwic3JjIjoiaW5ib3VuZF9hdXRoX2FjY2Vzc190b2tlbl9pZDo3NjE4ODczODE4NDM3NjQ4NDEwIn0.gaeukygroD2rZbln2oo5xjHzo_gBZ_nKSuHI4oE6jvFHFZ8Z-ov1mAgLQ8qxIaVpFdcPdnQMCMPWfLKyojhdhGHCwaBLkz1mSFFc7K0twNRUUhxoBVIm8Mn3SdmHYQgiKzNZCCv6EbbCEn2jR5HYAzkSMzU1fHxRauXcXxUXVF2fraGnCMyCpb6fBdulg51WnXJIMPc9ez8u2g6wHe4ZkHY5LKFrIrF8dvmwyxUjI7djF9Y0BlpPyT8Ccpoq3_Ewuv04h4XOtuLf7g34rzEDH9gFrwUSGhtpl4e7An1SMxhUyX0VLpZWmtaitL7h-Jq4SY5yPLTD0-hoPkvqnLmTBw"


def get_token():
    """获取飞书 access token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET})
    return resp.json().get("tenant_access_token")


def send_msg(token, open_id, text):
    """发送消息"""
    url = "https://open.feishu.cn/open-apis/im/v1/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    data = {"receive_id": open_id, "msg_type": "text", "content": json.dumps({"text": text})}
    resp = requests.post(url, headers=headers, json=data, params={"receive_id_type": "open_id"})
    return resp.json()


def call_coze(msg):
    """调用扣子"""
    headers = {"Authorization": f"Bearer {COZE_API_TOKEN}", "Content-Type": "application/json"}
    try:
        resp = requests.post(COZE_API_URL, headers=headers, json={"query": msg, "stream": False}, timeout=60)
        result = resp.json()
        return result.get("result", result.get("data", "抱歉，我无法回答。"))
    except Exception as e:
        return f"出错了: {str(e)}"


def main():
    print("=" * 50)
    print("飞书扣子机器人 - 官方长连接 SDK")
    print("=" * 50)
    print(f"App ID: {FEISHU_APP_ID}")
    print()
    print("提示：请确保已在飞书后台：")
    print("1. 开启「使用长连接接收事件」")
    print("2. 订阅事件 im.message.receive_v1")
    print("3. 点击「保存」")
    print()
    print("正在连接飞书服务器...")
    print()
    
    # 消息处理函数
    def on_p2p_message(event):
        print(f"[收到私聊消息]")
        try:
            msg = event.message
            sender = event.sender
            content = json.loads(msg.content)
            user_msg = content.get("text", "")
            open_id = sender.sender_id.open_id
            
            if user_msg:
                print(f"  用户消息: {user_msg}")
                reply = call_coze(user_msg)
                print(f"  扣子回复: {reply[:50]}...")
                
                token = get_token()
                if token:
                    result = send_msg(token, open_id, reply)
                    if result.get("code") == 0:
                        print("  ✓ 已发送回复")
                    else:
                        print(f"  ✗ 发送失败: {result.get('msg')}")
        except Exception as e:
            print(f"处理错误: {e}")
    
    # 事件处理函数
    def event_handler(event, data):
        print(f"[收到事件] type={event}, data={data}")
    
    # 连接成功处理
    def on_open(ws_client):
        print("✓ 已连接到飞书服务器！")
        print()
        print("=" * 50)
        print("机器人已就绪！")
        print("在飞书中搜索你的应用，开始对话测试")
        print("按 Ctrl+C 停止运行")
        print("=" * 50)
    
    # 创建并启动客户端
    client = ws.Client(
        FEISHU_APP_ID,
        FEISHU_APP_SECRET,
        event_handler=event_handler,
        on_open=on_open
    )
    
    # 注册私聊消息处理
    client.register_p2p_message_handler(on_p2P_message)
    
    client.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n机器人已停止")