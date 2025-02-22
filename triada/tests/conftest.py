import pytest
from unittest.mock import ANY


@pytest.hookimpl(tryfirst=True)
def pytest_assertrepr_compare(op, left, right):
    if isinstance(left, list) and isinstance(right, list):
        def clean_token(call_obj):
            if isinstance(call_obj, tuple) and 'params' in call_obj[1]:
                call_obj[1]['params']['access_token'] = "<HIDDEN>"
            return call_obj

        left_clean = [clean_token(c) for c in left]
        right_clean = [clean_token(c) for c in right]

        return [
            "Comparison failed, but access_token are hidden:",
            f"  Left:  {left_clean}",
            f"  Right: {right_clean}"
        ]
