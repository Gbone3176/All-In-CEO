import requests
import json

# 测试开始游戏API
print("测试 start_game API...")
start_response = requests.post('http://localhost:5001/api/start_game')
print(f"状态码: {start_response.status_code}")
try:
    start_data = start_response.json()
    print("成功接收JSON响应:")
    print(json.dumps(start_data, indent=2, ensure_ascii=False))
except Exception as e:
    print(f"JSON解析错误: {e}")
    print(f"响应内容类型: {start_response.headers.get('Content-Type')}")
    print(f"响应内容预览: {start_response.text[:200]}...")