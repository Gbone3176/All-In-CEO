import requests
import time
import json

BASE_URL = "http://localhost:5001/api"

def test_ipo_celebration():
    print("开始测试上市结局庆祝效果...")
    
    # 1. 启动新游戏
    print("步骤1: 启动新游戏")
    try:
        response = requests.post(f"{BASE_URL}/start_game")
        response.raise_for_status()
        game_id = response.json()["game_id"]
        print(f"  游戏ID: {game_id}")
    except Exception as e:
        print(f"  启动游戏失败: {e}")
        return False
    
    # 2. 连续做出积极决策，尝试达到上市结局
    print("步骤2: 连续做出积极决策，尝试达到上市结局")
    
    for decision_round in range(1, 15):  # 尝试14个决策轮次
        try:
            # 获取当前游戏状态
            response = requests.get(f"{BASE_URL}/game_state/{game_id}")
            response.raise_for_status()
            game_state = response.json()
            
            # 检查游戏是否已经结束
            if game_state.get("game_over", False):
                print(f"  游戏在第{decision_round}轮结束")
                
                # 检查是否为成功结局
                if "结局" in game_state.get("feedback", ""):
                    print(f"  结局信息: {game_state.get('feedback')}")
                    
                    # 检查是否为上市或成功结局
                    if any(keyword in game_state.get("feedback", "").lower() for keyword in ["成功", "胜利", "ipo", "上市"]):
                        print("✅ 检测到上市/成功结局！")
                        print("  庆祝撒花效果应该已经在前端显示")
                        return True
                    else:
                        print("❌ 这不是上市/成功结局")
                break
            
            # 尝试获取下一个会议
            response = requests.get(f"{BASE_URL}/next_meeting/{game_id}")
            response.raise_for_status()
            meeting_data = response.json()
            
            print(f"  第{decision_round}轮会议: {meeting_data.get('description', '未知会议')}")
            
            # 简单策略：选择看起来更积极的选项（通常是A选项）
            # 在实际游戏中，这会增加获得成功结局的机会
            selected_option = "A"
            
            # 提交决策
            response = requests.post(
                f"{BASE_URL}/make_decision/{game_id}",
                json={"selected_option": selected_option}
            )
            response.raise_for_status()
            decision_result = response.json()
            
            print(f"  选择: {selected_option}, 反馈: {decision_result.get('feedback', '无反馈')[:50]}...")
            
            # 短暂休息，避免请求过快
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  第{decision_round}轮出错: {e}")
            continue
    
    print("❌ 未能在测试轮次内达到上市/成功结局")
    print("提示: 在实际游戏中，玩家需要做出一系列积极决策才能触发上市结局")
    print("前端代码已更新，当触发包含'上市'、'IPO'、'成功'或'胜利'关键词的结局时，将显示庆祝撒花效果")
    return False

if __name__ == "__main__":
    print("=== 上市结局庆祝效果测试 ===")
    test_ipo_celebration()
    print("\n测试完成！请在浏览器中打开游戏，尝试达到上市结局，查看庆祝撒花效果")