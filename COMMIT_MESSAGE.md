refactor(partner): 重构伴侣模式架构,提升代码质量和模块化程度

本提交针对伴侣模式代码进行了全面重构,解决了代码审查中发现的多个架构问题,
涉及 SoC(关注点分离)、DRY(不要重复自己)、KISS(保持简单)、OCP(开闭原则)
等设计原则的改进。

一、新增 partner/companion.py — 对话桥接模块 (SoC, SRP)

- 从 llm.py 中抽离伴侣模式特有的对话逻辑 (原 ~80 行嵌套代码)
- 新增 build_companion_prompt() — 构建伴侣模式专属系统提示词
- 新增 update_companion_state() — 解析 LLM JSON 响应并更新角色状态
- 新增 companion_chat() — 完整对话入口,失败时回退到原始文本
- llm.py 中伴侣模式调用从 80+ 行缩减为 3 行:
    return companion_chat(msg, openai_history, client, custom_model,
                          partner_config, think_filter_switch, prompt)
- 避免在 companion.py 中直接 import llm 导致循环依赖, 将 base_prompt
  作为参数传入

二、重构 partner/characterStatus.py — 消除重复写文件逻辑 (DRY, KISS)

- 新增 _save() 内部方法, 统一将所有状态一次性写入 config.json
- set_current_location() / set_current_time_period() / set_current_action()
  / set_is_user_nearby() / set_choice_next_action() / put_agreed_event()
  / take_agreed_event() 等 7 个 setter 从各自包含 ~10 行重复写文件代码
  简化为 1 行 _save() 调用
- set_current_location() / set_current_action() 中 if/else 各写一次
  文件的冗余分支消除, 统一为: 先判断是否需添加到 options 列表, 再更新
  属性, 最后调 _save() 一次写入
- get_agreed_events() 改为返回 .copy() 副本, 防止外部模块直接修改
  内部列表 (接口隔离原则 ISP)
- 统一异常消息为 "伴侣配置文件同步错误" (原错误消息写 "导入错误")
- 代码净减少约 30 行

三、重构 partner/actions.py — 提取模板 + 装饰器注册 (DRY, OCP)

- 新增 _run_action(msg, notice_text, stream_prefix) 统一行为执行模板
  (stop_tts → chat_llm → notice → stream_insert → get_tts_play → return)
- 6 个 action 函数从各自 ~15 行含完整 try/except 的流程简化为
  ~3 行 _run_action() 调用
- 新增 @register_action(name) 装饰器实现行为自动注册
- registered_actions 由装饰器自动填充, 替代原 actionScheduler.py
  中的手动注册表
- action_talk_with_other(name) 参数改为 name=None 可选, 避免
  调度器随机选到时因缺参数报错
- 异常处理由模板函数统一负责, notice 消息更准确 (原 action_default
  的错误消息错误地复制了 "与环境互动出错")
- 代码净减少约 20 行

四、适配 partner/actionScheduler.py — 适配新的注册方式

- registered_actions 改为从 partner.actions 导入 (由装饰器自动填充)
- 替代原硬编码手动注册的行为字典
- 重置计数逻辑优化为 for key in action_counts 循环, 替代逐键赋值
- 添加注释说明计数仅针对需要防沉迷判断的行为

五、影响范围

- 无功能变更, 仅重构代码组织结构
- 对外接口 (llm.py 的 chat_llm、ase.py 的 run_ase_rp、
  actionScheduler 的 run_action) 保持不变
- 行为执行效果、调度策略、状态持久化逻辑均保持原有行为
