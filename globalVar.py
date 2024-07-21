import json
import os
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

def load_gcp_keys():
    keys = []
    key_names = []  # 新增：存储 key 文件名
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    # 从 .env 文件获取指定的 key 文件名，如果没有指定，则为 None
    specified_key = os.getenv('GCP_KEY_FILE')
    
    if specified_key:
        # 如果指定了 key 文件，只加载这个文件
        key_path = os.path.join(base_path, specified_key)
        if os.path.exists(key_path):
            with open(key_path, 'r') as f:
                keys.append(json.load(f))
            key_names.append(specified_key)  # 添加文件名
        else:
            print(f"警告: 指定的 key 文件 {specified_key} 不存在")
    else:
        # 如果没有指定 key 文件，加载所有 gcp-key*.json 文件
        key_files = sorted([f for f in os.listdir(base_path) if f.startswith('gcp-key') and f.endswith('.json')], 
                           key=lambda x: int(x.split('gcp-key')[1].split('.json')[0]))
        for file in key_files:
            with open(os.path.join(base_path, file), 'r') as f:
                keys.append(json.load(f))
            key_names.append(file)
    
    if not keys:
        raise ValueError("没有找到有效的 GCP key 文件")
    
    print(f"已加载 {len(keys)} 个 GCP key 文件")
    return keys, key_names # 返回 keys 和对应的文件名

# 加载 GCP keys
accountdata, key_file_names = load_gcp_keys()

# 从 .env 文件获取区域设置，如果没有设置，使用默认值
region = os.getenv('GCP_REGION', 'us-east5')

# 从 .env 文件获取切换频率，如果没有设置，使用默认值 0（不切换）
switch_frequency = int(os.getenv('GCP_KEY_SWITCH_FREQUENCY', '0'))
