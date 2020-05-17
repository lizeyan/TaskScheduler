from ts import str_product


def test_fill_template():
    assert set(str_product("{{ A }}", A=[1, 2, 3])) == {"1", "2", "3"}
    assert set(str_product("{{ A }}.{{ B }}", A=[1, 2, 3], B=[2, 3])) == {
        "1.2", "2.2", "3.2",
        "1.3", "2.3", "3.3",
    }
