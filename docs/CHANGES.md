# HumanStudyBench - Major Update: Prompt Builder System

## 更新日期：2025-10-27

---

## 🎯 解决的核心问题

### ❌ 旧问题

**使用者不知道如何使用 benchmark**：

1. **Specification 不等于 Agent 输入**
   - `specification.json` 是给研究者看的技术文档
   - 使用者不知道如何转换成 LLM prompt
   - 缺少从 "实验设计" 到 "参与者体验" 的桥梁

2. **Instructions.txt 的用途不明确**
   - 应该直接给 LLM 吗？
   - 如何与 trial prompts 结合？
   - 与 system prompt 的关系？

3. **每个 study 需要手动编写 prompts**
   - 容易遗漏关键信息（社会情境、confederate 反应）
   - 不同使用者写出的 prompts 不一致
   - 影响可复现性

### ✅ 新解决方案

**Prompt Builder System**: 自动将 specification 转换为 LLM prompts

```
specification.json → [Prompt Builder] → System Prompt + Trial Prompts
        ↓                                         ↓
   (技术设计)                              (参与者体验)
```

---

## 📦 新增组件

### 1. Prompt Templates (每个 study)

**位置**: `data/studies/study_XXX/materials/prompts/`

#### a) `system_prompt_template.txt`
- **作用**: 定义 LLM agent 的身份（参与者角色）
- **内容**: 年龄、性格、实验情境、心理状态
- **示例**:
  ```
  You are participating in a psychology experiment...
  YOUR IDENTITY:
  - Age: {{age}} years old
  - Personality: {{personality_description}}
  
  You may feel social pressure when others disagree...
  ```

#### b) `trial_prompt_template.txt`
- **作用**: 呈现每个试验的刺激
- **内容**: 视觉刺激（ASCII art）、社会情境、confederate 反应
- **示例**:
  ```
  Trial {{trial_number}}:
  
  STANDARD LINE: {{standard_length}} inches
  COMPARISON LINES:
    Line A: {{comparison_lines.A}} inches
  
  {{#if confederate_responses}}
  Others responded: {{#each confederate_responses}}...{{/each}}
  {{/if}}
  ```

### 2. Prompt Builder Class

**文件**: `src/agents/prompt_builder.py`

**核心类**:
- `PromptBuilder`: 基类，处理模板填充
- `AschPromptBuilder`: Asch 实验专用（视觉线段、从众压力）
- `MilgramPromptBuilder`: Milgram 实验专用（电击、权威压力）

**核心方法**:
```python
builder.build_system_prompt(participant_profile)  # 生成身份定义
builder.build_trial_prompt(trial_data)            # 生成试验刺激
builder.get_instructions()                        # 获取实验说明
```

### 3. 示例和文档

**示例代码**: `examples/30_prompt_builder_demo.py`
- 完整的 Prompt Builder 使用演示
- Asch 和 Milgram 两个实验的对比
- 与 LLM API 的集成示例

**完整指南**: `docs/prompt_builder_guide.md`
- 详细的使用方法
- 模板语法说明
- 为新 study 创建 templates 的 step-by-step 指南
- 最佳实践和常见问题

---

## 🚀 使用方法

### 简化版（3 行代码）

```python
from src.agents.prompt_builder import get_prompt_builder

builder = get_prompt_builder("study_001")
system_prompt = builder.build_system_prompt({"age": 20, "gender": "male"})
trial_prompt = builder.build_trial_prompt({"trial_number": 1, ...})
```

### 完整版（与 LLM 集成）

```python
import openai
from src.agents.prompt_builder import get_prompt_builder

# 1. 创建 builder
builder = get_prompt_builder("study_001")

# 2. 定义参与者
profile = {
    "age": 19,
    "gender": "male",
    "personality_traits": {"conformity_tendency": 0.75}
}

# 3. 生成 prompts
system_prompt = builder.build_system_prompt(profile)
instructions = builder.get_instructions()
trial_prompt = builder.build_trial_prompt({
    "trial_number": 7,
    "standard_length": 10,
    "comparison_lines": {"A": 8, "B": 10, "C": 12},
    "confederate_responses": ["A", "A", "A", "A", "A", "A"]
})

# 4. 调用 LLM
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": instructions},
        {"role": "assistant", "content": "Yes, I understand."},
        {"role": "user", "content": trial_prompt}
    ]
)

answer = response.choices[0].message.content  # "A" 或 "B"
```

---

## 📁 文件结构变化

### 新增文件

```
data/studies/study_001/materials/prompts/
├── system_prompt_template.txt      # NEW: Asch 参与者身份模板
└── trial_prompt_template.txt       # NEW: Asch 试验刺激模板

data/studies/study_002/materials/prompts/
├── system_prompt_template.txt      # NEW: Milgram 参与者身份模板
└── trial_prompt_template.txt       # NEW: Milgram 试验刺激模板

src/agents/
└── prompt_builder.py               # NEW: Prompt 自动生成系统

examples/
└── 30_prompt_builder_demo.py       # NEW: 完整使用演示

docs/
├── prompt_builder_guide.md         # NEW: 完整使用指南
└── CHANGES.md                       # NEW: 本更新文档
```

### 更新文件

```
README.md                            # UPDATED: 添加 Prompt Builder 快速开始
docs/getting_started.md              # (建议更新)
```

---

## 🎓 模板语法

Prompt Builder 支持简化的模板语法：

### 1. 变量替换
```
{{variable}}              → 简单替换
{{object.property}}       → 嵌套属性
```

### 2. 条件块
```
{{#if variable}}
  显示内容
{{/if}}
```

### 3. 循环
```
{{#each array}}
  {{this}}      ← 当前元素
  {{@index}}    ← 索引（从 1 开始）
{{/each}}

{{#each dictionary}}
  {{@key}}: {{this}}
{{/each}}
```

---

## 🔧 向后兼容性

### ✅ 完全向后兼容

- ✅ 所有旧代码继续工作
- ✅ `LLMParticipantAgent` 未改变
- ✅ `ParticipantPool` 未改变
- ✅ `specification.json` 格式未改变
- ✅ 评分系统未改变

### ➕ 纯增量更新

Prompt Builder 是**新增功能**，不影响现有工作流：

```python
# 旧方法（仍然工作）
agent = LLMParticipantAgent(profile)
response = agent.complete_trial(trial_data)

# 新方法（更清晰，推荐）
builder = get_prompt_builder("study_001")
system_prompt = builder.build_system_prompt(profile)
trial_prompt = builder.build_trial_prompt(trial_data)
```

---

## 💡 为新 Study 添加 Templates

### Step-by-Step

1. **创建目录**:
   ```bash
   mkdir -p data/studies/study_XXX/materials/prompts
   ```

2. **创建 system_prompt_template.txt**:
   - 定义参与者身份
   - 描述实验情境
   - 强调 "You are NOT an AI"
   - 说明心理状态和压力

3. **创建 trial_prompt_template.txt**:
   - 呈现刺激（用 ASCII art 或文字）
   - 包含社会情境（如果有）
   - 清晰提问
   - 说明 response 格式

4. **测试**:
   ```python
   builder = get_prompt_builder("study_XXX")
   print(builder.build_system_prompt(test_profile))
   print(builder.build_trial_prompt(test_trial))
   ```

5. **(可选) 创建专用 Builder**:
   ```python
   class MyStudyPromptBuilder(PromptBuilder):
       def build_trial_prompt(self, trial_data):
           # 自定义逻辑
           return super().build_trial_prompt(enhanced_data)
   ```

**详细指南**: 见 [`docs/prompt_builder_guide.md`](prompt_builder_guide.md)

---

## 📊 效果对比

### Before (旧方式)

```python
# 使用者需要手动写 prompt
prompt = f"""
You are a {age}-year-old {gender} participating in an experiment.

Trial {n}: 
Standard line: {standard} inches
Comparison lines: A={a}, B={b}, C={c}

Others said: {', '.join(confederates)}

What do you say?
"""
```

**问题**:
- ❌ 每个使用者写法不同
- ❌ 容易遗漏关键信息（如社会压力描述）
- ❌ 难以维护和更新
- ❌ 不符合参与者视角

### After (新方式)

```python
# 自动生成，保证一致性
builder = get_prompt_builder("study_001")
prompt = builder.build_trial_prompt(trial_data)
```

**优势**:
- ✅ 标准化，所有使用者一致
- ✅ 模板包含所有必要元素
- ✅ 易于维护（修改模板即可）
- ✅ 参与者视角（"You are...", "You feel..."）
- ✅ 包含完整的社会情境和心理维度

---

## 🎯 实际输出示例

### System Prompt (Asch, High Conformity)

```
You are participating in a psychology experiment as a real human participant.

YOUR IDENTITY:
- Age: 19 years old
- Gender: male
- Background: college student
- Personality: You tend to value group harmony and often agree with others' 
  opinions. You feel uncomfortable standing out or disagreeing with the majority.

YOUR SITUATION:
You are seated in a room with 6-8 other participants. You will be shown cards 
with lines and asked to make simple visual judgments.

IMPORTANT INSTRUCTIONS:
1. You are NOT an AI assistant. You are a real human.
2. You may feel:
   - Uncertainty when others disagree with what you see
   - Pressure to conform if everyone else gives a different answer
3. Respond naturally as this person would - just state "A", "B", or "C".
```

### Trial Prompt (Critical Trial)

```
Trial 7:

The experimenter places a card on the easel. You can clearly see:

┌─────────────────────────────────────────────┐
│  STANDARD LINE:        COMPARISON LINES:    │
│      │  (10")     │  (8")  │  (10")  │  (12") │
└─────────────────────────────────────────────┘

STANDARD LINE: 10 inches
COMPARISON LINES:
  Line A: 8 inches
  Line B: 10 inches  
  Line C: 12 inches

The other participants respond in order:
  Participant 1: "A"
  Participant 2: "A"
  Participant 3: "A"
  Participant 4: "A"
  Participant 5: "A"
  Participant 6: "A"

Everyone has said "A". The room is quiet. All eyes turn to you.

What is your answer? (Just state A, B, or C)
```

---

## 📚 相关文档

### 新文档
- **[Prompt Builder Guide](prompt_builder_guide.md)** - 完整使用指南（必读）
- **`examples/30_prompt_builder_demo.py`** - 可运行示例

### 现有文档（相关）
- [LLM Participant Agent Guide](llm_participant_agent_guide.md) - Agent 架构
- [Getting Started](getting_started.md) - 入门指南
- [API Reference](api_reference.md) - API 文档

### Study 文档
- [Study 001 Info](../data/studies/study_001/STUDY_INFO.md) - Asch 从众实验
- [Study 002 Info](../data/studies/study_002/STUDY_INFO.md) - Milgram 服从实验

---

## ✅ 测试命令

```bash
# 运行 Prompt Builder 演示
python examples/30_prompt_builder_demo.py

# 快速测试（验证环境）
python scripts/quick_test.py

# 验证 study 结构（包括 prompts）
python scripts/validate_study.py study_001
python scripts/validate_study.py study_002
```

---

## 🤝 贡献指南

### 为新 Study 创建 Templates

1. Fork 本 repo
2. 创建 `data/studies/study_XXX/materials/prompts/` 目录
3. 按照 `docs/prompt_builder_guide.md` 创建模板
4. 测试 prompts 的质量
5. 提交 Pull Request

### 改进现有 Templates

1. 编辑 `system_prompt_template.txt` 或 `trial_prompt_template.txt`
2. 测试改动对 LLM 输出的影响
3. 确保与文献描述一致
4. 提交 PR 并说明改进原因

---

## 📞 联系方式

如有问题或建议，请：
- 提交 GitHub Issue
- 阅读 `docs/prompt_builder_guide.md` 获取详细帮助
- 查看 `examples/30_prompt_builder_demo.py` 获取示例

---

## 📈 下一步计划

### 短期 (已完成)
- ✅ Prompt Builder 基础框架
- ✅ Asch 和 Milgram 模板
- ✅ 完整文档和示例

### 中期 (计划中)
- [ ] 更多 study 的 templates
- [ ] 多语言模板支持
- [ ] 可视化 prompt 编辑器
- [ ] 自动 prompt 优化工具

### 长期 (研究方向)
- [ ] 从文献自动生成 templates
- [ ] LLM-based prompt 质量评估
- [ ] 跨 study 的 prompt 一致性分析

---

## 🎉 总结

**Prompt Builder 系统解决了 HumanStudyBench 最大的可用性问题：如何将技术 specification 转换为 LLM 能理解的参与者体验。**

通过标准化的模板和自动化的转换，使用者现在可以：
- ✅ 快速上手（3 行代码）
- ✅ 保证 prompts 质量和一致性
- ✅ 专注于研究问题，而非 prompt engineering
- ✅ 轻松添加新的 studies

**立即开始**: `python examples/30_prompt_builder_demo.py` 🚀
