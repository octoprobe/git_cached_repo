# git_cached_repo

Cache an arbitrary number of Git repositories for fast access to branches, tags, commits, and pull requests.

## Programming Interface

### GitSpec

A checkout target is described in a single line:

- `https://github.com/micropython/micropython.git`\
    Checkout the default branch.
- `https://github.com/micropython/micropython.git@v1.25.0`\
    Checkout a branch, tag, or commit hash.
- `https://github.com/micropython/micropython.git~17468`\
    Checkout pull request `17468`.
- `https://github.com/micropython/micropython.git~17468@v1.25.0`\
    Checkout pull request `17468` and rebase it onto `v1.25.0`.

Parse a spec:

```python
GitSpec.parse("https://github.com/micropython/micropython.git~17468@v1.25.0")
```

You can also convert standard GitHub URLs into this syntax with `parse_github`:

* https://github.com/micropython/micropython/pull/17468/commits\
* https://github.com/micropython/micropython/commits/v1.25.0\
* https://github.com/micropython/micropython/commit/f498a16c7db6d4b2de200b3e0856528dfe0613c3#diff-69528cf7a1b680885089529ad7dd75caa165373a79f9d44cf32663215baebabf\
* https://github.com/micropython/micropython/tree/docs/library/bluetooth\


```python
GitSpec.parse_github("https://github.com/micropython/micropython/commits/v1.24-release/")
# returns a GitSpec with git_spec:
# "https://github.com/micropython/micropython.git@v1.24-release"
```

### CachedGitRepo

This checks out the repo and returns metadata:

```python
cache = CachedGitRepo(
    directory_cache=DIRECTORY_CACHE,
    git_spec="https://github.com/micropython/micropython.git@v1.24-release",
    prefix="test_checkout_",
)

cache.clean_directory_work_repo(directory_cache=DIRECTORY_CACHE)

metadata = cache.clone(
    git_clean=False,
    submodules=False,
    git_bare=True,
)
```

### GitMetadata

`GitMetadata` describes what was checked out, including:

- `url_link`
- `commit_hash`
- `command_describe`
- `command_log`
- `rebased`

Example PR: `https://github.com/micropython/micropython.git~17782`

    https://github.com/micropython/micropython.git~17782 7aed4bf

    git describe --all --long --dirty --always
    heads/pr-17782-0-g7aed4bf

    git log --oneline --decorate -n 20
    7aed4bf (HEAD -> pr-17782) tools/mpremote: Allow executing a .mpy directly.
    87cf777 tools/mpremote: Support raw REPL mpy mode.
    48bc39e tools/pyboard.py: Allow running .mpy directly.
    7d1f9f7 tests/test_utils.py: Send mpy files directly to raw REPL.
    6f2d6c5 tools/pyboard.py: Support sending mpy files directly.
    9bd4a05 shared/runtime/pyexec: Add raw REPL mpy paste mode.
    2da940e tests/run-perfbench.py: Skip large tests based on bm_params.
    5fcce2a tests/extmod/machine_uart_tx.py: Make minimum baud 4800, add 38400.
    5a460f7 py/objlist: Make list append allocation more gentle.
    8c071b5 tests/misc/rge_sm.py: Use list.append instead of list += [...].
    f754e72 tests/ports/stm32/adcall.py: Print values if test ADC fails.
    8f664dd tests/run-tests.py: Skip various tests on small SAMD targets.
    4f07934 tests/float/string_format_modulo2_intbig.py: Get working on esp8266.
    af38ee1 (BASE) (origin/master, origin/HEAD, master) samd/mphalport: Run events at least once in mp_hal_delay_ms.
    4e32820 nrf/mphalport: Run events at least once in mp_hal_delay_ms.

The log output shows:

- the current PR head (for example `(HEAD -> pr-17782)`)
- the base commit (marked as `(BASE)`)

The goal of the output is, that a developer may verify what is contained in the checkout.

## Logging and Debug Output

The project logs executed Git commands and timing via `util_subprocess`.

To enable DEBUG for these two modules only:

```python
import logging
from git_cached_repo import git_cached_repo, util_subprocess

logging.getLogger(util_subprocess.__file__).setLevel(logging.DEBUG)
logging.getLogger(git_cached_repo.__file__).setLevel(logging.DEBUG)
```

Run tests with console logging enabled:

```bash
pytest -s --log-cli-level=DEBUG tests/test_checkout.py
```

The last line shows the overall time: `https://github.com/micropython/micropython.git@v1.25.0: duration_s=3.7s`

Inbetween you see the git commands, for example:
```
DEBUG  util_subprocess.py:57 EXEC git describe --all --long --dirty --always
DEBUG  util_subprocess.py:58   cwd: tests/git_cache/work/test_checkout_github-com-micropython-micropython
DEBUG  util_subprocess.py:59   returncode: 0
DEBUG  util_subprocess.py:60   duration: 0.174s
DEBUG  util_subprocess.py:63   stdout: tags/v1.25.0-0-gf498a16c7d
DEBUG  util_subprocess.py:64   stderr: 
```


### Test Markers

Tests that access real internet repositories are marked with `@pytest.mark.internet`.

- Run all tests except internet tests:

```bash
pytest -m "not internet"
```

- Run internet tests only:

```bash
pytest -m "internet"
```

## Clone Strategy

With `git_bare=True`, the repository is cached as a mirror (`git clone --mirror`) in `git_cache/git-bare/`.

For each working checkout:

1. The mirror is fetched/updated.
2. The mirror is copied into a working repository.
3. The working copy checks out branch/tag/commit/PR as requested.

With `git_bare=False`, a direct non-bare clone is used.
