from __future__ import annotations

import logging
import pathlib
import subprocess
import time
import typing

logger = logging.getLogger(__file__)


class SubprocessExitCodeException(Exception):
    pass


def subprocess_run(
    args: list[str],
    cwd: pathlib.Path,
    env: dict[str, str] | None = None,
    timeout_s: float = 10.0,
) -> str | None:
    """
    Wrappsr around 'subprocess()'
    """
    assert isinstance(args, list)
    assert isinstance(cwd, pathlib.Path)
    assert isinstance(env, dict | None)
    assert isinstance(timeout_s, float | None)

    if env is not None:
        for key, value in env.items():
            assert isinstance(key, str)
            assert isinstance(value, str)

    args_text = " ".join(args)

    begin_s = time.monotonic()
    try:
        proc = subprocess.run(
            # Common args
            args=args,
            check=False,
            text=True,
            cwd=str(cwd),
            env=env,
            timeout=timeout_s,
            # Specific args
            capture_output=True,
        )

    except subprocess.TimeoutExpired as e:
        logger.info(f"EXEC {e!r}")
        # logger.exception(e)
        raise

    def log(f: typing.Callable[[str], None]) -> None:
        f(f"EXEC {args_text}")
        f(f"  cwd: {cwd}")
        f(f"  returncode: {proc.returncode}")
        f(f"  duration: {time.monotonic() - begin_s:0.3f}s")
        stdout = proc.stdout.strip()
        stderr = proc.stderr.strip()
        f(f"  stdout: {stdout}")
        f(f"  stderr: {stderr}")

    if proc.returncode != 0:
        log(logger.warning)
        msg = f"EXEC failed with returncode={proc.returncode}: {args_text}"
        msg += f"\n{proc.stdout.strip()}\n{proc.stderr.strip()}"
        raise SubprocessExitCodeException(msg)

    log(logger.debug)

    return proc.stdout.strip()
