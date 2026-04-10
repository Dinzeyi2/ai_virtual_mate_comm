"""
虚拟世界时间管理器

核心功能:
- 管理 virtual_time 字段 (时间、天数、比例)
- 时间段查询 (早上/中午/下午/晚上)
- 时间推进 (支持跨天检测)
- 配置文件持久化
"""

import json
import os


class VirtualTimeManager:
    """虚拟世界时间管理器 (单例模式)"""

    def __init__(self):
        self.state_path = os.path.join(os.path.dirname(__file__), '..', 'state.json')
        # 加载配置
        self.load()

    def get_ratio(self) -> float:
        """获取时间流速比例

        Returns:
            ratio = 虚拟秒/现实秒 = 86400 / (virtual_day_time * 60)
            例：virtual_day_time=15 → ratio = 86400 / 900 = 96
        """
        return 86400 / (self.virtual_day_time * 60)

    def get_time_str(self) -> str:
        """获取虚拟时间字符串 (HH:MM:SS)"""
        return self.virtual_world_time

    def get_time_minutes(self) -> str:
        """获取虚拟时间字符串 (HH:MM)"""
        parts = self.virtual_world_time.split(':')
        return f"{parts[0]}:{parts[1]}"

    def get_time_seconds(self) -> int:
        """获取虚拟时间秒数 (0-86399)"""
        parts = self.virtual_world_time.split(':')
        return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])

    def get_day(self) -> int:
        """获取虚拟世界天数"""
        return self.virtual_day

    def get_period(self) -> str:
        """根据当前虚拟时间返回时间段

        Returns:
            "早上" (6-11 点) | "中午" (12-15 点) | "下午" (16-19 点) | "晚上" (20-5 点)
        """
        hour = int(self.virtual_world_time.split(':')[0])

        # 晚上跨天处理 (20-23 点 和 0-5 点)
        if hour >= 20 or hour < 6:
            return "晚上"
        elif 6 <= hour <= 11:
            return "早上"
        elif 12 <= hour <= 15:
            return "中午"
        elif 16 <= hour <= 19:
            return "下午"


    def advance_seconds(self, elapsed_seconds: float):
        """根据现实流逝的秒数更新虚拟世界时间

        Args:
            elapsed_seconds: 现实世界流逝的秒数
        """
        ratio = self.get_ratio()
        virtual_elapsed = elapsed_seconds * ratio

        # 当前虚拟时间秒数
        current_seconds = self.get_time_seconds()
        new_seconds = current_seconds + virtual_elapsed

        # 处理跨天
        if new_seconds >= 86400:
            days_passed = int(new_seconds // 86400)
            self.virtual_day += days_passed
            new_seconds = new_seconds % 86400
            self.on_day_change()

        # 更新虚拟时间
        hours = int(new_seconds // 3600)
        minutes = int((new_seconds % 3600) // 60)
        seconds = int(new_seconds % 60)
        self.virtual_world_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"

        self.save()

    def on_day_change(self):
        """跨天通知回调

        子类可重写此方法实现跨天通知逻辑
        """
        pass

    def save(self):
        """保存状态到配置文件"""
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}

        data['virtual_time'] = {
            'virtual_day_time': self.virtual_day_time,
            'virtual_world_time': self.virtual_world_time,
            'virtual_day': self.virtual_day,
            'update_interval': self.update_interval
        }

        with open(self.state_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self):
        """从配置文件加载状态"""
        if not os.path.exists(self.state_path):
            self.save()
            return

        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            vt = data.get('virtual_time', {})
            self.virtual_day_time = vt.get('virtual_day_time', 15)
            self.virtual_world_time = vt.get('virtual_world_time', '06:00:00')
            self.virtual_day = vt.get('virtual_day', 0)
            self.update_interval = vt.get('update_interval', 1)

        except Exception as e:
            print(f"虚拟时间配置加载失败：{e}")



