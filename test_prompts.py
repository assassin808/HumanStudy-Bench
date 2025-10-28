"""
测试 Prompt Builder - 显示实际生成的 prompts

这个脚本会：
1. 加载 study 配置
2. 生成 trials
3. 创建参与者 profile
4. 显示完整的 system prompt 和 trial prompts
"""

import os
import sys
from pathlib import Path

# 加载 .env
if Path(".env").exists():
    with open(".env") as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

from src.core.study_config import get_study_config
from src.agents.prompt_builder import get_prompt_builder
from src.agents.llm_participant_agent import LLMParticipantAgent
import json


def test_prompts(study_id="study_001", n_trials=3):
    """测试并显示 prompts"""
    
    print("="*80)
    print(f"Testing Prompt Builder for {study_id}")
    print("="*80)
    
    # 1. 加载 study
    study_path = Path(f"data/studies/{study_id}")
    with open(study_path / "specification.json") as f:
        spec = json.load(f)
    
    print(f"\n📚 Study: {spec.get('title', study_id)}")
    print(f"Type: {spec.get('study_type', 'unknown')}")
    
    # 2. 创建 config 和 trials
    config = get_study_config(study_id, study_path, spec)
    trials = config.create_trials()[:n_trials]  # 只取前 n_trials
    
    print(f"\n🔬 Generated {len(trials)} trials (showing first {n_trials})")
    
    # 3. 创建 prompt builder
    builder = get_prompt_builder(study_id)
    instructions = builder.get_instructions()
    
    print(f"\n📋 Instructions ({len(instructions)} chars):")
    print("-" * 80)
    print(instructions[:500] + "..." if len(instructions) > 500 else instructions)
    print("-" * 80)
    
    # 4. 创建一个示例参与者 profile
    import numpy as np
    np.random.seed(42)
    
    # Generate sample profile
    if 'asch' in study_id.lower() or 'conformity' in spec.get('study_type', '').lower():
        profile = {
            "participant_id": 1,
            "age": 22,
            "gender": "male",
            "personality_traits": {
                "conformity_tendency": 0.65,
                "independence": 0.35
            }
        }
    elif 'milgram' in study_id.lower() or 'obedience' in spec.get('study_type', '').lower():
        profile = {
            "participant_id": 1,
            "age": 35,
            "gender": "male",
            "occupation": "teacher",
            "personality_traits": {
                "authority_obedience": 0.70,
                "empathy": 0.60,
                "moral_courage": 0.40
            }
        }
    else:
        profile = {
            "participant_id": 1,
            "age": 25,
            "gender": "female"
        }
    
    # Create agent with this profile
    agent = LLMParticipantAgent(
        participant_id=1,
        profile=profile,
        use_real_llm=True,
        model="mistralai/mistral-nemo"
    )
    
    print(f"\n👤 Sample Participant Profile:")
    print(f"   Age: {profile.get('age')}")
    print(f"   Gender: {profile.get('gender')}")
    print(f"   Personality Traits:")
    for trait, value in profile.get('personality_traits', {}).items():
        print(f"      - {trait}: {value:.2f}")
    
    # 5. 生成 system prompt
    system_prompt = builder.build_system_prompt(profile)
    
    print(f"\n🤖 System Prompt ({len(system_prompt)} chars):")
    print("=" * 80)
    print(system_prompt)
    print("=" * 80)
    
    # 6. 显示每个 trial 的 prompt
    for i, trial in enumerate(trials, 1):
        trial_prompt = builder.build_trial_prompt(trial)
        
        print(f"\n📝 Trial {i}/{len(trials)} Prompt ({len(trial_prompt)} chars):")
        print("-" * 80)
        print(f"Trial Data: {json.dumps({k: v for k, v in trial.items() if k != 'confederate_responses'}, indent=2)}")
        if 'confederate_responses' in trial and trial['confederate_responses']:
            print(f"Confederates: {trial['confederate_responses']}")
        print("-" * 80)
        print(trial_prompt)
        print("-" * 80)
        
        # 如果是第一个 trial，实际调用 LLM 看看返回
        if i == 1:
            print(f"\n🔄 Calling LLM with this prompt...")
            try:
                # 给 agent 指令
                agent.instructions = instructions
                
                # 模拟响应
                response = agent._simulate_response(trial, trial_prompt)
                
                print(f"\n✅ LLM Response:")
                print(f"   Answer: {response}")
                print(f"   Type: {type(response)}")
                
            except Exception as e:
                print(f"\n❌ Error calling LLM: {e}")
                import traceback
                traceback.print_exc()
    
    print("\n" + "="*80)
    print("Prompt Testing Complete!")
    print("="*80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test prompt builder and show generated prompts")
    parser.add_argument("--study", default="study_001", help="Study ID (default: study_001)")
    parser.add_argument("--n-trials", type=int, default=3, help="Number of trials to show (default: 3)")
    
    args = parser.parse_args()
    
    test_prompts(args.study, args.n_trials)
