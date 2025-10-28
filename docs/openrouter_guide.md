# OpenRouter Integration Guide

## 概述

HumanStudyBench 现已支持 **OpenRouter API**，并使用 **`mistralai/mistral-nemo`** 作为默认模型。

OpenRouter 提供了统一的 API 接口访问多个 LLM 提供商（OpenAI, Anthropic, Google, Meta 等）。

---

## 快速开始

### 1. 获取 API Key

访问 https://openrouter.ai/ 获取 API key：

```bash
# 注册并获取 key（格式：sk-or-v1-...）
```

### 2. 设置环境变量

```bash
export OPENROUTER_API_KEY="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"
```

### 3. 运行示例

```bash
# 运行 OpenRouter demo
python examples/40_openrouter_demo.py

# 或使用任何现有示例（会自动使用 mistralai/mistral-nemo）
python examples/10_llm_participant_demo.py
```

---

## 使用方法

### 基础使用（使用默认模型）

```python
from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.agents.prompt_builder import get_prompt_builder

# 加载 study
benchmark = HumanStudyBench("data")
study = benchmark.load_study("study_001")

# 创建 prompt builder
prompt_builder = get_prompt_builder("study_001")

# 创建 participant pool（默认使用 mistralai/mistral-nemo）
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,  # 使用真实 LLM
    random_seed=42      # 可复现
)

# 创建 trials
trials = [...]  # 你的 trial 数据

# 运行实验
results = pool.run_experiment(
    trials,
    study.specification["procedure"]["instructions"],
    prompt_builder=prompt_builder
)
```

### 使用其他 OpenRouter 模型

```python
# 使用 Claude 3 Sonnet
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="anthropic/claude-3-sonnet",  # 指定模型
    random_seed=42
)

# 使用 Gemini Pro
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="google/gemini-pro",
    random_seed=42
)

# 使用 Llama 3
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="meta-llama/llama-3-70b-instruct",
    random_seed=42
)
```

### 仍然支持 OpenAI（向后兼容）

```python
# 使用 OpenAI GPT-4
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="gpt-4",  # OpenAI 模型（不含 "/"）
    api_key=os.environ.get("OPENAI_API_KEY"),  # 会自动使用 OPENAI_API_KEY
    random_seed=42
)
```

---

## 支持的模型

### OpenRouter 热门模型

| 模型 | 说明 | 推荐场景 |
|------|------|---------|
| `mistralai/mistral-nemo` | **默认模型**，性价比高 | 日常实验 |
| `anthropic/claude-3-sonnet` | Claude 3，推理能力强 | 复杂任务 |
| `anthropic/claude-3-opus` | Claude 3 最强版本 | 最高质量 |
| `google/gemini-pro` | Google Gemini | 多模态任务 |
| `meta-llama/llama-3-70b-instruct` | Meta Llama 3 | 开源选择 |
| `openai/gpt-4-turbo` | OpenAI GPT-4 Turbo | OpenAI 用户 |
| `openai/gpt-3.5-turbo` | GPT-3.5 | 快速+便宜 |

完整模型列表：https://openrouter.ai/models

---

## API Key 检测逻辑

系统会自动检测使用哪个 API key：

```python
# 对于 OpenRouter 模型（包含 "/"）
model = "mistralai/mistral-nemo"
# → 自动使用 OPENROUTER_API_KEY
# → API base: https://openrouter.ai/api/v1

# 对于 OpenAI 模型（不含 "/"）
model = "gpt-4"
# → 自动使用 OPENAI_API_KEY
# → API base: https://api.openai.com/v1

# 手动指定 API key（覆盖环境变量）
pool = ParticipantPool(
    ...,
    model="mistralai/mistral-nemo",
    api_key="sk-or-v1-...",  # 手动指定
)
```

---

## 高级配置

### 自定义 API Base URL

```python
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="custom-model",
    api_base="https://your-custom-endpoint.com/v1",  # 自定义
    api_key="your-key"
)
```

### 单个 Agent（不使用 Pool）

```python
from src.agents.llm_participant_agent import LLMParticipantAgent

agent = LLMParticipantAgent(
    participant_id=1,
    profile={"age": 20, "gender": "male"},
    model="mistralai/mistral-nemo",  # 默认
    use_real_llm=True
)

# 使用 agent
response = agent.complete_trial(
    trial_prompt="Which line matches?",
    trial_info={...}
)
```

---

## 成本估算

OpenRouter 不同模型价格不同。以 `mistralai/mistral-nemo` 为例：

- **输入**: ~$0.15 / 1M tokens
- **输出**: ~$0.15 / 1M tokens

**示例实验成本**:
- 50 participants × 18 trials = 900 completions
- 平均每次 ~200 tokens (system + user + response)
- 总计: ~180,000 tokens = **$0.027** (约 0.2 元)

查看实时价格：https://openrouter.ai/models

---

## 测试与验证

### 运行集成测试

```bash
python scripts/test_openrouter.py
```

测试内容：
- ✓ OpenRouter 模型检测
- ✓ 默认模型配置
- ✓ API key 环境变量检测
- ✓ Benchmark 集成
- ✓ 向后兼容性（OpenAI）

### 模拟模式测试（不消耗 API）

```python
# use_real_llm=False 会模拟响应，不调用 API
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=False,  # 模拟模式，免费
    model="mistralai/mistral-nemo",
    random_seed=42
)
```

---

## 常见问题

### Q: 为什么选择 mistralai/mistral-nemo 作为默认？

A: 
- 性价比高（~$0.15/1M tokens）
- 性能优秀（适合大多数心理学实验）
- 响应速度快
- 支持长上下文

### Q: 如何切换回 OpenAI？

A: 只需指定不含 "/" 的模型名：

```python
pool = ParticipantPool(
    ...,
    model="gpt-4",  # 自动使用 OpenAI API
)
```

### Q: 可以使用本地模型吗？

A: 可以，通过 `api_base` 指向本地服务：

```python
pool = ParticipantPool(
    ...,
    model="local-llama",
    api_base="http://localhost:8000/v1",  # 本地 API
    api_key="dummy"
)
```

### Q: OpenRouter 和直接调用 OpenAI 有什么区别？

A: 
- **OpenRouter**: 统一接口，多个模型，可能有额外 markup
- **OpenAI 直接**: 仅 OpenAI 模型，官方价格

两种方式都支持，可根据需求选择。

---

## 示例代码

### 完整示例：运行 Asch 实验

```python
import os
from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.agents.prompt_builder import get_prompt_builder

# 设置 API key
os.environ["OPENROUTER_API_KEY"] = "sk-or-v1-..."

# 加载 study
benchmark = HumanStudyBench("data")
study = benchmark.load_study("study_001")
prompt_builder = get_prompt_builder("study_001")

# 创建 pool
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="mistralai/mistral-nemo",  # 默认
    random_seed=42
)

# 创建 trials
trials = []
for i in range(1, 19):
    is_critical = i > 6 and (i - 6) % 3 != 0
    trials.append({
        "trial_number": i,
        "study_type": "asch_conformity",
        "trial_type": "critical" if is_critical else "neutral",
        "standard_line_length": 8 + (i % 4),
        "comparison_lines": {"A": 7, "B": 8 + (i % 4), "C": 11},
        "correct_answer": "B",
        "confederate_responses": ["A"] * 6 if is_critical else []
    })

# 运行实验
instructions = study.specification["procedure"]["instructions"]
results = pool.run_experiment(trials, instructions, prompt_builder=prompt_builder)

# 查看结果
conformity_stats = results["descriptive_statistics"]["conformity_rate"]["experimental"]
print(f"Mean conformity: {conformity_stats['mean']*100:.1f}%")
```

### 比较多个模型

```python
models = [
    "mistralai/mistral-nemo",
    "anthropic/claude-3-sonnet",
    "google/gemini-pro"
]

for model in models:
    pool = ParticipantPool(
        study_specification=study.specification,
        n_participants=10,
        use_real_llm=True,
        model=model,
        random_seed=42
    )
    
    results = pool.run_experiment(trials, instructions, prompt_builder=prompt_builder)
    
    conformity_rate = results["descriptive_statistics"]["conformity_rate"]["experimental"]["mean"]
    print(f"{model}: {conformity_rate*100:.1f}% conformity")
```

---

## 技术细节

### 自动检测逻辑

```python
# 模型名包含 "/" → OpenRouter
self.is_openrouter = "/" in model

if self.is_openrouter:
    self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
    self.api_base = "https://openrouter.ai/api/v1"
else:
    self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
    self.api_base = None  # 使用 OpenAI 默认
```

### API 调用实现

```python
from openai import OpenAI

# OpenRouter
client = OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

# OpenAI
client = OpenAI(api_key=api_key)

# 统一接口
response = client.chat.completions.create(
    model=model,
    messages=[...],
    temperature=0.7,
    max_tokens=150
)
```

---

## 相关资源

- **OpenRouter 官网**: https://openrouter.ai/
- **模型列表**: https://openrouter.ai/models
- **定价**: https://openrouter.ai/models（每个模型页面）
- **API 文档**: https://openrouter.ai/docs

---

## 更新日志

### 2025-10-28: OpenRouter 集成

- ✅ 添加 OpenRouter API 支持
- ✅ 默认模型改为 `mistralai/mistral-nemo`
- ✅ 自动检测 `OPENROUTER_API_KEY` 环境变量
- ✅ 支持所有 OpenRouter 模型
- ✅ 保持向后兼容 OpenAI
- ✅ 新增 `examples/40_openrouter_demo.py`
- ✅ 新增 `scripts/test_openrouter.py`
- ✅ 全面测试通过

---

## 支持

如有问题，请查看：
- 示例代码: `examples/40_openrouter_demo.py`
- 测试代码: `scripts/test_openrouter.py`
- API 参考: `docs/api_reference.md`
