import pytest

import matched


@pytest.fixture
def raw_choices():
    return {
        "mz6952": ["code1", "code3", "code2"],  # code3 invalid for mz6952's course
        "gc48": ["code2", "code3"],  # code3 invalid for gc48's course
        "jq1239": ["code3", "code1"],
        "yzq85": ["invalid_code", "code2", "code3", "code1", "code1"],
        "xeq483": ["code1", "code1", "code3"],  # code1 duplicated
    }


@pytest.fixture
def nmax():
    return {"code1": 1, "code2": 2, "code3": 1}


@pytest.fixture
def courses():
    return {
        "mz6952": "course1",
        "gc48": "course1",
        "jq1239": "course2",
        "yzq85": "course2",
        "xeq483": "course1",
    }


@pytest.fixture
def eligible_courses():
    return {
        "code1": ["course1", "course2"],
        "code2": ["course1"],
        "code3": ["course2"],
    }


@pytest.fixture
def scores():
    return {
        "mz6952": 70,
        "gc48": 80,
        "jq1239": 90,
        "yzq85": 60,
        "xeq483": 85,
    }


@pytest.fixture
def cleaned_choices(raw_choices, nmax, courses, eligible_courses):
    cleaned = matched.filter_invalid_code(raw_choices, nmax)
    cleaned = matched.filter_invalid_course(cleaned, courses, eligible_courses)
    return matched.deduplicate(cleaned)
