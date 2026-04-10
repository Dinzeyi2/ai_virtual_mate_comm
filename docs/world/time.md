# 虚拟世界时间配置说明

## 文件位置

`partner/world/state.json`

## 配置结构

```json
{
  "virtual_time": {
    "virtual_day_time": 15,
    "virtual_world_time": "06:00:00",
    "virtual_day": 0,
    "update_interval": 1
  }
}
```

## 字段说明

### virtual_day_time

- **类型**: 整数
- **默认值**: `15`
- **含义**: 虚拟世界 1 天相当于现实世界的分钟数
- **说明**: 
  - 值越小，虚拟时间流速越快
  - 15 表示虚拟 1 天 = 现实 15 分钟
  - 30 表示虚拟 1 天 = 现实 30 分钟

### virtual_world_time

- **类型**: 字符串
- **格式**: `"HH:MM:SS"`
- **默认值**: `"06:00:00"`
- **含义**: 当前虚拟世界的时间
- **范围**: `00:00:00` 到 `23:59:59`
- **说明**: 
  - 精确到秒
  - 24 小时制
  - 到达 `23:59:59` 后下一秒归零为 `00:00:00` 并触发跨天

### virtual_day

- **类型**: 整数
- **默认值**: `0`
- **含义**: 虚拟世界从开始到现在的天数
- **说明**: 
  - 从 0 开始计数
  - 每当地图时间从 `23:59:59` 进入 `00:00:00` 时 +1

### update_interval

- **类型**: 整数
- **默认值**: `1`
- **含义**: 后台计时器更新虚拟时间的频率 (秒)
- **说明**: 
  - 值越小更新越频繁，时间流逝更平滑
  - 值越大资源消耗越少
  - 推荐保持 1 秒

## 时间比例计算

虚拟时间流速比例 (ratio) 由以下公式计算:

```
ratio = 86400 / (virtual_day_time × 60)
```

- `86400` = 虚拟世界 1 天的秒数
- `virtual_day_time × 60` = 现实世界对应分钟换算成秒

**示例**:
- `virtual_day_time = 15` → `ratio = 86400 / 900 = 96`
- `virtual_day_time = 30` → `ratio = 86400 / 1800 = 48`
- `virtual_day_time = 60` → `ratio = 86400 / 3600 = 24`

ratio 的含义：现实每过 1 秒，虚拟世界过 `ratio` 秒

## 时间段划分

虚拟世界时间被划分为 4 个时间段:

| 时间段 | 时间范围 | 说明 |
|--------|----------|------|
| 早上 | 06:00 - 11:59 | 早晨到上午 |
| 中午 | 12:00 - 15:59 | 正午到下午早段 |
| 下午 | 16:00 - 19:59 | 下午到晚饭后 |
| 晚上 | 20:00 - 05:59 | 晚上到次日凌晨 (跨天) |

**注意**: 晚上时间段跨越两天 (20-23 点 和 0-5 点)

## 实现逻辑

### 时间更新流程

1. 后台计时器每秒唤醒
2. 读取 `update_interval` 和 `virtual_day_time`
3. 计算虚拟流逝秒数 = `update_interval × ratio`
4. 调用 `advance_seconds()` 更新虚拟时间
5. 检测是否跨天 (秒数 ≥ 86400)
6. 跨天则天数 +1，时间归零
7. 保存配置到文件

### 跨天检测

```
新秒数 = 当前秒数 + 虚拟流逝秒数

如果 新秒数 >= 86400:
    天数 += 新秒数 // 86400
    新秒数 = 新秒数 % 86400
    调用 on_day_change() 通知
```

### 时间段判断逻辑

```python
hour = 虚拟时间的小时数

if hour >= 20 or hour < 6:
    return "晚上"
elif 6 <= hour <= 11:
    return "早上"
elif 12 <= hour <= 15:
    return "中午"
elif 16 <= hour <= 19:
    return "下午"
```

## API 使用

### 获取当前时间段

```python
from partner.world.time.manager import virtual_time_manager

period = virtual_time_manager.get_period()  # "早上" | "中午" | "下午" | "晚上"
```

### 获取虚拟时间

```python
# 精确到秒
time_str = virtual_time_manager.get_time_str()  # "14:30:45"

# 精确到分钟
time_min = virtual_time_manager.get_time_minutes()  # "14:30"

# 秒数形式
time_sec = virtual_time_manager.get_time_seconds()  # 52245
```

### 获取天数

```python
day = virtual_time_manager.get_day()  # 0, 1, 2, ...
```

### 手动推进时间

```python
# 推进 60 秒现实时间
virtual_time_manager.advance_seconds(60)
```

### 跨天通知

重写 `on_day_change()` 方法:

```python
def on_day_change(self):
    # 自定义跨天处理逻辑
    print(f"虚拟世界进入第 {self.virtual_day} 天")
```
