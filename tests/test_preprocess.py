import pytest

import matched


class TestFilterInvalidCode:
    def test_filter_invalid_code(self, raw_choices, nmax):
        filtered = matched.filter_invalid_code(raw_choices, nmax)

        # invalid_code is not a key in nmax, so it is dropped.
        assert filtered["yzq85"] == ["code2", "code3", "code1", "code1"]

        # Students with no invalid codes are unaffected.
        assert filtered["mz6952"] == raw_choices["mz6952"]

    def test_all_codes_invalid(self, nmax):
        filtered = matched.filter_invalid_code({"newuser": ["bad1", "bad2"]}, nmax)

        assert filtered == {"newuser": []}


class TestFilterInvalidCourse:
    def test_filter_invalid_course(self, raw_choices, nmax, courses, eligible_courses):
        filtered = matched.filter_invalid_code(raw_choices, nmax)
        filtered = matched.filter_invalid_course(filtered, courses, eligible_courses)

        assert filtered == {
            "mz6952": ["code1", "code2"],
            "gc48": ["code2"],
            "jq1239": ["code3", "code1"],
            "yzq85": ["code3", "code1", "code1"],
            "xeq483": ["code1", "code1"],
        }

    def test_code_missing_from_eligible_courses(self):
        # A code absent from eligible_courses entirely is eligible for nobody.
        filtered = matched.filter_invalid_course(
            {"newuser": ["unlisted_code"]}, {"newuser": "course1"}, {}
        )

        assert filtered == {"newuser": []}

    def test_missing_course_entry_raises(self, eligible_courses):
        with pytest.raises(KeyError, match="newuser"):
            matched.filter_invalid_course({"newuser": ["code1"]}, {}, eligible_courses)


class TestDeduplicate:
    def test_deduplicate(self):
        choices = {
            "yzq85": ["code3", "code1", "code1"],
            "xeq483": ["code1", "code1"],
            "jq1239": ["code3", "code1"],
        }

        deduped = matched.deduplicate(choices)

        # Repeated codes are dropped, keeping the first (best) occurrence.
        assert deduped["yzq85"] == ["code3", "code1"]
        assert deduped["xeq483"] == ["code1"]

        # Already-unique lists are unaffected.
        assert deduped["jq1239"] == ["code3", "code1"]

    def test_empty_list(self):
        assert matched.deduplicate({"newuser": []}) == {"newuser": []}


class TestCombined:
    def test_combined(self, raw_choices, nmax, courses, eligible_courses):
        cleaned = matched.filter_invalid_code(raw_choices, nmax)
        cleaned = matched.filter_invalid_course(cleaned, courses, eligible_courses)
        cleaned = matched.deduplicate(cleaned)

        assert cleaned == {
            "mz6952": ["code1", "code2"],
            "gc48": ["code2"],
            "jq1239": ["code3", "code1"],
            "yzq85": ["code3", "code1"],
            "xeq483": ["code1"],
        }

    def test_combined_empty(self, nmax, courses, eligible_courses):
        cleaned = matched.filter_invalid_code({}, nmax)
        cleaned = matched.filter_invalid_course(cleaned, courses, eligible_courses)
        cleaned = matched.deduplicate(cleaned)

        assert cleaned == {}
