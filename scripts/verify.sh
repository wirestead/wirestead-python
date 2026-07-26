#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON_BIN="${PYTHON:-python3}"
RUN_SOURCE=1
RUN_VCPKG=1
RUN_INSTALLED=0
RUN_INTEGRATION=0
CORE_SOURCE_DIR="${WIRESTEAD_CORE_SOURCE_DIR:-}"
INSTALLED_PREFIX="${WIRESTEAD_INSTALL_PREFIX:-}"

if [[ -z "$CORE_SOURCE_DIR" && -d "$PROJECT_ROOT/../wirestead" ]]; then
  CORE_SOURCE_DIR="$PROJECT_ROOT/../wirestead"
elif [[ -z "$CORE_SOURCE_DIR" && -d "$PROJECT_ROOT/../unilink" ]]; then
  CORE_SOURCE_DIR="$PROJECT_ROOT/../unilink"
fi

usage() {
  cat <<'EOF'
Usage: scripts/verify.sh [options]

Options:
  --core-source PATH        Path to the Wirestead C++ core source tree.
  --skip-source             Skip the local core source package install.
  --skip-vcpkg              Skip the vcpkg package install.
  --installed-prefix PATH   Run installed-package validation with PATH.
  --run-integration         Enable loopback integration tests.
  --help, -h                Show this help message.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --core-source)
      if [[ $# -lt 2 ]]; then
        echo "--core-source requires a path" >&2
        exit 1
      fi
      CORE_SOURCE_DIR="$2"
      RUN_SOURCE=1
      shift 2
      ;;
    --skip-source)
      RUN_SOURCE=0
      shift
      ;;
    --skip-vcpkg)
      RUN_VCPKG=0
      shift
      ;;
    --installed-prefix)
      if [[ $# -lt 2 ]]; then
        echo "--installed-prefix requires a path" >&2
        exit 1
      fi
      INSTALLED_PREFIX="$2"
      RUN_INSTALLED=1
      shift 2
      ;;
    --run-integration)
      RUN_INTEGRATION=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

section() {
  printf '\n===== %s =====\n' "$*"
}

create_venv() {
  local name="$1"
  local venv_dir="$PROJECT_ROOT/build/verify-${name}-venv"
  rm -rf "$venv_dir"
  "$PYTHON_BIN" -m venv "$venv_dir"
  echo "$venv_dir/bin/python"
}

run_python_smoke() {
  local python="$1"
  "$python" -c "import wirestead; print(wirestead.__version__)"
}

run_tests() {
  local python="$1"
  if [[ "$RUN_INTEGRATION" -eq 1 ]]; then
    WIRESTEAD_PYTHON_RUN_LOOPBACK_TESTS=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$python" -m pytest -q -p pytest_asyncio.plugin -m "not serial"
  else
    PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 "$python" -m pytest -q -p pytest_asyncio.plugin -m "not serial and not integration"
  fi
}

install_and_test() {
  local name="$1"
  shift
  local install_args=("$@")
  local python
  python="$(create_venv "$name")"

  section "Installing Python tooling for ${name}"
  "$python" -m pip install -U pip
  "$python" -m pip install "pytest>=8,<9" "pytest-asyncio>=1.4.0" scikit-build-core "pybind11>=2.11,<3"

  if [[ "$name" == "installed" ]]; then
    install_args+=(
      "--config-settings=cmake.define.pybind11_DIR=$("$python" -m pybind11 --cmakedir)"
    )
  fi

  section "Installing Wirestead Python via ${name}"
  "$python" -m pip install . --no-build-isolation "${install_args[@]}"

  section "Running smoke tests for ${name}"
  run_python_smoke "$python"
  run_tests "$python"
}

section "Checking whitespace"
git diff --check

if [[ "$RUN_SOURCE" -eq 1 ]]; then
  if [[ -z "$CORE_SOURCE_DIR" ]]; then
    echo "WIRESTEAD_CORE_SOURCE_DIR is not set and ../wirestead does not exist." >&2
    echo "Pass --core-source PATH or --skip-source." >&2
    exit 1
  elif [[ ! -f "$CORE_SOURCE_DIR/CMakeLists.txt" ]]; then
    echo "Core source path does not contain CMakeLists.txt: $CORE_SOURCE_DIR" >&2
    exit 1
  fi
  install_and_test \
    "source" \
    "--config-settings=cmake.define.WIRESTEAD_CORE_SOURCE_DIR=$CORE_SOURCE_DIR"
fi

if [[ "$RUN_VCPKG" -eq 1 ]]; then
  if [[ -z "${VCPKG_ROOT:-}" ]]; then
    echo "VCPKG_ROOT is not set. Set VCPKG_ROOT or pass --skip-vcpkg." >&2
    exit 1
  elif [[ ! -f "${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" ]]; then
    echo "VCPKG_ROOT does not contain scripts/buildsystems/vcpkg.cmake." >&2
    echo "Set VCPKG_ROOT to a bootstrapped vcpkg checkout or pass --skip-vcpkg." >&2
    exit 1
  fi

  vcpkg_settings=(
    "--config-settings=cmake.define.CMAKE_TOOLCHAIN_FILE=${VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake"
  )
  if [[ -n "${VCPKG_TARGET_TRIPLET:-}" ]]; then
    vcpkg_settings+=(
      "--config-settings=cmake.define.VCPKG_TARGET_TRIPLET=${VCPKG_TARGET_TRIPLET}"
    )
  fi
  install_and_test "vcpkg" "${vcpkg_settings[@]}"
fi

if [[ "$RUN_INSTALLED" -eq 1 ]]; then
  if [[ -z "$INSTALLED_PREFIX" ]]; then
    echo "Installed prefix is empty" >&2
    exit 1
  fi
  install_and_test \
    "installed" \
    "--config-settings=cmake.define.CMAKE_PREFIX_PATH=$INSTALLED_PREFIX"
fi

section "Verification complete"
