# Prompt Builder Guide

## 问题：使用者不知道如何将 Specification 转换为 LLM 输入

### 旧的问题

❌ **使用者遇到的困难**：
1. 看到 `specification.json` 不知道如何转换成 LLM prompt
2. `instructions.txt` 应该如何使用？直接给 LLM？
3. 每个 study 的刺激呈现方式不同，需要手动编写 prompt
4. 容易遗漏关键信息（社会情境、confederate 反应等）
5. 不同使用者写出的 prompt 不一致，影响可复现性

❌ **具体例子**：

```python
# 使用者看到 specification.json 里的:
{
    "trial": {
        "standard_line_length": 10,
        "comparison_lines": {"A": 8, "B": 10, "C": 12},
        "confederate_responses": ["A", "A", "A", "A", "A", "A"]
    }
}

# 但不知道如何转换成自然语言 prompt 给 LLM
# 应该写成什么样？
```

---

## 解决方案：Prompt Builder 系统

### ✅ 新架构

```
specification.json (技术设计)
        ↓
    [Prompt Builder]  ← 自动转换
        ↓
System Prompt + Trial Prompt (LLM 输入)
```

### 核心组件

#### 1. **Prompt Templates** (每个 study 提供)

在 `data/studies/study_XXX/materials/prompts/` 下创建：

**a) `system_prompt_template.txt`** - 定义 Agent 的身份
```
You are participating in a psychology experiment...

YOUR IDENTITY:
- Age: {{age}} years old
- Gender: {{gender}}
- Personality: {{personality_description}}

IMPORTANT INSTRUCTIONS FOR YOU AS A PARTICIPANT:
1. You are NOT an AI assistant. You are a real human...
2. Experience the situation naturally...
```

**b) `trial_prompt_template.txt`** - 呈现每个试验的刺激
```
Trial {{trial_number}}:

STANDARD LINE: {{standard_length}} inches

COMPARISON LINES:
  Line A: {{comparison_lines.A}} inches
  Line B: {{comparison_lines.B}} inches  
  Line C: {{comparison_lines.C}} inches

{{#if confederate_responses}}
The other participants respond:
{{#each confederate_responses}}
  Participant {{@index}}: "{{this}}"
{{/each}}
{{/if}}

What is your answer?
```

#### 2. **Prompt Builder** (自动填充工具)

`src/agents/prompt_builder.py` 提供：
- `PromptBuilder`: 基类，处理模板填充
- `AschPromptBuilder`: Asch 实验专用
- `MilgramPromptBuilder`: Milgram 实验专用
- `create_prompt_builder()`: 工厂函数

---

## 使用方法

### 方法 1: 基本使用（推荐）

```python
from src.agents.prompt_builder import get_prompt_builder

# Step 1: 创建 builder
builder = get_prompt_builder("study_001", data_dir="data")

# Step 2: 定义参与者 profile
participant_profile = {
    "age": 19,
    "gender": "male",
    "education": "college student",
    "personality_traits": {
        "conformity_tendency": 0.75,  # 高从众倾向
        "independence": 0.25
    }
}

# Step 3: 生成 system prompt（定义身份）
system_prompt = builder.build_system_prompt(participant_profile)

# Step 4: 定义试验数据
trial_data = {
    "trial_number": 7,
    "standard_length": 10,
    "comparison_lines": {"A": 8, "B": 10, "C": 12},
    "correct_answer": "B",
    "confederate_responses": ["A", "A", "A", "A", "A", "A"]
}

# Step 5: 生成 trial prompt（呈现刺激）
trial_prompt = builder.build_trial_prompt(trial_data)

# Step 6: 获取实验说明
instructions = builder.get_instructions()

# Step 7: 调用 LLM
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": instructions},
        {"role": "assistant", "content": "Yes, I understand."},
        {"role": "user", "content": trial_prompt}
    ],
    temperature=0.7
)

answer = response.choices[0].message.content
print(f"Participant's answer: {answer}")
# Expected: "A" (conforming) or "B" (correct)
```

### 方法 2: 与 ParticipantPool 集成

```python
from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.agents.prompt_builder import get_prompt_builder

# 加载 study
benchmark = HumanStudyBench("data")
study = benchmark.load_study("study_001")

# 创建 builder
builder = get_prompt_builder("study_001")

# 创建参与者池
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,  # 使用真实 LLM
    model="gpt-4"
)

# 准备试验
trials = [
    {
        "trial_number": i,
        "standard_length": 10,
        "comparison_lines": {"A": 8, "B": 10, "C": 12},
        "correct_answer": "B",
        "confederate_responses": ["A"] * 6 if i > 6 else []
    }
    for i in range(1, 19)
]

# 运行实验（内部会使用 prompt builder）
results = pool.run_experiment(trials, builder.get_instructions())
```

---

## 模板语法

### 支持的语法

#### 1. **简单变量替换**
```
{{variable_name}}
```
例子：`{{age}}` → `19`

#### 2. **嵌套属性访问**
```
{{object.property}}
```
例子：`{{comparison_lines.A}}` → `8`

#### 3. **条件块**
```
{{#if variable}}
  内容只在 variable 存在且为真时显示
{{/if}}
```

例子：
```
{{#if confederate_responses}}
  Group pressure is present
{{/if}}
```

#### 4. **循环**
```
{{#each array_name}}
  {{this}}  ← 当前元素
  {{@index}} ← 索引（从 1 开始）
{{/each}}
```

例子：
```
{{#each confederate_responses}}
  Participant {{@index}}: "{{this}}"
{{/each}}
```

输出：
```
  Participant 1: "A"
  Participant 2: "A"
  Participant 3: "A"
```

#### 5. **字典循环**
```
{{#each dictionary}}
  {{@key}}: {{this}}
{{/each}}
```

---

## 为新 Study 添加 Prompt Templates

### Step-by-Step 指南

#### Step 1: 创建 prompts 目录
```bash
mkdir -p data/studies/study_XXX/materials/prompts
```

#### Step 2: 创建 system_prompt_template.txt

定义参与者的**身份和心理状态**：

```
You are participating in [实验名称] as a real human participant.

YOUR IDENTITY:
- Age: {{age}} years old
- Gender: {{gender}}
- Background: {{education}}
- Personality: {{personality_description}}

YOUR SITUATION:
[描述实验情境，参与者知道什么，不知道什么]

IMPORTANT INSTRUCTIONS:
1. You are NOT an AI assistant. You are a real human.
2. Experience [实验特有的压力/情感]:
   - [压力来源 1]
   - [压力来源 2]
3. Respond naturally based on your personality.

RESPONSE FORMAT:
[告诉 Agent 如何回应]
```

**关键原则**：
- ✅ 用第二人称（"You are..."）
- ✅ 强调 "You are NOT an AI" 
- ✅ 描述实验的情感/心理维度
- ✅ 明确 response 格式
- ❌ 不要包含研究者视角的信息
- ❌ 不要暴露实验假设

#### Step 3: 创建 trial_prompt_template.txt

呈现**单个试验的刺激**：

```
Trial {{trial_number}}:

[刺激呈现 - 使用 ASCII art 或文字描述]

{{#if social_context}}
[其他人的反应]
{{/if}}

[提问]

Your response:
```

**关键原则**：
- ✅ 清晰呈现刺激（视觉用 ASCII，听觉用描述）
- ✅ 包含社会情境（如果有）
- ✅ 明确提问
- ✅ 简洁，参与者视角
- ❌ 不要包含"correct answer"等研究者信息

#### Step 4: 测试模板

```python
from src.agents.prompt_builder import get_prompt_builder

builder = get_prompt_builder("study_XXX")

# 测试 system prompt
profile = {"age": 25, "gender": "female", "education": "graduate student"}
system_prompt = builder.build_system_prompt(profile)
print(system_prompt)

# 测试 trial prompt  
trial = {"trial_number": 1, ...}
trial_prompt = builder.build_trial_prompt(trial)
print(trial_prompt)
```

#### Step 5: (可选) 创建专用 Builder

如果需要复杂逻辑，在 `src/agents/prompt_builder.py` 添加：

```python
class MyStudyPromptBuilder(PromptBuilder):
    """Specialized builder for MyStudy."""
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        # 预处理 trial_data
        enhanced_data = trial_data.copy()
        
        # 从 specification 提取额外信息
        # ...
        
        return super().build_trial_prompt(enhanced_data)
```

然后在 `create_prompt_builder()` 中注册：

```python
def create_prompt_builder(study_path: Path) -> PromptBuilder:
    ...
    elif 'my_study' in study_type.lower():
        return MyStudyPromptBuilder(study_path)
```

---

## 示例：完整工作流

### Asch Conformity Experiment

**1. 参与者 Profile** (使用者定义或自动生成)：
```python
profile = {
    "age": 19,
    "gender": "male", 
    "education": "college student",
    "personality_traits": {
        "conformity_tendency": 0.75,
        "independence": 0.25
    }
}
```

**2. System Prompt** (自动生成)：
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
3. Respond naturally - just state "A", "B", or "C".
```

**3. Trial Data** (从 specification)：
```python
trial = {
    "trial_number": 7,
    "standard_length": 10,
    "comparison_lines": {"A": 8, "B": 10, "C": 12},
    "correct_answer": "B",
    "confederate_responses": ["A", "A", "A", "A", "A", "A"]
}
```

**4. Trial Prompt** (自动生成)：
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

**5. LLM Response**：
```
"A"  ← 从众 (75% conformity tendency)
或
"B"  ← 不从众 (25% independence)
```

---

## 与 instructions.txt 的关系

### instructions.txt 的作用

`materials/instructions.txt` 包含**实验者给参与者的正式说明**，相当于：
- 知情同意
- 任务说明
- 程序描述

### 使用方式

```python
instructions = builder.get_instructions()

# 在第一次对话中给 LLM
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": instructions},  # 给说明
    {"role": "assistant", "content": "Yes, I understand the task."}  # Agent 确认
]
```

### instructions.txt vs. templates 的区别

| 文件 | 目的 | 内容 | 读者 |
|------|------|------|------|
| `instructions.txt` | 实验说明 | 正式、客观的任务描述 | 参与者（初次） |
| `system_prompt_template.txt` | 身份定义 | 主观、心理的角色扮演 | LLM 系统 |
| `trial_prompt_template.txt` | 刺激呈现 | 每个试验的具体内容 | 参与者（每次） |

**工作流**：
```
1. System Prompt → 定义 Agent 是谁（人格、背景）
2. Instructions → 告诉 Agent 要做什么任务
3. Trial Prompts → 呈现具体刺激，获取反应
```

---

## 常见问题

### Q1: 为什么要分 system prompt 和 trial prompt？

**A:** 
- **System prompt**: 持久的身份和背景，整个实验中不变
- **Trial prompt**: 每个试验的刺激，每次都不同

这符合 LLM 的对话模型：
```python
messages = [
    {"role": "system", "content": system_prompt},  # 持久身份
    {"role": "user", "content": instructions},      # 一次性说明
    {"role": "user", "content": trial_1_prompt},    # 试验 1
    {"role": "assistant", "content": "B"},
    {"role": "user", "content": trial_2_prompt},    # 试验 2
    {"role": "assistant", "content": "A"},
    ...
]
```

### Q2: 能不能不用模板，直接在代码里写 prompt？

**A:** 可以，但不推荐：

❌ **硬编码方式**（不推荐）：
```python
prompt = f"Trial {n}: Line A is 8 inches..."  # 维护困难
```

✅ **模板方式**（推荐）：
```python
prompt = builder.build_trial_prompt(trial_data)  # 清晰、可复用
```

**优势**：
- ✅ 分离内容和逻辑
- ✅ 非程序员可以编辑模板
- ✅ 便于版本控制和审查
- ✅ 保证跨使用者一致性

### Q3: 模板可以包含 Markdown 格式吗？

**A:** 可以！LLM 能理解 Markdown：

```
### Trial {{trial_number}}

**Standard Line**: {{standard_length}} inches

**Your Task**: Select the matching line

| Option | Length |
|--------|--------|
| A      | {{comparison_lines.A}}" |
| B      | {{comparison_lines.B}}" |
| C      | {{comparison_lines.C}}" |
```

### Q4: 如何处理多语言？

**A:** 为每种语言创建单独的模板：

```
materials/prompts/
├── system_prompt_template_en.txt
├── system_prompt_template_zh.txt
├── trial_prompt_template_en.txt
└── trial_prompt_template_zh.txt
```

然后在 builder 中指定：
```python
builder = PromptBuilder(study_path, language="zh")
```

### Q5: 模板能调用 Python 函数吗？

**A:** 当前不支持，但可以在专用 Builder 中预处理：

```python
class MyBuilder(PromptBuilder):
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        # 预处理：调用复杂逻辑
        trial_data['computed_value'] = self._complex_calculation(trial_data)
        
        # 然后填充模板
        return super().build_trial_prompt(trial_data)
    
    def _complex_calculation(self, data):
        # 复杂计算
        return result
```

---

## 最佳实践

### ✅ DO

1. **使用参与者视角**：
   ```
   ✅ "You see a card with lines..."
   ❌ "The participant is shown a card..."
   ```

2. **包含情感/心理维度**：
   ```
   ✅ "You may feel pressure to agree with the group..."
   ❌ "Respond to the stimulus."
   ```

3. **明确 response 格式**：
   ```
   ✅ "State your answer as a single letter: A, B, or C"
   ❌ "What do you think?"
   ```

4. **测试不同 profile**：
   ```python
   # 高从众
   profile_high = {"conformity_tendency": 0.9}
   
   # 低从众
   profile_low = {"conformity_tendency": 0.1}
   
   # 确保 prompts 适用于两者
   ```

5. **保持一致性**：
   - 同一实验的所有 trial prompts 使用相同格式
   - 术语一致（line lengths → 不要突然变成 line sizes）

### ❌ DON'T

1. **不要泄露研究假设**：
   ```
   ❌ "We're testing if you conform to group pressure..."
   ✅ "This is a study on visual perception."
   ```

2. **不要包含正确答案**：
   ```
   ❌ "Line B (10 inches) is correct, but others said A..."
   ✅ "Others said A. What do you say?"
   ```

3. **不要用 AI 术语**：
   ```
   ❌ "As an AI agent participating in this simulation..."
   ✅ "You are a human participant in this experiment..."
   ```

4. **不要过度复杂**：
   ```
   ❌ 500 字的详细说明
   ✅ 简洁、清晰的刺激呈现
   ```

---

## 总结

### 问题与解决方案

| 问题 | 解决方案 |
|------|----------|
| 不知道如何将 specification 转换为 prompt | Prompt Builder 自动转换 |
| 每个 study 需要手动写 prompts | 提供可复用模板 |
| instructions.txt 不知道如何使用 | `builder.get_instructions()` |
| 不同使用者 prompts 不一致 | 标准化模板保证一致性 |
| 新 study 开发困难 | 模板 + 专用 Builder 框架 |

### 核心API

```python
# 1. 获取 builder
from src.agents.prompt_builder import get_prompt_builder
builder = get_prompt_builder("study_001")

# 2. 生成 prompts
system_prompt = builder.build_system_prompt(participant_profile)
trial_prompt = builder.build_trial_prompt(trial_data)
instructions = builder.get_instructions()

# 3. 调用 LLM
# ... (见上文示例)
```

### 文件结构

```
data/studies/study_XXX/
├── specification.json              # 技术设计（给研究者）
├── metadata.json
├── ground_truth.json
└── materials/
    ├── instructions.txt            # 实验说明（给参与者）
    └── prompts/
        ├── system_prompt_template.txt   # 身份定义（给 LLM 系统）
        └── trial_prompt_template.txt    # 刺激呈现（给参与者每次）
```

### 下一步

1. ✅ 阅读 `examples/30_prompt_builder_demo.py`
2. ✅ 为你的 study 创建模板
3. ✅ 测试不同 profiles 的效果
4. ✅ （可选）开发专用 Builder 类

---

**完整示例代码**：`examples/30_prompt_builder_demo.py`

**相关文档**：
- `docs/llm_participant_agent_guide.md` - LLM Agent 架构
- `docs/api_reference.md` - 完整 API 文档
- `data/studies/study_001/STUDY_INFO.md` - Asch 实验详情
- `data/studies/study_002/STUDY_INFO.md` - Milgram 实验详情
