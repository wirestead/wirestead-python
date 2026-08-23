#!/usr/bin/env bash
# Regenerate the type stub for the compiled extension.
#
# The stub is committed rather than generated during the build: the wheels are
# built for four platforms and cross-compiled for manylinux aarch64, and
# generating would mean importing the freshly built extension on each of them.
# Committing keeps the build free of that step and puts API surface changes in
# the pull request diff. CI regenerates and diffs to catch drift.
#
# Requires the package to be installed in the active interpreter.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON:-python3}"
OUT_DIR="$(mktemp -d)"
trap 'rm -rf "$OUT_DIR"' EXIT

"$PYTHON_BIN" -m pybind11_stubgen wirestead._core -o "$OUT_DIR" --exit-code
cp "$OUT_DIR/wirestead/_core.pyi" src/wirestead/_core.pyi

echo "Wrote src/wirestead/_core.pyi"
