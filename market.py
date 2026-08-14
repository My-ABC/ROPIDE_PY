import requests
import json
import time

def get_market_list():
    """获取 RopIDE 市场程序列表"""
    url = "https://ropide.pages.dev/api/market"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        print(f"获取列表失败: {e}")
        return []

def download_market_program(item_id):
    """根据 ID 下载程序文件"""
    url = f"https://ropide.pages.dev/api/market?id={item_id}"
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        if data and data.get('data'):
            return json.loads(data['data'])
    except requests.RequestException as e:
        print(f"下载失败: {e}")
    return None

def publish_to_market(name, author, model, description, file_data):
    """
    发布程序到 RopIDE 市场
    
    Args:
        name: 程序名称（如 "tetris v2.2"）
        author: 作者名称
        model: 适用型号（如 "fx-991CNX (VerF)"）
        description: 程序描述
        file_data: 项目数据（包含 input, gadgets, leftStartAddress 等）
    
    Returns:
        bool: 是否发布成功
    """
    url = "https://ropide.pages.dev/api/market"
    
    payload = {
        "name": name,
        "author": author,
        "model": model,
        "description": description,
        "data": json.dumps(file_data),
        "timestamp": int(time.time() * 1000)
    }
    
    try:
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        print(f"✅ 发布成功: {name}")
        return True
    except requests.RequestException as e:
        print(f"❌ 发布失败: {e}")
        return False
