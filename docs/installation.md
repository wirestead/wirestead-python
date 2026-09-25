# Installation

## PyPI (recommended)

Prebuilt wheels are published for Python 3.10 through 3.13 on Linux
(`manylinux_2_28` x86_64 and aarch64), macOS (arm64), and Windows (amd64).
No C++ toolchain or Wirestead core checkout is required.

```bash
pip install wirestead
```

On a platform with no matching wheel — Intel macOS, musl/Alpine, other CPU
architectures, PyPy, or a CPython release newer than the list above — `pip`
falls back to the source distribution. That build needs a Wirestead C++ core,
which the source distribution does not vendor, so it stops with instructions
pointing at the methods below rather than completing. The compatible core ref
is recorded in `WIRESTEAD_CORE_REF`.

The methods below build the extension locally and are meant for contributors,
other Python versions/platforms, or consuming a custom core build.

## Development install with local core source

```bash
git clone https://github.com/wirestead/wirestead.git
git clone https://github.com/wirestead/wirestead-python.git

cd wirestead-python

python -m pip install -U pip
python -m pip install -e . \
  -Ccmake.define.WIRESTEAD_CORE_SOURCE_DIR=../wirestead
```

## Install with an installed Wirestead core package

```bash
cmake -S ../wirestead -B ../wirestead-build \
  -DCMAKE_BUILD_TYPE=Release \
  -DWIRESTEAD_BUILD_TESTS=OFF \
  -DWIRESTEAD_BUILD_DOCS=OFF

cmake --build ../wirestead-build --parallel
cmake --install ../wirestead-build --prefix ../wirestead-install

cd ../wirestead-python
python -m pip install . \
  -Ccmake.define.CMAKE_PREFIX_PATH=../wirestead-install
```

## Install with vcpkg

The repository includes a `vcpkg.json` manifest that depends on
`wirestead`. This path requires a vcpkg checkout that contains the official
`wirestead` port for the matching 0.9.x release line.

```bash
export VCPKG_ROOT=/path/to/vcpkg

python -m pip install . \
  -Ccmake.define.CMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake
```

## Smoke test

```bash
python -c "import wirestead; print(wirestead.__version__)"
```

## Local verification

```bash
scripts/verify.sh --core-source ../wirestead
```

Set `VCPKG_ROOT` to run vcpkg validation, or pass `--skip-vcpkg`. Add
`--installed-prefix /path/to/wirestead/install` to validate against an installed
core package.


## Core send-result compatibility

The package's release core pin remains in WIRESTEAD_CORE_REF (currently
v0.9.6). Source builds also support the structured SendResult/FanoutResult
API introduced for core v0.10; CI checks core commit
638d6a4277832cfa0e965da73abad56fedd7e6dd on Linux, macOS and Windows.

Python send, send_line, send_blocking and send_to still return actual bool
values: True means local queue admission, not delivery. Broadcast returns True
when at least one target accepted, including partial acceptance; False includes
both no targets and all targets rejecting. Python does not expose rejection
reasons or fanout counts in this compatibility change.

The asyncio facade and committed type stubs keep their existing bool contract.
Rich Python result objects and a release core-pin upgrade are separate changes.
