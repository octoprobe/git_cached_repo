# git_cached_repo
Cache a arbitrary number of git repost for fast access of branches, tags and PR's

## Programming interface

### GitSpec

A commit should is defined in a one-liner.

https://github.com/micropython/micropython.git **Checkout 'master'**\
https://github.com/micropython/micropython.git@v1.25.0 **Checkout 'v1.25.0' (might be branch/hash/tag).**\
https://github.com/micropython/micropython.git~17468 **Checkout PR '17468'. Valid PR numbers may be found on the github.com.**\
https://github.com/micropython/micropython.git~17468@v1.25.0 **Checkout PR '17468' and try to rebase on 'v1.25.0'.**\

This is how to parse a string from above:

```python
GitSpec.parse("https://github.com/micropython/micropython.git~17468@v1.25.0")
```

Github url's may be converted in above syntax using `parse_github`:

https://github.com/micropython/micropython/pull/17468/commits\
https://github.com/micropython/micropython/commits/v1.25.0\
https://github.com/micropython/micropython/commit/f498a16c7db6d4b2de200b3e0856528dfe0613c3#diff-69528cf7a1b680885089529ad7dd75caa165373a79f9d44cf32663215baebabf\
https://github.com/micropython/micropython/tree/docs/library/bluetooth\


```python
GitSpec.parse_github("https://github.com/micropython/micropython/commits/v1.24-release/")
# returns: https://github.com/micropython/micropython.git@v1.24-release
```

### CachedGitRepo

Below code will clone the repo into a directory.

```python
    cache = CachedGitRepo(
        directory_cache=DIRECTORY_CACHE,
        git_spec=https://github.com/micropython/micropython/commits/v1.24-release/,
        prefix="test_checkout_",
    )
    cache.clean_directory_work_repo(directory_cache=DIRECTORY_CACHE)
    metadata = cache.clone(
        git_clean=False,
        submodules=testparam.submodules,
        git_bare=git_bare,
    )
```

### GitMetadata

This class describes what was checked out.

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

Above output shows the commit: `7aed4bf`

Above output shows the commits of the PR. The line `(HEAD -> pr-17782)` is the current state of the PR. The line `(BASE) (origin/master, origin/HEAD, master)` is where the PR diverts from `master`.

The goal of the output is, that a developer may verify what is tested.

## Commands and logout

In the debug output you find all git commands which where executed and their duration.

```python
logging.getLogger(util_subprocess.__file__).setLevel(logging.DEBUG)
logging.getLogger(git_cached_repo.__file__).setLevel(logging.DEBUG)
```

Run all pytests with debug output:

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

## Clone strategy

A repo will first be cloned using `git clone --mirror`.

Now the repo will be file copied and presented to the calling module. On this `repo git checkout` etc. will be applied.