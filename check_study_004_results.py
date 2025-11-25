"""
快速测试 Study 004 - 查看 LLM 响应
"""
import json
from pathlib import Path

# 尝试读取最近的结果
result_files = sorted(Path("results").glob("full_benchmark_*.json"), key=lambda x: x.stat().st_mtime, reverse=True)

if result_files:
    latest = result_files[0]
    print(f"Reading: {latest}")
    
    try:
        with open(latest, 'r') as f:
            data = json.load(f)
        
        # 查看 study_004 的结果
        for study in data.get("studies", []):
            if study["study_id"] == "study_004":
                print("\n" + "="*80)
                print("STUDY 004 RESULTS")
                print("="*80)
                
                # 查看描述性统计
                desc_stats = study.get("descriptive_statistics", {})
                print("\nDescriptive Statistics:")
                for problem, stats in desc_stats.items():
                    print(f"\n{problem}:")
                    print(f"  n: {stats.get('n')}")
                    print(f"  bias_count: {stats.get('bias_count')}")
                    print(f"  bias_proportion: {stats.get('bias_proportion', 0):.3f}")
                    print(f"  interpretation: {stats.get('interpretation')}")
                
                # 查看推断性统计
                inf_stats = study.get("inferential_statistics", {})
                print("\nInferential Statistics:")
                for test, result in inf_stats.items():
                    if isinstance(result, dict) and 'p_value' in result:
                        print(f"\n{test}:")
                        print(f"  p_value: {result.get('p_value', 'N/A')}")
                        print(f"  significant: {result.get('significant', False)}")
                
                # 查看个别响应样本
                individual = study.get("individual_data", [])
                print(f"\n\nSample Responses (first 5):")
                for i, participant in enumerate(individual[:5]):
                    profile = participant.get("profile", {})
                    responses = participant.get("responses", [])
                    if responses:
                        print(f"\nParticipant {i} ({profile.get('assigned_problem')}):")
                        for resp in responses:
                            print(f"  Response: {resp.get('response', 'N/A')}")
                
                break
    except Exception as e:
        print(f"Error reading file: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No result files found")

