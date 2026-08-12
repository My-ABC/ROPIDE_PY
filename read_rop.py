import json

def read_rop_file(file_name: str):
    """读取 .rop 文件，返回解析所需的数据"""
    try:
        with open(file_name, mode='r', encoding='utf-8') as f:
            # 直接读取文件内容，不是 json.loads(code)
            data = json.load(f)
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None

    # 安全获取字段
    co = data.get('input', '')
    leftaddr = data.get('leftStartAddress', 'E9E0')
    rightaddr = data.get('rightStartAddress', 'D9D0')
    gadgets = data.get('gadgets', [])

    return {
        'input': co,
        'leftStartAddress': leftaddr,
        'rightStartAddress': rightaddr,
        'gadgets': gadgets
    }