import pytest

import matched


class TestMatch:
    def test_match(self, cleaned_choices, scores, nmax):
        allocated = matched.match(cleaned_choices, scores, nmax)

        assert allocated == {
            "mz6952": "code2",  # lost oversubscribed code1 to xeq483, got 2nd choice
            "gc48": "code2",
            "jq1239": "code3",  # won code3 over yzq85 on score
            "yzq85": None,  # code3 lost, and code1 fallback was already full
            "xeq483": "code1",  # won code1 over mz6952 on score
        }

        # No project exceeds its nmax capacity.
        counts = {}
        for code in allocated.values():
            if code is not None:
                counts[code] = counts.get(code, 0) + 1
        assert all(count <= nmax[code] for code, count in counts.items())

    def test_missing_score_raises(self, cleaned_choices, nmax):
        with pytest.raises(ValueError, match="scores"):
            matched.match(cleaned_choices, {}, nmax)

    def test_missing_nmax_raises(self, cleaned_choices, scores):
        with pytest.raises(ValueError, match="nmax"):
            matched.match(cleaned_choices, scores, {"code1": 1})

    def test_empty_choices(self):
        assert matched.match({}, {}, {}) == {}

    def test_inconsistent_nmax_raises_assertion_error(self):
        # A negative nmax is logically inconsistent (capacity can't be negative), so
        # it should hit the "should never happen" internal safety net, not silently
        # misbehave.
        with pytest.raises(AssertionError, match="should never happen"):
            matched.match({"user": ["code1"]}, {"user": 10}, {"code1": -1})


class TestChoiceRank:
    def test_choice_rank(self, cleaned_choices, scores, nmax):
        allocated = matched.match(cleaned_choices, scores, nmax)

        assert matched.choice_rank(cleaned_choices, allocated) == {
            "mz6952": 2,
            "gc48": 1,
            "jq1239": 1,
            "yzq85": None,
            "xeq483": 1,
        }

    def test_choice_rank_all_unallocated(self, cleaned_choices):
        allocated = dict.fromkeys(cleaned_choices)

        assert matched.choice_rank(cleaned_choices, allocated) == dict.fromkeys(
            cleaned_choices
        )


class TestShortlist:
    @pytest.mark.parametrize(
        ("code", "expected"),
        [
            ("code1", ["jq1239", "xeq483", "mz6952", "yzq85"]),
            ("nonexistent_code", []),
        ],
    )
    def test_shortlist(self, cleaned_choices, scores, code, expected):
        assert matched.shortlist(cleaned_choices, scores, code) == expected
