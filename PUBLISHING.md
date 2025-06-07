# Publishing python-kanka to PyPI

This document describes how to publish new releases of python-kanka to PyPI.

## Prerequisites

1. **PyPI Account**: You need an account on [PyPI](https://pypi.org/) and optionally [Test PyPI](https://test.pypi.org/)
2. **PyPI API Token**: Generate an API token from your PyPI account settings
3. **GitHub Repository Access**: Push access to the repository for creating tags and releases

## Setting up GitHub Secrets

Add your PyPI API token as a GitHub secret:

1. Go to Settings → Secrets and variables → Actions
2. Add a new repository secret named `PYPI_API_TOKEN` with your PyPI token
3. (Optional) Add `TEST_PYPI_API_TOKEN` for Test PyPI

Note: The GitHub Actions workflow uses trusted publishing, so you may not need tokens if you configure it on PyPI.

## Publishing Process

### 1. Update Version Number

Edit `setup.py` and update the version number:

```python
version="2.0.1",  # Update this
```

### 2. Update CHANGELOG.md

Document all changes since the last release in `CHANGELOG.md`.

### 3. Commit Changes

```bash
git add setup.py CHANGELOG.md
git commit -m "Bump version to 2.0.1"
git push origin main
```

### 4. Create a Git Tag

```bash
git tag -a v2.0.1 -m "Release version 2.0.1"
git push origin v2.0.1
```

### 5. Create a GitHub Release

1. Go to the repository's Releases page
2. Click "Create a new release"
3. Choose the tag you just created
4. Set the release title (e.g., "v2.0.1")
5. Add release notes (can copy from CHANGELOG.md)
6. Click "Publish release"

The GitHub Actions workflow will automatically:
- Build the package
- Run tests
- Upload to PyPI

### 6. Verify the Release

Check that the package is available:

```bash
pip install --upgrade python-kanka
```

## Manual Publishing (Alternative)

If you need to publish manually:

### 1. Install Build Tools

```bash
pip install --upgrade build twine
```

### 2. Build the Package

```bash
python -m build
```

This creates files in the `dist/` directory:
- `python_kanka-2.0.1-py3-none-any.whl`
- `python_kanka-2.0.1.tar.gz`

### 3. Check the Package

```bash
twine check dist/*
```

### 4. Upload to Test PyPI (Optional)

```bash
twine upload --repository testpypi dist/*
```

Test installation:
```bash
pip install --index-url https://test.pypi.org/simple/ python-kanka
```

### 5. Upload to PyPI

```bash
twine upload dist/*
```

## Testing Workflow Without Release

You can manually trigger the publish workflow to test on Test PyPI:

1. Go to Actions → Publish to PyPI
2. Click "Run workflow"
3. Leave "Publish to Test PyPI" checked
4. Click "Run workflow"

## Version Management

Consider using a tool like `bump2version` for consistent version updates:

```bash
pip install bump2version

# For patch release (2.0.0 → 2.0.1)
bump2version patch

# For minor release (2.0.1 → 2.1.0)
bump2version minor

# For major release (2.1.0 → 3.0.0)
bump2version major
```

## Troubleshooting

### Package Not Found After Publishing

PyPI can take a few minutes to update. Wait and try again.

### Build Errors

Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
pip install -r dev-requirements.txt
```

### Authentication Errors

- Verify your API token is correct
- Ensure the token has upload permissions
- Check if you're using the correct repository URL

## Post-Release Tasks

After a successful release:

1. Update the version in `setup.py` to the next development version (e.g., "2.0.2.dev0")
2. Commit with message "Start development on 2.0.2"
3. Announce the release (optional)
