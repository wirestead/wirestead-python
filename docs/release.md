# Release Policy

## Versioning

Wirestead Python follows the Wirestead C++ core release line.

| Wirestead Python | Wirestead core |
|---|---|
| 0.9.x | 0.9.x |

Wirestead Python uses the same minor version as the supported Wirestead C++ core
release line. Patch releases should align with the matching Wirestead C++ core
patch release when the core tag exists.

Patch releases may contain Python packaging, binding, documentation, or CI fixes
without requiring a matching Wirestead core patch release, as long as they remain
compatible with the same core minor release line.

## Release Checklist

1. Confirm the target Wirestead core release line.
2. Update `pyproject.toml`, `CMakeLists.txt`, and `src/wirestead/_version.py`.
3. Update `CHANGELOG.md` and `docs/compatibility.md`.
4. Run local verification against the supported core consumption paths.
5. Push the release commit and confirm CI passes on Linux, macOS, and Windows.
6. Create and push the matching git tag, for example `v0.9.0`.
7. Confirm the Release workflow uploaded the source distribution and wheels to
   the GitHub release.
8. Optionally publish to PyPI following [Publishing to PyPI](#publishing-to-pypi)
   below, starting with `testpypi`.

## Local Verification

```bash
scripts/verify.sh --core-source ../wirestead
```

Set `VCPKG_ROOT` to a vcpkg checkout that contains the official `wirestead`
port for the matching 0.9.x release line. To include installed-package
validation, first install the matching core release and pass the prefix:

```bash
scripts/verify.sh \
  --core-source ../wirestead \
  --installed-prefix ../wirestead-install
```

## Release Assets

The Release workflow always publishes GitHub release assets (source
distribution and wheels).

Wheel files keep their standard Python wheel filenames so they remain directly
installable with `pip install ./<wheel-file>.whl`. Artifact grouping follows the
same platform-oriented style as the Wirestead core release workflow:

- `manylinux_2_28-x86_64`
- `macos-15-arm64`
- `windows-amd64`

The Linux wheel is built with `cibuildwheel` against the `manylinux_2_28` image
so it carries a `manylinux` platform tag PyPI will accept (a plain
`linux_x86_64` wheel built on a stock Ubuntu runner is rejected by PyPI
uploads). Boost is supplied through a scratch `vcpkg` install inside the
manylinux container, the same dependency source already used for macOS and
Windows wheels.

The source distribution is built with `python -m build --sdist`.

For an existing tag, run the Release workflow manually with `tag_name` set to
that tag and `upload` enabled. Future `v*` tag pushes trigger the same workflow
automatically.

## Publishing to PyPI

PyPI publishing is a separate, manual opt-in step — it does not run on tag
push. This is deliberate: a bad upload under a given version cannot be
replaced, only yanked, so publishing stays a deliberate action until the flow
has proven itself.

1. One-time setup on PyPI, for each of `testpypi` (test.pypi.org) and `pypi`
   (pypi.org):
   - Register a "pending publisher" for the `wirestead` project name under
     Account Settings → Publishing, pointing at
     `wirestead/wirestead-python`, workflow `release.yml`, environment name
     matching the index (`testpypi` or `pypi`).
   - No API token is stored in the repo — publishing uses OIDC Trusted
     Publishing.
2. One-time setup on GitHub: create the `testpypi` and `pypi` environments
   under repo Settings → Environments so they match the names referenced by
   the `publish-pypi` job and registered on PyPI.
3. Run the Release workflow manually (`workflow_dispatch`) with:
   - `tag_name` set to the release tag to publish.
   - `publish_pypi` set to `true`.
   - `pypi_target` set to `testpypi` first. Verify with
     `pip install --index-url https://test.pypi.org/simple/ wirestead`.
4. Re-run with `pypi_target` set to `pypi` once the TestPyPI install has been
   verified.
