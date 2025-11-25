"""
运行 Study_006 (Social Norms and Conservation) 使用真实 LLM

使用方法:
    python run_study_006.py --n-participants 50 --model mistralai/mistral-nemo
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.evaluation.scorer import Scorer
from src.core.study_config import get_study_config

# Import study configurations
import src.studies


def main():
    parser = argparse.ArgumentParser(description="运行 Study_006 使用真实 LLM")
    parser.add_argument("--n-participants", type=int, default=50,
                       help="参与者数量（默认：50，原始研究为1595）")
    parser.add_argument("--model", type=str, default="mistralai/mistral-nemo",
                       help="模型名称（默认：mistralai/mistral-nemo）")
    parser.add_argument("--random-seed", type=int, default=42,
                       help="随机种子（默认：42）")
    parser.add_argument("--num-workers", type=int, default=4,
                       help="并行worker数量（默认：4）")
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print(" " * 25 + "Study_006 - Social Norms and Conservation")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Model: {args.model}")
    print(f"Participants: {args.n_participants}")
    print(f"Random Seed: {args.random_seed}")
    print(f"Workers: {args.num_workers}")
    print("="*80)
    
    # Check API key
    api_key = os.environ.get('OPENROUTER_API_KEY') or os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("\n❌ 错误: 未找到API Key")
        print("请设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY 环境变量")
        return
    
    # Load study
    print("\n[1/5] 加载Study_006...")
    benchmark = HumanStudyBench("data")
    study = benchmark.load_study("study_006")
    print(f"  ✓ Study: {study.metadata['title']}")
    print(f"  ✓ Author: {study.metadata['authors'][0]} ({study.metadata['year']})")
    print(f"  ✓ Domain: {study.metadata['domain']}")
    
    # Get study config
    print("\n[2/5] 初始化Study配置...")
    study_path = study.materials_path.parent
    study_config = get_study_config("study_006", study_path, study.specification)
    prompt_builder = study_config.get_prompt_builder()
    instructions = prompt_builder.get_instructions()
    trials = study_config.create_trials()
    
    print(f"  ✓ Trials: {len(trials)}")
    print(f"  ✓ Instructions loaded: {len(instructions)} 字符")
    
    # Generate participant profiles
    print(f"\n[3/5] 生成 {args.n_participants} 个参与者profiles...")
    profiles = study_config.generate_participant_profiles(
        args.n_participants, 
        random_seed=args.random_seed
    )
    
    # 统计各条件的分布
    from collections import Counter
    condition_counts = Counter(p['message_condition'] for p in profiles)
    print("  ✓ 条件分布:")
    for condition, count in sorted(condition_counts.items()):
        print(f"    - {condition}: {count}")
    
    # Create participant pool - directly create agents with study-specific profiles
    print(f"\n[4/5] 创建LLM参与者池...")
    from src.agents.llm_participant_agent import LLMParticipantAgent
    
    # Fix specification for ParticipantPool initialization
    # (it expects numeric values, not None)
    import copy
    spec_for_pool = copy.deepcopy(study.specification)
    participants_spec = spec_for_pool.get('participants', {})
    
    # Fix gender_distribution
    if participants_spec.get('gender_distribution', {}).get('male') is None:
        participants_spec['gender_distribution'] = {'male': 50, 'female': 50}
    
    # Fix age_mean and age_sd if None
    if participants_spec.get('age_mean') is None:
        age_range = participants_spec.get('age_range', [18, 80])
        participants_spec['age_mean'] = sum(age_range) / 2
    if participants_spec.get('age_sd') is None:
        participants_spec['age_sd'] = 15.0
    
    # Create pool with fixed specification and pass our profiles
    pool = ParticipantPool(
        study_specification=spec_for_pool,
        n_participants=args.n_participants,
        use_real_llm=True,
        model=args.model,
        api_key=api_key,
        random_seed=args.random_seed,
        num_workers=args.num_workers,
        prompt_builder=prompt_builder,
        profiles=profiles  # Pass our study-specific profiles
    )
    
    print(f"  ✓ 创建了 {len(pool.participants)} 个LLM agents")
    
    # Run experiment
    print(f"\n[5/5] 运行实验（这可能需要几分钟）...")
    start_time = time.time()
    
    results = pool.run_experiment(trials, instructions)
    
    elapsed_time = time.time() - start_time
    print(f"  ✓ 实验完成！耗时: {elapsed_time:.1f} 秒")
    
    # Aggregate results
    print("\n" + "="*80)
    print("结果聚合和分析")
    print("="*80)
    
    # Convert results to format expected by aggregate_results
    # results from pool.run_experiment() returns: {'individual_data': [...], 'descriptive_statistics': {...}, ...}
    # individual_data contains participant summaries with 'responses' key
    
    individual_data = results.get('individual_data', [])
    
    results_for_aggregation = {
        'participants': []
    }
    
    for i, participant_data in enumerate(individual_data):
        # Get profile from the agent
        agent = pool.participants[i]
        profile = agent.profile
        
        # Extract trial_responses from participant_data
        # participant_data is from agent.get_summary(), which has 'responses' key
        trial_responses = participant_data.get('responses', [])
        
        # Convert responses format to trial_responses format expected by aggregate_results
        # responses format: [{'trial_number': 1, 'response': 'A) Participate', ...}, ...]
        # trial_responses format: [{'response': 'A) Participate', ...}, ...]
        formatted_responses = []
        for resp in trial_responses:
            formatted_responses.append({
                'response': resp.get('response', ''),
                'trial_info': {'trial_number': resp.get('trial_number', 1)}
            })
        
        participant_result = {
            'participant_id': i,
            'message_condition': profile.get('message_condition', 'unknown'),
            'trial_responses': formatted_responses
        }
        results_for_aggregation['participants'].append(participant_result)
    
    aggregated = study_config.aggregate_results(results_for_aggregation)
    
    print("\n【描述性统计】")
    n_total = aggregated.get('n_total', len(results.get('participants', [])))
    print(f"总参与者数: {n_total}")
    print("\n各条件的毛巾重复使用率:")
    for condition in ['environmental', 'descriptive_norm_guest', 'descriptive_norm_room', 
                      'descriptive_norm_citizen', 'descriptive_norm_gender']:
        if condition in aggregated.get('by_condition', {}):
            cond_data = aggregated['by_condition'][condition]
            rate = cond_data.get('towel_reuse_rate', 0.0)
            n = cond_data.get('n', 0)
            count = cond_data.get('towel_reuse_count', 0)
            print(f"  {condition:30s}: {rate:.1%} ({count}/{n})")
    
    if 'descriptive_norms_combined' in aggregated:
        combined = aggregated['descriptive_norms_combined']
        print(f"\n  所有描述性规范条件合并: {combined.get('towel_reuse_rate', 0.0):.1%} ({combined.get('towel_reuse_count', 0)}/{combined.get('n', 0)})")
    
    # Score results
    print("\n" + "="*80)
    print("评估结果")
    print("="*80)
    
    scorer = Scorer()
    score_result = scorer.score_study(study, {
        'individual_data': results.get('participants', []),
        'aggregated': aggregated,
        'descriptive_statistics': {
            'by_condition': aggregated['by_condition']
        }
    })
    
    phenomenon = score_result.get('phenomenon_result', {})
    data = score_result.get('data_result', {})
    
    print("\n【现象级测试 (Phenomenon-Level)】")
    print(f"  通过: {phenomenon.get('passed', False)}")
    print(f"  分数: {phenomenon.get('score', 0.0):.2f}")
    print(f"  通过测试: {phenomenon.get('passed_tests', 0)}/{phenomenon.get('total_tests', 0)}")
    
    if 'tests' in phenomenon:
        print("\n  详细测试结果:")
        for test_id, test_result in phenomenon['tests'].items():
            status = "✓ PASS" if test_result.get('passed') else "✗ FAIL"
            print(f"    {test_id}: {status}")
            if 'details' in test_result:
                details = test_result['details']
                if 'error' in details:
                    print(f"      错误: {details['error']}")
                elif 'direction' in details:
                    print(f"      方向: {details.get('direction', 'N/A')}")
                    print(f"      正确方向: {details.get('correct_direction', 'N/A')}")
    
    print("\n【数据级测试 (Data-Level)】")
    print(f"  通过: {data.get('passed', False)}")
    print(f"  分数: {data.get('score', 0.0):.2f}")
    print(f"  通过测试: {data.get('passed_tests', 0)}/{data.get('total_tests', 0)}")
    
    print(f"\n【总体分数】")
    print(f"  Overall Score: {score_result.get('overall_score', 0.0):.2f}")
    
    # Save results
    output_dir = Path("results/study_006")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"results_{timestamp}.json"
    
    output_data = {
        "study_id": "study_006",
        "timestamp": timestamp,
        "model": args.model,
        "n_participants": args.n_participants,
        "random_seed": args.random_seed,
        "elapsed_time_seconds": elapsed_time,
        "aggregated_results": aggregated,
        "score_result": score_result,
        "raw_results": results
    }
    
    with open(output_file, 'w') as f:
        json.dump(output_data, f, indent=2, default=str)
    
    print(f"\n✓ 结果已保存到: {output_file}")
    
    print("\n" + "="*80)
    print("完成！")
    print("="*80)


if __name__ == "__main__":
    main()

