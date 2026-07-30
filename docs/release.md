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

## vcpkg Baseline

`VCPKG_BASELINE` pins the `microsoft/vcpkg` commit that CI and the release
workflow check out. Boost is supplied from that checkout, so leaving it
unpinned made every run depend on whatever `vcpkg` had on its default branch at
that moment — the drift that broke the Windows consumer sample with LNK2038
runtime-library mismatches in `wirestead#552`.

Bump it deliberately, in its own commit, and let CI validate the new commit:

```bash
git ls-remote https://github.com/microsoft/vcpkg.git HEAD
```

The pinned commit must contain the `wirestead` port for the matching release
line. A full 40-character SHA is required; `tests/test_project_metadata.py`
rejects a branch name or short SHA.

## Release Assets

The Release workflow always builds the source distribution and wheels as
GitHub Actions artifacts. It publishes them to a GitHub Release only for a
`v*` tag push or when a manual run enables `upload`.

Wheel files keep their standard Python wheel filenames so they remain directly
installable with `pip install ./<wheel-file>.whl`. Artifact grouping follows the
same platform-oriented style as the Wirestead core release workflow:

- `manylinux_2_28-x86_64`
- `manylinux_2_28-aarch64`
- `macos-15-arm64`
- `windows-amd64`

The Linux wheels are built with `cibuildwheel` against the `manylinux_2_28`
image so they carry a `manylinux` platform tag PyPI will accept (a plain
`linux_x86_64`/`linux_aarch64` wheel built on a stock Ubuntu runner is
rejected by PyPI uploads). The aarch64 leg runs on a native `ubuntu-24.04-arm`
hosted runner rather than x86_64-with-QEMU, so build times stay comparable to
the x86_64 leg. Boost is supplied through a scratch `vcpkg` install inside the
manylinux container, the same dependency source already used for macOS and
Windows wheels.

The source distribution is built with `python -m build --sdist`.

To validate the current release workflow without publishing, run:

```bash
gh workflow run release.yml \
  -f source_ref=main \
  -f tag_name=v0.9.1 \
  -f upload=false \
  -f publish_pypi=false
```

`source_ref` selects the `wirestead-python` Git ref. The compatible core ref is
read from `WIRESTEAD_CORE_REF`. `tag_name` must match the canonical package
version in `src/wirestead/_version.py`; the workflow rejects a mismatch before
publishing.

For an existing tag, run the Release workflow manually with both `source_ref`
and `tag_name` set to that tag and `upload` enabled. Future `v*` tag pushes
trigger the same workflow automatically.

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

   Both one-time steps above are already done for the `wirestead` project —
   only steps 3-4 are needed for each new release.
3. Run the Release workflow manually (`workflow_dispatch`) with:
   - `source_ref` set to the release tag to publish.
   - `tag_name` set to the release tag to publish.
   - `publish_pypi` set to `true`.
   - `pypi_target` set to `testpypi` first. Verify with
     `pip install --index-url https://test.pypi.org/simple/ wirestead`.
4. Re-run with `pypi_target` set to `pypi` once the TestPyPI install has been
   verified.

### Known pitfalls

These surfaced the first time the workflow actually ran end to end and are
fixed in the current `release.yml`, but are worth knowing if the manylinux
job or dependency pins change again:

- `pypa/cibuildwheel` doesn't publish a bare major-version tag (`v4`) the way
  `actions/checkout` does — pin to an actual tag (`v4.1`, `v4.1.1`, etc.).
- Keep the Python version matrix aligned across Linux, macOS, Windows,
  `requires-python`, README support tables, and PyPI classifiers. Before
  expanding the matrix again, confirm `actions/setup-python`, pybind11,
  scikit-build-core, and cibuildwheel support the target CPython ABI tags.
- Test-tooling floors track the interpreter range. `pytest-asyncio` requires
  Python 3.10 from 1.3 onward and 3.9 from 1.0 onward, so the plain
  `pytest-asyncio>=1.4.0` in `pyproject.toml`'s `test` extra is only valid
  while `requires-python` stays at 3.10 or newer. Lowering the floor again
  would need environment markers. `CIBW_TEST_REQUIRES` and the CI jobs install
  `pytest-asyncio` unpinned, so CI never exercises the extra as a consumer
  would — the "Validate test extra resolves" step in `ci.yml` covers that
  blind spot and should stay whenever the Python matrix changes.
- PyPI validates `classifiers` against the trove-classifiers list at upload
  time, not at build time — an invalid entry (e.g. a C++-standard
  sub-classifier that doesn't exist, unlike Python's) only fails on the
  actual `twine upload`, after wheels have already built successfully.
