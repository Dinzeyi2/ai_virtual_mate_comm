"""
伴侣模式专用对话桥接模块
职责: 构建 prompt → 调用 LLM → 解析 JSON → 更新状态 → 返回回复
从 llm.py 中抽离，实现关注点分离 (SoC)
"""

import json
from tts import notice


def build_companion_prompt(base_prompt, partner_config):
    """构建伴侣模式专属系统提示词"""
    agreed_events = partner_config.get_agreed_events()
    current_event = agreed_events[0] if agreed_events else ''

    return base_prompt + "/no_think" + f"""
                    请你严格按照如下json格式进行回答：{partner_config.response_rule}
                    请你记住你当前扮演角色的人物状态:
                    人物当前的位置:{partner_config.get_current_location()},
                    可供参考的人物位置:{partner_config.get_current_location_options()}
                    当前对话的时间段:{partner_config.get_current_time_period()}
                    当前人物正在干什么:{partner_config.get_current_action()}
                    可供参考的人物行为:{partner_config.get_current_action_options()}
                    当前与用户约定的事:{current_event}
                    待完成的约定事件:{partner_config.get_agreed_events()}
                    当前对话场景下用户是否在角色的身边:{partner_config.get_is_user_nearby()}
                    请你严格遵循以下要求：
                    在你遵循回答格式进行回答的时候如：人物位置和行为在对应参考列表里有相同意思的选择则选择参考列表里的选项
                    在你遵循回答格式进行回答的时候:如你扮演的角色与他人对话则他人说话的内容应当放到"()"表示
                    在你遵循回答格式进行回答的时候:严禁在你的回答中多次强调与用户约定的内容{partner_config.get_agreed_events()}
                    在你遵循回答格式进行回答的时候如：产生的新的约定事件在待完成的约定事件列表里有相同意思的事件则不要添加新的约定事件且回答中is_new_event设置为False
                    前后回答的逻辑应当连贯
                    回复中提到的所有事物（人、物品、环境细节）必须与当前状态匹配
                    不能突然提及另一个地点的东西，除非明确发生了场景转换
                    场景转换必须通过明确的过渡描述，不能跳跃

                    """


def update_companion_state(partner_config, res_json, openai_history, think_filter_switch):
    """解析 LLM 返回的 JSON 并更新伴侣状态，返回回复消息"""
    res = json.loads(res_json)

    # 获取 llm 返回消息并添加至历史对话
    openai_history.append({"role": "assistant", "content": res['message']})

    # 更新角色状态
    partner_config.set_current_action(res['action'])
    partner_config.set_current_location(res['location'])
    partner_config.set_is_user_nearby(res['is_user_nearby'])
    partner_config.set_current_time_period(res['time_period'])

    # 更新下一次主动行为
    choice_next_action = res.get('choice_next_action', {})
    if choice_next_action and choice_next_action.get('action'):
        partner_config.set_choice_next_action(
            choice_next_action['action'],
            choice_next_action.get('params')
        )

    # 约定事件管理
    if res['is_completion']:
        partner_config.take_agreed_event()
    if res['is_new_event']:
        partner_config.put_agreed_event(res['new_event'])

    # 返回消息处理
    res_message = res['message']
    if think_filter_switch == "on":
        res_message = res_message.split("</think>")[-1].strip()
    return res_message


def companion_chat(msg, openai_history, client, custom_model, partner_config, think_filter_switch, base_prompt):
    """伴侣模式专用对话入口

    Args:
        msg: 用户消息
        openai_history: 对话历史列表
        client: OpenAI 客户端实例
        custom_model: 模型名称
        partner_config: characterStatus 实例
        think_filter_switch: 思考标签过滤开关
        base_prompt: 基础角色设定 prompt

    Returns:
        回复消息字符串
    """
    # 构建提示词
    prompt1 = build_companion_prompt(base_prompt, partner_config)

    # 加入用户消息
    openai_history.append({"role": "user", "content": msg})

    # 构造消息列表
    messages = [{"role": "system", "content": prompt1}]
    messages.extend(openai_history)

    # 发送聊天请求 (采用 json_object 约束模型返回格式)
    # TODO: 提供接口判断当前配置模型与接口是否支持 json_object 或 json_schema
    completion = client.chat.completions.create(
        model=custom_model,
        messages=messages,
        response_format={"type": "json_object"}
    )

    res_json = completion.choices[0].message.content

    # 尝试解析 JSON 并更新状态
    try:
        return update_companion_state(partner_config, res_json, openai_history, think_filter_switch)
    except Exception as e:
        print(e)
        notice('模型未按指定格式回复')
        # 回退: 直接返回原始文本
        res = res_json
        if think_filter_switch == "on":
            res = res.split("</think>")[-1].strip()
        return res
