# 伴侣模式文生图功能文档

## 一、功能概述

伴侣模式文生图功能允许 LLM 在对话过程中根据对话内容自动生成图像，并将生成的图片插入到聊天框中。该功能通过配置化的方式控制图片生成的开关、频率和提示词，实现灵活的图像生成管理。

## 二、文件结构

```
ai_virtual_mate_comm/
├── partner/
│   ├── generateImage/
│   │   ├── generator.py              # 文生图生成器核心逻辑
│   │   ├── __init__.py               # 模块导出
│   │   └── output/                   # 生成的图片保存目录
│   │
│   ├── characterStatus.py            # 角色状态管理 (含图片生成配置)
│   └── companion.py                  # 伴侣对话桥接模块
│
├── comfyuiAPI/
│   └── api.py                        # ComfyUI WebSocket API 封装
│
└── docs/
    └── generateImage/
        └── image_generation.md       # 本文档
```

---

## 三、配置管理

### 3.1 配置文件位置

图片生成配置存储在 `partner/config.json` 的 `last_status.generate_image` 对象中。

### 3.2 配置结构

```json
{
  "last_status": {
    "generate_image": {
      "positive_prompt": "",
      "negative_prompt": "",
      "other_prompt": "",
      "is_generate": false,
      "generate_frequency": "always",
      "generate_frequency_options": ["always", "often", "little"],
      "counts": 0
    }
  }
}
```

### 3.3 配置字段说明

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| **positive_prompt** | string | `""` | 正向自定义提示词，追加到 LLM 返回的 prompt 之后 |
| **negative_prompt** | string | `""` | 负向自定义提示词，自动添加 `NEGATIVE:` 前缀 |
| **other_prompt** | string | `""` | 其他自定义提示词，直接追加到末尾 |
| **is_generate** | bool | `false` | 图片生成总开关，`true` 为开启 |
| **generate_frequency** | string | `"always"` | 生成频率，可选值：`always`、`often`、`little` |
| **generate_frequency_options** | list | `["always", "often", "little"]` | 频率可选值列表 |
| **counts** | int | `0` | 内部计数器，用于频率控制 |

### 3.4 频率说明

| 频率值 | 含义 | 生成规则 |
|--------|------|----------|
| **always** | 每次生成 | 每次 LLM 返回 prompt 字段时都生成图片 |
| **often** | 较频繁 | 每 3 次对话生成 1 次（第 3、6、9...次） |
| **little** | 较少 | 每 5 次对话生成 1 次（第 5、10、15...次） |

**计数器逻辑**:
- 每次调用 `should_generate_image()` 时计数器 +1
- 达到阈值时生成图片并重置计数器为 0
- `always` 模式下计数器不工作

---

## 四、核心 API

### 4.1 characterStatus 类 - 图片生成配置管理

**文件位置**: `partner/characterStatus.py`

#### 4.1.1 获取/设置生成开关

```python
from partner.characterStatus import characterStatus

partner_config = characterStatus()

# 获取生成开关状态
is_enabled = partner_config.get_is_generate()  # True | False

# 设置生成开关
partner_config.set_is_generate(True)   # 开启
partner_config.set_is_generate(False)  # 关闭
```

#### 4.1.2 获取/设置生成频率

```python
# 获取当前频率
freq = partner_config.get_generate_frequency()  # "always" | "often" | "little"

# 设置生成频率
partner_config.set_generate_frequency('often')
```

#### 4.1.3 判断是否应该生成

```python
# 内部调用，根据频率和计数器判断
should_gen = partner_config.should_generate_image()  # True | False
```

**返回值说明**:
- `False`: 未开启生成 或 频率未到
- `True`: 应该生成图片（计数器达到阈值）

#### 4.1.4 获取/设置自定义提示词

```python
# 获取所有自定义提示词
prompts = partner_config.get_image_prompts()
# 返回: {'positive': '', 'negative': '', 'other': ''}

# 设置单个提示词
partner_config.set_image_prompt('positive_prompt', 'masterpiece, best quality')
partner_config.set_image_prompt('negative_prompt', 'low quality, bad anatomy')
partner_config.set_image_prompt('other_prompt', 'detailed skin texture')
```

#### 4.1.5 重置计数器

```python
partner_config.reset_generate_counts()  # 将 counts 重置为 0
```

---

### 4.2 generator.py - 文生图生成器

**文件位置**: `partner/generateImage/generator.py`

#### 4.2.1 build_image_prompt()

**职责**: 将 LLM 返回的 prompt 字典与自定义提示词组合成完整的提示词字符串

```python
def build_image_prompt(prompt_dict, partner_config=None):
    """
    Args:
        prompt_dict: LLM 返回的 prompt 字典，包含以下字段:
            - scene: 场景描述 (如 "liyue, harbor, terrace, night")
            - emotion: 情绪表情 (如 "blushing, shy, trembling")
            - focus: 核心焦点 (如 "face, flushed, eyes, watery")
            - lighting: 光线描述 (如 "soft moonlight, warm lantern glow")
            - camera: 镜头构图 (如 "close-up, face, slightly above")
        partner_config: characterStatus 实例，用于获取自定义提示词

    Returns:
        组合后的提示词字符串，用逗号分隔各部分
    """
```

**组合逻辑**:

```
最终提示词 = [scene] + [emotion] + [focus] + [lighting] + [camera]
           + [positive_prompt]
           + [NEGATIVE: negative_prompt]
           + [other_prompt]
```

**示例**:

```python
prompt_dict = {
    'scene': 'bedroom, evening, moonlight',
    'emotion': 'shy, blushing',
    'focus': 'face, eyes',
    'lighting': 'soft rim light',
    'camera': 'close-up'
}

# 不使用自定义提示词
result = build_image_prompt(prompt_dict)
# 输出: "bedroom, evening, moonlight, shy, blushing, face, eyes, soft rim light, close-up"

# 使用自定义提示词
partner_config.set_image_prompt('positive_prompt', 'masterpiece, best quality')
result = build_image_prompt(prompt_dict, partner_config)
# 输出: "bedroom, evening, moonlight, shy, blushing, face, eyes, soft rim light, close-up, masterpiece, best quality"
```

#### 4.2.2 generate_companion_image()

**职责**: 伴侣模式文生图主接口，调用 ComfyUI API 生成图像

```python
def generate_companion_image(prompt_dict, save_path=None, partner_config=None):
    """
    Args:
        prompt_dict: LLM 返回的 prompt 字典
        save_path: 图片保存路径（可选，默认为模块 output 目录）
        partner_config: characterStatus 实例，用于获取自定义提示词

    Returns:
        生成的图片本地路径 (str)，生成失败返回 None
    """
```

**调用示例**:

```python
from partner.generateImage.generator import generate_companion_image

prompt_dict = {
    'scene': 'liyue harbor at night',
    'emotion': 'calm, serene',
    'focus': 'moonlight, lanterns',
    'lighting': 'soft moonlight, warm glow',
    'camera': 'wide shot, cinematic'
}

image_path = generate_companion_image(prompt_dict, partner_config=partner_config)
print(f"图片已保存到：{image_path}")
```

---

## 五、工作流程

### 5.1 完整图片生成流程

```
用户输入消息
    │
    ▼
llm.py → 检测到伴侣模式
    │
    ▼
companion_chat() 调用 LLM
    │
    ▼
LLM 返回 JSON (包含 prompt 字段)
    │
    ▼
update_companion_state() 解析 JSON
    │
    ├─→ 更新角色状态
    ├─→ 更新约定事件
    └─→ 检测图片生成配置
            │
            ▼
        partner_config.get_is_generate()
            │
            ├─ False → 打印"图片生成未开启"，跳过
            │
            └─ True → partner_config.should_generate_image()
                        │
                        ├─ False → 打印"频率未到，跳过本次生成"
                        │
                        └─ True → generate_companion_image()
                                    │
                                    ▼
                                build_image_prompt() 组合提示词
                                    │
                                    ▼
                                comfyuiAPI.generate_image_with_websocket()
                                    │
                                    ▼
                                调用 ComfyUI WebSocket API
                                    │
                                    ▼
                                保存图片到 partner/generateImage/output/
                                    │
                                    ▼
                                返回图片路径
                                    │
                                    ▼
                                on_image_generated(image_path)
                                    │
                                    ▼
                                insert_image_to_chat() 插入聊天框
```

### 5.2 companion.py 中的触发逻辑

**文件位置**: `partner/companion.py` (第 165-180 行)

```python
# 处理文生图：检查 is_generate 配置
if 'prompt' in res and res['prompt'] and on_image_generated:
    from .generateImage import generate_companion_image

    def generate_image_async():
        try:
            prompt_dict = res['prompt']

            # 使用 partner_config 判断是否开启生成
            if partner_config.get_is_generate():
                # 进一步检查频率
                if partner_config.should_generate_image():
                    image_path = generate_companion_image(prompt_dict, partner_config=partner_config)
                    if image_path and on_image_generated:
                        on_image_generated(image_path)
                else:
                    print("[companion] 频率未到，跳过本次生成")
            else:
                print("[companion] 图片生成未开启")
        except Exception as e:
            print(f"[companion] 文生图异常：{e}")

    Thread(target=generate_image_async, daemon=True).start()
```

**关键点**:
1. 只有 LLM 返回 JSON 包含 `prompt` 字段时才触发
2. 异步执行，不阻塞对话流程
3. 双层检查：先检查开关，再检查频率

---

## 六、使用示例

### 6.1 开启图片生成

```python
from partner.characterStatus import characterStatus

partner_config = characterStatus()

# 开启图片生成
partner_config.set_is_generate(True)

# 设置频率为 always（每次都生成）
partner_config.set_generate_frequency('always')
```

### 6.2 配置自定义提示词

```python
# 设置通用高质量提示词
partner_config.set_image_prompt('positive_prompt', 'masterpiece, best quality, ultra detailed')

# 设置负面提示词
partner_config.set_image_prompt('negative_prompt', 'low quality, worst quality, bad anatomy, blurry')

# 添加额外的风格描述
partner_config.set_image_prompt('other_prompt', 'anime style, cel shading')
```

### 6.3 设置生成频率

```python
# 每 3 次对话生成 1 次（节省资源）
partner_config.set_generate_frequency('often')

# 每 5 次对话生成 1 次（最低频率）
partner_config.set_generate_frequency('little')
```

### 6.4 完整对话场景示例

```python
from partner.characterStatus import characterStatus

# 初始化
partner_config = characterStatus()

# 配置图片生成
partner_config.set_is_generate(True)
partner_config.set_generate_frequency('often')  # 每 3 次生成 1 次
partner_config.set_image_prompt('positive_prompt', 'masterpiece, best quality')

# 第 1 次对话 - 不会生成
# 用户："甘雨，我们去月海亭看星星吧"
# 系统：should_generate_image() → False, counts=1

# 第 2 次对话 - 不会生成
# 用户："你喜欢吃什么？"
# 系统：should_generate_image() → False, counts=2

# 第 3 次对话 - 会生成
# 用户："今晚的月色真美"
# 系统：should_generate_image() → True, counts 重置为 0
#      → 调用 generate_companion_image()
#      → 图片插入聊天框
```

---

## 七、技术细节

### 7.1 ComfyUI 集成

文生图功能通过 `comfyuiAPI/api.py` 与 ComfyUI 服务器通信：

```python
# comfyuiAPI/api.py
def generate_image_with_websocket(prompt_text, save_path="comfyuiAPI/output"):
    """
    使用 WebSocket 方式生成图像

    流程:
    1. 创建 WebSocket 连接到 ComfyUI 服务器
    2. 通过 HTTP POST 到 /prompt 端点提交任务
    3. 通过 WebSocket 监听执行进度
    4. 执行完成后通过 /api/history/{prompt_id} 获取图片信息
    5. 下载图片到本地
    """
```

### 7.2 异步执行

图片生成在独立线程中执行，避免阻塞主对话流程：

```python
Thread(target=generate_image_async, daemon=True).start()
```

**优点**:
- 不影响对话响应速度
- 用户可继续输入消息
- 生成完成后自动插入聊天框

### 7.3 错误处理

```python
try:
    image_path = generate_companion_image(prompt_dict, partner_config=partner_config)
    if image_path and on_image_generated:
        on_image_generated(image_path)
except Exception as e:
    print(f"[companion] 文生图异常：{e}")
```

**异常情况**:
- ComfyUI 服务器不可用
- 提示词为空
- 图片下载失败
- 网络超时

---

## 八、调试与日志

### 8.1 日志输出

```
[companion] 图片生成未开启          # is_generate = False
[companion] 频率未到，跳过本次生成    # 频率控制
[generateImage] 提示词为空，跳过生成  # prompt_dict 为空
[generateImage] 开始生成图像，提示词：...  # 开始生成
[generateImage] Prompt ID: ...       # ComfyUI 返回的 prompt_id
[generateImage] 图像生成成功：...     # 生成完成
[generateImage] 文生图异常：...       # 生成失败
```

### 8.2 配置验证

```python
# 检查配置是否正确加载
import json
with open('partner/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    print(json.dumps(config['last_status'].get('generate_image'), indent=2, ensure_ascii=False))
```

---

## 九、最佳实践

### 9.1 提示词优化建议

| 类型 | 推荐内容 |
|------|----------|
| **positive_prompt** | `masterpiece, best quality, ultra detailed, 8k` |
| **negative_prompt** | `low quality, worst quality, bad anatomy, blurry, watermark` |
| **other_prompt** | `anime style, cel shading, soft lighting` |

### 9.2 频率选择建议

| 场景 | 推荐频率 |
|------|----------|
| 测试/开发 | `always` (快速验证) |
| 日常使用 | `often` (平衡体验和资源) |
| 低配置环境 | `little` (节省资源) |

### 9.3 性能优化

1. **避免 always 长期使用**: 频繁生成会增加 ComfyUI 服务器负载
2. **合理设置 negative_prompt**: 可显著降低崩图率
3. **监控 counts 计数器**: 可通过 `get_generate_counts()` 查看当前计数

---

## 十、故障排除

### 10.1 图片不生成

**检查清单**:
1. `is_generate` 是否为 `True`
2. LLM 返回的 JSON 是否包含 `prompt` 字段
3. ComfyUI 服务器是否可访问
4. 查看日志是否有错误信息

### 10.2 生成频率不符合预期

```python
# 检查当前频率设置
print(partner_config.get_generate_frequency())  # 应为 "always", "often", 或 "little"

# 检查计数器
print(partner_config.get_generate_counts())  # 查看当前计数

# 手动重置计数器
partner_config.reset_generate_counts()
```

### 10.3 提示词不生效

确保 `partner_config` 参数正确传递给 `generate_companion_image()`:

```python
# 正确
image_path = generate_companion_image(prompt_dict, partner_config=partner_config)

# 错误 - partner_config 未传递，自定义提示词不会生效
image_path = generate_companion_image(prompt_dict)
```

---

## 十一、相关文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| 生成器核心 | `partner/generateImage/generator.py` | 提示词组合 + ComfyUI 调用 |
| 配置管理 | `partner/characterStatus.py` | generate_image 配置管理 |
| 对话桥接 | `partner/companion.py` | 图片生成触发逻辑 |
| ComfyUI API | `comfyuiAPI/api.py` | WebSocket 通信封装 |
| 配置文件 | `partner/config.json` | 配置存储 |
| 输出目录 | `partner/generateImage/output/` | 生成的图片保存位置 |
