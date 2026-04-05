from partner.actions import action_self_talking,action_push_agreed_event,action_express_body_state,action_interact_with_environment,action_default
from sys_init import partner_config
# 调用次数记录
action_counts = {
    'action_self_talking': 0,
    'action_talk_with_other': 0,
    'action_push_agreed_event': 0
}

# 行为注册表
registered_actions = {
    'action_self_talking': action_self_talking,
    'action_push_agreed_event': action_push_agreed_event,
    'action_express_body_state': action_express_body_state,
    'action_interact_with_environment': action_interact_with_environment,
    'action_default': action_default
}

# 伴侣模式主动模式入口
def run_action():
    """先判断条件再执行行为"""
    import random

    # 检查触发条件：action_self_talking + action_talk_with_other >= 2
    other_actions_count = action_counts['action_self_talking'] + action_counts['action_talk_with_other']

    if other_actions_count >= 2:
        # 条件满足，强制触发推动约定事件
        action_counts['action_self_talking'] = 0
        action_counts['action_talk_with_other'] = 0
        action_counts['action_push_agreed_event'] += 1
        result = registered_actions['action_push_agreed_event']()
    else:
        # 条件不满足，从registered_actions的key中随机选择行为执行
        action_list = list(registered_actions.keys())
        if len(partner_config.get_agreed_events()) == 0:
            # 如果当前无约定事件，从列表中排除action_push_agreed_event
            action_list = [k for k in action_list if k != 'action_push_agreed_event']
        action_name = random.choice(action_list)
        result = registered_actions[action_name]()
        action_counts[action_name] += 1

    return result


def get_action_counts():
    """获取各行为的调用次数"""
    return action_counts.copy()


def reset_counts():
    """重置所有计数"""
    for key in action_counts:
        action_counts[key] = 0
