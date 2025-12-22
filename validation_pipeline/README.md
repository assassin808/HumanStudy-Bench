# Validation Pipeline

验证研究实现是否与原始论文一致。

## 快速开始

```bash
# 安装依赖
pip install -r validation_pipeline/requirements.txt

# 配置API密钥（在项目根目录创建 .env 文件）
echo "GOOGLE_API_KEY=your_key_here" > .env

# 运行验证
python validation_pipeline/run_validation.py study_001
```

## 输入文件

Pipeline 自动从以下位置读取文件：

### 必需文件位置
```
data/studies/{study_id}/
├── *.pdf                          # 原始论文PDF（自动查找）
├── *.md                           # 论文摘要markdown（自动查找）
├── STUDY_INFO.md                  # 研究信息
├── ground_truth.json              # 人类数据真值
├── metadata.json                  # 研究元数据
└── specification.json             # 实验规范

src/studies/{study_id}_config.py  # 研究配置代码（可选）
```

### 输入文件说明

| 文件 | 用途 |
|------|------|
| `*.pdf` | 原始研究论文，用于提取实验描述 |
| `*.md` | 论文摘要/笔记 |
| `STUDY_INFO.md` | 研究基本信息 |
| `ground_truth.json` | 人类参与者的真实数据 |
| `metadata.json` | 研究元数据（参与者信息等） |
| `specification.json` | 实验规范（材料、条件等） |
| `{study_id}_config.py` | 研究实现代码 |

## 输出文件

验证结果保存在：

```
validation_pipeline/outputs/
├── {study_id}_validation_{timestamp}.json      # 完整验证结果（JSON）
└── {study_id}_validation_summary_{timestamp}.md  # 人类可读摘要（Markdown）
```

### 输出内容

**JSON文件** 包含4个验证结果：
- `completeness`: 实验完整性检查
- `consistency`: 实验设置一致性检查
- `data_validation`: 数据准确性验证
- `checklist`: 验证清单

**Markdown摘要** 包含：
- 各验证项的分数
- 关键问题列表
- 整体评估

## 使用方法

### 基本用法
```bash
python validation_pipeline/run_validation.py study_001
```

### 自定义路径
```bash
python validation_pipeline/run_validation.py study_001 \
    --study-path data/studies/study_001 \
    --config-path src/studies/study_001_config.py \
    --output-dir validation_pipeline/outputs
```

### 批量运行
```bash
for study in study_002 study_003 study_004 study_005 study_006; do
  python validation_pipeline/run_validation.py $study
done
```

## Pipeline 架构

```
DocumentLoader
    ↓
加载文件 → documents = {
    pdfs: {...},
    study_info: "...",
    markdown: {...},
    json: {ground_truth.json, metadata.json, specification.json},
    config_code: "..."
}
    ↓
┌─────────────────────────────────────────────────┐
│ 1. ExperimentCompletenessAgent                  │
│    输入: pdfs, study_info, specification.json, │
│          config_code                            │
│    输出: experiments_in_paper,                 │
│          completeness_summary                   │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ 2. ExperimentConsistencyAgent                   │
│    输入: pdfs, study_info, specification.json,  │
│          metadata.json, config_code             │
│    输出: comparison_by_aspect,                  │
│          consistency_summary                   │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ 3. DataValidationAgent                          │
│    输入: pdfs, ground_truth.json,              │
│          metadata.json                          │
│    输出: participant_data_validation,          │
│          experimental_data_validation,          │
│          validation_summary                     │
└─────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────┐
│ 4. ChecklistGeneratorAgent                      │
│    输入: documents + previous_results          │
│         (completeness, consistency,            │
│          data_validation)                       │
│    输出: checklist_sections,                   │
│          checklist_summary                     │
└─────────────────────────────────────────────────┘
    ↓
保存结果 → JSON + Markdown
```

## Agent 输入输出详情

### 1. ExperimentCompletenessAgent
**输入:**
- `documents["pdfs"]` - 论文PDF文本
- `documents["study_info"]` - STUDY_INFO.md内容
- `documents["json"]["specification.json"]` - 实验规范
- `documents["config_code"]` - 实现代码

**输出:**
```json
{
  "agent": "ExperimentCompletenessAgent",
  "status": "completed",
  "results": {
    "experiments_in_paper": [...],
    "completeness_summary": {
      "total_experiments": 0,
      "included_experiments": 0,
      "completeness_score": 0.0
    }
  }
}
```

### 2. ExperimentConsistencyAgent
**输入:**
- `documents["pdfs"]` - 论文PDF文本
- `documents["study_info"]` - STUDY_INFO.md内容
- `documents["json"]["specification.json"]` - 实验规范
- `documents["json"]["metadata.json"]` - 元数据
- `documents["config_code"]` - 实现代码

**输出:**
```json
{
  "agent": "ExperimentConsistencyAgent",
  "status": "completed",
  "results": {
    "comparison_by_aspect": {
      "participants": {...},
      "procedure": {...},
      "materials": {...}
    },
    "consistency_summary": {
      "consistency_score": 0.0
    }
  }
}
```

### 3. DataValidationAgent
**输入:**
- `documents["pdfs"]` - 论文PDF文本
- `documents["json"]["ground_truth.json"]` - 人类数据
- `documents["json"]["metadata.json"]` - 元数据

**输出:**
```json
{
  "agent": "DataValidationAgent",
  "status": "completed",
  "results": {
    "participant_data_validation": {...},
    "experimental_data_validation": [...],
    "validation_summary": {
      "data_accuracy_score": 0.0
    }
  }
}
```

### 4. ChecklistGeneratorAgent
**输入:**
- `documents` - 所有文档
- `previous_results` - 前3个agent的结果

**输出:**
```json
{
  "agent": "ChecklistGeneratorAgent",
  "status": "completed",
  "results": {
    "checklist_sections": [
      {"section_id": "completeness", "items": [...]},
      {"section_id": "consistency", "items": [...]},
      {"section_id": "data_accuracy", "items": [...]}
    ],
    "checklist_summary": {...}
  }
}
```

## 配置

- **API密钥**: 在项目根目录创建 `.env` 文件，添加 `GOOGLE_API_KEY=your_key`
- **默认模型**: `models/gemini-3-flash-preview`
- **输出目录**: `validation_pipeline/outputs`

## 程序化使用

```python
from validation_pipeline.pipeline import ValidationPipeline
from pathlib import Path

pipeline = ValidationPipeline()
results = pipeline.validate_study("study_001")
```
