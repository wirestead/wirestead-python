# Compatibility

## Python and Ubuntu support policy

The Python floor remains `>=3.10`. Python 3.8 and 3.9 are not supported.
The next release targets standard (GIL-enabled) CPython 3.10 through 3.14.
3.14 passed CI and release-wheel validation on 2026-10-20
([Release run 39335390480](https://github.com/wirestead/wirestead-python/actions/runs/39335390480));
its wheels are not yet published. PyPy and free-threaded CPython are separate
targets and are not currently supported.

New upstream-supported CPython versions become supported only after build,
test, and installed-wheel checks pass. Already-supported Ubuntu LTS default
interpreters remain compatibility targets through that LTS's standard security
maintenance period, even if upstream CPython support ends earlier. This is a
Wirestead compatibility commitment, not a promise to patch the interpreter.
Ubuntu Pro/ESM does not automatically extend Wirestead's support window.

The following Ubuntu userspace checks run on both x86_64 and aarch64 using
the same `manylinux_2_28` release wheels:

| Ubuntu LTS | Python tested | Support scope | Standard Ubuntu maintenance ends |
|---|---|---|---|
| 20.04 | Separately installed 3.12 | Compatibility target; default 3.8 excluded | May 2025 (ended) |
| 22.04 | Default 3.10 | LTS default-interpreter target | May 2027 |
| 24.04 | Default 3.12 | Primary development and validation environment | May 2029 |
| 26.04 | Default 3.14 | New LTS default-interpreter target | May 2031 |

All eight Ubuntu/architecture combinations passed the Release workflow
validation of 2026-10-20
([run 39335390480](https://github.com/wirestead/wirestead-python/actions/runs/39335390480);
`upload=false`, `publish_pypi=false`, vcpkg baseline `664933b8d385`). Each later
release must pass them again: both publishing jobs require the Ubuntu wheel
checks. Container checks validate userspace installation
and TCP, UDP, and UDS loopback; they do not certify each distribution's kernel or
physical serial hardware. Additional Python/Ubuntu combinations are not implied
by the table. Ubuntu 20.04 is a compatibility exception, reviewed at each minor
release, rather than a commitment to its ESM lifetime.

The Linux wheel baseline stays at `manylinux_2_28` on x86_64 and aarch64.
Wheel consumers do not need a C++ compiler. Source builds separately require
a compatible C++20 toolchain, CMake, dependencies, and the matching core;
supporting an OS for wheel installation does not promise a build with its
default compiler. See [installation](installation.md) for supported build paths.

### Removing support

- Announce Python or OS removals at least six months before they take effect.
- Raise Python or Linux binary minimums only in a minor release (or major
  release), never in a patch release.
- Do not remove Python 3.10 before Ubuntu 22.04 standard maintenance ends in
  May 2027. This policy is not itself a removal announcement or a fixed date.
- When raising the floor, consider upstream support, retained LTS defaults,
  dependency availability, and actual users, including whether 3.11 is still
  needed. Publish the last compatible Wirestead release and migration path.
- Old releases remaining downloadable does not imply ongoing maintenance.
  A 3.8/3.9 legacy line requires an identified consumer, explicit platforms,
  maintenance scope, and an end date; no such line is maintained by default.

Sources: [Ubuntu release cycle](https://ubuntu.com/about/release-cycle),
[Ubuntu Python versions](https://ubuntu.com/developers/docs/reference/availability/python/),
[Ubuntu 26.04 changes](https://documentation.ubuntu.com/release-notes/26.04/summary-for-lts-users/),
[CPython lifecycle](https://devguide.python.org/versions/), and
[manylinux tags](https://packaging.python.org/en/latest/specifications/platform-compatibility-tags/).

## Core compatibility

Wirestead Python does not implement transports itself. It binds to the Wirestead
C++ core library.

| Wirestead Python | Supported Wirestead core |
|---|---|
| 0.10.x | 0.10.x |
| 0.9.x | 0.9.x |

## Validated core versions

The current release line is validated against:

| Wirestead Python | Validated Wirestead core refs |
|---|---|
| 0.10.1 | v0.10.1 |
| 0.10.0 | v0.10.0 |
| 0.9.6 | v0.9.6 |
| 0.9.5 | v0.9.5 |
| 0.9.4 | v0.9.4 |
| 0.9.3 | v0.9.3 |
| 0.9.2 | v0.9.2 |
| 0.9.1 | v0.9.1 |
| 0.9.0 | v0.9.0 |

Additional patch versions in the same minor line may also work, but CI
validation tracks the versions listed above.

## Versioning

Wirestead Python follows the Wirestead C++ core minor release line.

Patch versions may differ when Python packaging, binding, documentation, or CI
fixes do not require a matching Wirestead core patch release.

## Stability

The Python package is experimental until the C++ core public API reaches a
stable release line.

## ABI policy

Python wheels may statically link or bundle the Wirestead C++ core. C++ ABI
stability is not guaranteed across incompatible core versions before v1.0.

## Dependency policy

Wheel builds use pybind11 3.x, with 3.1.0 or newer required for the current
Python matrix. Keep CI, release, and local verification build dependency
ranges aligned with `pyproject.toml`; they drifted once, and the untested half
of the range only surfaced when a dependency bump tried to use it.

## UDS support

`Wirestead Python` exposes `UdsClient`, `UdsServer`, `AsyncUdsClient`, and
`AsyncUdsServer` when the underlying Wirestead core is built with UDS support.

UDS support is intended for local IPC use cases such as Packet Probe Viewer
integration.

Validation status:

| Platform | UDS Python API | Loopback test |
|---|---:|---:|
| Linux | supported | tested |
| macOS | supported | tested |
| Windows | Supported | binding and installed-wheel loopback |
