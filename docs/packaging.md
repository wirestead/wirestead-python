# Packaging & PyInstaller Notes

`Wirestead Python` includes the compiled C++ extension `wirestead._core`.

Applications that bundle `Wirestead Python` with tools such as PyInstaller must
ensure that:

- `wirestead._core` compiled extension is included
- Required Wirestead core C++ runtime libraries are discoverable
- On Windows, DLL directories are configured correctly
- vcpkg or installed runtime DLLs are included in the bundle when needed

`src/wirestead/__init__.py` contains logic to configure Windows DLL directories
at import time. When packaging, make sure that any required shared libraries
(like `.dll` or `.so`) are placed in the application bundle directory so they
can be loaded by the extension.
