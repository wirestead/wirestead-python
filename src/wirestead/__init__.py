import os
from pathlib import Path
import sys

from ._version import __version__

_dll_dir_handles = []
_registered_dll_dirs = set()


def _register_windows_dll_directory(directory: Path) -> None:
    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return

    try:
        resolved_dir = str(directory.resolve())
        if not os.path.isdir(resolved_dir) or resolved_dir in _registered_dll_dirs:
            return

        handle = os.add_dll_directory(resolved_dir)
        _dll_dir_handles.append(handle)
        _registered_dll_dirs.add(resolved_dir)
    except Exception:
        pass


def _add_windows_dll_directories(package_dir: Path) -> None:
    if os.name != "nt" or not hasattr(os, "add_dll_directory"):
        return

    _register_windows_dll_directory(package_dir)

    for path_str in os.environ.get("WIRESTEAD_WINDOWS_DLL_DIRS", "").split(
        os.pathsep
    ):
        if path_str:
            _register_windows_dll_directory(Path(path_str))

    for path_str in os.environ.get("PATH", "").split(os.pathsep):
        if not path_str:
            continue
        path_lower = path_str.lower()
        if (
            "vcpkg" in path_lower
            or "wirestead" in path_lower
            or "unilink" in path_lower
        ):
            _register_windows_dll_directory(Path(path_str))


try:
    _add_windows_dll_directories(Path(__file__).resolve().parent)
    from ._core import *
except ImportError as exc:
    raise ImportError(
        "Failed to import the Wirestead Python extension. "
        "Make sure the package was built with a compatible Wirestead C++ core."
    ) from exc

__all__ = [
    name
    for name in globals()
    if not name.startswith("_") and name not in {"os", "Path", "sys"}
]

del os, Path, sys
