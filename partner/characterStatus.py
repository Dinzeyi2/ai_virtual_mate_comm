import json

config_path = 'partner/config.json'
try: 
    with open(config_path,'r', encoding='utf-8') as f:
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
        self._current_location = config_json['last_status']['location']  # 初始化当前角色的所处的位置
        self._current_time_period = config_json['last_status']['time_period']  # 初始化当前对话的时间段
        self._current_action =config_json['last_status']['action']  # 初始化当前角色的行为
        self._agreed_events = config_json['last_status']['agreed_events']  # 初始化今天中与用户约定好的事
        self._current_location_options = config_json['last_status']['current_location_options']  # 初始化自迭代的可选角色位置选项
        self._current_action_options = config_json['last_status']['current_action_options']  # 初始化自迭代的可选角色行为选项
        self._is_user_nearby = config_json['last_status']['is_user_nearby']  # 初始化用户是否在角色身边
        self._choice_next_action = config_json['last_status']['choice_next_action']  # 初始化下一次主动行为的配置

    # current_location
    def get_current_location(self):
        return self._current_location

    def set_current_location(self, value):
        try: 
            
                # 同步更新config文件与对象状态
            if value not in self._current_location_options:
                self._current_location_options.append(value)
                self._current_location = value
                config_json['last_status']['location'] = value
                if value not in config_json['last_status']['current_location_options']:
                    config_json['last_status']['current_location_options'].append(value)
                with open(config_path,'w+', encoding='utf-8') as f:
                    json.dump(config_json, f, ensure_ascii=False, indent=4)
            else:
                config_json['last_status']['location'] = value
                self._current_location = value
                with open(config_path,'w+', encoding='utf-8') as f:
                    json.dump(config_json, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise Exception(f"伴侣配置文件导入错误{e}")

    # current_time_period
    def get_current_time_period(self):
        return self._current_time_period

    def set_current_time_period(self, value):
        try:            
            # 同步更新config文件与对象状态
            self._current_time_period = value

            config_json['last_status']['time_period'] = value
            with open(config_path,'w+', encoding='utf-8') as f:
                json.dump(config_json, f, ensure_ascii=False, indent=4)

        except Exception as e:
            raise Exception(f"伴侣配置文件导入错误{e}")

    # current_action
    def get_current_action(self):
        return self._current_action

    def set_current_action(self, value):
        try: 
            
            # 同步更新config文件与对象状态
            if value not in self._current_action_options:
                self._current_action_options.append(value)
                self._current_action = value
                
                config_json['last_status']['action'] = value
                if value not in config_json['last_status']['current_action_options']:
                    config_json['last_status']['current_action_options'].append(value)
                with open(config_path,'w+', encoding='utf-8') as f:
                    json.dump(config_json, f, ensure_ascii=False, indent=4)          
            else:
                config_json['last_status']['action'] = value
                self._current_action = value
                with open(config_path,'w+', encoding='utf-8') as f:
                    json.dump(config_json, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise Exception(f"伴侣配置文件导入错误{e}")  

    # agreed_event
    def get_agreed_events(self):
        return self._agreed_events

    def put_agreed_event(self, value):
        try:
            # 同步更新config文件与对象状态
            self._agreed_events.append(value)
            config_json['last_status']['agreed_events'] = self._agreed_events.copy()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_json, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")
        
    def take_agreed_event(self):
        try:
            # 同步更新config文件与对象状态
            if not self._agreed_events:
                return None
            event = self._agreed_events.pop(0)
            config_json['last_status']['agreed_events'] = self._agreed_events.copy()
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_json, f, ensure_ascii=False, indent=4)
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
            config_json['last_status']['is_user_nearby'] = value
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_json, f, ensure_ascii=False, indent=4)
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
            config_json['last_status']['choice_next_action'] = self._choice_next_action
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_json, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise Exception(f"伴侣配置文件同步错误{e}")
    

    

if __name__ == '__main__':
    a = characterStatus()
    print(a.get_current_action_options())
    print(a.get_current_location_options())

    a.set_current_action('工作')
    a.set_current_location('家')
    a.set_current_time_period('早上')
    print(a.get_agreed_events())
    print(a.get_current_action())
    print(a.get_current_location())
    print(a.get_current_time_period())