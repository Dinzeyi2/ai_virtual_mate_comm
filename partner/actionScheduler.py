import random
from partner.actions import registered_actions, load_action_json
from sys_init import partner_config
import json


def is_valid_choice(choice):
    """判断 LLM 返回的 choice_next_action 是否有效

    有效性标准:
    1. 必须是 dict
    2. 必须有 action 字段且非空
    3. action 必须在 registered_actions 中存在
    4. 如果有 params，必须是 dict 或 None
    5. action_talk_with_other 必须有有效的 character_name 参数
    """
    if not isinstance(choice, dict):
        return False

    action = choice.get('action')
    if not action or not isinstance(action, str):
        return False

    if action not in registered_actions:
        return False

    params = choice.get('params')
    if params is not None and not isinstance(params, dict):
        return False

    # action_talk_with_other 必须有有效的 character_name
    if action == 'action_talk_with_other':
        if not params:
            return False
        character_name = params.get('character_name')
        if not character_name or not isinstance(character_name, str):
            return False

    return True


def get_actual_ratio(action_name, actions):
    """计算实际占比 = count / 总次数"""
    total = sum(a['count'] for a in actions.values())
    if total == 0:
        return 0
    return actions[action_name]['count'] / total


def get_expected_ratio(action_name, weights, actions):
    """计算期望占比 = 权重 / 总权重（剔除权重为 0 的行为）"""
    valid_weights = {k: v for k, v in weights.items() if v > 0 and k in actions}
    if not valid_weights:
        return 0
    return weights.get(action_name, 0) / sum(valid_weights.values())


def select_by_weights(weights, actions):
    """按权重随机选择行为"""
    # 过滤出权重>0 且在 actions 中存在的行为
    valid_actions = {k: v for k, v in weights.items() if v > 0 and k in actions}
    if not valid_actions:
        return None

    action_names = list(valid_actions.keys())
    action_weights = list(valid_actions.values())
    return random.choices(action_names, weights=action_weights, k=1)[0]


def select_min_over_threshold(actions, weights, threshold_coefficient):
    """选择超过阈值最少的行为 (actual_ratio / expected_ratio 最小)"""
    min_ratio = float('inf')
    selected = None

    for action_name in actions:
        weight = weights.get(action_name, 0)
        if weight <= 0:
            continue

        actual_ratio = get_actual_ratio(action_name, actions)
        expected_ratio = get_expected_ratio(action_name, weights, actions)

        if expected_ratio == 0:
            continue

        over_ratio = actual_ratio / expected_ratio if expected_ratio > 0 else float('inf')
        if over_ratio < min_ratio:
            min_ratio = over_ratio
            selected = action_name

    return selected


def execute_action(action_name, params=None):
    """执行行为"""
    action_func = registered_actions.get(action_name)
    if not action_func:
        print(f"警告：行为 '{action_name}' 不存在")
        return None

    try:
        if params:
            return action_func(**params)
        else:
            return action_func()
    except Exception as e:
        print(f"执行行为 '{action_name}' 异常：{e}")
        return None


def run_action():
    """伴侣模式主动对话统一调度入口

    调度策略:
    1. 获取当前场景 (is_user_nearby)
    2. 读取 action.json 获取该场景的权重配置
    3. 获取 LLM 选择的 choice_next_action
    4. 如果 choice_next_action 有效且未超过优先级阈值 → 执行
    5. 否则按权重随机选择行为
    6. 检查选中行为是否超过阈值，超过则重新选择
    7. 如果所有行为都超过阈值，选择超过最少的那个
    """
    # 1. 获取当前状态
    is_user_nearby = partner_config.get_is_user_nearby()
    scene_key = f"is_user_nearby_{str(is_user_nearby).lower()}"

    # 2. 读取 action.json
    action_data = load_action_json()
    weights = action_data['proportion'].get(scene_key, {})
    actions = action_data['actions']

    if not weights:
        print(f"警告：场景 '{scene_key}' 的权重配置不存在，使用默认权重")
        weights = action_data['proportion'].get('is_user_nearby_false', {})

    # 3. 获取 LLM 选择的 choice_next_action
    choice = partner_config.get_choice_next_action()

    # 4. 判断 choice_next_action 是否有效
    if is_valid_choice(choice):
        action_name = choice['action']
        params = choice.get('params')

        # 计算阈值
        actual_ratio = get_actual_ratio(action_name, actions)
        expected_ratio = get_expected_ratio(action_name, weights, actions)
        threshold = expected_ratio * action_data['priority_coefficient']

        if actual_ratio <= threshold:
            print(f"执行 LLM 选择的行为：{action_name} (实际占比={actual_ratio:.2%}, 期望占比={expected_ratio:.2%}, 阈值={threshold:.2%})")
            return execute_action(action_name, params)
        else:
            print(f"LLM 选择的行为 '{action_name}' 超过优先级阈值，进入权重随机选择 (实际占比={actual_ratio:.2%}, 阈值={threshold:.2%})")

    # 5. LLM 选择无效或超过阈值，按权重随机选择
    selected_action = select_by_weights(weights, actions)
    if not selected_action:
        print("错误：没有可用的行为")
        return None

    # 6. 检查选中行为是否超过阈值，超过则重新选择
    threshold_coefficient = action_data['threshold_coefficient']
    tried_actions = set()

    while True:
        tried_actions.add(selected_action)

        actual_ratio = get_actual_ratio(selected_action, actions)
        expected_ratio = get_expected_ratio(selected_action, weights, actions)
        threshold = expected_ratio * threshold_coefficient

        if actual_ratio <= threshold:
            print(f"选中行为：{selected_action} (实际占比={actual_ratio:.2%}, 期望占比={expected_ratio:.2%}, 阈值={threshold:.2%})")
            break

        # 重新选择（排除已选过的）
        weights[selected_action] = 0
        remaining_actions = {k: v for k, v in weights.items() if v > 0 and k in actions and k not in tried_actions}

        if not remaining_actions:
            # 所有行为都超过阈值，选择超过最少的
            selected_action = select_min_over_threshold(actions, action_data['proportion'].get(scene_key, {}), action_data['threshold_coefficient'])
            print(f"所有行为都超过阈值，选择超过最少的：{selected_action}")
            break

        selected_action = select_by_weights(weights, actions)
        if not selected_action:
            # 没有可选的行为了
            selected_action = select_min_over_threshold(actions, action_data['proportion'].get(scene_key, {}), action_data['threshold_coefficient'])
            print(f"没有可选的行为，选择超过最少的：{selected_action}")
            break

    # 7. 执行选中的行为
    params = choice.get('params') if choice and choice.get('action') == selected_action else None
    return execute_action(selected_action, params)
