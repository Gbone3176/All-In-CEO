import requests
import json

def test_gradient_effect():
    print("===== 测试梯度系数效果 =====")
    
    # 重置游戏并获取初始状态
    reset_response = requests.post('http://localhost:5001/api/start_game')
    print(f"初始游戏启动状态码: {reset_response.status_code}")
    
    if reset_response.status_code != 200:
        print("启动游戏失败！")
        return
    
    # 初始决策测试（early stage，系数应为1.0）
    print("\n1. 测试 Early Stage (1.0x) 影响值:")
    make_decision(1, 'A')
    
    # 修改游戏阶段到mid stage（系数应为2.0）
    print("\n2. 测试 Mid Stage (2.0x) 影响值:")
    modify_stage(2.5)
    make_decision(2, 'B')
    
    # 修改游戏阶段到late stage（系数应为3.0）
    print("\n3. 测试 Late Stage (3.0x) 影响值:")
    modify_stage(3.5)
    make_decision(3, 'A')
    
    # 修改游戏阶段到final stage（系数应为4.0）
    print("\n4. 测试 Final Stage (4.0x) 影响值:")
    modify_stage(4.5)
    make_decision(4, 'B')
    
    print("\n===== 梯度系数测试完成 =====")

def make_decision(decision_id, option):
    try:
        response = requests.post(
            'http://localhost:5001/api/make_decision',
            json={'option': option}
        )
        
        print(f"决策 {decision_id} 响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"  选择: {option}")
            print(f"  当前阶段: {data['current_state']['story_stage']}")
            print(f"  金钱变化: {data['money_change']}")
            print(f"  士气变化: {data['morale_change']}")
            print(f"  市场前景变化: {data['market_prospect_change']}")
            return data
        else:
            print(f"  错误: {response.text}")
    except Exception as e:
        print(f"  异常: {str(e)}")
    return None

def modify_stage(new_stage):
    # 注意：这个函数只是为了测试目的，实际代码中可能需要添加一个API端点来修改stage
    print(f"手动设置游戏阶段为: {new_stage}")
    print("(注意：在实际环境中，需要添加API端点来修改stage进行精确测试)")
    # 在实际测试中，可以取消下面的注释并确保后端有相应的API端点
    # try:
    #     response = requests.post(
    #         'http://localhost:5001/api/set_stage',
    #         json={'stage': new_stage}
    #     )
    #     print(f"  设置阶段状态码: {response.status_code}")
    # except Exception as e:
    #     print(f"  设置阶段失败: {str(e)}")

if __name__ == "__main__":
    test_gradient_effect()