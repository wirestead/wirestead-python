# Compatibility

## Core compatibility

Wirestead Python does not implement transports itself. It binds to the Wirestead
C++ core library.

| Wirestead Python | Supported Wirestead core |
|---|---|
| 0.9.x | 0.9.x |

## Validated core versions

The current release line is validated against:

| Wirestead Python | Validated Wirestead core refs |
|---|---|
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

Wheel builds use pybind11 2.13 or newer. Keep CI, release, and local
verification build dependency ranges aligned with `pyproject.toml`.

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
| Windows | API exposed; loopback validation pending | pending |
