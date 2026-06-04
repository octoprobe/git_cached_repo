# git_cached_repo
Cache a arbitrary number of git repost for fast access of branches, tags and PR's


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
