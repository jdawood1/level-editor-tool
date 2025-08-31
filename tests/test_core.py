from editor.core import new_level, add_object, stats


def test_flow(tmp_path):
    lp = new_level("ci_demo", 10, 10)
    add_object(lp, "coin", 2, 2)
    s = stats(lp)
    assert s["objects"] == 1
