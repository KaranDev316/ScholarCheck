"""Access rules are per agent, so the matching has to be explicit."""

import pytest

from app.collect.robots import RobotsRules

UNIVERSITY = """
Sitemap: https://www.example.edu/sitemap.xml

User-agent: *
Disallow: /search?*
Disallow: /library/images/
Allow: /library/images/public/
"""

AGENT_SPECIFIC = """
User-agent: *
Disallow: /

User-agent: ScholarCheck
Allow: /awards/
"""


def test_a_plain_rule_blocks_the_matching_path() -> None:
    rules = RobotsRules.parse(UNIVERSITY)

    assert rules.allows("https://www.example.edu/awards/x", user_agent="ScholarCheck")
    assert not rules.allows(
        "https://www.example.edu/library/images/x.png", user_agent="ScholarCheck"
    )


def test_a_longer_allow_wins_over_a_shorter_disallow() -> None:
    rules = RobotsRules.parse(UNIVERSITY)

    assert rules.allows(
        "https://www.example.edu/library/images/public/x.png",
        user_agent="ScholarCheck",
    )


def test_a_wildcard_matches_a_query_string() -> None:
    rules = RobotsRules.parse(UNIVERSITY)

    assert not rules.allows("https://www.example.edu/search?q=award", user_agent="ScholarCheck")
    assert rules.allows("https://www.example.edu/scholarships", user_agent="ScholarCheck")


def test_our_own_group_replaces_the_wildcard_group() -> None:
    """A group naming us is the whole answer; the ``*`` block no longer applies."""

    rules = RobotsRules.parse(AGENT_SPECIFIC)

    assert rules.allows("https://www.example.edu/awards/x", user_agent="ScholarCheck/0.1")
    assert rules.allows("https://www.example.edu/news", user_agent="ScholarCheck/0.1")
    assert not rules.allows("https://www.example.edu/awards/x", user_agent="OtherBot/2")


def test_an_empty_disallow_restricts_nothing() -> None:
    rules = RobotsRules.parse("User-agent: *\nDisallow:\n")

    assert rules.allows("https://www.example.edu/anything", user_agent="ScholarCheck")


def test_a_site_without_rules_is_readable() -> None:
    assert RobotsRules.parse("").allows("https://www.example.edu/x", user_agent="ScholarCheck")


@pytest.mark.parametrize(
    ("pattern", "path", "allowed"),
    [
        ("/awards/*/deadline$", "/awards/2027/deadline", False),
        ("/awards/*/deadline$", "/awards/2027/deadline/extra", True),
        ("/awards/*/deadline$", "/awards/deadline", True),
    ],
)
def test_wildcards_and_end_anchors(pattern: str, path: str, allowed: bool) -> None:
    rules = RobotsRules.parse(f"User-agent: *\nDisallow: {pattern}\n")

    assert rules.allows(f"https://www.example.edu{path}", user_agent="ScholarCheck") is allowed
