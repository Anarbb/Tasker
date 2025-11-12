# Packaging Guide

This document explains how to build RPM packages for Tasker.

**Note:** DEB packages for Ubuntu/Debian are currently not supported due to GTK4 styling issues. Only RPM packages for Fedora/RHEL-based distributions are available.

## Prerequisites

### For RPM (Fedora/RHEL/CentOS/Rocky/AlmaLinux)
```bash
sudo dnf install rpm-build rpmdevtools python3-devel python3-setuptools python3-gobject gtk4 polkit
```

Or use the automated script:
```bash
./build-deps-install.sh
```

## Building Locally

### RPM Package

1. Update the version in `tasker.spec` if needed (default is 1.0.0)
2. Build the package:
```bash
make rpm VERSION=1.0.0
```

The built RPM will be in `~/rpmbuild/RPMS/noarch/tasker-1.0.0-1.*.noarch.rpm`

### Manual RPM Build

If you prefer to build manually without the Makefile:

```bash
# Setup RPM build tree
rpmdev-setuptree

# Create source tarball
mkdir -p /tmp/tasker-1.0.0
cp -r *.py *.css *.desktop *.spec *.png setup.py README.md LICENSE /tmp/tasker-1.0.0/
cd /tmp && tar czf tasker-1.0.0.tar.gz tasker-1.0.0
cp /tmp/tasker-1.0.0.tar.gz ~/rpmbuild/SOURCES/

# Copy spec file and build
cp tasker.spec ~/rpmbuild/SPECS/
rpmbuild -ba ~/rpmbuild/SPECS/tasker.spec
```

## Using GitHub Actions

### Automatic Release Builds

The easiest way to create a release with packages:

1. Go to the **Actions** tab in GitHub
2. Select **Build Packages and Create Release** workflow
3. Click **Run workflow**
4. Enter the version number (e.g., `1.0.0`)
5. Optionally mark as pre-release
6. Click **Run workflow**

The workflow will:
- Build RPM packages (both binary and source RPM)
- Create a GitHub release with tag `v{version}`
- Upload packages to the release
- Generate installation instructions

Users can then download and install directly from the [Releases page](https://github.com/Anarbb/tasker/releases).

### What Gets Built

- **Binary RPM** (`tasker-1.0.0-1.*.noarch.rpm`): Ready-to-install package
- **Source RPM** (`tasker-1.0.0-1.*.src.rpm`): Source package for rebuilding

## Package Contents

The RPM package installs:
- Python modules (`main.py`, `cron_manager.py`, `task_dialog.py`) to Python's site-packages
- Executable script `tasker` to `/usr/bin/`
- Desktop file to `/usr/share/applications/me.arbaoui.tasker.desktop`
- Icon to `/usr/share/icons/hicolor/48x48/apps/tasker.png`
- CSS file to `/usr/share/tasker/ui.css`
- Documentation (README.md, LICENSE) to `/usr/share/doc/tasker/`

## Testing Packages

### Test RPM Installation
```bash
# Install
sudo dnf install ~/rpmbuild/RPMS/noarch/tasker-1.0.0-1.*.noarch.rpm

# Verify installation
which tasker
tasker --help

# Launch the application
tasker
```

### Verify Package Contents
```bash
# List files in the RPM
rpm -qlp ~/rpmbuild/RPMS/noarch/tasker-1.0.0-1.*.noarch.rpm

# Check dependencies
rpm -qRp ~/rpmbuild/RPMS/noarch/tasker-1.0.0-1.*.noarch.rpm
```

## Troubleshooting

### RPM Build Fails
- Check that all build dependencies are installed: `./build-deps-install.sh`
- Verify `tasker.spec` syntax: `rpmlint tasker.spec`
- Check build logs in `~/rpmbuild/BUILD/`
- Review the spec file for correct paths and file lists

### Installation Issues

**"nothing provides /usr/sbin/python3" error:**
- This was fixed in version 1.0.1 with the `%py3_shebang_fix` macro
- Rebuild the package or download the latest release

**Missing dependencies:**
```bash
# Install dependencies manually
sudo dnf install python3-gobject gtk4 polkit

# Then retry installation
sudo dnf install ./tasker-1.0.0-1.*.noarch.rpm
```

### Runtime Issues
- Ensure GTK4 is installed: `sudo dnf install gtk4`
- Check Python version: `python3 --version` (requires 3.10+)
- Verify PyGObject installation: `python3 -c "import gi; gi.require_version('Gtk', '4.0')"`

## For Developers

### Version Bumping Checklist

When releasing a new version:

1. Update version in `tasker.spec` (`%define version X.Y.Z`)
2. Update version in `setup.py` (`version="X.Y.Z"`)
3. Update changelog in `tasker.spec`
4. Commit changes
5. Run GitHub Actions workflow with the new version
6. Verify the release on GitHub

### Local Testing Before Release

```bash
# Build locally
make rpm VERSION=1.0.0

# Install in a VM or container
podman run -it fedora:latest
# Inside container:
dnf install ./tasker-1.0.0-1.*.noarch.rpm
tasker
```

