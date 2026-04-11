"""
角色卡片配置管理类
职责：管理 character_card 配置（位于 partner/config.json），提供角色卡片读写接口
"""

import json
import os

# 配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')


class CharacterCardManager:
    """角色卡片配置管理类"""

    def __init__(self):
        """初始化并加载配置"""
        self._config = None
        self._base_url = None
        self._load_config()

    def _load_config(self):
        """从配置文件加载 character_card 配置"""
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                self._config = json.load(f)

            if 'character_card' not in self._config:
                self._config['character_card'] = {
                    'base_url': 'partner/characterCard'
                }
                self._save_config()

            self._base_url = self._config['character_card'].get('base_url', 'partner/characterCard')
        except Exception as e:
            raise Exception(f"角色卡片配置文件加载失败：{e}")

    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise Exception(f"角色卡片配置文件保存失败：{e}")

    def _get_config(self):
        """获取 character_card 配置对象（确保存在）"""
        if 'character_card' not in self._config:
            self._config['character_card'] = {
                'base_url': 'partner/characterCard'
            }
            self._save_config()
        return self._config['character_card']

    # ==================== 角色启用状态管理 ====================

    def get_enabled_characters(self):
        """获取所有启用的角色列表"""
        config = self._get_config()
        enabled = []
        for key, value in config.items():
            if key == 'base_url':
                continue
            if isinstance(value, dict) and value.get('enabled', False):
                enabled.append(key)
        return enabled

    def is_enabled(self, character_name):
        """检查指定角色是否启用"""
        config = self._get_config()
        if character_name not in config:
            return False
        character_config = config[character_name]
        if isinstance(character_config, dict):
            return character_config.get('enabled', False)
        return False

    def set_enabled(self, character_name, enabled):
        """设置角色启用状态"""
        config = self._get_config()
        if character_name not in config:
            config[character_name] = {
                'enabled': enabled,
                'files': []
            }
        else:
            if isinstance(config[character_name], dict):
                config[character_name]['enabled'] = enabled
            else:
                config[character_name] = {
                    'enabled': enabled,
                    'files': []
                }
        self._save_config()

    # ==================== 角色文件管理 ====================

    def get_character_files(self, character_name):
        """获取角色卡片文件列表"""
        config = self._get_config()
        if character_name not in config:
            return []
        character_config = config[character_name]
        if isinstance(character_config, dict):
            return character_config.get('files', [])
        return []

    def set_character_files(self, character_name, files):
        """设置角色卡片文件列表"""
        config = self._get_config()
        if character_name not in config:
            config[character_name] = {
                'enabled': False,
                'files': files
            }
        else:
            if isinstance(config[character_name], dict):
                config[character_name]['files'] = files
            else:
                config[character_name] = {
                    'enabled': False,
                    'files': files
                }
        self._save_config()

    def add_character_file(self, character_name, filename):
        """添加角色卡片文件到列表"""
        config = self._get_config()
        if character_name not in config:
            config[character_name] = {
                'enabled': False,
                'files': [filename]
            }
        else:
            if isinstance(config[character_name], dict):
                if 'files' not in config[character_name]:
                    config[character_name]['files'] = []
                if filename not in config[character_name]['files']:
                    config[character_name]['files'].append(filename)
            else:
                config[character_name] = {
                    'enabled': False,
                    'files': [filename]
                }
        self._save_config()

    # ==================== 文件路径解析 ====================

    def get_base_url(self):
        """获取角色卡片目录基础路径"""
        return self._base_url

    def get_file_path(self, character_name, filename):
        """获取角色卡片文件完整路径"""
        # CONFIG_PATH 是 partner/config.json，规范化后获取 partner 目录
        partner_dir = os.path.dirname(os.path.normpath(CONFIG_PATH))
        # characterCard 目录在 partner/ 下
        character_dir = os.path.join(partner_dir, 'characterCard', character_name)
        return os.path.normpath(os.path.join(character_dir, filename))

    def read_card_content(self, character_name, filename):
        """读取角色卡片文件内容"""
        file_path = self.get_file_path(character_name, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            raise Exception(f"读取角色卡片文件失败 [{file_path}]: {e}")

    def read_all_cards(self, character_name):
        """读取角色所有卡片文件内容，返回字典 {filename: content}"""
        files = self.get_character_files(character_name)
        result = {}
        for filename in files:
            try:
                result[filename] = self.read_card_content(character_name, filename)
            except Exception:
                result[filename] = None
        return result

    # ==================== 完整配置 ====================

    def get_character_card_config(self):
        """获取完整的角色卡片配置"""
        return self._get_config()

    def add_character(self, character_name, enabled=False, files=None):
        """添加新角色配置"""
        config = self._get_config()
        config[character_name] = {
            'enabled': enabled,
            'files': files if files is not None else []
        }
        self._save_config()


# 全局单例
character_card_manager = CharacterCardManager()


if __name__ == '__main__':
    print("=" * 50)
    print("CharacterCardManager 测试")
    print("=" * 50)

    # 测试 1: 基础路径
    print("\n[测试 1] 基础路径")
    print(f"base_url: {character_card_manager.get_base_url()}")

    # 测试 2: 启用的角色
    print("\n[测试 2] 启用的角色")
    print(f"enabled characters: {character_card_manager.get_enabled_characters()}")

    # 测试 3: 甘雨启用状态
    print("\n[测试 3] 甘雨启用状态")
    print(f"甘雨 enabled: {character_card_manager.is_enabled('甘雨')}")

    # 测试 4: 甘雨文件列表
    print("\n[测试 4] 甘雨文件列表")
    print(f"甘雨 files: {character_card_manager.get_character_files('甘雨')}")

    # 测试 5: 文件路径
    print("\n[测试 5] 文件路径")
    path = character_card_manager.get_file_path('甘雨', 'ganyu-research.md')
    print(f"ganyu-research.md: {path}")

    # 测试 6: 读取文件内容
    print("\n[测试 6] 读取文件内容")
    content = character_card_manager.read_card_content('甘雨', 'ganyu-research.md')
    print(f"ganyu-research.md: {len(content)} 字符")
    print(f"前 100 字符：{content[:100]}...")

    # 测试 7: 读取所有卡片
    print("\n[测试 7] 读取所有卡片")
    cards = character_card_manager.read_all_cards('甘雨')
    for filename, content in cards.items():
        if content:
            print(f"  {filename}: {len(content)} 字符")

    print("\n" + "=" * 50)
    print("所有测试通过！")
    print("=" * 50)
