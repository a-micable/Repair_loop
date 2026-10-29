from repairloop.patching import PatchError, apply_line_edits, apply_replace


def test_replace_once():
    assert apply_replace("aa bb aa", "bb", "XX") == "aa XX aa"


def test_replace_all():
    assert apply_replace("a b a", "a", "x", replace_all=True) == "x b x"


def test_ambiguous():
    try:
        apply_replace("a a", "a", "x")
        assert False
    except PatchError:
        pass


def test_line_edits():
    text = "one\ntwo\nthree\n"
    out = apply_line_edits(text, 2, 2, "TWO\n")
    assert out.splitlines()[1] == "TWO"
