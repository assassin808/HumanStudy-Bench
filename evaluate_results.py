"""
评估已保存的实验结果

不重新运行实验，直接从缓存加载 raw_results 并重新评分。
适用于：
1. 修改了评分逻辑后，想重新评估已有结果
2. 已经跑完实验，想查看详细评分
3. 对比不同评分标准下的结果

使用方法:
    # 评估最近一次运行的结果
    python evaluate_results.py
    
    # 评估指定的缓存文件
    python evaluate_results.py --cache results/cache/study_001__mistralai_mistral_nemo__n5__seed42.json
    
    # 评估所有缓存
    python evaluate_results.py --all
"""

import argparse
import json
from pathlib import Path
from datetime import datetime

from src.core.benchmark import HumanStudyBench
from src.evaluation.scorer import Scorer
from src.core.study_config import get_study_config


def evaluate_cached_result(cache_file: Path, benchmark: HumanStudyBench) -> dict:
    """
    评估单个缓存文件
    
    Args:
        cache_file: 缓存文件路径
        benchmark: HumanStudyBench 实例
    
    Returns:
        评估结果字典
    """
    print(f"\n{'='*80}")
    print(f"Evaluating: {cache_file.name}")
    print(f"{'='*80}")
    
    # 加载缓存
    try:
        with open(cache_file, 'r') as f:
            cached = json.load(f)
    except Exception as e:
        print(f"❌ Failed to load cache: {e}")
        return None
    
    # 提取元数据
    study_id = cached.get("study_id")
    model = cached.get("model", "unknown")
    n_participants = cached.get("n_participants", 0)
    random_seed = cached.get("random_seed", 42)
    raw_results = cached.get("raw_results")
    
    if not study_id or not raw_results:
        print(f"❌ Invalid cache file: missing study_id or raw_results")
        return None
    
    print(f"Study: {study_id}")
    print(f"Model: {model}")
    print(f"Participants: {n_participants}")
    print(f"Random Seed: {random_seed}")
    
    # 加载 study
    try:
        study = benchmark.load_study(study_id)
    except Exception as e:
        print(f"❌ Failed to load study: {e}")
        return None
    
    print(f"Title: {study.metadata['title']}")
    print(f"Author: {study.metadata['authors'][0]} ({study.metadata['year']})")
    
    # 获取 study config 并聚合结果
    study_path = study.materials_path.parent
    study_config = get_study_config(study_id, study_path, study.specification)
    
    print("\nAggregating results...")
    results = study_config.aggregate_results(raw_results)
    
    # 评分
    print("Scoring...")
    scorer = Scorer()
    score_result = scorer.score_study(study, results)
    
    # 显示结果
    print("\n" + "-"*80)
    print("RESULTS")
    print("-"*80)
    
    # Study-specific results
    if study_id == "study_001":  # Asch
        conformity_stats = results.get("descriptive_statistics", {}).get(
            "conformity_rate", {}
        ).get("experimental", {})
        
        if conformity_stats:
            print(f"Conformity Rate: {conformity_stats.get('mean', 0):.1%} (SD={conformity_stats.get('sd', 0):.3f})")
            print(f"Range: [{conformity_stats.get('min', 0):.1%}, {conformity_stats.get('max', 0):.1%}]")
            print(f"Never conformed: {conformity_stats.get('never_conformed', 0)}/{n_participants}")
            print(f"Always conformed: {conformity_stats.get('always_conformed', 0)}/{n_participants}")
            print(f"At least once: {conformity_stats.get('at_least_once', 0)}/{n_participants}")
    
    elif study_id == "study_002":  # Milgram
        shock_stats = results.get("descriptive_statistics", {}).get(
            "shock_level", {}
        ).get("experimental", {})
        
        if shock_stats:
            print(f"Mean Max Shock: {shock_stats.get('mean', 0):.1f} (SD={shock_stats.get('sd', 0):.2f})")
            print(f"Obedience Rate: {shock_stats.get('obedience_rate', 0):.1%}")
            print(f"Went to 450V: {shock_stats.get('obedient_count', 0)}/{n_participants}")
    
    # Validation
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
    
    # Pass/fail
    pass_eval = study.evaluate_pass_status(score_result['total_score'])
    
    print(f"\n{'='*80}")
    print(f"Grade: {pass_eval['grade'].upper()}")
    print(f"Status: {'✅ PASSED' if pass_eval['passed'] else '❌ FAILED'}")
    print(f"Threshold: {pass_eval['threshold']:.0%}")
    print(f"Score: {score_result['total_score']:.1%}")
    print(f"{'='*80}")
    
    return {
        "cache_file": str(cache_file),
        "study_id": study_id,
        "model": model,
        "n_participants": n_participants,
        "random_seed": random_seed,
        "score": score_result['total_score'],
        "grade": pass_eval['grade'],
        "passed": pass_eval['passed'],
        "tests_passed": passed_tests,
        "tests_total": total_tests,
        "results": results,
        "score_result": score_result
    }


def main():
    parser = argparse.ArgumentParser(description="评估已保存的实验结果")
    parser.add_argument("--cache", type=str, help="指定缓存文件路径")
    parser.add_argument("--cache-dir", type=str, default="results/cache", help="缓存目录（默认：results/cache）")
    parser.add_argument("--all", action="store_true", help="评估所有缓存文件")
    parser.add_argument("--latest", action="store_true", help="评估最新的缓存文件（默认）")
    
    args = parser.parse_args()
    
    # Banner
    print("\n" + "="*80)
    print(" "*25 + "HumanStudyBench - Evaluate Results")
    print("="*80)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # Load benchmark
    benchmark = HumanStudyBench("data")
    
    cache_dir = Path(args.cache_dir)
    if not cache_dir.exists():
        print(f"\n❌ Cache directory not found: {cache_dir}")
        print("Run experiments with --use-cache first to generate cache files.")
        return
    
    # 确定要评估的文件
    cache_files = []
    
    if args.cache:
        # 指定文件
        cache_file = Path(args.cache)
        if not cache_file.exists():
            print(f"\n❌ Cache file not found: {cache_file}")
            return
        cache_files = [cache_file]
    
    elif args.all:
        # 所有缓存文件
        cache_files = sorted(cache_dir.glob("*.json"))
        if not cache_files:
            print(f"\n❌ No cache files found in {cache_dir}")
            return
        print(f"\nFound {len(cache_files)} cache files")
    
    else:
        # 最新文件（默认）
        cache_files = sorted(cache_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not cache_files:
            print(f"\n❌ No cache files found in {cache_dir}")
            return
        cache_files = [cache_files[0]]
        print(f"\nEvaluating latest cache file")
    
    # 评估
    results = []
    for cache_file in cache_files:
        result = evaluate_cached_result(cache_file, benchmark)
        if result:
            results.append(result)
    
    # 总结（如果评估了多个文件）
    if len(results) > 1:
        print("\n" + "="*80)
        print(" "*30 + "SUMMARY")
        print("="*80)
        
        print(f"\nTotal evaluations: {len(results)}")
        passed = sum(1 for r in results if r['passed'])
        print(f"Passed: {passed}/{len(results)} ({passed/len(results):.0%})")
        avg_score = sum(r['score'] for r in results) / len(results)
        print(f"Average score: {avg_score:.1%}")
        
        print("\n" + "-"*80)
        print("Per-cache results:")
        print("-"*80)
        
        for r in results:
            status_symbol = "✅" if r['passed'] else "❌"
            cache_name = Path(r['cache_file']).name
            print(f"{status_symbol} {cache_name:50s} | Score: {r['score']:5.1%} | Tests: {r['tests_passed']}/{r['tests_total']}")
    
    print("\n" + "="*80)
    print("Evaluation complete!")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
