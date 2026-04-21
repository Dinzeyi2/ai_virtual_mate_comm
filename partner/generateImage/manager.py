"""
伴侣模式文生图配置管理类
职责：管理 generate_image 配置（位于 config.json 根级别），提供配置读写接口
"""

import json
import os

# 配置文件路径
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')


class GenerateImageConfig:
    """图片生成配置管理类"""

    def __init__(self):
        """初始化并加载配置"""
        self._config = None
        self._load_config()

    def _load_config(self):
        """从配置文件加载"""
        try:
            with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
        except Exception as e:
            raise Exception(f"文生图配置文件加载失败：{e}")

    def _save_config(self):
        """保存配置到文件"""
        try:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            raise Exception(f"文生图配置文件保存失败：{e}")

    def _get_config(self):
        """获取配置对象（确保存在）"""
        if 'generate_image' not in self._config:
            # 如果配置不存在，初始化默认值
            self._config['generate_image'] = {
                'positive_prompt': '',
                'negative_prompt': '',
                'other_prompt': '',
                'is_generate': False,
                'generate_frequency': 'always',
                'generate_frequency_options': ['always', 'often', 'little'],
                'counts': 0
            }
            self._save_config()
        return self._config['generate_image']

    # ==================== 开关控制 ====================

    def get_is_generate(self):
        """判断是否开启图片生成"""
        config = self._get_config()
        return config.get('is_generate', False)

    def set_is_generate(self, value):
        """设置图片生成开关"""
        config = self._get_config()
        config['is_generate'] = bool(value)
        self._save_config()

    # ==================== 频率控制 ====================

    def get_generate_frequency(self):
        """获取生成频率"""
        config = self._get_config()
        return config.get('generate_frequency', 'always')

    def set_generate_frequency(self, value):
        """设置生成频率"""
        config = self._get_config()
        options = config.get('generate_frequency_options', ['always', 'often', 'little'])
        if value in options:
            config['generate_frequency'] = value
            self._save_config()

    def get_generate_counts(self):
        """获取当前计数器"""
        config = self._get_config()
        return config.get('counts', 0)

    def reset_generate_counts(self):
        """重置计数器"""
        config = self._get_config()
        config['counts'] = 0
        self._save_config()

    def should_generate_image(self):
        """根据频率配置和计数器判断是否应该生成图片

        逻辑说明:
        - always: 每次都生成
        - often: 每 3 次生成 1 次 (第 3、6、9...次生成)
        - little: 每 5 次生成 1 次 (第 5、10、15...次生成)
        """
        if not self.get_is_generate():
            return False

        config = self._get_config()
        frequency = config.get('generate_frequency', 'always')

        if frequency == 'always':
            return True

        counts = config.get('counts', 0)

        # 先递增计数器
        config['counts'] = counts + 1
        self._save_config()

        # 检查是否达到阈值
        if frequency == 'often' and config['counts'] >= 3:
            config['counts'] = 0
            self._save_config()
            return True
        elif frequency == 'little' and config['counts'] >= 5:
            config['counts'] = 0
            self._save_config()
            return True

        return False

    # ==================== 提示词管理 ====================

    def get_image_prompts(self):
        """获取自定义提示词"""
        config = self._get_config()
        prompts = {
            'positive': config.get('positive_prompt', ''),
            'negative': config.get('negative_prompt', ''),
            'other': config.get('other_prompt', '')
        }
        return prompts

    def set_image_prompt(self, prompt_type, value):
        """设置指定类型的提示词"""
        config = self._get_config()
        if prompt_type in ['positive_prompt', 'negative_prompt', 'other_prompt']:
            config[prompt_type] = value
            self._save_config()

    def get_positive_prompt(self):
        """获取正向提示词"""
        config = self._get_config()
        return config.get('positive_prompt', '')

    def get_negative_prompt(self):
        """获取负向提示词"""
        config = self._get_config()
        return config.get('negative_prompt', '')

    def get_other_prompt(self):
        """获取其他提示词"""
        config = self._get_config()
        return config.get('other_prompt', '')

    # ==================== 完整配置 ====================

    def get_generate_image_config(self):
        """获取完整的图片生成配置"""
        return self._get_config()


# 全局单例
generate_image_config = GenerateImageConfig()
