from openai import OpenAI
import os
import json
import textwrap  # 用于处理多行字符串的缩进，提高代码可读性

# 预定义示例响应，用于向模型展示期望的输出格式
# 示例1：包含所有字段的完整响应
example1_response = json.dumps(
    {
        "info": {"name": "张三", "age": "25岁", "email": "zhangsan@example.com"},
        "hobby": ["唱歌"]
    },
    ensure_ascii=False
)
# 示例2：包含多个hobby的响应
example2_response = json.dumps(
    {
        "info": {"name": "李四", "age": "30岁", "email": "lisi@example.com"},
        "hobby": ["跳舞", "游泳"]
    },
    ensure_ascii=False
)
# 示例3：不包含hobby字段的响应（hobby非必需）
example3_response = json.dumps(
    {
        "info": {"name": "赵六", "age": "28岁", "email": "zhaoliu@example.com"}
    },
    ensure_ascii=False
)
# 示例4：另一个不包含hobby字段的响应
example4_response = json.dumps(
    {
        "info": {"name": "孙七", "age": "35岁", "email": "sunqi@example.com"}
    },
    ensure_ascii=False
)

# 初始化OpenAI客户端
client = OpenAI(
    # 若没有配置环境变量，请将下行替换为：api_key="sk-xxx"
    # 各地域的API Key不同。获取API Key：https://help.aliyun.com/zh/model-studio/get-api-key
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    # 以下是北京地域base_url，如果使用新加坡地域的模型，需要将base_url替换为：https://dashscope-intl.aliyuncs.com/compatible-mode/v1
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

# dedent的作用是去除每行开头的公共缩进，使字符串在代码中可以美观地缩进，但在运行时不会包含这些额外的空格
system_prompt = textwrap.dedent(f"""\
    请从用户输入中提取个人信息并按照指定的JSON Schema格式输出：

    【输出格式要求】
    输出必须严格遵循以下JSON结构：
    {{
      "info": {{
        "name": "字符串类型，必需字段，用户姓名",
        "age": "字符串类型，必需字段，格式为'数字+岁'，例如'25岁'",
        "email": "字符串类型，必需字段，标准邮箱格式，例如'user@example.com'"
      }},
      "hobby": ["字符串数组类型，非必需字段，包含用户的所有爱好，如未提及则完全不输出此字段"]
    }}

    【字段提取规则】
    1. name: 从文本中识别用户姓名，必需提取
    2. age: 识别年龄信息，转换为"数字+岁"格式，必需提取
    3. email: 识别邮箱地址，保持原始格式，必需提取
    4. hobby: 识别用户爱好，以字符串数组形式输出，如未提及爱好信息则完全省略hobby字段

    【参考示例】
    示例1（包含爱好）：
    Q：我叫张三，今年25岁，邮箱是zhangsan@example.com，爱好是唱歌
    A：{example1_response}

    示例2（包含多个爱好）：
    Q：我叫李四，今年30岁，邮箱是lisi@example.com，平时喜欢跳舞和游泳
    A：{example2_response}

    示例3（不包含爱好）：
    Q：我叫赵六，今年28岁，我的邮箱是zhaoliu@example.com
    A：{example3_response}

    示例4（不包含爱好）：
    Q：我是孙七，35岁，邮箱sunqi@example.com
    A：{example4_response}

    请严格按照上述格式和规则提取信息并输出JSON。如果用户未提及爱好，则不要在输出中包含hobby字段。\
""")

# 调用大模型API进行信息提取
completion = client.chat.completions.create(
    model="qwen-plus",
    messages=[
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": "大家好，我叫刘五，今年34岁，邮箱是liuwu@example.com，平时喜欢打篮球和旅游", 
        },
    ],
    response_format={"type": "json_object"},  # 指定返回JSON格式
)

# 提取并打印模型生成的JSON结果
json_string = completion.choices[0].message.content
print(json_string)

if __name__ == '__main__':
     response_rul_prompt = textwrap.dedent(f"""\
    请从用户输入中提取个人信息并按照指定的JSON Schema格式输出：

    【输出格式要求】
    输出必须严格遵循以下JSON结构：
    {{
        "time_period": "字符串类型，必需字段,表示本次对话结束后的时间段，你必须从这列表中选择一个值[早上，中午，下午，晚上，凌晨]如时间段无变化则保持不变",
        "is_user_nearby": "字符串类型，必需字段,表示当前对话结束后你用户是否在你扮演的角色旁或者你扮演的角色能否看到用户。你能只能选择true,false这两种值",
        "action": '字符串类型，必需字段,表示当前对话结束后你扮演角色的行为", 
        "location": "字符串类型，必需字段,表示当前对话结束后你扮演角色的位置", 
        "is_completion": "布尔类型，必需字段,表示当前对话结束后是否完成与用户约定的事件，你只能选择true,false两种值", 
        "is_new_event": "布尔类型，必需字段,表示当前对话结束后是否产生新的与用户约束的事件,你只能选择true,false", 
        "new_event": "字符串类型，必需字段,表示当前对话结束后产生的新的与用户约定的事件", 
        "message": "字符串类型，必需字段,表示你的回答，回复", 
        "choice_next_action": "字符串类型，必需字段,表示当前对话结束后，角色主动发起下一步行为的选择。你必须根据当前情境从以下选项中选择最合适的一个——action_self_talking：角色独处、无明确事项时，进行自言自语或内心独白；action_push_agreed_event：当前存在与用户未完成的约定事件时，选择此项来推进事件；action_express_body_state：角色有明显身体状态需要表达时才选（如饿、累、困、冷等），不可随意滥用；action_interact_with_environment：角色在当前位置有可互动的环境元素时选择；action_talk_with_other：角色需要主动找其他人说话时选择，需同时填写character_name；action_default：不符合以上任何情境时选择此默认项。你必须从以下列表中选择一个值", 
        "next_destination_llm": "字符串类型，必需字段,表示当前会话结束后你扮演的角色要前往的目的地，如无变化则保持原值或填空字符串', 
        "next_destination_user": "字符串类型，必需字段,表示当前会话结束后用户要前往的目的地，如无变化则保持原值或填空字符串"
    }}
    【choice_next_action字段可选值列表】
    [
    {{"action": "action_self_talking", "params": null}},
    {{"action": "action_push_agreed_event", "params": null}},
    {{"action": "action_express_body_state", "params": null}},
    {{"action": "action_interact_with_environment", "params": null}},
    {{"action": "action_talk_with_other", "params": {{"character_name": "字符串类型，必需字段,表示你扮演的角色与其他人对话的名字"}}}},
    {{"action": "action_default","params": null }}
    ]
    【time_period字段可选值列表】
    [早上，中午，下午，晚上，凌晨]
    【参考示例】
    示例1：
    {{example_response}}
    请严格按照上述格式和规则提取信息并输出JSON。\
""")
     print(response_rul_prompt)