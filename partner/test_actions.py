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

def test_action_self_talking():
    print("=== Test action_self_talking ===")
    reset_config()

    with patch('llm.chat_llm', return_value="Test Reply") as mock_chat, \
         patch('llm.notice') as mock_notice, \
         patch('llm.stream_insert') as mock_stream, \
         patch('tts.stop_tts') as mock_stop, \
         patch('tts.get_tts_play') as mock_play:

        from actions import action_self_talking

        result = action_self_talking()

        assert mock_stop.called, "stop_tts should be called"
        assert mock_chat.called, "chat_llm should be called"
        assert mock_notice.called, "notice should be called"
        assert "self-talking" in mock_notice.call_args[0][0].lower() or "自言自语" in mock_notice.call_args[0][0], f"notice should contain self-talking, got: {mock_notice.call_args[0][0]}"
        assert mock_stream.called, "stream_insert should be called"
        assert mock_play.called, "get_tts_play should be called"
        assert result == "Test Reply", f"result should be 'Test Reply', got: {result}"

        print("PASS: action_self_talking")

def test_action_push_agreed_event():
    print("\n=== Test action_push_agreed_event ===")
    reset_config()

    with patch('llm.chat_llm', return_value="Test Reply") as mock_chat, \
         patch('llm.notice') as mock_notice, \
         patch('llm.stream_insert') as mock_stream, \
         patch('tts.stop_tts') as mock_stop, \
         patch('tts.get_tts_play') as mock_play, \
         patch('characterStatus.characterStatus') as mock_cs:

        mock_cs_instance = MagicMock()
        mock_cs_instance.get_agreed_events.return_value = ['Event 1', 'Event 2']
        mock_cs.return_value = mock_cs_instance

        from actions import action_push_agreed_event
        importlib.reload(actions)
        actions.partner_status = mock_cs_instance

        result = action_push_agreed_event()

        assert mock_stop.called, "stop_tts should be called"
        assert mock_chat.called, "chat_llm should be called"
        assert mock_notice.called, "notice should be called"
        assert mock_stream.called, "stream_insert should be called"
        assert mock_play.called, "get_tts_play should be called"
        assert result == "Test Reply", f"result should be 'Test Reply', got: {result}"

        print("PASS: action_push_agreed_event")

        # Test with no agreed events
        mock_chat.reset_mock()
        mock_cs_instance.get_agreed_events.return_value = []
        result = action_push_agreed_event()
        assert result is None, "should return None when no events"
        assert not mock_chat.called, "chat_llm should NOT be called when no events"
        print("PASS: action_push_agreed_event (no events)")

def test_action_talk_with_other():
    print("\n=== Test action_talk_with_other ===")
    reset_config()

    with patch('llm.chat_llm', return_value="Test Reply") as mock_chat, \
         patch('llm.notice') as mock_notice, \
         patch('llm.stream_insert') as mock_stream, \
         patch('tts.stop_tts') as mock_stop, \
         patch('tts.get_tts_play') as mock_play:

        from actions import action_talk_with_other

        result = action_talk_with_other()

        assert mock_stop.called, "stop_tts should be called"
        assert mock_chat.called, "chat_llm should be called"
        assert mock_notice.called, "notice should be called"
        assert mock_stream.called, "stream_insert should be called"
        assert mock_play.called, "get_tts_play should be called"
        assert result == "Test Reply", f"result should be 'Test Reply', got: {result}"

        print("PASS: action_talk_with_other")

# Run tests
import importlib
import actions

try:
    test_action_self_talking()
    test_action_push_agreed_event()
    test_action_talk_with_other()
    print("\nAll tests PASSED!")
finally:
    shutil.move('partner/config.json.bak', 'partner/config.json')
    print("\nConfig file restored")
