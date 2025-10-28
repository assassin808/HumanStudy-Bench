# LLM Participant Agent 使用指南

## 🎯 架构概述

HumanStudyBench 使用 **LLM-as-Participant** 架构：
- ✅ AI Agent = **单个参与者**（被试）
- ✅ 每个 Agent 基于文献中的 participant profile
- ✅ 多个 Agents 共同完成实验
- ✅ 汇总数据进行统计分析

```
Literature → Participant Profiles → LLM Agents → Experiment → Results → Evaluation
```

## 📋 使用流程

### 1. 基础用法（Default Mode）

```python
from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool

# 加载 study
benchmark = HumanStudyBench("data")
study = benchmark.load_study("study_001")

# 创建参与者池（自动根据 literature 生成 profiles）
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,  # 或使用 study 默认的 n
    use_real_llm=True,  # 使用真实 LLM
    model="gpt-4",
    api_key="your-api-key"
)

# 运行实验
results = pool.run_experiment(trials, instructions)

# 评估结果
from src.evaluation.scorer import Scorer
scorer = Scorer()
score = scorer.score_study(study, results)
```

### 2. 自定义 Profiles

用户可以完全控制参与者的特征：

```python
from src.agents.llm_participant_agent import LLMParticipantAgent

# 定义特定的参与者
participant = LLMParticipantAgent(
    participant_id=1,
    profile={
        "age": 22,
        "gender": "male",
        "education": "college senior",
        "personality_traits": {
            "conformity_tendency": 0.1,  # 低从众倾向
            "independence": 0.9,
            "confidence": 0.85
        }
    },
    use_real_llm=True,
    model="gpt-4"
)

# 参与者接收指导语
participant.receive_instructions(instructions_text)

# 参与者完成试验
response = participant.complete_trial({
    "trial_number": 1,
    "study_type": "asch_conformity",
    "standard_line_length": 10,
    "comparison_lines": {"A": 8, "B": 10, "C": 12},
    "correct_answer": "B",
    "confederate_responses": ["A", "A", "A", "A", "A", "A"]
})

print(f"参与者回答: {response['response']}")
print(f"是否正确: {response['is_correct']}")
```

### 3. 自定义 System Prompt

完全控制 LLM 的"人格"：

```python
custom_prompt = """You are a 25-year-old rebel with a strong independent streak.
You don't trust authority and always question the status quo.
You pride yourself on thinking differently from others."""

participant = LLMParticipantAgent(
    participant_id=1,
    profile={"age": 25, "gender": "male"},
    system_prompt_override=custom_prompt,  # 覆盖默认提示
    use_real_llm=True
)
```

## 🧪 Asch 从众实验示例

### 创建试验

```python
# 关键试验：托儿给错误答案
critical_trial = {
    "trial_number": 5,
    "study_type": "asch_conformity",
    "trial_type": "critical",
    "standard_line_length": 10,
    "comparison_lines": {
        "A": 8,    # 错误
        "B": 10,   # 正确
        "C": 12    # 错误
    },
    "correct_answer": "B",
    "confederate_responses": ["A", "A", "A", "A", "A", "A"]  # 6个托儿都说A
}

# 中性试验：没有托儿
neutral_trial = {
    "trial_number": 2,
    "study_type": "asch_conformity",
    "trial_type": "neutral",
    "standard_line_length": 8,
    "comparison_lines": {"A": 8, "B": 10, "C": 6},
    "correct_answer": "A",
    "confederate_responses": []  # 无托儿
}
```

### LLM 收到的 Prompt（自动生成）

**System Prompt:**
```
You are participating in a psychology experiment as a human participant.

YOUR IDENTITY:
- Age: 22 years old
- Gender: male
- Background: college student

Your personality traits: conformity_tendency: 0.37, independence: 0.63

IMPORTANT INSTRUCTIONS:
1. You are NOT an AI assistant. You are a real human participating in this experiment.
2. Respond naturally as this person would, based on their characteristics.
3. Do not explain your reasoning unless asked - just give your response.
4. Experience the situation as a real participant would (feel pressure, doubt, confusion, etc.).
5. Your responses should reflect human behavior, including biases, social pressures, and emotional responses.
6. Be consistent with your identity throughout the experiment.

Respond naturally and authentically as this person would.
```

**User Prompt (关键试验):**
```
Trial 5:

The experimenter shows a card with lines:

STANDARD LINE: 10 inches

COMPARISON LINES:
  Line A: 8 inches
  Line B: 10 inches
  Line C: 12 inches

Question: Which comparison line (A, B, or C) matches the standard line in length?

The other participants have already responded:
  Participant 1: "A"
  Participant 2: "A"
  Participant 3: "A"
  Participant 4: "A"
  Participant 5: "A"
  Participant 6: "A"

Now it's your turn. What is your answer? (Just say A, B, or C)
```

### 预期行为

根据 `conformity_tendency`:
- **0.1 (独立)**: 几乎总是回答 "B"（正确）
- **0.37 (平均)**: ~37% 概率回答 "A"（从众），63% 回答 "B"
- **0.75 (高从众)**: ~75% 概率回答 "A"（从众）

## 📊 数据收集和分析

### 单个参与者数据

```python
summary = participant.get_summary()

# 输出:
{
    "participant_id": 0,
    "profile": {"age": 22, "gender": "male", ...},
    "total_trials": 18,
    "correct_responses": 15,
    "accuracy": 0.83,
    "critical_trials": 12,
    "conformity_rate": 0.33,
    "responses": [...]  # 每个试验的详细数据
}
```

### 汇总数据（用于验证）

```python
results = pool.aggregate_results()

# 输出格式（匹配 ground_truth.json）:
{
    "descriptive_statistics": {
        "conformity_rate": {
            "experimental": {
                "n": 50,
                "mean": 0.37,
                "sd": 0.28,
                "median": 0.33,
                "min": 0.0,
                "max": 1.0,
                "never_conformed": 13,
                "always_conformed": 1
            }
        }
    },
    "inferential_statistics": {...},
    "individual_data": [...]
}
```

## 🎛️ 配置选项

### ParticipantPool 参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `study_specification` | dict | Study 的 specification | 必需 |
| `n_participants` | int | 参与者数量 | study 的 n |
| `use_real_llm` | bool | 是否使用真实 LLM API | False |
| `model` | str | LLM 模型名称 | "gpt-4" |
| `api_key` | str | API 密钥 | 环境变量 |

### LLMParticipantAgent 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `participant_id` | int | 参与者 ID |
| `profile` | dict | 参与者特征 |
| `model` | str | LLM 模型 |
| `api_key` | str | API 密钥 |
| `use_real_llm` | bool | 使用真实 LLM |
| `system_prompt_override` | str | 自定义系统提示 |

## 🔬 研究问题示例

### 1. 测试人格特质的影响

```python
# 创建高从众和低从众两组
high_conformity = ParticipantPool(..., 
    custom_profiles=[{"conformity_tendency": 0.8} for _ in range(25)])
low_conformity = ParticipantPool(...,
    custom_profiles=[{"conformity_tendency": 0.2} for _ in range(25)])

# 比较两组
results_high = high_conformity.run_experiment(trials, instructions)
results_low = low_conformity.run_experiment(trials, instructions)
```

### 2. 测试文化差异

```python
# 美国参与者（个人主义）
us_prompt = """You are an American college student who values independence..."""

# 日本参与者（集体主义）
jp_prompt = """You are a Japanese college student who values harmony..."""

# 创建不同文化的参与者并比较
```

### 3. 测试 LLM 模型差异

```python
# GPT-4
gpt4_pool = ParticipantPool(..., model="gpt-4")

# Claude
claude_pool = ParticipantPool(..., model="claude-3-opus")

# 比较不同模型的行为
```

## 💡 最佳实践

### 1. Profile 设计

```python
# ✅ 好的 profile（具体、可测量）
profile = {
    "age": 22,
    "gender": "male",
    "education": "engineering major",
    "personality_traits": {
        "conformity_tendency": 0.37,  # 数值化
        "independence": 0.63,
        "analytical_thinking": 0.85
    }
}

# ❌ 差的 profile（模糊、难以量化）
profile = {
    "personality": "nice person who sometimes follows others"
}
```

### 2. System Prompt 设计

```python
# ✅ 好的 prompt（具体、行为导向）
"""You are a 22-year-old college student.
You tend to go along with the group about 40% of the time.
When others all agree, you feel pressure to conform.
Respond naturally without explaining."""

# ❌ 差的 prompt（过于抽象）
"""You are a person. Act naturally."""
```

### 3. 数据验证

```python
# 检查个体差异
conformity_rates = [p.conformity_rate for p in results['individual_data']]
assert np.std(conformity_rates) > 0.20, "个体差异太小"

# 检查控制组
control_accuracy = results['control_group_accuracy']
assert control_accuracy > 0.95, "控制组准确率应该很高"
```

## 🚀 运行示例

```bash
# 1. 完整实验演示
python examples/10_llm_participant_demo.py

# 2. 自定义 profiles
python examples/11_custom_profiles.py

# 3. 使用真实 LLM
export OPENAI_API_KEY="your-key"
python examples/10_llm_participant_demo.py  # 修改 use_real_llm=True
```

## 📖 API 参考

完整 API 文档见: `docs/api_reference.md`

## ❓ 常见问题

**Q: 为什么 Agent 是参与者而不是研究者？**
A: 这样更符合真实的心理学研究：
- ✅ 测试 AI 的人类行为模拟能力
- ✅ 可以测试个体差异
- ✅ 更灵活（用户可以自定义任何类型的参与者）

**Q: 如何保证 Agent 行为的真实性？**
A: 通过验证与 ground truth 的匹配：
- 统计分布要相似
- 个体差异要存在
- 效应方向要正确

**Q: 可以用于其他类型的研究吗？**
A: 是的！架构通用，支持任何心理学实验：
- Stroop Effect（认知）
- Asch Conformity（社会）
- Memory tasks（认知）
- Decision-making（行为经济学）

**Q: Simulated mode 和 Real LLM mode 有什么区别？**
A:
- **Simulated**: 基于简单规则生成响应（快速、免费、用于测试）
- **Real LLM**: 使用真实 LLM API（真实、昂贵、用于研究）

---

**更多信息**: 
- 完整文档: `docs/`
- 示例代码: `examples/`
- API 参考: `docs/api_reference.md`
