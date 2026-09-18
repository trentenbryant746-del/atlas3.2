"""Each engine check() row becomes one test. See conftest.py."""


def test_check(check_row):
    name, ok, detail = check_row
    assert ok, f"{name}: {detail}"
