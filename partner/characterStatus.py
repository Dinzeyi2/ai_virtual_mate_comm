import json

config_path = 'partner/config.json'
try:
    with open(config_path, 'r', encoding='utf-8') as f:
        config_json = json.load(f)
except Exception as e:
    raise Exception(f"伴侣配置文件导入错误{e}")


# 数据封装
class characterStatus:

    response_rule = config_json['response_rule']
    response_rule_schema = config_json['response_rule_schema']
    response_rule_object = config_json['response_rule_object']

    def __init__(self):
        # 对象属性
        self._current_location = config_json['last_status']['location']
        self._current_action = config_json['last_status']['action']
        self._agreed_events = config_json['last_status']['agreed_events']
        self._current_location_options = config_json['last_status']['current_location_options']
        self._current_action_options = config_json['last_status']['current_action_options']
        self._is_user_nearby = config_json['last_status']['is_user_nearby']
        self._choice_next_action = config_json['last_status']['choice_next_action']
        self._destination_llm = config_json['last_status'].get('destination_llm', '')
        self._destination_user = config_json['last_status'].get('destination_user', '')

        # 图片生成配置
        default_generate_image = {
            'positive_prompt': '',
            'negative_prompt': '',
            'other_prompt': '',
            'is_generate': False,
            'generate_frequency': 'always',
            'generate_frequency_options': ['always', 'often', 'little'],
            'counts': 0
        }
        self._generate_image_config = config_json['last_status'].get('generate_image', default_generate_image)

    def _save(self):
        """将内存状态同步写入配置文件"""
        try:
            config_json['last_status']['location'] = self._current_location
            config_json['last_status']['action'] = self._current_action
            config_json['last_status']['agreed_events'] = self._agreed_events.copy()
            config_json['last_status']['current_location_options'] = self._current_location_options
            config_json['last_status']['current_action_options'] = self._current_action_options
            config_json['last_status']['is_user_nearby'] = self._is_user_nearby
            config_json['last_status']['choice_next_action'] = self._choice_next_action
            config_json['last_status']['destination_llm'] = self._destination_llm
            config_json['last_status']['destination_user'] = self._destination_user
            config_json['last_status']['generate_image'] = self._generate_image_config
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_json, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")

    # current_location
    def get_current_location(self):
        return self._current_location

    def set_current_location(self, value):
        try:
            if value not in self._current_location_options:
                self._current_location_options.append(value)
            self._current_location = value
            self._save()
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")

    # current_action
    def get_current_action(self):
        return self._current_action

    def set_current_action(self, value):
        try:
            if value not in self._current_action_options:
                self._current_action_options.append(value)
            self._current_action = value
            self._save()
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")

    # agreed_event
    def get_agreed_events(self):
        return self._agreed_events.copy()

    def put_agreed_event(self, value):
        try:
            self._agreed_events.append(value)
            self._save()
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")

    def take_agreed_event(self):
        try:
            if not self._agreed_events:
                return None
            event = self._agreed_events.pop(0)
            self._save()
            return event
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")

    def get_current_action_options(self):
        return self._current_action_options

    def get_current_location_options(self):
        return self._current_location_options

    # is_user_nearby
    def get_is_user_nearby(self):
        return self._is_user_nearby

    def set_is_user_nearby(self, value):
        try:
            self._is_user_nearby = value
            self._save()
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")

    # choice_next_action
    def get_choice_next_action(self):
        """获取下一次主动行为的配置，返回 {"action": "...", "params": {...}} 或 {"action": "...", "params": null}"""
        return self._choice_next_action

    def set_choice_next_action(self, action, params=None):
        """设置下一次主动行为的配置
        Args:
            action: 行为名称，如 "action_self_talking"
            params: 行为参数，如 {"character_name": "甘雨"} 或 None
        """
        try:
            self._choice_next_action = {"action": action, "params": params}
            self._save()
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")

    # destination_llm / destination_user
    def get_destination_llm(self):
        """获取 LLM 扮演的角色要前往的目的地"""
        return self._destination_llm

    def set_destination_llm(self, value):
        """设置 LLM 扮演的角色要前往的目的地"""
        try:
            self._destination_llm = value
            self._save()
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")

    def get_destination_user(self):
        """获取用户要前往的目的地"""
        return self._destination_user

    def set_destination_user(self, value):
        """设置用户要前往的目的地"""
        try:
            self._destination_user = value
            self._save()
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")

    # generate_image 配置管理
    def get_generate_image_config(self):
        """获取完整的图片生成配置"""
        return self._generate_image_config

    def get_is_generate(self):
        """判断是否开启图片生成"""
        return self._generate_image_config.get('is_generate', False)

    def set_is_generate(self, value):
        """设置图片生成开关"""
        self._generate_image_config['is_generate'] = bool(value)
        self._save()

    def get_generate_frequency(self):
        """获取生成频率"""
        return self._generate_image_config.get('generate_frequency', 'always')

    def set_generate_frequency(self, value):
        """设置生成频率"""
        if value in self._generate_image_config.get('generate_frequency_options', []):
            self._generate_image_config['generate_frequency'] = value
            self._save()

    def get_generate_counts(self):
        """获取当前计数器"""
        return self._generate_image_config.get('counts', 0)

    def reset_generate_counts(self):
        """重置计数器"""
        self._generate_image_config['counts'] = 0
        self._save()

    def should_generate_image(self):
        """根据频率配置和计数器判断是否应该生成图片

        逻辑说明:
        - always: 每次都生成
        - often: 每 3 次生成 1 次 (第 3、6、9...次生成)
        - little: 每 5 次生成 1 次 (第 5、10、15...次生成)
        """
        if not self._generate_image_config.get('is_generate', False):
            return False

        frequency = self._generate_image_config.get('generate_frequency', 'always')

        if frequency == 'always':
            return True

        counts = self._generate_image_config.get('counts', 0)

        # 先递增计数器
        self._generate_image_config['counts'] = counts + 1
        self._save()

        # 检查是否达到阈值
        if frequency == 'often' and self._generate_image_config['counts'] >= 3:
            self._generate_image_config['counts'] = 0
            self._save()
            return True
        elif frequency == 'little' and self._generate_image_config['counts'] >= 5:
            self._generate_image_config['counts'] = 0
            self._save()
            return True

        return False

    def get_image_prompts(self):
        """获取自定义提示词"""
        config = self._generate_image_config
        prompts = {
            'positive': config.get('positive_prompt', ''),
            'negative': config.get('negative_prompt', ''),
            'other': config.get('other_prompt', '')
        }
        return prompts

    def set_image_prompt(self, prompt_type, value):
        """设置指定类型的提示词"""
        if prompt_type in ['positive_prompt', 'negative_prompt', 'other_prompt']:
            self._generate_image_config[prompt_type] = value
            self._save()


if __name__ == '__main__':
    a = characterStatus()
    print(a.get_current_action_options())
    print(a.get_current_location_options())

    a.set_current_action('工作')
    a.set_current_location('家')
    print(a.get_agreed_events())
    print(a.get_current_action())
    print(a.get_current_location())
