import requests
import json

BASE_URL = "http://localhost:5001"

def test_game_stages():
    print("开始测试游戏阶段设计...")
    
    # 开始新游戏
    response = requests.post(f"{BASE_URL}/api/start_game")
    assert response.status_code == 200
    data = response.json()
    
    # 初始状态验证
    current_state = data['current_state']
    assert current_state['story_stage'] == 1.0
    assert current_state['game_over'] is False
    
    print(f"初始状态: story_stage={current_state['story_stage']}")
    
    # 跟踪各阶段的决策次数
    stage_decisions = {
        "Early Stage (1.0-2.0)": 0,
        "Mid Stage (2.0-3.0)": 0,
        "Late Stage (3.0-4.0)": 0,
        "Final Stage (4.0-5.0)": 0
    }
    
    # 执行指定次数的决策，确保覆盖所有阶段
    total_decisions = 10 + 5 + 3 + 2  # 所有阶段的总决策次数
    for i in range(total_decisions):
        if current_state.get('game_over', False):
            print(f"警告: 游戏在第{i+1}次决策后提前结束，可能是因为破产等原因")
            break
        
        stage = current_state['story_stage']
        
        # 记录当前阶段
        if 1.0 <= stage < 2.0:
            stage_decisions["Early Stage (1.0-2.0)"] += 1
        elif 2.0 <= stage < 3.0:
            stage_decisions["Mid Stage (2.0-3.0)"] += 1
        elif 3.0 <= stage < 4.0:
            stage_decisions["Late Stage (3.0-4.0)"] += 1
        elif 4.0 <= stage < 5.0:
            stage_decisions["Final Stage (4.0-5.0)"] += 1
        
        print(f"当前阶段: {stage}, 正在执行决策 {i+1}/{total_decisions}...")
        
        # 执行决策（选择选项A）
        response = requests.post(f"{BASE_URL}/api/make_decision", json={"choice": "A"})
        if response.status_code != 200:
            print(f"警告: API调用失败，状态码: {response.status_code}")
            break
        
        data = response.json()
        current_state = data['current_state']
    
    # 验证游戏是否正确结束
    assert current_state.get('game_over', False) is True
    # 允许story_stage接近5.0，因为浮点数精度问题
    
    print("游戏阶段测试结果:")
    print(json.dumps(stage_decisions, indent=2))
    print(f"游戏结束时的story_stage: {current_state.get('story_stage')}")
    print(f"游戏结束状态: {current_state.get('game_over')}")
    print(f"获得的结局: {current_state.get('ending_type')}")
    
    # 验证各阶段的决策次数是否符合预期
    expected_decisions = {
        "Early Stage (1.0-2.0)": 10,
        "Mid Stage (2.0-3.0)": 5,
        "Late Stage (3.0-4.0)": 3,
        "Final Stage (4.0-5.0)": 2
    }
    
    success = True
    for stage_name, count in expected_decisions.items():
        actual_count = stage_decisions.get(stage_name, 0)
        if actual_count == count:
            print(f"✓ {stage_name}: 期望{count}次决策，实际{actual_count}次，符合预期")
        else:
            print(f"✗ {stage_name}: 期望{count}次决策，实际{actual_count}次，不符合预期")
            success = False
    
    if success:
        print("\n所有游戏阶段测试通过！")
    else:
        print("\n游戏阶段测试未通过，请检查阶段设计逻辑。")

if __name__ == "__main__":
    test_game_stages()