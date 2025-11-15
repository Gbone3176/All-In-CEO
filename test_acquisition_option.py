import requests
import json

BASE_URL = "http://localhost:5001"

def test_acquisition_ending():
    print("开始测试接受收购选项的特殊结束逻辑...")
    
    # 启动新游戏
    print("启动新游戏...")
    start_response = requests.post(f"{BASE_URL}/api/start_game")
    
    if start_response.status_code != 200:
        print(f"启动游戏失败: {start_response.status_code}")
        return
    
    start_data = start_response.json()
    print(f"游戏启动成功，初始状态: story_stage={start_data.get('current_state', {}).get('story_stage', '未知')}")
    
    # 查找包含接受收购选项的会议
    print("寻找包含接受收购选项的会议...")
    found_acquisition_option = False
    
    # 我们可能需要经过几个会议才能找到接受收购的选项
    for i in range(20):  # 设置一个合理的上限，避免无限循环
        print(f"\n第{i+1}次尝试获取会议...")
        
        # 获取当前会议
        meeting_response = requests.get(f"{BASE_URL}/api/get_next_meeting")
        
        if meeting_response.status_code != 200:
            print(f"获取会议失败: {meeting_response.status_code}")
            break
        
        meeting_data = meeting_response.json()
        
        # 检查选项A是否是接受收购
        if 'optionA' in meeting_data and "接受收购，创始团队获得现金退出（个人收益平均5000万），员工获得3倍薪资补偿，但公司失去独立性。" in meeting_data['optionA']:
            print(f"找到接受收购选项! 选项A: {meeting_data['optionA'][:100]}...")
            # 选择接受收购选项
            decision_response = requests.post(f"{BASE_URL}/api/make_decision", json={"option": "A"})
            
            if decision_response.status_code != 200:
                print(f"做出决策失败: {decision_response.status_code}")
                return
            
            decision_data = decision_response.json()
            current_state = decision_data.get('current_state', {})
            
            # 验证游戏是否结束且结局类型正确
            if current_state.get('game_over', False):
                print("✅ 游戏成功结束")
                print(f"游戏结束类型: {current_state.get('ending_type', '未知')}")
                print(f"最终结局文本: {current_state.get('ending_text', '无')}")
                
                # 验证结局类型是否为'acquisition'
                if current_state.get('ending_type') == 'acquisition':
                    print("✅ 成功验证: 选择接受收购选项后，游戏正确结束并进入清算界面!")
                else:
                    print("❌ 验证失败: 游戏虽然结束，但结局类型不是'acquisition'")
                    
                found_acquisition_option = True
                break
            else:
                print("❌ 验证失败: 选择接受收购选项后，游戏没有结束")
                return
        # 检查选项B是否是接受收购
        elif 'optionB' in meeting_data and "接受收购，创始团队获得现金退出（个人收益平均5000万），员工获得3倍薪资补偿，但公司失去独立性。" in meeting_data['optionB']:
            print(f"找到接受收购选项! 选项B: {meeting_data['optionB'][:100]}...")
            # 选择接受收购选项
            decision_response = requests.post(f"{BASE_URL}/api/make_decision", json={"option": "B"})
            
            if decision_response.status_code != 200:
                print(f"做出决策失败: {decision_response.status_code}")
                return
            
            decision_data = decision_response.json()
            current_state = decision_data.get('current_state', {})
            
            # 验证游戏是否结束且结局类型正确
            if current_state.get('game_over', False):
                print("✅ 游戏成功结束")
                print(f"游戏结束类型: {current_state.get('ending_type', '未知')}")
                print(f"最终结局文本: {current_state.get('ending_text', '无')}")
                
                # 验证结局类型是否为'acquisition'
                if current_state.get('ending_type') == 'acquisition':
                    print("✅ 成功验证: 选择接受收购选项后，游戏正确结束并进入清算界面!")
                else:
                    print("❌ 验证失败: 游戏虽然结束，但结局类型不是'acquisition'")
                    
                found_acquisition_option = True
                break
            else:
                print("❌ 验证失败: 选择接受收购选项后，游戏没有结束")
                return
        else:
            print(f"未找到接受收购选项，选择选项A继续...")
            # 选择选项A继续游戏
            decision_response = requests.post(f"{BASE_URL}/api/make_decision", json={"option": "A"})
            
            if decision_response.status_code != 200:
                print(f"做出决策失败: {decision_response.status_code}")
                break
    
    if not found_acquisition_option:
        print("\n⚠️ 在尝试次数内未找到包含接受收购选项的会议，无法完成测试。")
        print("建议手动在游戏中触发该选项进行验证。")

if __name__ == "__main__":
    test_acquisition_ending()