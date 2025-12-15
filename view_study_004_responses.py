"""
临时脚本：直接在实验结束时保存并查看响应
"""
import json
import sys
from pathlib import Path

# 导入必要模块
sys.path.insert(0, str(Path.cwd()))

from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.core.study_config import get_study_config
from src.agents.prompt_builder import get_prompt_builder

# 设置API密钥
import os
os.environ['OPENROUTER_API_KEY'] = open('.env').read().split('OPENROUTER_API_KEY=')[1].split('\n')[0]

# 加载study
benchmark = HumanStudyBench("data")
study = benchmark.load_study("study_004")
study_path = study.materials_path.parent
study_config = get_study_config("study_004", study_path, study.specification)

# 创建小规模实验（9人，每个条件1人）
n_participants = 9
profiles = study_config.generate_participant_profiles(n_participants, random_seed=42)
builder = study_config.get_prompt_builder()
instructions = builder.get_instructions()
trials = study_config.create_trials()

# 创建参与者池
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=n_participants,
    use_real_llm=True,
    model="mistralai/mistral-nemo",
    random_seed=42,
    num_workers=3,
    profiles=profiles,
    prompt_builder=builder
)

print("Running mini-experiment...")
raw_results = pool.run_experiment(trials, instructions, prompt_builder=builder)

# 聚合结果
results = study_config.aggregate_results(raw_results)

# 打印详细响应
print("\n" + "="*80)
print("DETAILED RESPONSES")
print("="*80)

for i, participant in enumerate(raw_results.get("individual_data", [])):
    profile = participant.get("profile", {})
    problem = profile.get("assigned_problem", "unknown")
    responses = participant.get("responses", [])
    
    print(f"\n--- Participant {i} ({problem}) ---")
    for resp in responses:
        response_text = resp.get("response", "N/A")
        print(f"Response: {response_text}")

# 打印聚合统计
print("\n" + "="*80)
print("AGGREGATED STATISTICS")
print("="*80)

desc_stats = results.get("descriptive_statistics", {})
for problem, stats in desc_stats.items():
    print(f"\n{problem}:")
    print(f"  Total: {stats.get('n', 0)}")
    print(f"  Bias count: {stats.get('bias_count', 0)}")
    print(f"  Bias proportion: {stats.get('bias_proportion', 0):.2%}")

# 保存到文件
output_file = "study_004_detailed_responses.json"

# 转换numpy类型为python原生类型
def convert_types(obj):
    import numpy as np
    if isinstance(obj, dict):
        return {k: convert_types(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_types(v) for v in obj]
    elif isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    else:
        return obj

safe_results = convert_types(results)
safe_raw = convert_types(raw_results)

with open(output_file, 'w') as f:
    json.dump({
        "aggregated": safe_results,
        "raw": safe_raw
    }, f, indent=2)

print(f"\n✅ Saved to {output_file}")



