"""Access rules, read before any page is fetched.

Robots rules are per user-agent, so matching has to be explicit: the longest
matching path prefix decides, a specific group for our agent outranks the ``*``
group, and an unreachable ``robots.txt`` is treated as "no restriction stated"
while a stated restriction is obeyed. Getting this wrong would mean quoting a
page we were not allowed to fetch, which invalidates the evidence.
"""

import re
from dataclasses import dataclass, field
from urllib.parse import urlsplit


@dataclass(frozen=True)
class RobotsRules:
    """The rules that apply to one site, keyed by user-agent group."""

    groups: dict[str, tuple[tuple[bool, str], ...]] = field(default_factory=dict)

    def allows(self, url: str, *, user_agent: str) -> bool:
        """True when ``user_agent`` may fetch ``url`` under these rules."""

        rules = self._rules_for(user_agent)
        if not rules:
            return True
        split = urlsplit(url)
        target = split.path or "/"
        if split.query:
            target = f"{target}?{split.query}"

        best: tuple[int, bool] | None = None
        for allowed, pattern in rules:
            if not _matches(pattern, target):
                continue
            score = len(pattern.rstrip("$"))
            if best is None or score > best[0] or (score == best[0] and allowed):
                best = (score, allowed)
        return True if best is None else best[1]

    def _rules_for(self, user_agent: str) -> tuple[tuple[bool, str], ...]:
        wanted = user_agent.lower()
        exact = [
            (agent, rules)
            for agent, rules in self.groups.items()
            if agent != "*" and agent in wanted
        ]
        if exact:
            agent, rules = max(exact, key=lambda item: len(item[0]))
            return rules
        return self.groups.get("*", ())

    @classmethod
    def parse(cls, text: str) -> "RobotsRules":
        """Read ``robots.txt`` content; unknown lines are ignored on purpose."""

        groups: dict[str, list[tuple[bool, str]]] = {}
        current: list[str] = []
        # A group is a run of User-agent lines followed by its rules.
        for raw in text.splitlines():
            line = raw.split("#", 1)[0].strip()
            if not line or ":" not in line:
                continue
            name, _, value = line.partition(":")
            name = name.strip().lower()
            value = value.strip()

            if name == "user-agent":
                if current and rules_started(groups, current):
                    current = []
                current.append(value.lower())
                groups.setdefault(value.lower(), [])
            elif name in {"allow", "disallow"} and current:
                for agent in current:
                    groups.setdefault(agent, []).append((name == "allow", value))

        return cls(groups={agent: tuple(rules) for agent, rules in groups.items()})


def rules_started(groups: dict[str, list[tuple[bool, str]]], agents: list[str]) -> bool:
    """True once any agent in the current run already has a rule."""

    return any(groups.get(agent) for agent in agents)


def _matches(pattern: str, path: str) -> bool:
    """Apply a robots path pattern, including ``*`` and a trailing ``$``."""

    if not pattern:
        return False  # "Disallow:" with no path restricts nothing.
    anchored = pattern.endswith("$")
    body = pattern[:-1] if anchored else pattern
    expression = "".join(
        ".*" if character == "*" else re.escape(character) for character in body
    )
    return re.match(expression + ("$" if anchored else ""), path) is not None


__all__ = ["RobotsRules"]
