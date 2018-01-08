from utils import assess_answer

class TestAnswer(object):
    def test_expected_not_iterable(self):
        expected = None
        actual = assess_answer(5, '5\n', conversion_func=int)

        assert expected == actual

    def test_expected_is_actual(self):
        expected = None
        actual = assess_answer([5], '5\n', conversion_func=int)

        assert expected == actual

    def test_expected_is_actual_long_answer(self):
        expected = None
        actual = assess_answer([1, 2, 3, 4, 5], '1\n2\n3\n4\n5\n', conversion_func=int)

        assert expected == actual

    def test_actual_too_long(self):
        expected = 'Extra values provided in answer'
        actual = assess_answer([1, 2, 3, 4, 5], '1\n2\n3\n4\n5\n6\n7\n8\n', conversion_func=int)

        assert expected == actual

    def test_actual_too_short(self):
        expected = 'Not enough values provided in answer'
        actual = assess_answer([1, 2, 3, 4, 5], '1\n2\n3\n', conversion_func=int)

        assert expected == actual

    def test_expected_actual_mismatch(self):
        expected = "Value at index 3 does not match\nExpected: 4 (<class 'int'>) Actual: 3 (<class 'int'>)"
        actual = assess_answer([1, 2, 3, 4, 5], '1\n2\n3\n3\n4\n', conversion_func=int)

        assert expected == actual

    def test_no_conversion_func(self):
        expected = None
        actual = assess_answer(['1', '2', '3', '4', '5'], '1\n2\n3\n4\n5\n')

        assert expected == actual
