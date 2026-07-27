#!/usr/bin/env python3
"""Install a built wheel in a fresh venv and run the consumer smoke test."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


def _python_in_venv(venv_dir: Path) -> Path:
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _current_cp_tag() -> str:
    return f"cp{sys.version_info.major}{sys.version_info.minor}"


def _select_wheel(wheel_dir: Path) -> Path:
    cp_tag = _current_cp_tag()
    wheels = sorted(p for p in wheel_dir.rglob("*.whl") if cp_tag in p.name)
    if not wheels:
        all_wheels = "\n".join(str(p) for p in sorted(wheel_dir.rglob("*.whl")))
        raise SystemExit(f"no {cp_tag} wheel found under {wheel_dir}\n{all_wheels}")
    if len(wheels) > 1:
        listed = "\n".join(str(p) for p in wheels)
        raise SystemExit(f"multiple {cp_tag} wheels found:\n{listed}")
    return wheels[0]


def _run(command: list[str], *, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    print("+ " + " ".join(command), flush=True)
    return subprocess.run(command, cwd=cwd, check=check, text=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel-dir", required=True)
    parser.add_argument("--project-root", required=True)
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()

    expected_version = args.expected_version[1:] if args.expected_version.startswith("v") else args.expected_version
    wheel_dir = Path(args.wheel_dir).resolve()
    project_root = Path(args.project_root).resolve()
    wheel = _select_wheel(wheel_dir)
    print(f"selected wheel: {wheel}", flush=True)

    venv_dir = Path(tempfile.mkdtemp(prefix="wirestead-wheel-consumer-"))
    work_dir = Path(tempfile.mkdtemp(prefix="wirestead-wheel-work-"))
    try:
        _run([sys.executable, "-m", "venv", str(venv_dir)])
        python = _python_in_venv(venv_dir)

        existing = _run([str(python), "-m", "pip", "show", "wirestead"], check=False)
        if existing.returncode == 0:
            raise SystemExit("fresh consumer venv unexpectedly already contains wirestead")
        print("preinstall check: wirestead is absent", flush=True)

        _run([str(python), "-m", "pip", "install", str(wheel)])
        _run(
            [
                str(python),
                str(project_root / "scripts" / "consumer_smoke.py"),
                "--project-root",
                str(project_root),
                "--expected-version",
                expected_version,
            ],
            cwd=work_dir,
        )
    finally:
        shutil.rmtree(venv_dir, ignore_errors=True)
        shutil.rmtree(work_dir, ignore_errors=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
