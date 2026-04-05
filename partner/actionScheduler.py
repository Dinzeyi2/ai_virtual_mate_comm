from partner.actions import registered_actions
from sys_init import partner_config

# 行为调用计数 (只计数需要防沉迷判断的行为)
action_counts = {
    'action_self_talking': 0,
    'action_talk_with_other': 0,
    'action_push_agreed_event': 0,
}

# 约定事件连续推进次数 (防止 LLM 反复说同样的话)
consecutive_push_count = 0
MAX_CONSECUTIVE_PUSH = 2  # 连续推进上限, 达到后切换其他行为


def reset_push_count():
    """用户说话时重置连续推进计数"""
    global consecutive_push_count
    consecutive_push_count = 0


def _should_skip_push():
    """判断是否应跳过推动约定事件 (防止 LLM 反复催促同一件事)"""
    return consecutive_push_count >= MAX_CONSECUTIVE_PUSH


def _record_push_executed():
    """记录一次推动约定事件的执行"""
    global consecutive_push_count
    consecutive_push_count += 1

# 伴侣模式主动模式入口
def run_action():
    """先判断条件再执行行为"""
    import random

    # 检查触发条件：action_self_talking + action_talk_with_other >= 2
    other_actions_count = action_counts['action_self_talking'] + action_counts['action_talk_with_other']

    if other_actions_count >= 2:
        # 条件满足，强制触发推动约定事件
        for key in action_counts:
            action_counts[key] = 0
        action_counts['action_push_agreed_event'] += 1
        _record_push_executed()
        result = registered_actions['action_push_agreed_event']()
    else:
        # 条件不满足，从 registered_actions 中随机选择行为执行
        action_list = list(registered_actions.keys())
        if len(partner_config.get_agreed_events()) == 0:
            # 如果当前无约定事件，从列表中排除 action_push_agreed_event
            action_list = [k for k in action_list if k != 'action_push_agreed_event']
        # 连续推进次数达到上限时，排除推动约定事件
        if _should_skip_push() and 'action_push_agreed_event' in action_list:
            action_list = [k for k in action_list if k != 'action_push_agreed_event']
        if not action_list:
            # 兜底: 只剩一个选项时也排除推动
            action_list = ['action_self_talking']
        action_name = random.choice(action_list)
        result = registered_actions[action_name]()
        action_counts[action_name] += 1
        if action_name == 'action_push_agreed_event':
            _record_push_executed()

    return result


def get_action_counts():
    """获取各行为的调用次数"""
    return action_counts.copy()


def reset_counts():
    """重置所有计数"""
    for key in action_counts:
        action_counts[key] = 0
