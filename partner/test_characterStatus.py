import json
import shutil

# 必须在导入 characterStatus 之前备份
shutil.copy('partner/config.json', 'partner/config.json.bak')

from characterStatus import characterStatus
import characterStatus as cs_module

def reset_config():
    """重置配置文件到初始状态"""
    default_config = {
        "response_rule": "test",
        "last_status": {
            "location": "",
            "time_period": "",
            "action": "",
            "agreed_events": [],
            "is_user_nearby": False,
            "current_location_options": [""],
            "current_action_options": [""]
        }
    }
    with open('partner/config.json', 'w', encoding='utf-8') as f:
        json.dump(default_config, f, ensure_ascii=False, indent=4)
    # 重新加载模块级别的 config_json
    with open('partner/config.json', 'r', encoding='utf-8') as f:
        cs_module.config_json = json.load(f)

def test_basic():
    print("=== 测试基本get方法 ===")
    reset_config()
    status = characterStatus()

    print(f"response_rule: {characterStatus.response_rule}")
    print(f"current_location: {status.get_current_location()}")
    print(f"current_time_period: {status.get_current_time_period()}")
    print(f"current_action: {status.get_current_action()}")
    print(f"agreed_events: {status.get_agreed_events()}")
    print(f"current_location_options: {status.get_current_location_options()}")
    print(f"current_action_options: {status.get_current_action_options()}")
    print(f"is_user_nearby: {status.get_is_user_nearby()}")

def test_setters():
    print("\n=== 测试set方法 ===")
    reset_config()
    status = characterStatus()

    status.set_current_location('家')
    print(f"set_current_location('家'): {status.get_current_location()}")

    status.set_current_time_period('早上')
    print(f"set_current_time_period('早上'): {status.get_current_time_period()}")

    status.set_current_action('工作')
    print(f"set_current_action('工作'): {status.get_current_action()}")

    status.put_agreed_event('下午去买东西')
    print(f"put_agreed_event('下午去买东西'): {status.get_agreed_events()}")

def test_take_agreed_event():
    print("\n=== 测试take_agreed_event ===")
    reset_config()
    status = characterStatus()

    status.put_agreed_event('事件1')
    status.put_agreed_event('事件2')
    print(f"添加后: {status.get_agreed_events()}")

    event = status.take_agreed_event()
    print(f"take_agreed_event(): {event}")
    print(f"取出后: {status.get_agreed_events()}")

    # 再次取出
    event2 = status.take_agreed_event()
    print(f"第二次取出: {event2}")
    print(f"取出后: {status.get_agreed_events()}")

def test_config_sync():
    print("\n=== 测试配置文件同步 ===")
    reset_config()
    status = characterStatus()

    status.set_current_location('公司')
    status.set_current_time_period('中午')
    status.set_current_action('开会')
    status.put_agreed_event('晚上吃饭')

    # 重新读取配置验证
    with open('partner/config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    print(f"config.json last_status: {config['last_status']}")

def test_is_user_nearby():
    print("\n=== 测试 is_user_nearby ===")
    reset_config()
    status = characterStatus()

    print(f"初始值: {status.get_is_user_nearby()}")
    status.set_is_user_nearby(True)
    print(f"set True后: {status.get_is_user_nearby()}")

if __name__ == '__main__':
    try:
        test_basic()
        test_setters()
        test_take_agreed_event()
        test_config_sync()
        test_is_user_nearby()
        print("\n所有测试通过!")
    finally:
        # 恢复备份
        shutil.move('partner/config.json.bak', 'partner/config.json')
        # 重新加载 config_json
        with open('partner/config.json', 'r', encoding='utf-8') as f:
            cs_module.config_json = json.load(f)
