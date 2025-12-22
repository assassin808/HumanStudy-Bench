# Study Materials 手动检查清单

## 检查重点
需要验证从论文中提取的 materials 是否：
1. **内容准确** - 与原始论文中的描述一致
2. **格式正确** - 符合实验要求
3. **完整性** - 包含所有必要的实验材料

---

## Study 001 - False Consensus Effect (Ross et al., 1977)

### 关键材料（必须检查）
- ✅ **`study_1_supermarket.txt`** - Study 1 场景1：超市场景
- ✅ **`study_1_term_paper.txt`** - Study 1 场景2：学期论文场景
- ✅ **`study_1_traffic_ticket.txt`** - Study 1 场景3：交通罚单场景
- ✅ **`study_1_space_program.txt`** - Study 1 场景4：太空计划场景
- ✅ **`study_2_items.json`** - Study 2 完整问卷（34项）- **重要：检查所有34项是否完整**
- ✅ **`study_3_sign_joes.txt`** - Study 3 场景1："Eat at Joe's" 标志
- ✅ **`study_3_sign_repent.txt`** - Study 3 场景2："Repent" 标志

### 检查要点
- Study 1: 每个场景应包含两个选项（Option A/B），参与者需要选择并估计共识
- Study 2: JSON 文件应包含完整的34项问卷，每项有 option_a 和 option_b
- Study 3: 两个标志场景，参与者需要估计选择每个选项的人数比例

---

## Study 002 - Anchoring Effect (Jacowitz & Kahneman, 1995)

### 关键材料（必须检查）
- ✅ **`instructions.txt`** - 实验说明
- ✅ **`system_prompt.txt`** - 系统提示词

### 15个估计问题（检查高低锚点是否正确）
- ✅ `mississippi_high.txt` / `mississippi_low.txt` - 密西西比河长度
- ✅ `everest_high.txt` / `everest_low.txt` - 珠穆朗玛峰高度
- ✅ `meat_high.txt` / `meat_low.txt` - 美国人年均肉类消费
- ✅ `sf_nyc_high.txt` / `sf_nyc_low.txt` - 旧金山到纽约距离
- ✅ `redwood_high.txt` / `redwood_low.txt` - 最高红杉高度
- ✅ `un_members_high.txt` / `un_members_low.txt` - 联合国成员数
- ✅ `female_profs_high.txt` / `female_profs_low.txt` - 伯克利女教授数
- ✅ `chicago_high.txt` / `chicago_low.txt` - 芝加哥人口
- ✅ `telephone_high.txt` / `telephone_low.txt` - 电话发明年份
- ✅ `babies_high.txt` / `babies_low.txt` - 美国日均出生婴儿数
- ✅ `cat_speed_high.txt` / `cat_speed_low.txt` - 家猫最高速度
- ✅ `gas_usage_high.txt` / `gas_usage_low.txt` - 美国人月均用油量
- ✅ `bars_berkeley_high.txt` / `bars_berkeley_low.txt` - 伯克利酒吧数
- ✅ `colleges_ca_high.txt` / `colleges_ca_low.txt` - 加州州立大学数
- ✅ `lincoln_high.txt` / `lincoln_low.txt` - 林肯总统任期

### 检查要点
- 每个问题的高锚点和低锚点应与 specification.json 中的数值一致
- 锚点数值参考：`specification.json` 中的 `materials.questions` 部分
- 格式：应包含锚点数值和问题描述

---

## Study 003 - Framing Effect (Tversky & Kahneman, 1981)

### 关键材料（必须检查）
- ✅ **`instructions.txt`** - 实验说明
- ✅ **`system_prompt.txt`** - 系统提示词

### 11个决策问题（检查框架是否正确）
- ✅ **`problem_01.txt`** - Asian Disease (Gain Frame) - **关键：检查收益框架表述**
- ✅ **`problem_02.txt`** - Asian Disease (Loss Frame) - **关键：检查损失框架表述**
- ✅ **`problem_03.txt`** - Concurrent Decisions (Gain/Loss)
- ✅ **`problem_04.txt`** - Combined Options
- ✅ **`problem_05.txt`** - Certainty Effect (A vs B)
- ✅ **`problem_06.txt`** - Two-Stage Game (C vs D)
- ✅ **`problem_07.txt`** - Pseudocertainty Control (E vs F)
- ✅ **`problem_08.txt`** - Lost Cash ($10 bill)
- ✅ **`problem_09.txt`** - Lost Ticket ($10 ticket)
- ✅ **`problem_10_1.txt`** - Calculator Discount (Low Base Price)
- ✅ **`problem_10_2.txt`** - Calculator Discount (High Base Price)

### 检查要点
- **Problem 01 vs 02**: 必须是对同一问题的收益/损失框架表述，内容应完全对应
- 每个问题应包含两个选项（Program A vs Program B 或类似）
- 检查数值是否与论文一致（如 200人获救 vs 400人获救等）

---

## Study 004 - Representativeness Heuristic (Kahneman & Tversky, 1972)

### 关键材料（必须检查）
- ✅ **`instructions.txt`** - 实验说明
- ✅ **`system_prompt.txt`** - 系统提示词

### 9个概率判断问题
- ✅ **`birth_sequence.txt`** - 出生顺序序列概率判断
- ✅ **`program_choice.txt`** - 学生项目选择（基于班级构成）
- ✅ **`marbles_distribution.txt`** - 随机分布判断
- ✅ **`hospital_problem.txt`** - 抽样分布方差（医院问题）
- ✅ **`word_length.txt`** - 抽样分布方差（页面 vs 行）
- ✅ **`height_check.txt`** - 抽样分布方差（3 vs 1）
- ✅ **`posterior_chips.txt`** - 后验概率（忽略基础率）
- ✅ **`posterior_height_1.txt`** - 后验概率（单个案例）
- ✅ **`posterior_height_6.txt`** - 后验概率（6个样本）

### 检查要点
- 每个问题应包含统计信息和需要判断的问题
- 检查数值是否正确（如概率、比例等）
- 确保问题描述清晰，包含所有必要的背景信息

---

## Study 005 - Administrative Obedience (Meeus & Raaijmakers, 1986)

### 关键材料（必须检查）
- ✅ **`instructions.txt`** - 实验说明
- ✅ **`system_prompt.txt`** - 系统提示词
- ✅ **`remarks.txt`** - 15条压力性评论（如果单独文件）

### 实验条件材料
- ✅ **`obedience_first_trial.txt`** - 服从条件：第一次试次
- ✅ **`obedience_incremental.txt`** - 服从条件：渐进式试次
- ✅ **`control_first_trial.txt`** - 控制条件：第一次试次
- ✅ **`control_incremental.txt`** - 控制条件：渐进式试次

### 检查要点
- 15条压力性评论应与 specification.json 中的 `materials.stressful_remarks` 一致
- 检查评论的递进强度是否正确
- 检查实验者提示（prods）是否正确
- 检查同盟者抗议的描述是否准确

---

## Study 006 - Social Norms (Goldstein & Cialdini, 2008)

### 关键材料（必须检查）
- ✅ **`instructions.txt`** - 实验说明
- ✅ **`system_prompt.txt`** - 系统提示词
- ✅ **`environmental_message.txt`** - 环境信息（对照组）
- ✅ **`descriptive_norm_guest.txt`** - 描述性规范（酒店客人）
- ✅ **`descriptive_norm_room.txt`** - 描述性规范（同一房间）
- ✅ **`descriptive_norm_citizen.txt`** - 描述性规范（公民身份）
- ✅ **`descriptive_norm_gender.txt`** - 描述性规范（性别）

### 检查要点
- **环境信息**：应不包含描述性规范，只强调环境保护
- **描述性规范**：应包含"75%的客人参与"等统计信息
- **同一房间规范**：应强调"这个房间"（provincial norm）
- **公民/性别规范**：应强调身份认同（meaningful identity）
- 检查百分比数值是否正确（75%, 76%, 74%等）

---

## 通用检查项

### 所有 study 都需要检查：
1. **`instructions.txt`** - 实验说明是否清晰、完整
2. **`system_prompt.txt`** - 系统提示词是否符合实验要求
3. **文件编码** - 确保 UTF-8 编码，无乱码
4. **格式一致性** - 同一 study 内的材料格式应一致
5. **数值准确性** - 所有数字、百分比应与论文一致

### 建议检查顺序：
1. **先检查关键材料**（instructions, system_prompt）
2. **再检查核心实验材料**（问题、场景等）
3. **最后检查辅助材料**（如果有）

---

## 快速检查脚本

可以运行以下命令快速查看所有 materials 文件：

```bash
# 查看所有 materials 文件列表
find data/studies -name "*.txt" -o -name "*.json" | grep materials | sort

# 统计每个 study 的 materials 数量
for study in study_001 study_002 study_003 study_004 study_005 study_006; do
  echo "$study: $(find data/studies/$study/materials -type f | wc -l) files"
done
```

