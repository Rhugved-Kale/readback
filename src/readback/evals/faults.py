"""Fault profiles applied to FakeAdapter's FaultConfig.

Five profiles, each parameterised by which app it hits. A profile is a pure
description; `apply_profile` turns it into FaultConfig objects for the three
fake adapters.

Determinism matters more than realism here. Every profile that involves a
choice (which app to hit, when relevant) draws from a seeded RNG, and the seed
is recorded on every run record, so any failure the matrix finds can be
reproduced exactly rather than chased. A flaky eval is worse than no eval: it
trains you to ignore it.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Mapping

from ..adapters.fake import FaultConfig

NONE = "none"
ERROR_AFTER_WRITE = "error_after_write"
TIMEOUT_AFTER_COMMIT = "timeout_after_commit"
RATE_LIMIT_STORM = "rate_limit_storm"
STALE_READ = "stale_read"

PROFILES: tuple[str, ...] = (
    NONE,
    ERROR_AFTER_WRITE,
    TIMEOUT_AFTER_COMMIT,
    RATE_LIMIT_STORM,
    STALE_READ,
)

APPS: tuple[str, ...] = ("stripe", "notion", "slack")

#: 429s before the provider relents. FakeAdapter retries up to APPLY_RETRY_BUDGET
#: (5), so 3 is a storm the run should survive -- the point is that surviving it
#: must not produce duplicate writes, not that it fails.
STORM_LENGTH = 3

#: Reads served from pre-write state before the replica catches up. FakeAdapter
#: spends READ_RETRY_BUDGET (4) fresh reads, so 2 is recoverable: verify must
#: re-read rather than believe the first answer.
STALE_READS = 2


@dataclass
class FaultPlan:
    """A concrete, reproducible fault assignment for one run."""

    profile: str
    target_app: str | None
    seed: int

    @property
    def label(self) -> str:
        if self.profile == NONE:
            return NONE
        return f"{self.profile}@{self.target_app}"

    def to_dict(self) -> dict:
        return {"profile": self.profile, "target_app": self.target_app, "seed": self.seed}


def plan_faults(profile: str, seed: int, target_app: str | None = None) -> FaultPlan:
    """Choose which app this profile hits, deterministically from the seed."""
    if profile not in PROFILES:
        raise ValueError(f"unknown fault profile {profile!r}; have {PROFILES}")
    if profile == NONE:
        return FaultPlan(profile=NONE, target_app=None, seed=seed)
    if target_app is None:
        target_app = random.Random(seed).choice(APPS)
    return FaultPlan(profile=profile, target_app=target_app, seed=seed)


def configs_for(plan: FaultPlan) -> Mapping[str, FaultConfig]:
    """FaultConfig per app. Apps not targeted get a clean config."""
    configs = {app: FaultConfig() for app in APPS}
    if plan.profile == NONE or plan.target_app is None:
        return configs

    target = configs[plan.target_app]
    if plan.profile == ERROR_AFTER_WRITE:
        target.fail_after_write = True
    elif plan.profile == TIMEOUT_AFTER_COMMIT:
        target.timeout_after_commit = True
    elif plan.profile == RATE_LIMIT_STORM:
        target.rate_limit_storm = STORM_LENGTH
    elif plan.profile == STALE_READ:
        target.stale_read = STALE_READS
    return configs
