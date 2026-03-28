import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import shutil
from unittest.mock import patch, MagicMock

# 备份
shutil.copy('partner/config.json', 'partner/config.json.bak')

def reset_config():
    """重置配置文件"""
    default_config = {
        "response_rule": "test",
        "last_status": {
            "location": "",
            "time_period": "",
            "action": "",
            "agreed_events": [],
            "is_user_nearby": False,
            "current_location_options": [""],
            "current_action_options": [""]
        }
    }
    with open('partner/config.json', 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)

# Mock 所有依赖
mock_chat_llm = MagicMock(return_value="Test Reply")
mock_notice = MagicMock()
mock_stream_insert = MagicMock()
mock_get_tts_play = MagicMock()
mock_stop_tts = MagicMock()

with patch('llm.chat_llm', mock_chat_llm), \
     patch('llm.notice', mock_notice), \
     patch('llm.stream_insert', mock_stream_insert), \
     patch('tts.stop_tts', mock_stop_tts), \
     patch('tts.get_tts_play', mock_get_tts_play):

    # 导入模块
    import actions
    import actionScheduler

    print("=== Integration Test: actions + actionScheduler ===\n")

    # Test 1: action_self_talking
    print("Test 1: action_self_talking")
    reset_config()
    mock_chat_llm.reset_mock()
    mock_notice.reset_mock()
    try:
        result = actions.action_self_talking()
        assert result == "Test Reply", f"Expected 'Test Reply', got {result}"
        assert mock_stop_tts.called, "stop_tts should be called"
        assert mock_chat_llm.called, "chat_llm should be called"
        print("  PASS\n")
    except Exception as e:
        print(f"  FAIL: {e}\n")

    # Test 2: action_push_agreed_event (有事件)
    print("Test 2: action_push_agreed_event (has events)")
    reset_config()
    mock_chat_llm.reset_mock()
    mock_notice.reset_mock()
    try:
        actions.partner_status.put_agreed_event('Event 1')
        result = actions.action_push_agreed_event()
        assert result == "Test Reply", f"Expected 'Test Reply', got {result}"
        assert mock_chat_llm.called, "chat_llm should be called"
        print("  PASS\n")
    except Exception as e:
        print(f"  FAIL: {e}\n")

    # Test 3: action_push_agreed_event (无事件)
    print("Test 3: action_push_agreed_event (no events)")
    reset_config()
    mock_chat_llm.reset_mock()
    # 直接 patch partner_status 的返回值
    with patch.object(actions.partner_status, 'get_agreed_events', return_value=[]):
        result = actions.action_push_agreed_event()
    assert result is None, f"Expected None, got {result}"
    assert not mock_chat_llm.called, "chat_llm should NOT be called"
    print("  PASS\n")

    # Test 4: action_talk_with_other
    print("Test 4: action_talk_with_other")
    reset_config()
    mock_chat_llm.reset_mock()
    mock_notice.reset_mock()
    try:
        result = actions.action_talk_with_other()
        assert result == "Test Reply", f"Expected 'Test Reply', got {result}"
        assert mock_chat_llm.called, "chat_llm should be called"
        print("  PASS\n")
    except Exception as e:
        print(f"  FAIL: {e}\n")

    # Test 5: actionScheduler - 计数触发
    print("Test 5: actionScheduler - count trigger")
    reset_config()
    actionScheduler.reset_counts()
    mock_chat_llm.reset_mock()
    try:
        # 前两次调用应该随机执行
        actionScheduler.run_action()  # 第1次
        actionScheduler.run_action()  # 第2次

        counts = actionScheduler.get_action_counts()
        print(f"  Counts after 2 runs: {counts}")
        total = counts['action_self_talking'] + counts['action_talk_with_other'] + counts['action_push_agreed_event']
        assert total == 2, f"Expected 2 calls, got {total}"
        print("  PASS\n")
    except Exception as e:
        print(f"  FAIL: {e}\n")

    # Test 6: actionScheduler - reset_counts
    print("Test 6: actionScheduler - reset_counts")
    try:
        actionScheduler.reset_counts()
        counts = actionScheduler.get_action_counts()
        assert all(v == 0 for v in counts.values()), f"Expected all zeros, got {counts}"
        print("  PASS\n")
    except Exception as e:
        print(f"  FAIL: {e}\n")

    print("=== All Integration Tests Completed ===")

# 恢复配置
shutil.move('partner/config.json.bak', 'partner/config.json')
print("\nConfig file restored")
