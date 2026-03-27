from llm import chat_llm, notice, stream_insert
from tts import stop_tts, get_tts_play
from partner.characterStatus import characterStatus
from sys_init import mate_name
# 全局角色状态实例
partner_status = characterStatus()


def action_self_talking():
    """自言自语 - LLM扮演的角色自己和自己说话"""
    try:
        stop_tts()
        msg = "请你根据当前人物状态信息进行自然自语"
        bot_response = chat_llm(msg)
        notice(f"{mate_name}自言自语")
        stream_insert(f"{mate_name}（自言自语）:\n    {bot_response}\n")
        get_tts_play(bot_response)
        return bot_response
    except Exception as e:
        notice(f"自言自语出错: {e}")
        return None


def action_push_agreed_event():
    """主动推进对话到当前约定的事件"""
    try:
        agreed_events = partner_status.get_agreed_events()
        if not agreed_events:
            return None

        stop_tts()
        current_event = agreed_events[0]
        msg = "请你自己主动推进对话到当前与用户约定的事件"
        bot_response = chat_llm(msg)
        notice(f"{mate_name}推动约定事件")
        stream_insert(f"{mate_name}:\n    {bot_response}\n")
        get_tts_play(bot_response)
        return bot_response
    except Exception as e:
        notice(f"推动约定事件出错: {e}")
        return None


def action_talk_with_other():
    """LLM扮演的角色与其他角色进行对话"""
    try:
        stop_tts()
        msg = "请你依据你扮演角色的人际关系以及当前状态，在扮演角色的人际关系中选出一个合理的角色进行对话"
        bot_response = chat_llm(msg)
        notice(f"{mate_name}对话")
        stream_insert(f"{mate_name}:\n    {bot_response}\n")
        get_tts_play(bot_response)
        return bot_response
    except Exception as e:
        notice(f"与其他角色对话出错: {e}")
        return None
