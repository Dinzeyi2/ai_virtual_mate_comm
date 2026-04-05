from llm import chat_llm, notice, stream_insert
from tts import stop_tts, get_tts_play
from sys_init import mate_name, partner_config
"""
Actions 准则：
该文件设置的行为均要满足以下条件:
    1. 被动式回复无法发生的行为
    2. 契合伴侣模式思想
"""



def action_self_talking():
    """自言自语 - LLM扮演的角色自己和自己说话"""
    try:
        print('角色自言自语')
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
        print('主动推进对话')
        agreed_events = partner_config.get_agreed_events()
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


#TODO llm应该可以在保持主要与用户对话的情况下，根据对话情况自主选择一名人物进行对话
def action_talk_with_other(name):
    """LLM扮演的角色与其他角色进行对话"""
    try:
        stop_tts()
        print(f'角色与{name}对话')
        msg = "请你依据你扮演角色的人际关系以及当前状态，在扮演角色的人际关系中选出一个合理的角色进行对话"
        bot_response = chat_llm(msg)
        notice(f"{mate_name}对话")
        stream_insert(f"{mate_name}与{name}对话:\n    {bot_response}\n")
        get_tts_play(bot_response)
        return bot_response
    except Exception as e:
        notice(f"与其他角色对话出错: {e}")
        return None


def action_express_body_state():
    """表达身体状态 - LLM扮演的角色描述自己当前的身体状态或动作"""
    try:
        print('角色表达身体状态')
        stop_tts()
        msg = """主动表达一个“身体”的感受或需求，比如困了、饿了、冷了，
                并基于这个状态提出一个交互邀请或结束当前话题
                """
        bot_response = chat_llm(msg)
        notice(f"{mate_name}表达身体状态")
        stream_insert(f"{mate_name}（身体状态）:\n    {bot_response}\n")
        get_tts_play(bot_response)
        return bot_response
    except Exception as e:
        notice(f"表达身体状态出错: {e}")
        return None


def action_interact_with_environment():
    """与环境互动 - LLM扮演的角色与周围环境中的物体或场景进行互动"""
    try:
        print('角色与环境互动')
        stop_tts()
        msg = """        
        请你根据当前人物状态信息和所在环境，描述角色与周围环境中的物体或场景进行互动
        如：拿起桌上的水杯等，“听见”窗外的雨声，“闻到”饭菜的香味，或者“看到”桌上的某件物品。
        可以有说话内容也可以只有动作。"""
        bot_response = chat_llm(msg)
        notice(f"{mate_name}与环境互动")
        stream_insert(f"{mate_name}\n    {bot_response}\n")
        get_tts_play(bot_response)
        return bot_response
    except Exception as e:
        notice(f"与环境互动出错: {e}")
        return None
    
def action_default():
    """正常与用户对话"""
    try:
        
        stop_tts()
        msg = """        
        请你根据当前人物状态信息，所在环境以及历史对话说出你扮演角色的下一句话s
        """
        bot_response = chat_llm(msg)
        notice(f"{mate_name}")
        stream_insert(f"{mate_name}\n    {bot_response}\n")
        get_tts_play(bot_response)
        return bot_response
    except Exception as e:
        notice(f"与环境互动出错: {e}")
        return None

