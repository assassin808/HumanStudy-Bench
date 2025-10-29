# Study 003 Participant Profile Implementation Summary

## ✅ 完成的修改

### 1. **Study003Config - 自定义参与者生成**
文件: `src/studies/study_003_config.py`

添加了 `generate_participant_profiles()` 方法，基于原文的参与者特征生成 profiles：

**原文参与者信息** (Tversky & Kahneman, 1981):
- N = 152 (76 per frame)
- Population: University students and faculty
- **未报告**: 年龄分布、性别分布

**实现的生成逻辑**:
```python
- 70% students (age 18-25, mean ~21)
- 30% faculty (age 30-65, mean ~45)
- 50/50 random assignment to positive_frame / negative_frame
- NO gender field (忠实原文，未报告则不生成)
- Custom background text for each education level
- framing_condition stored in profile
```

---

### 2. **ParticipantPool - 支持自定义 Profiles**
文件: `src/agents/llm_participant_agent.py`

**修改 `__init__`**:
- 添加可选参数 `profiles: Optional[List[Dict[str, Any]]] = None`
- 如果提供 profiles，直接使用；否则调用默认的 `_generate_profiles()`

**修改 `run_experiment`**:
- 在调用 `build_trial_prompt()` 之前，将 `participant.profile` 添加到 trial 数据中
- 支持 frame-specific prompt 构建

---

### 3. **LLMParticipantAgent - 灵活的 System Prompt**
文件: `src/agents/llm_participant_agent.py` 

**修改 `_construct_system_prompt()`**:
```python
- Gender: 仅在 profile 包含时显示（Study 003 不显示）
- Background: 优先使用 profile['background']，否则用 education
- Personality traits: 格式化为小数 (0.00 - 1.00)
```

**示例 System Prompt** (Study 003):
```
YOUR IDENTITY:
- Age: 21 years old
- Background: You are a university student who considers different 
  perspectives when making decisions.

(No gender field - 忠实原文)
```

---

### 4. **PromptBuilder - Frame-Specific 材料加载**
文件: `src/agents/prompt_builder.py`

**修改 `build_trial_prompt()`**:
```python
# 检测 framing_condition
participant_profile = trial_data.get('participant_profile', {})
framing_condition = participant_profile.get('framing_condition')

if framing_condition:
    # 加载 materials/positive_frame.txt 或 negative_frame.txt
    frame_file = self.materials_path / f"{framing_condition}.txt"
    trial_data = {**trial_data, 'scenario': frame_text}
```

---

### 5. **run_full_benchmark.py - 使用 Study Config Profiles**
文件: `run_full_benchmark.py`

**修改 `run_study()`**:
```python
# Generate participant profiles using study config if available
profiles = None
if hasattr(study_config, 'generate_participant_profiles'):
    profiles = study_config.generate_participant_profiles(n_participants, random_seed)

# Pass to ParticipantPool
pool = ParticipantPool(..., profiles=profiles)
```

---

### 6. **新增材料文件**
文件: `data/studies/study_003/materials/prompts/trial_prompt_template.txt`

```
{{scenario}}

Which of the two programs would you favor?

Please respond with either "Program A" or "Program B", and briefly explain your reasoning.
```

---

### 7. **Study Config 注册**
文件: `src/core/study_config.py`

添加 study_003 的 lazy import:
```python
elif study_id == "study_003":
    from src.studies.study_003_config import Study003Config
```

---

## 🔬 验证结果

### Profile 生成测试
```bash
$ python test_study003_profiles.py
✓ Generated 10 profiles
Frame Distribution: 50% positive, 50% negative
Age Distribution: 18-52 (mean 32.4)
Education: 50% students, 50% faculty
Gender field: False (正确！)
```

### 完整 Prompt 构建测试
```bash
$ python test_study003_full_prompt.py
✓ System prompts: No gender, custom background ✓
✓ Trial prompts: Frame-specific scenarios ✓

Positive Frame: "200 people will be saved"
Negative Frame: "400 people will die"
```

---

## 📊 与其他 Studies 对比

| Feature | Study 001 (Asch) | Study 002 (Milgram) | Study 003 (Framing) |
|---------|------------------|---------------------|---------------------|
| **Profile Generation** | Default | Default | ✨ **Custom** |
| **Gender in Prompt** | Yes | Yes | **No** (忠实原文) |
| **Background Field** | Education only | Education only | **Custom text** |
| **Frame Assignment** | N/A | N/A | **50/50 in profile** |
| **Material Loading** | Fixed | Fixed | **Dynamic by frame** |

---

## 🎯 核心设计原则

### ✅ **忠实原文**
- 只生成原文报告的特征
- 未报告的数据（如 gender）→ 不生成
- 参与者分布 (students + faculty) → 70/30 建模

### ✅ **灵活扩展**
- Study config 可选择性覆盖 `generate_participant_profiles()`
- System prompt 自适应 profile 字段
- PromptBuilder 自动检测 framing_condition

### ✅ **向后兼容**
- Study 001/002 继续使用默认 profile 生成
- 所有修改都是可选的（向后兼容）
- 不破坏现有代码

---

## 🚀 使用方法

### 运行 Study 003
```bash
# 使用自定义 profiles
python run_full_benchmark.py \
  --real-llm \
  --studies study_003 \
  --n-participants 152 \
  --random-seed 42 \
  --use-cache

# 结果将正确显示:
# - 76 participants in positive_frame
# - 76 participants in negative_frame
# - University students & faculty mix
# - No gender bias in system prompts
```

### 为新 Study 添加自定义 Profiles

1. 在 `StudyXXXConfig` 中实现 `generate_participant_profiles()`:
```python
def generate_participant_profiles(self, n_participants, random_seed=None):
    # 基于 specification['participants'] 生成
    return profiles
```

2. `run_full_benchmark.py` 会自动检测并使用

---

## ✨ 关键改进

1. **Specification 驱动**: Profiles 基于 `specification.json` 生成，而非硬编码
2. **数据忠实性**: 只生成原文报告的特征（gender: null → 不生成）
3. **Frame 分配**: 在 profile 中完成，确保 50/50 split
4. **Dynamic 材料加载**: 根据 framing_condition 自动选择材料
5. **清晰的 System Prompts**: 背景描述更具体（students vs faculty）

---

## 📝 文件清单

### 修改的文件
1. `src/studies/study_003_config.py` - 添加 `generate_participant_profiles()`
2. `src/agents/llm_participant_agent.py` - 支持自定义 profiles
3. `src/agents/prompt_builder.py` - Frame-specific 材料加载
4. `run_full_benchmark.py` - 使用 study config profiles
5. `src/core/study_config.py` - 注册 study_003

### 新增的文件
1. `data/studies/study_003/materials/prompts/trial_prompt_template.txt`
2. `test_study003_profiles.py` - Profile 生成测试
3. `test_study003_full_prompt.py` - 完整 prompt 测试
4. `STUDY_003_PROFILE_IMPLEMENTATION.md` - 本文档

---

## ✅ 验证清单

- [x] Profiles 基于 specification 生成
- [x] 年龄分布符合 university population
- [x] Education 分布为 students + faculty
- [x] Gender 字段不存在（忠实原文）
- [x] Frame 分配 50/50
- [x] System prompts 无 gender
- [x] Custom background 文本
- [x] Trial prompts 加载正确的 frame 材料
- [x] Positive frame: "saved" language
- [x] Negative frame: "die" language
- [x] 向后兼容 Study 001/002

---

## 🎓 研究意义

这个实现展示了如何让 LLM benchmark **忠实于原始研究的方法学**:

1. **数据完整性**: 只模拟报告的特征
2. **透明性**: 清楚标注哪些是建模假设（70/30 student/faculty split）
3. **可重现性**: Random seed 控制 profile 生成
4. **灵活性**: 每个 study 可自定义 profile 生成逻辑

这为未来添加更多 studies 提供了清晰的模式。
