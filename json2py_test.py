def run_tests():
    test_cases = [
        # 基本类型
        ('123', 123.0),
        ('"hello"', 'hello'),
        ('true', True),
        ('false', False),
        ('null', None),

        # 数组
        ('[]', []),
        ('[1, "a", true]', [1.0, 'a', True]),
        ('[[], [1]]', [[], [1.0]]),

        # 对象
        ('{}', {}),
        ('{"name": "John", "age": 30}', {'name': 'John', 'age': 30.0}),
        ('{"nested": {"key": [false]}}', {'nested': {'key': [False]}}),

        # 数字边界
        ('-3.14', -3.14),
        ('1e5', 100000.0),
        ('2.5e-3', 0.0025),
    ]

    error_cases = [
        ('01', '前导零'),  # 前导零
        ('1.', '小数部分缺少数字'),
        ('{"key": }', '非法token'),
        ('[1,,2]', '非法token'),
        ('tru', '期望e,实际为eof'),  # 不完整的关键字
        ('"unclosed', '期望"'),
    ]

    print("===== 正常用例测试 =====")
    passed = failed = 0
    for s, expected in test_cases:
        try:
            result = json2py(s)
            assert result == expected, f"\n输入: {s}\n预期: {expected}\n实际: {result}"
            print(f"✅ 通过: {s}")
            passed += 1
        except Exception as e:
            print(f"❌ 失败: {s}\n错误: {e}")
            failed += 1

    print("\n===== 异常用例测试 =====")
    error_passed = error_failed = 0
    for s, keyword in error_cases:
        try:
            json2py(s)
            print(f"❌ 失败: {s} (未触发错误)")
            error_failed += 1
        except Exception as e:
            if keyword in str(e):
                print(f"✅ 通过: {s} 触发错误: {str(e)[:30]}...")
                error_passed += 1
            else:
                print(f"❌ 失败: {s} 错误类型不匹配\n预期包含: {keyword}\n实际错误: {e}")
                error_failed += 1

    print(f"\n总计: 正常用例通过 {passed}/{len(test_cases)}, 异常用例通过 {error_passed}/{len(error_cases)}")

run_tests()