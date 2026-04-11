# 角色卡片配置系统文档

## 一、功能概述

角色卡片配置系统用于管理虚拟伴侣的角色人设卡片（Character Card）。通过配置化的方式，可以灵活地启用/禁用角色、管理角色的卡片文件（如角色设定、技能档案等），并提供统一的读取接口供 LLM 使用。

角色卡片是塑造虚拟伴侣人格、行为模式、语言风格的核心数据，通常包含：
- 角色身份背景
- 性格特征和思维模式
- 语言表达习惯
- 行为决策逻辑
- 对话模板示例

---

## 二、文件结构

```
ai_virtual_mate_comm/
├── partner/
│   ├── characterCard/
│   │   ├── manager.py                    # 角色卡片配置管理类
│   │   ├── __init__.py                   # 模块导出
│   │   │
│   │   └── 甘雨/                          # 角色卡片目录（角色名命名）
│   │       ├── ganyu-research.md         # 角色思维框架文档
│   │       └── SKILL.md                  # 角色资料档案
│   │
│   └── config.json                       # 伴侣配置文件 (character_card 位于根级别)
│
└── docs/
    └── characterCard/
        └── character_card.md             # 本文档
```

---

## 三、配置管理

### 3.1 配置文件位置

角色卡片配置存储在 `partner/config.json` 的**根级别** `character_card` 对象中。

### 3.2 配置结构

```json
{
    "response_rule": "...",
    "response_rule_schema": { ... },
    "response_rule_object": { ... },
    "character_card": {
        "base_url": "partner/characterCard",
        "甘雨": {
            "enabled": true,
            "files": ["ganyu-research.md", "SKILL.md"]
        }
    },
    "last_status": { ... }
}
```

### 3.3 配置字段说明

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| **base_url** | string | `"partner/characterCard"` | 角色卡片目录的相对路径（固定字段） |
| **{角色名}** | object | - | 角色配置对象，键名为角色名称（如 `甘雨`、`刻晴`） |
| **{角色名}.enabled** | bool | `false` | 是否启用该角色，`true` 为启用 |
| **{角色名}.files** | list | `[]` | 角色卡片文件列表，存储 `.md` 文件名 |

### 3.4 角色目录命名规范

| 层级 | 命名规则 | 示例 |
|------|----------|------|
| 角色目录 | 使用角色中文名 | `partner/characterCard/甘雨/` |
| 卡片文件 | 小写字母 + 连字符 | `ganyu-research.md`、`skill.md` |

---

## 四、核心 API

### 4.1 CharacterCardManager 类 - 角色卡片配置管理

**文件位置**: `partner/characterCard/manager.py`

**实例化**:

```python
from partner.characterCard.manager import character_card_manager

# 使用全局单例（推荐）
manager = character_card_manager

# 或创建新实例
from partner.characterCard.manager import CharacterCardManager
manager = CharacterCardManager()
```

---

#### 4.1.1 基础路径获取

```python
# 获取角色卡片目录基础路径
base_url = manager.get_base_url()  # "partner/characterCard"
```

---

#### 4.1.2 角色启用状态管理

```python
# 获取所有启用的角色列表
enabled = manager.get_enabled_characters()  # ["甘雨", "刻晴"]

# 检查指定角色是否启用
is_enabled = manager.is_enabled("甘雨")  # True | False

# 设置角色启用状态
manager.set_enabled("甘雨", True)   # 启用
manager.set_enabled("甘雨", False)  # 禁用
```

---

#### 4.1.3 角色文件列表管理

```python
# 获取角色的卡片文件列表
files = manager.get_character_files("甘雨")
# 返回：["ganyu-research.md", "SKILL.md"]

# 设置角色的卡片文件列表
manager.set_character_files("甘雨", ["ganyu-research.md", "SKILL.md"])

# 添加单个文件到角色
manager.add_character_file("甘雨", "voice_pattern.md")
```

---

#### 4.1.4 文件路径解析

```python
# 获取角色卡片的完整文件路径
path = manager.get_file_path("甘雨", "ganyu-research.md")
# 返回：e:\AIBOT\dev\ai_virtual_mate_comm\partner\characterCard\甘雨\ganyu-research.md
```

---

#### 4.1.5 读取卡片内容

```python
# 读取单个卡片文件内容
content = manager.read_card_content("甘雨", "ganyu-research.md")
# 返回：文件完整内容（字符串）

# 读取角色所有卡片文件内容
cards = manager.read_all_cards("甘雨")
# 返回：{"ganyu-research.md": "内容...", "SKILL.md": "内容..."}
# 某个文件读取失败时，对应值为 None
```

---

#### 4.1.6 添加新角色

```python
# 添加新角色配置
manager.add_character("刻晴", enabled=True, files=["keqing-research.md"])
```

---

#### 4.1.7 获取完整配置

```python
# 获取完整的 character_card 配置
config = manager.get_character_card_config()
# 返回：{"base_url": "...", "甘雨": {...}, ...}
```

---

## 五、使用示例

### 5.1 检查角色是否启用并读取卡片

```python
from partner.characterCard.manager import character_card_manager

if character_card_manager.is_enabled("甘雨"):
    # 读取所有卡片内容
    cards = character_card_manager.read_all_cards("甘雨")
    
    # 合并所有卡片内容作为 LLM 的系统提示词
    system_prompt = "\n\n".join(cards.values())
    print(system_prompt)
else:
    print("甘雨角色未启用")
```

### 5.2 动态启用角色

```python
from partner.characterCard.manager import character_card_manager

# 启用甘雨角色
character_card_manager.set_enabled("甘雨", True)

# 验证启用状态
print(f"甘雨已启用：{character_card_manager.is_enabled('甘雨')}")
```

### 5.3 添加新角色

```python
from partner.characterCard.manager import character_card_manager

# 添加新角色"刻晴"
character_card_manager.add_character(
    character_name="刻晴",
    enabled=True,
    files=["keqing-research.md", "keqing-skill.md"]
)

# 添加额外文件
character_card_manager.add_character_file("刻晴", "voice_samples.md")
```

### 5.4 完整对话集成示例

```python
from partner.characterCard.manager import character_card_manager

def build_system_prompt(character_name):
    """为指定角色构建系统提示词"""
    
    if not character_card_manager.is_enabled(character_name):
        raise ValueError(f"角色 {character_name} 未启用")
    
    # 读取所有卡片
    cards = character_card_manager.read_all_cards(character_name)
    
    # 过滤掉读取失败的卡片
    valid_cards = {k: v for k, v in cards.items() if v is not None}
    
    if not valid_cards:
        raise ValueError(f"角色 {character_name} 没有可用的卡片文件")
    
    # 构建系统提示词
    sections = []
    for filename, content in valid_cards.items():
        sections.append(f"## {filename}\n\n{content}")
    
    return "\n\n---\n\n".join(sections)


# 使用示例
system_prompt = build_system_prompt("甘雨")
print(system_prompt)  # 传递给 LLM 作为系统提示词
```

---

## 六、工作流程

### 6.1 角色卡片加载流程

```
LLM 对话初始化
    │
    ▼
检测伴侣模式配置
    │
    ▼
character_card_manager.is_enabled(character_name)
    │
    ├─ False → 使用默认提示词，不加载角色卡片
    │
    └─ True → character_card_manager.read_all_cards(character_name)
                │
                ▼
            遍历 files 列表读取每个.md 文件
                │
                ├─ 读取成功 → 内容存入字典
                │
                └─ 读取失败 → 对应值为 None
                │
                ▼
            合并所有卡片内容
                │
                ▼
            构建系统提示词
                │
                ▼
            传递给 LLM
```

### 6.2 companion.py 中的集成点

在伴侣对话初始化时加载角色卡片：

```python
from partner.characterCard.manager import character_card_manager

def init_companion_chat(character_name):
    """初始化伴侣对话"""
    
    # 检查角色是否启用
    if not character_card_manager.is_enabled(character_name):
        print(f"[companion] 角色 {character_name} 未启用")
        return
    
    # 读取角色卡片
    cards = character_card_manager.read_all_cards(character_name)
    
    # 构建系统提示词
    system_prompt = build_system_prompt_from_cards(cards)
    
    # 传递给 LLM
    llm.set_system_prompt(system_prompt)
```

---

## 七、技术细节

### 7.1 配置持久化

`CharacterCardManager` 类负责读取和写入 `partner/config.json`:

```python
# 内部实现
def _load_config(self):
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        self._config = json.load(f)

def _save_config(self):
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(self._config, f, ensure_ascii=False, indent=4)
```

每次调用 `set_*` 或 `add_*` 方法时会自动保存配置到文件。

### 7.2 路径解析逻辑

```python
def get_file_path(self, character_name, filename):
    # CONFIG_PATH 指向 partner/config.json
    partner_dir = os.path.dirname(os.path.normpath(CONFIG_PATH))
    # characterCard 目录在 partner/ 下
    character_dir = os.path.join(partner_dir, 'characterCard', character_name)
    return os.path.normpath(os.path.join(character_dir, filename))
```

### 7.3 错误处理

```python
def read_card_content(self, character_name, filename):
    file_path = self.get_file_path(character_name, filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"读取角色卡片文件失败 [{file_path}]: {e}")
```

---

## 八、调试与日志

### 8.1 配置验证

```python
from partner.characterCard.manager import character_card_manager
import json

# 检查配置是否正确加载
print("当前配置:", character_card_manager.get_character_card_config())

# 或直接读取配置文件
with open('partner/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
    print(json.dumps(config['character_card'], indent=2, ensure_ascii=False))
```

### 8.2 文件存在性检查

```python
import os
from partner.characterCard.manager import character_card_manager

# 检查角色目录是否存在
char_name = "甘雨"
char_dir = character_card_manager.get_file_path(char_name, "")[:-1]  # 去掉文件名
print(f"{char_name} 目录：{char_dir}")
print(f"目录存在：{os.path.exists(char_dir)}")

# 检查卡片文件是否存在
for filename in character_card_manager.get_character_files(char_name):
    path = character_card_manager.get_file_path(char_name, filename)
    print(f"  {filename}: {os.path.exists(path)}")
```

---

## 九、最佳实践

### 9.1 角色卡片文件组织

| 文件类型 | 推荐命名 | 内容说明 |
|----------|----------|----------|
| 思维框架 | `{角色名}-research.md` | 身份卡、核心心智模型、决策启发式 |
| 资料档案 | `SKILL.md` | 说话风格、肢体语言、对话模板 |
| 语音模式 | `voice_pattern.md` | 口癖、语气词、常用表达 |
| 人际关系 | `relationships.md` | 与其他角色的关系网 |

### 9.2 卡片内容建议

**思维框架文档结构**:

```markdown
# {角色名}思维框架

## 身份卡
- 姓名、年龄、职业
- 核心身份认同

## 核心心智模型
- 价值观和信念
- 决策优先级

## 决策启发式
- 典型情境下的反应模式

## 表达 DNA
- 语言风格特征
- 肢体语言习惯
```

**资料档案结构**:

```markdown
# {角色名}资料档案

## 说话风格
- 常用词汇
- 句式特点

## 肢体语言
- 标志性动作
- 表情习惯

## 对话模板
- 开场白示例
- 回应模式

## 性格分析
- MBTI 类型
- 九型人格
```

### 9.3 性能优化

1. **避免频繁读取文件**: 在对话初始化时一次性读取所有卡片，后续复用
2. **合理组织卡片内容**: 将常用内容放在单独文件，减少不必要的解析
3. **使用 UTF-8 编码**: 确保所有.md 文件使用 UTF-8 编码，避免中文乱码

---

## 十、故障排除

### 10.1 角色未启用

```python
# 检查启用状态
print(character_card_manager.is_enabled("甘雨"))  # 应为 True

# 启用角色
character_card_manager.set_enabled("甘雨", True)
```

### 10.2 卡片文件读取失败

```python
import os
from partner.characterCard.manager import character_card_manager

# 检查文件路径
path = character_card_manager.get_file_path("甘雨", "ganyu-research.md")
print(f"预期路径：{path}")
print(f"文件存在：{os.path.exists(path)}")

# 检查目录内容
char_dir = os.path.dirname(path)
print(f"目录内容：{os.listdir(char_dir)}")
```

### 10.3 配置不生效

```python
# 重新加载配置
character_card_manager._load_config()

# 验证配置内容
config = character_card_manager.get_character_card_config()
print(json.dumps(config, indent=2, ensure_ascii=False))
```

---

## 十一、相关文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| 配置管理类 | `partner/characterCard/manager.py` | CharacterCardManager 类，配置读写 |
| 配置文件 | `partner/config.json` | character_card 配置存储（根级别） |
| 角色卡片目录 | `partner/characterCard/{角色名}/` | 角色卡片文件存储位置 |

---

## 十二、扩展示例

### 12.1 批量启用所有角色

```python
from partner.characterCard.manager import character_card_manager
import os

# 获取 characterCard 目录下所有子目录（即所有角色）
char_dir = character_card_manager.get_base_url()
for item in os.listdir(char_dir):
    item_path = os.path.join(char_dir, item)
    if os.path.isdir(item_path) and not item.startswith('__'):
        # 为每个角色添加配置（如果不存在）
        character_card_manager.add_character(item, enabled=True)
        print(f"已启用角色：{item}")
```

### 12.2 导出角色配置备份

```python
from partner.characterCard.manager import character_card_manager
import json

# 导出当前配置
config = character_card_manager.get_character_card_config()

# 保存到备份文件
with open('character_card_backup.json', 'w', encoding='utf-8') as f:
    json.dump(config, f, ensure_ascii=False, indent=4)

print("角色卡片配置已备份到 character_card_backup.json")
```

### 12.3 从备份恢复配置

```python
from partner.characterCard.manager import character_card_manager
import json

# 从备份文件恢复
with open('character_card_backup.json', 'r', encoding='utf-8') as f:
    backup_config = json.load(f)

# 遍历备份配置，恢复每个角色
for char_name, char_config in backup_config.items():
    if char_name == 'base_url':
        continue
    if isinstance(char_config, dict):
        character_card_manager.set_enabled(char_name, char_config.get('enabled', False))
        character_card_manager.set_character_files(char_name, char_config.get('files', []))

print("角色卡片配置已恢复")
```
