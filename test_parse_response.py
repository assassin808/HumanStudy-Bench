"""
测试 _parse_response() 函数的解析能力
"""

from src.agents.llm_participant_agent import LLMParticipantAgent

# 创建一个测试 agent
agent = LLMParticipantAgent(
    participant_id=0,
    profile={"age": 17, "education": "high school"},
    use_real_llm=False
)

# 测试用例
test_cases = [
    # Study 004 Birth Sequence 数字回答
    ("36", {}, "36", "纯数字"),
    ("50", {}, "50", "纯数字"),
    ("72", {}, "72", "纯数字"),
    ("I estimate 30 families", {}, "30", "数字在句子中"),
    ("Maybe around 45?", {}, "45", "数字在句子中"),
    
    # Study 004 Program Choice 字母回答
    ("A", {}, "A", "纯字母"),
    ("B", {}, "B", "纯字母"),
    ("Program A", {}, "A", "Program + 字母"),
    ("Program B", {}, "B", "Program + 字母"),
    ("I choose Program A", {}, "A", "字母在句子中"),
    
    # 其他格式
    ("The answer is A", {}, "A", "字母在句子末尾"),
    ("Option B seems correct", {}, "B", "Option + 字母"),
]

print("=" * 80)
print("测试 _parse_response() 解析功能")
print("=" * 80)

passed = 0
failed = 0

for response_text, trial_info, expected, description in test_cases:
    result = agent._parse_response(response_text, trial_info)
    status = "✅ PASS" if result == expected else "❌ FAIL"
    
    if result == expected:
        passed += 1
    else:
        failed += 1
    
    print(f"\n{status} {description}")
    print(f"  输入: '{response_text}'")
    print(f"  期望: '{expected}'")
    print(f"  实际: '{result}'")

print("\n" + "=" * 80)
print(f"测试结果: {passed} 通过, {failed} 失败")
print("=" * 80)
