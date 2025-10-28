# HumanStudyBench 完整使用指南

## 🎯 快速开始：完整运行 Benchmark

### 方法 1：使用模拟模式（快速测试，不消耗 API）

```bash
# 运行完整 benchmark（所有研究，模拟模式）
python run_full_benchmark.py

# 运行单个研究
python run_full_benchmark.py --studies study_001

# 使用更少的参与者（加速）
python run_full_benchmark.py --n-participants 20
```

### 方法 2：使用真实 LLM（推荐：OpenRouter）

```bash
# 设置 API key
export OPENROUTER_API_KEY="your-key"

# 运行完整 benchmark（使用 mistralai/mistral-nemo）
python run_full_benchmark.py --real-llm

# 使用其他模型
python run_full_benchmark.py --real-llm --model anthropic/claude-3-sonnet

# 使用 OpenAI（直接）
export OPENAI_API_KEY="your-openai-key"
python run_full_benchmark.py --real-llm --model gpt-4
```

### 方法 3：运行单个示例

```bash
# Asch conformity 实验（模拟模式）
python examples/10_llm_participant_demo.py

# OpenRouter demo（真实 LLM）
export OPENROUTER_API_KEY="your-key"
python examples/40_openrouter_demo.py

# Prompt Builder demo
python examples/30_prompt_builder_demo.py
```

---

## 📊 Benchmark 结构

### 当前可用的研究

1. **Study 001 - Asch Conformity (1952)**
   - Domain: Social Psychology
   - Difficulty: Easy
   - Task: Line judgment with group pressure
   - N: 123 participants (50 experimental + 37 control in original)
   - Key metric: Conformity rate (~37% in original)

2. **Study 002 - Milgram Obedience (1963)**
   - Domain: Social Psychology
   - Difficulty: Medium
   - Task: Teacher-learner shock administration
   - N: 40 participants
   - Key metric: Obedience rate (~65% to 450V in original)

---

## 🔧 如何集成你的 AI Agent

### 选项 A：使用 OpenRouter（推荐）

如果你的模型在 OpenRouter 上可用：

```python
from src.agents.llm_participant_agent import ParticipantPool
from src.agents.prompt_builder import get_prompt_builder

# 1. 加载研究
benchmark = HumanStudyBench("data")
study = benchmark.load_study("study_001")
builder = get_prompt_builder("study_001")

# 2. 创建 participant pool（自动使用 OpenRouter）
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="mistralai/mistral-nemo",  # 或你的模型
    random_seed=42
)

# 3. 准备 trials
trials = create_asch_trials()  # 见 run_full_benchmark.py
instructions = builder.get_instructions()

# 4. 运行实验
results = pool.run_experiment(trials, instructions, prompt_builder=builder)

# 5. 评分
from src.evaluation.scorer import Scorer
scorer = Scorer()
score, report = scorer.score_study(study, results)
print(f"Score: {score:.1%}")
```

**可用模型**（OpenRouter）：
- `mistralai/mistral-nemo` - 默认，性价比高
- `anthropic/claude-3-sonnet` - 高质量推理
- `google/gemini-pro` - Google 旗舰
- `meta-llama/llama-3-70b-instruct` - 开源
- `openai/gpt-4-turbo` - 通过 OpenRouter 访问 OpenAI

查看更多：https://openrouter.ai/models

### 选项 B：使用 OpenAI（直接）

```python
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="gpt-4",  # 不含 "/" = OpenAI
    random_seed=42
)
# 系统会自动使用 OPENAI_API_KEY
```

### 选项 C：自定义 HTTP API（OpenAI 兼容）

如果你的 endpoint 兼容 OpenAI API：

```python
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="your-model-name",
    api_key="your-key",
    api_base="https://your-endpoint.com/v1",  # 自定义 base URL
    random_seed=42
)
```

### 选项 D：完全自定义 API（非 OpenAI 兼容）

创建自定义 agent adapter：

```python
# my_agent.py
import requests
from src.agents.llm_participant_agent import LLMParticipantAgent

class MyCustomAgent(LLMParticipantAgent):
    """适配你的 API"""
    
    def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """
        重写这个方法来调用你的 API
        
        Args:
            system_prompt: 参与者身份 prompt
            user_message: Trial prompt（实验刺激）
        
        Returns:
            模型响应（纯文本）
        """
        # 示例：调用自定义 HTTP API
        url = "https://your-api.example.com/generate"
        
        payload = {
            "system": system_prompt,
            "prompt": user_message,
            "temperature": 0.7,
            "max_tokens": 150
        }
        
        headers = {"Authorization": f"Bearer {self.api_key}"}
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        # 必须返回纯文本字符串
        # Agent 会自动解析 A/B/C（Asch）或 continue/stop（Milgram）
        return data["text"].strip()
```

使用你的自定义 agent：

```python
from my_agent import MyCustomAgent

# 创建单个 agent
profile = {"age": 22, "gender": "female", 
           "personality_traits": {"conformity_tendency": 0.5}}

agent = MyCustomAgent(
    participant_id=1,
    profile=profile,
    model="your-model",
    api_key="your-key",
    use_real_llm=True
)

# 运行单个 trial
trial_prompt = builder.build_trial_prompt(trials[0])
result = agent.complete_trial(trial_prompt, trials[0])
print(result)
```

或创建一个完整的 pool wrapper：

```python
# 创建多个 agents 并运行完整实验
agents = []
for i, profile in enumerate(pool.profiles):
    agent = MyCustomAgent(
        participant_id=i,
        profile=profile,
        model="your-model",
        api_key="your-key",
        use_real_llm=True
    )
    agents.append(agent)

# 手动运行实验循环
for trial in trials:
    trial_prompt = builder.build_trial_prompt(trial)
    for agent in agents:
        result = agent.complete_trial(trial_prompt, trial)
        # 收集结果
```

---

## 📈 理解输出

### Benchmark 运行输出

```
================================================================================
                    HumanStudyBench - Full Benchmark Run
================================================================================
Date: 2025-10-28 00:52:32
Mode: Real LLM
Model: mistralai/mistral-nemo
Random Seed: 42
================================================================================

Studies to run: study_001, study_002

# ... 每个研究的详细结果 ...

================================================================================
                         BENCHMARK SUMMARY
================================================================================

Studies run: 2
Passed: 1/2 (50%)
Average score: 65.5%
Total time: 120.5s (2.0min)

Per-study results:
✅ study_001    | Score: 78.0% | Grade: pass         | Tests: 4/5
❌ study_002    | Score: 53.0% | Grade: fail         | Tests: 2/5

================================================================================
✅ BENCHMARK PASSED
   Average Score: 65.5% (threshold: 60%)
   Pass Rate: 1/2 (50%, threshold: 50%)
================================================================================

Results saved to: results/full_benchmark_20251028_005232.json
```

### 评分标准

**单个研究**：
- **70%+ = PASS** - 成功复现原始研究
- **85%+ = HIGH QUALITY** - 高质量复现
- **100% = PERFECT** - 完美复现

**整体 Benchmark**：
- 平均分 ≥ 60%
- 至少 50% 的研究通过

### 结果文件

运行后会生成两个 JSON 文件：

1. **`results/full_benchmark_TIMESTAMP.json`** - 摘要
   ```json
   {
     "timestamp": "20251028_005232",
     "model": "mistralai/mistral-nemo",
     "summary": {
       "total_studies": 2,
       "passed_studies": 1,
       "average_score": 0.655
     },
     "studies": [...]
   }
   ```

2. **`results/full_benchmark_detailed_TIMESTAMP.json`** - 详细结果
   - 包含每个测试的详细分数
   - 统计检验结果
   - 与原始研究的对比

---

## 🧪 验证和测试

### 运行单元测试

```bash
# 安装 dev 依赖（如果还没有）
pip install -e .[dev]

# 运行所有测试
pytest

# 快速测试（只运行导入测试）
pytest tests/test_benchmark.py::test_import -v
```

### 快速验证安装

```bash
# 验证数据加载
python scripts/quick_test.py

# 验证 OpenRouter API
python scripts/quick_test_openrouter.py
```

---

## 📚 深入理解

### Prompt Builder 系统

Prompt Builder 自动将 `specification.json` 转换为自然语言 prompts：

```python
builder = get_prompt_builder("study_001")

# 1. System prompt（参与者身份）
system_prompt = builder.build_system_prompt({
    "age": 20,
    "gender": "male",
    "personality_traits": {"conformity_tendency": 0.75}
})
# → "你是一个 20 岁的男性，正在参加心理学实验..."

# 2. Instructions（实验说明）
instructions = builder.get_instructions()
# → 从 materials/instructions.txt 读取

# 3. Trial prompt（具体试次）
trial_prompt = builder.build_trial_prompt({
    "trial_number": 7,
    "standard_line_length": 10,
    "comparison_lines": {"A": 8, "B": 10, "C": 12},
    "confederate_responses": ["A"] * 6
})
# → "Trial 7: 标准线 [10 units]，比较线 A/B/C，其他人都说 A..."
```

**模板位置**：
- `data/studies/study_001/materials/prompts/system_prompt_template.txt`
- `data/studies/study_001/materials/prompts/trial_prompt_template.txt`

**模板语法**：
- `{{variable}}` - 简单替换
- `{{object.property}}` - 嵌套属性
- `{{#if variable}}...{{/if}}` - 条件块
- `{{#each array}}{{this}}{{/each}}` - 循环

### ParticipantPool 工作流程

```python
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="mistralai/mistral-nemo",
    random_seed=42
)
```

内部发生了什么：

1. **生成参与者 profiles** - 基于 specification 中的人口统计学信息
   - 年龄：正态分布采样（M=20, SD=2）
   - 性别：按分布随机采样
   - 个性特征：Beta 分布（conformity_tendency, authority_obedience 等）

2. **创建 LLM agents** - 每个参与者一个 agent
   - 每个 agent 有独特的 profile
   - Agent 接收 system prompt（基于 profile）

3. **运行实验**：
   ```python
   results = pool.run_experiment(trials, instructions, prompt_builder)
   ```
   - 给每个参与者发送 instructions
   - 对每个 trial：
     - 生成 trial prompt（包含刺激、confederate 响应等）
     - 每个参与者做出响应
     - 记录响应（A/B/C 或 continue/stop）

4. **聚合结果**：
   - 计算描述性统计（mean, SD, range）
   - 按组分析（实验组 vs 控制组）
   - 个体差异分析

### 评分系统

`Scorer` 将你的结果与 `ground_truth.json` 对比：

```python
scorer = Scorer()
score_result = scorer.score_study(study, results)
```

**验证测试**（Study 001 - Asch）：
1. `conformity_rate_range` - 从众率是否在合理范围（30-44%）
2. `group_difference_significant` - 实验组 vs 控制组是否显著不同
3. `majority_conformed_at_least_once` - 是否大多数人至少从众一次
4. `control_group_high_accuracy` - 控制组是否高准确率（>95%）
5. `individual_differences_present` - 是否存在个体差异

每个测试返回 0-1 分，最终分数 = 所有测试的平均分。

---

## 💡 常见问题

### Q: 模拟模式为什么分数是 0？

A: 模拟模式缺少控制组数据和完整的统计检验实现。这是正常的。模拟模式用于：
- 快速测试代码
- 验证工作流程
- 不消耗 API credits

要获得真实评分，使用 `--real-llm` 模式。

### Q: 如何减少 API 消耗？

1. 使用更少的参与者：
   ```bash
   python run_full_benchmark.py --real-llm --n-participants 10
   ```

2. 只运行单个研究：
   ```bash
   python run_full_benchmark.py --real-llm --studies study_001
   ```

3. 使用便宜的模型：
   ```bash
   python run_full_benchmark.py --real-llm --model mistralai/mistral-nemo
   ```
   （mistralai/mistral-nemo ≈ $0.15/1M tokens，比 GPT-4 便宜 200 倍）

### Q: 如何保证可复现性？

设置 `random_seed`：
```bash
python run_full_benchmark.py --real-llm --random-seed 42
```

或在代码中：
```python
pool = ParticipantPool(..., random_seed=42)
```

相同的 seed → 相同的 participant profiles → 可复现的结果

### Q: 支持哪些研究类型？

当前：
- ✅ Asch conformity（从众）
- ✅ Milgram obedience（服从）

计划中：
- 🚧 Stanford Prison Experiment
- 🚧 Trolley Problem
- 🚧 Ultimatum Game

### Q: 如何添加新的研究？

查看 `docs/paper_curation_guide.md` 获取完整指南。

---

## 🚀 下一步

1. **快速测试**：
   ```bash
   python run_full_benchmark.py
   ```

2. **真实运行**：
   ```bash
   export OPENROUTER_API_KEY="your-key"
   python run_full_benchmark.py --real-llm --n-participants 20
   ```

3. **集成你的 agent**：
   - 选择上述选项 A/B/C/D
   - 创建 adapter（如果需要）
   - 运行并评分

4. **查看详细文档**：
   - `docs/getting_started.md`
   - `docs/prompt_builder_guide.md`
   - `docs/openrouter_guide.md`
   - `docs/llm_participant_agent_guide.md`

---

## 📞 获取帮助

- 查看示例：`examples/`
- 阅读文档：`docs/`
- 运行测试：`pytest`
- 查看代码：`src/`

Happy benchmarking! 🎉
