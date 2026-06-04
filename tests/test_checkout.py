"""
Checkout differnt repos, branches, tags and PR

 3.9s [https://github.com/micropython/micropython.git]
26.9s [https://github.com/micropython/micropython.git~17232]
 4.1s [https://github.com/micropython/micropython.git@v1.25.0]
91.5s [https://github.com/micropython/micropython.git@v1.25.0-SUBMODULES]
 8.5s [https://github.com/micropython/micropython.git~17113@v1.25.0]
"""

from __future__ import annotations

import dataclasses
import pathlib
import time

import pytest

from git_cached_repo.git_cached_repo import CachedGitRepo, GitMetadata
from git_cached_repo.util_subprocess import SubprocessExitCodeException

DIRECTORY_OF_THIS_FILE = pathlib.Path(__file__).parent

DIRECTORY_CACHE = DIRECTORY_OF_THIS_FILE / "git_cache"
DIRECTORY_CACHE.mkdir(parents=True, exist_ok=True)


@dataclasses.dataclass(frozen=True, repr=True)
class Ttestparam:
    spec: str
    submodules: bool

    expected_url_link: str
    expected_commit_hash_short: str | None
    expected_rebased: bool
    expected_command_describe: str

    @property
    def pytest_id(self) -> str:
        submodules = "-SUBMODULES" if self.submodules else ""
        return self.spec + submodules
        # return self.spec.replace(" ", "-").replace("https://", "").replace("/", "_")

    @staticmethod
    def expected_template(metadata: GitMetadata) -> str:
        elems = [
            f"expected_url_link='{metadata.url_link}',",
            f"expected_commit_hash_short='{metadata.commit_hash_short}',",
            f"expected_rebased={metadata.rebased},",
            f"expected_command_describe='{metadata.command_describe.stdout}',",
        ]
        return "\n".join(elems)

    def passed(self, metadata: GitMetadata) -> bool:
        if self.expected_url_link != metadata.url_link:
            return False
        if self.expected_commit_hash_short:
            if self.expected_commit_hash_short != metadata.commit_hash_short:
                return False
        if self.expected_rebased != metadata.rebased:
            return False
        if not metadata.command_describe.stdout.startswith(
            self.expected_command_describe
        ):
            return False
        return True


_TESTPARAM_A = Ttestparam(
    spec="https://github.com/micropython/micropython.git",
    submodules=False,
    expected_url_link="https://github.com/micropython/micropython",
    expected_commit_hash_short=None,
    expected_rebased=False,
    expected_command_describe="heads/master-0-",
)
_TESTPARAM_B = Ttestparam(
    spec="https://github.com/micropython/micropython.git~17232",
    submodules=False,
    expected_url_link="https://github.com/micropython/micropython/pull/17232",
    expected_commit_hash_short=None,
    expected_rebased=False,
    expected_command_describe="heads/pr-17232-0-",
)
_TESTPARAM_C = Ttestparam(
    spec="https://github.com/micropython/micropython.git@f498a16",
    submodules=False,
    expected_url_link="https://github.com/micropython/micropython/tree/f498a16",
    expected_commit_hash_short="f498a16",
    expected_rebased=False,
    expected_command_describe="tags/v1.25.0-0-gf498a16c7d",
)
_TESTPARAM_D = Ttestparam(
    spec="https://github.com/micropython/micropython.git@v1.25.0",
    submodules=False,
    expected_url_link="https://github.com/micropython/micropython/tree/v1.25.0",
    expected_commit_hash_short="f498a16",
    expected_rebased=False,
    expected_command_describe="tags/v1.25.0-0-gf498a16",
)
_TESTPARAM_E = Ttestparam(
    spec="https://github.com/micropython/micropython.git@v1.25.0",
    submodules=True,
    expected_url_link="https://github.com/micropython/micropython/tree/v1.25.0",
    expected_commit_hash_short="f498a16",
    expected_rebased=False,
    expected_command_describe="tags/v1.25.0-0-gf498a16",
)
_TESTPARAM_F = Ttestparam(
    spec="https://github.com/micropython/micropython.git~17113@v1.25.0",
    submodules=False,
    expected_url_link="https://github.com/micropython/micropython/pull/17113",
    expected_commit_hash_short="a758313",
    expected_rebased=True,
    expected_command_describe="heads/pr-17113-0-",
)
_TESTPARAMS = [
    _TESTPARAM_A,
    _TESTPARAM_B,
    _TESTPARAM_C,
    _TESTPARAM_D,
    _TESTPARAM_E,
    _TESTPARAM_F,
]


def _test_checkout(testparam: Ttestparam, git_bare: bool) -> None:

    cache = CachedGitRepo(
        directory_cache=DIRECTORY_CACHE,
        git_spec=testparam.spec,
        prefix="test_checkout_",
    )
    cache.clean_directory_work_repo(directory_cache=DIRECTORY_CACHE)
    try:
        begin_s = time.monotonic()
        metadata = cache.clone(
            git_clean=False, submodules=testparam.submodules, git_bare=git_bare
        )
        duration_s = time.monotonic() - begin_s
        print(f"{duration_s=:04.1f}s {git_bare=} {testparam.pytest_id}")
        passed = testparam.passed(metadata)
        if not passed:
            print(testparam.expected_template(metadata=metadata))
        assert passed
    except SubprocessExitCodeException as e:
        raise ValueError(f"Failed: {e.__class__.__name__}: {e}") from e


@pytest.mark.parametrize("git_bare", (True, False), ids=lambda git_bare: f"{git_bare=}")
@pytest.mark.parametrize(
    "testparam", _TESTPARAMS, ids=lambda testparam: testparam.pytest_id
)
@pytest.mark.internet
def test_checkout(testparam: Ttestparam, git_bare: bool) -> None:
    _test_checkout(testparam, git_bare=git_bare)


if __name__ == "__main__":
    _test_checkout(testparam=_TESTPARAM_B, git_bare=True)
