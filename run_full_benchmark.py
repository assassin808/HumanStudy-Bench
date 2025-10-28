"""
完整运行 HumanStudyBench - 所有研究的完整评估

这个脚本会：
1. 加载所有可用的研究
2. 使用 LLM participant agents 运行每个研究
3. 评分和验证
4. 生成完整的 benchmark 报告

使用方法:
    # 模拟模式（快速测试，不消耗 API）
    python run_full_benchmark.py
    
    # 真实 LLM 模式（需要 API key）
    export OPENROUTER_API_KEY="your-key"
    python run_full_benchmark.py --real-llm --model mistralai/mistral-nemo
"""

import argparse
import json
import time
from datetime import datetime
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.agents.prompt_builder import get_prompt_builder
from src.evaluation.scorer import Scorer
from src.core.study_config import get_study_config


def _slugify(text: str) -> str:
    return ''.join(c if c.isalnum() else '_' for c in text)


def run_study(study_id, benchmark, use_real_llm=False, model="mistralai/mistral-nemo", 
              n_participants=None, random_seed=42, num_workers: int = None,
              use_cache: bool = False, cache_dir: str = "results/cache"):
    """
    运行单个研究
    
    Args:
        study_id: 研究 ID (e.g., "study_001")
        benchmark: HumanStudyBench 实例
        use_real_llm: 是否使用真实 LLM API
        model: 模型名称
        n_participants: 参与者数量（None = 使用 specification 中的数量）
        random_seed: 随机种子（保证可复现）
        num_workers: 并行 worker 数量
        use_cache: 是否启用缓存（如存在则加载缓存，否则运行并保存）
        cache_dir: 缓存目录
    
    Returns:
        Dict with study results and evaluation
    """
    print("\n" + "="*80)
    print(f"Running {study_id}")
    print("="*80)

    # Load study
    study = benchmark.load_study(study_id)
    print(f"Study: {study.metadata['title']}")
    print(f"Author: {study.metadata['authors'][0]} ({study.metadata['year']})")
    print(f"Domain: {study.metadata['domain']}")
    print(f"Difficulty: {study.metadata['difficulty']}")

    # Create prompt builder
    builder = get_prompt_builder(study_id)
    instructions = builder.get_instructions()

    # Determine participant count
    if n_participants is None:
        n_participants = study.specification['participants']['n']

    print(f"\nParticipants: {n_participants}")
    print(f"Model: {model} (Real LLM: {use_real_llm})")

    # Get study config (encapsulates all study-specific logic)
    # Study object doesn't have path, reconstruct from materials_path
    study_path = study.materials_path.parent  # materials_path = study_path / "materials"
    study_config = get_study_config(study_id, study_path, study.specification)
    print(f"Config: {study_config}")

    # Create trials using study config
    trials = study_config.create_trials()
    print(f"Trials: {len(trials)}")

    # Cache setup
    start_time = time.time()
    model_slug = _slugify(model)
    cache_path = Path(cache_dir) / f"{study_id}__{model_slug}__n{n_participants}__seed{random_seed}.json"
    raw_results = None
    if use_cache and cache_path.exists():
        print(f"\n🔄 Loading cached raw results from {cache_path}")
        try:
            with open(cache_path, 'r') as f:
                cached = json.load(f)
            raw_results = cached.get('raw_results') or cached
        except Exception as e:
            print(f"⚠️  Failed to load cache: {e} (will run experiment)")

    # Create participant pool
    pool = ParticipantPool(
        study_specification=study.specification,
        n_participants=n_participants,
        use_real_llm=use_real_llm,
        model=model,
        random_seed=random_seed,
        num_workers=num_workers
    )

    # Run experiment
    if raw_results is None:
        # Ensure cache dir exists if needed
        if use_cache:
            Path(cache_dir).mkdir(parents=True, exist_ok=True)

        raw_results = pool.run_experiment(trials, instructions, prompt_builder=builder)

        # Save cache
        if use_cache:
            payload = {
                "version": 1,
                "study_id": study_id,
                "model": model,
                "n_participants": n_participants,
                "random_seed": random_seed,
                "raw_results": raw_results,
            }
            with open(cache_path, 'w') as f:
                json.dump(payload, f)
            print(f"💾 Cached raw results to {cache_path}")

    # Apply study-specific result aggregation
    results = study_config.aggregate_results(raw_results)

    elapsed = time.time() - start_time
    print(f"\n⏱️  Experiment completed in {elapsed:.1f}s")

    # Evaluate with scorer (may use custom_scoring from config)
    scorer = Scorer()
    custom_scores = study_config.custom_scoring(results, study.ground_truth)
    if custom_scores:
        print(f"\n📊 Custom scoring applied: {custom_scores}")

    score_result = scorer.score_study(study, results)

    # Display results
    print("\n" + "-"*80)
    print("RESULTS")
    print("-"*80)
    
    # Get main metric (varies by study type)
    if study_id == "study_001":  # Asch
        conformity_stats = results.get("descriptive_statistics", {}).get(
            "conformity_rate", {}
        ).get("experimental", {})
        
        if conformity_stats:
            print(f"Conformity Rate: {conformity_stats.get('mean', 0):.1%} (SD={conformity_stats.get('sd', 0):.3f})")
            print(f"Range: [{conformity_stats.get('min', 0):.1%}, {conformity_stats.get('max', 0):.1%}]")
            print(f"Never conformed: {conformity_stats.get('never_conformed', 0)}/{n_participants}")
            print(f"Always conformed: {conformity_stats.get('always_conformed', 0)}/{n_participants}")
    
    elif study_id == "study_002":  # Milgram
        shock_stats = results.get("descriptive_statistics", {}).get(
            "shock_level", {}
        ).get("experimental", {})
        
        if shock_stats:
            print(f"Mean Max Shock: {shock_stats.get('mean', 0):.1f} (SD={shock_stats.get('sd', 0):.2f})")
            print(f"Obedience Rate: {shock_stats.get('obedience_rate', 0):.1%}")
            print(f"Went to 450V: {shock_stats.get('obedient_count', 0)}/{n_participants}")
    
    # Scoring
    print("\n" + "-"*80)
    print("VALIDATION")
    print("-"*80)
    
    passed_tests = sum(1 for t in score_result['tests'].values() if t['status'] == 'PASS')
    total_tests = len(score_result['tests'])
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    print(f"Overall score: {score_result['total_score']:.1%}")
    
    for test_id, test_result in score_result['tests'].items():
        status_symbol = "✅" if test_result['status'] == "PASS" else "❌"
        print(f"  {status_symbol} {test_id}: {test_result['status']} (score: {test_result['score']:.2f})")
    
    # Pass/fail evaluation
    pass_eval = study.evaluate_pass_status(score_result['total_score'])
    
    print(f"\n{'='*80}")
    print(f"Grade: {pass_eval['grade'].upper()}")
    print(f"Status: {'✅ PASSED' if pass_eval['passed'] else '❌ FAILED'}")
    print(f"Threshold: {pass_eval['threshold']:.0%}")
    print(f"Score: {score_result['total_score']:.1%}")
    print(f"{'='*80}")
    
    return {
        "study_id": study_id,
        "title": study.metadata['title'],
        "n_participants": n_participants,
        "model": model,
        "use_real_llm": use_real_llm,
        "elapsed_time": elapsed,
        "score": score_result['total_score'],
        "grade": pass_eval['grade'],
        "passed": pass_eval['passed'],
        "tests_passed": passed_tests,
        "tests_total": total_tests,
        "results": results,
        "score_result": score_result
    }


def main():
    parser = argparse.ArgumentParser(description="运行完整的 HumanStudyBench")
    parser.add_argument("--real-llm", action="store_true", 
                       help="使用真实 LLM API（需要设置 OPENROUTER_API_KEY 或 OPENAI_API_KEY）")
    parser.add_argument("--model", type=str, default="mistralai/mistral-nemo",
                       help="模型名称 (默认: mistralai/mistral-nemo)")
    parser.add_argument("--n-participants", type=int, default=None,
                       help="参与者数量（默认：使用各研究 specification 中的数量）")
    parser.add_argument("--studies", type=str, nargs="+", default=None,
                       help="指定运行的研究 ID（默认：运行所有）")
    parser.add_argument("--random-seed", type=int, default=42,
                       help="随机种子，用于可复现性（默认：42）")
    parser.add_argument("--num-workers", type=int, default=None,
                       help="并行 worker 数（仅在 --real-llm 时生效，默认: min(8,n_participants))")
    parser.add_argument("--use-cache", action="store_true", help="启用结果缓存（优先加载缓存，否则运行后保存）")
    parser.add_argument("--cache-dir", type=str, default="results/cache", help="缓存目录")
    
    args = parser.parse_args()
    
    # Banner
    print("\n" + "="*80)
    print(" "*20 + "HumanStudyBench - Full Benchmark Run")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {'Real LLM' if args.real_llm else 'Simulation'}")
    print(f"Model: {args.model}")
    print(f"Random Seed: {args.random_seed}")
    print("="*80)
    
    # Load benchmark
    benchmark = HumanStudyBench("data")
    
    # Get list of studies to run
    if args.studies:
        study_ids = args.studies
    else:
        # Get all studies from registry
        study_ids = [s['id'] for s in benchmark.registry['studies'] if s.get('status') == 'active']
    
    print(f"\nStudies to run: {', '.join(study_ids)}")
    
    # Run each study
    all_results = []
    
    for study_id in study_ids:
        try:
            result = run_study(
                study_id=study_id,
                benchmark=benchmark,
                use_real_llm=args.real_llm,
                model=args.model,
                n_participants=args.n_participants,
                random_seed=args.random_seed,
                num_workers=args.num_workers,
                use_cache=args.use_cache,
                cache_dir=args.cache_dir
            )
            
            if result:
                all_results.append(result)
        
        except Exception as e:
            print(f"\n❌ Error running {study_id}: {e}")
            import traceback
            traceback.print_exc()
    
    # Summary report
    print("\n" + "="*80)
    print(" "*25 + "BENCHMARK SUMMARY")
    print("="*80)
    
    if not all_results:
        print("No studies completed successfully.")
        return
    
    total_studies = len(all_results)
    passed_studies = sum(1 for r in all_results if r['passed'])
    total_time = sum(r['elapsed_time'] for r in all_results)
    avg_score = sum(r['score'] for r in all_results) / total_studies
    
    print(f"\nStudies run: {total_studies}")
    print(f"Passed: {passed_studies}/{total_studies} ({passed_studies/total_studies:.0%})")
    print(f"Average score: {avg_score:.1%}")
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f}min)")
    
    print("\n" + "-"*80)
    print("Per-study results:")
    print("-"*80)
    
    for result in all_results:
        status_symbol = "✅" if result['passed'] else "❌"
        print(f"{status_symbol} {result['study_id']:12s} | Score: {result['score']:5.1%} | "
              f"Grade: {result['grade']:12s} | Tests: {result['tests_passed']}/{result['tests_total']}")
    
    # Benchmark-level pass/fail
    print("\n" + "="*80)
    
    # Benchmark pass criteria (from HumanStudyBench class)
    BENCHMARK_PASS_THRESHOLD = 0.60
    MIN_PASS_RATE = 0.50
    
    benchmark_passed = (
        avg_score >= BENCHMARK_PASS_THRESHOLD and 
        passed_studies / total_studies >= MIN_PASS_RATE
    )
    
    if benchmark_passed:
        print("✅ BENCHMARK PASSED")
    else:
        print("❌ BENCHMARK FAILED")
    
    print(f"   Average Score: {avg_score:.1%} (threshold: {BENCHMARK_PASS_THRESHOLD:.0%})")
    print(f"   Pass Rate: {passed_studies}/{total_studies} ({passed_studies/total_studies:.0%}, threshold: {MIN_PASS_RATE:.0%})")
    print("="*80)
    
    # Save results
    output_dir = Path("results")
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"full_benchmark_{timestamp}.json"
    
    # Prepare serializable data
    save_data = {
        "timestamp": timestamp,
        "model": args.model,
        "use_real_llm": args.real_llm,
        "random_seed": args.random_seed,
        "summary": {
            "total_studies": total_studies,
            "passed_studies": passed_studies,
            "pass_rate": passed_studies / total_studies,
            "average_score": avg_score,
            "total_time": total_time,
            "benchmark_passed": benchmark_passed
        },
        "studies": [
            {
                "study_id": r['study_id'],
                "title": r['title'],
                "score": r['score'],
                "grade": r['grade'],
                "passed": r['passed'],
                "tests_passed": r['tests_passed'],
                "tests_total": r['tests_total'],
                "elapsed_time": r['elapsed_time']
            }
            for r in all_results
        ]
    }
    
    with open(output_file, 'w') as f:
        json.dump(save_data, f, indent=2)
    
    print(f"\nResults saved to: {output_file}")
    
    # Also save detailed results
    detailed_file = output_dir / f"full_benchmark_detailed_{timestamp}.json"
    
    detailed_data = {
        "timestamp": timestamp,
        "model": args.model,
        "use_real_llm": args.real_llm,
        "random_seed": args.random_seed,
        "summary": save_data["summary"],
        "studies": [
            {
                **{k: r[k] for k in ['study_id', 'title', 'score', 'grade', 'passed', 
                                     'tests_passed', 'tests_total', 'elapsed_time']},
                "test_details": r['score_result']['tests']
            }
            for r in all_results
        ]
    }
    
    with open(detailed_file, 'w') as f:
        json.dump(detailed_data, f, indent=2)
    
    print(f"Detailed results saved to: {detailed_file}")
    
    print("\n" + "="*80)
    print("Benchmark run complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
