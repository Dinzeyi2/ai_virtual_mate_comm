"""
虚拟世界后台计时器

功能:
- 导入时自动启动后台线程
- 每隔 update_interval 秒更新虚拟时间
- 使用 daemon 线程，主程序退出时自动停止
"""

import time
import threading
from sys_init import virtual_time_manager


def _timer_loop():
    """后台计时循环"""
    while True:
        interval = virtual_time_manager.update_interval
        ratio = virtual_time_manager.get_ratio()



        # 更新虚拟时间
        print('更新虚拟世界时间')
        virtual_time_manager.advance_seconds(interval)

        # 等待下一个更新周期
        time.sleep(interval)


# 创建并启动后台线程
_timer_thread = threading.Thread(target=_timer_loop, daemon=True)
_timer_thread.start()
