from llm import chat_llm, notice, stream_insert
from tts import stop_tts, get_tts_play
from sys_init import mate_name, partner_config

"""
Actions 准则：
该文件设置的行为均要满足以下条件:
    1. 被动式回复无法发生的行为
    2. 契合伴侣模式思想
"""


def _run_action(msg, notice_text, stream_prefix):
    """行为执行模板函数"""
    try:
        stop_tts()
        bot_response = chat_llm(msg)
        notice(notice_text)
        stream_insert(f"{stream_prefix}\n    {bot_response}\n")
        get_tts_play(bot_response)
        return bot_response
    except Exception as e:
        notice(f"{notice_text}出错: {e}")
        return None


# 行为注册表 (通过 register_action 装饰器自动注册)
registered_actions = {}


def register_action(name):
    """行为注册装饰器"""
    def decorator(func):
        registered_actions[name] = func
        return func
    return decorator


@register_action('action_self_talking')
def action_self_talking():
    """自言自语 - LLM扮演的角色自己和自己说话"""
    print('角色自言自语')
    return _run_action(
        msg="请你根据当前人物状态信息进行自然自语",
        notice_text=f"{mate_name}自言自语",
        stream_prefix=f"{mate_name}（自言自语）:"
    )


@register_action('action_push_agreed_event')
def action_push_agreed_event():
    """主动推进对话到当前约定的事件"""
    agreed_events = partner_config.get_agreed_events()
    if not agreed_events:
        return None
    print('主动推进对话')
    return _run_action(
        msg="请你自己主动推进对话到当前与用户约定的事件",
        notice_text=f"{mate_name}推动约定事件",
        stream_prefix=f"{mate_name}:"
    )


#TODO llm应该可以在保持主要与用户对话的情况下，根据对话情况自主选择一名人物进行对话
@register_action('action_talk_with_other')
def action_talk_with_other(name=None):
    """LLM扮演的角色与其他角色进行对话"""
    print(f'角色与{name}对话')
    return _run_action(
        msg="请你依据你扮演角色的人际关系以及当前状态，在扮演角色的人际关系中选出一个合理的角色进行对话",
        notice_text=f"{mate_name}对话",
        stream_prefix=f"{mate_name}与{name}对话:"
    )


@register_action('action_express_body_state')
def action_express_body_state():
    """表达身体状态 - LLM扮演的角色描述自己当前的身体状态或动作"""
    print('角色表达身体状态')
    return _run_action(
        msg="""主动表达一个"身体"的感受或需求，比如困了、饿了、冷了，
                并基于这个状态提出一个交互邀请或结束当前话题
                """,
        notice_text=f"{mate_name}表达身体状态",
        stream_prefix=f"{mate_name}（身体状态）:"
    )


@register_action('action_interact_with_environment')
def action_interact_with_environment():
    """与环境互动 - LLM扮演的角色与周围环境中的物体或场景进行互动"""
    print('角色与环境互动')
    return _run_action(
        msg="""
        请你根据当前人物状态信息和所在环境，描述角色与周围环境中的物体或场景进行互动
        如：拿起桌上的水杯等，"听见"窗外的雨声，"闻到"饭菜的香味，或者"看到"桌上的某件物品。
        可以有说话内容也可以只有动作。""",
        notice_text=f"{mate_name}与环境互动",
        stream_prefix=f"{mate_name}:"
    )


@register_action('action_default')
def action_default():
    """正常与用户对话"""
    return _run_action(
        msg="""
        请你根据当前人物状态信息，所在环境以及历史对话说出你扮演角色的下一句话""",
        notice_text=f"{mate_name}",
        stream_prefix=f"{mate_name}:"
    )
