# Summary: Your Two Questions Answered

## ✅ Question 1: Type 2 测试应该用连续分数，差距大时为 0 分

**问题**: 之前的分档评分（0.7/0.8/0.9/1.0）不满意，希望差距大就是 0 分

**解决方案**: 已实现连续线性评分

### 新的评分公式

```python
# Cohen's h 测试 (D1, D2)
score = max(0.0, 1.0 - cohens_h / 0.8)

# 绝对差异测试 (D3)
score = max(0.0, 1.0 - abs_diff / 0.3)
```

### 效果对比

| Cohen's h | 旧评分 | 新评分 | 变化 |
|---|---|---|---|
| 0.00 | 1.0 | 1.000 | 完美匹配 |
| 0.10 | 1.0 | 0.875 | 更精确 |
| 0.20 | 0.9 | 0.750 | 更严格 |
| 0.40 | 0.9 | 0.500 | ⚠️ 显著降低 |
| 0.60 | 0.8 | 0.250 | ⚠️ 大幅降低 |
| 0.80 | 0.7 | **0.000** | ✅ 真正的 0 分！ |
| 1.00 | 0.7 | **0.000** | ✅ 真正的 0 分！ |

**关键改进**:
- ✅ h ≥ 0.8 → 分数 = 0.0（差距大就是 0 分）
- ✅ 分数随差距**连续平滑变化**
- ✅ 没有阶梯效应（h=0.49 vs h=0.51 不会突然跳档）
- ✅ 更好地奖励高相似度

---

## ✅ Question 2: 是否分别保留 P 测试和 D 测试的数据

**问题**: 需要单独保留 phenomenon 和 data 的测试结果

**解决方案**: 已实现分离存储

### 返回结构

```python
results = {
    "study_id": "study_003",
    "total_score": 0.85,           # 总分
    "passed": True,
    
    # 全部测试（合并）
    "tests": {
        "P1": {...},
        "P2": {...},
        "D1": {...},
        "D2": {...},
        "D3": {...}
    },
    
    # 🆕 单独的现象级测试
    "phenomenon_tests": {
        "P1": {
            "score": 1.0,
            "weight": 2.0,
            "critical": True,
            "passed": True,
            "details": {...}
        },
        "P2": {
            "score": 1.0,
            "weight": 2.0,
            "critical": True,
            "passed": True,
            "details": {...}
        }
    },
    
    # 🆕 单独的数据级测试
    "data_tests": {
        "D1": {
            "score": 0.945,
            "weight": 1.0,
            "critical": False,
            "passed": True,
            "details": {
                "cohens_h": 0.044,
                "match_quality": "excellent",
                ...
            }
        },
        "D2": {...},
        "D3": {...}
    },
    
    # 🆕 分别的平均分
    "phenomenon_score": 1.0,       # P 测试平均分
    "data_score": 0.909,           # D 测试平均分
    
    # 🆕 权重细节
    "total_weight": 6.5,
    "phenomenon_weight": 4.0,      # P 测试总权重
    "data_weight": 2.5             # D 测试总权重
}
```

### 使用示例

```python
# 获取所有现象级测试
phenomenon_results = results["phenomenon_tests"]
for test_id, test_data in phenomenon_results.items():
    print(f"{test_id}: {test_data['score']}")

# 获取所有数据级测试
data_results = results["data_tests"]
for test_id, test_data in data_results.items():
    print(f"{test_id}: Cohen's h = {test_data['details']['cohens_h']}")

# 比较两类测试的表现
print(f"Phenomenon score: {results['phenomenon_score']:.1%}")
print(f"Data score: {results['data_score']:.1%}")
```

---

## 📊 实际运行示例

```bash
$ python test_two_tier_evaluation.py

============================================================
TEST 3: Data-Level Tests (Continuous Scoring)
============================================================

Good match
  D1: agent=0.70, human=0.72
    Cohen's h = 0.044 → Excellent
    Score = max(0, 1 - 0.044/0.80) = 0.945  ✅ 连续评分
  
  D2: agent=0.25, human=0.22
    Cohen's h = 0.071 → Excellent
    Score = max(0, 1 - 0.071/0.80) = 0.912  ✅ 连续评分
  
  D3: agent=0.45, human=0.50
    Difference = 0.050 → Excellent
    Score = max(0, 1 - 0.050/0.30) = 0.833  ✅ 连续评分
  
  Data-level score: 90.9% (weighted average)

Scenario 5: Large Difference Agent (h≥0.8)
  D1: h=0.8 → score=0.0  ✅ 差距大就是 0 分！
  D2: h=0.8 → score=0.0  ✅ 差距大就是 0 分！
  D3: diff≥0.3 → score=0.0  ✅ 差距大就是 0 分！
  
  Total score: 61.5%
  Result: ❌ FAIL
```

---

## 🎯 总结

### Question 1 ✅
- **实现了连续评分**：`score = max(0, 1 - h/0.8)`
- **差距大就是 0 分**：h ≥ 0.8 → score = 0.0
- **平滑变化**：没有阶梯效应
- **更严格**：要求更高的数据相似度

### Question 2 ✅
- **分别存储**：`phenomenon_tests` 和 `data_tests`
- **分别计算平均分**：`phenomenon_score` 和 `data_score`
- **保留合并结果**：`tests` 仍包含所有测试
- **权重明确**：`phenomenon_weight` 和 `data_weight`

---

## 📂 修改的文件

1. **`src/evaluation/scorer.py`**
   - 改用连续评分公式
   - 添加 `phenomenon_tests` 和 `data_tests` 分离
   - 添加 `phenomenon_score` 和 `data_score`

2. **`test_two_tier_evaluation.py`**
   - 更新测试以验证连续评分
   - 添加 h≥0.8 → score=0 的场景测试

3. **`docs/CONTINUOUS_SCORING_UPDATE.md`**
   - 完整文档说明新系统

---

## ✅ 测试结果

```
✅ Cohen's h calculations verified
✅ Phenomenon-level tests verified
✅ Data-level tests verified (continuous scoring)
✅ Integrated scoring verified (continuous)
✅ ALL TESTS PASSED
```

**Status**: 生产就绪 🚀
