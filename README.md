# Tasker

<p align="center">
  <img src="tasker.png" alt="Tasker Icon" width="200"/>
</p>

## Features

- **Simple interface**: Create, edit, and delete cron jobs without touching the command line
- **User and system crontabs**: Switch between managing your user crontab and the system crontab
- **Easy scheduling**: Simple mode for common schedules (hourly, daily, weekly, monthly) or advanced mode for full cron syntax
- **Task names**: Add descriptive names/comments to your cron jobs
- **Modern UI**: Clean GTK4 interface that fits in with GNOME/GTK-based desktops

## Requirements

- Python 3.10+
- PyGObject (GTK4 bindings)
- polkit (for system crontab support)

On Fedora-based distributions:

```bash
# Fedora/RHEL/CentOS/Rocky/AlmaLinux
sudo dnf install python3-gobject gtk4 polkit
```

On other distributions:

```bash
# Debian/Ubuntu (experimental support - may have UI issues)
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0 polkit

# Arch Linux
sudo pacman -S python-gobject gtk4 polkit
```

**Note:** Ubuntu/Debian support is currently experimental and may have styling/UI issues with GTK4.

## Installation

### From GitHub Release (Recommended)

Download the latest release from the [GitHub Releases](https://github.com/Anarbb/tasker/releases) page.

#### Fedora/RHEL/CentOS/Rocky/AlmaLinux

```bash
# Download the RPM from the latest release
wget https://github.com/Anarbb/tasker/releases/latest/download/tasker-1.0.0-1.fc42.noarch.rpm

# Install with dnf
sudo dnf install ./tasker-1.0.0-1.fc42.noarch.rpm
```

**Or manually:**
1. Visit [Releases](https://github.com/Anarbb/tasker/releases/latest)
2. Download the `.rpm` file
3. Double-click to install, or use: `sudo dnf install ./tasker-*.rpm`

#### Ubuntu/Debian (Not Currently Supported)

Ubuntu/Debian packages are currently disabled due to GTK4 styling issues. For these distributions, please use the "From Source" installation method below.

### From Source

For distributions without a package or if you want the latest development version:

```bash
# Clone the repository
git clone https://github.com/Anarbb/tasker.git
cd tasker

# Install dependencies (Fedora example)
sudo dnf install python3-gobject gtk4 polkit

# Run directly
python3 main.py

# Or install system-wide
sudo python3 setup.py install
tasker
```

## Usage

1. **Add a task**: Click the "Add Task" button
2. **Set a name**: Give your task a descriptive name (optional)
3. **Choose schedule**: 
   - Use simple mode for common schedules (hourly, daily, weekly, monthly)
   - Toggle "Advanced" for full cron syntax control
4. **Enter command**: Provide the full path to the script or command to run
5. **Save**: Click "Save" to add the task to your crontab

### Managing Tasks

- **Edit**: Click the edit icon on any task
- **Delete**: Click the delete icon (you'll be asked to confirm)
- **Refresh**: Click the refresh button to reload tasks from crontab
- **System crontab**: Toggle the "System" switch in the header to manage system-wide cron jobs (requires authentication)

## Notes

- When switching to system crontab mode, you'll be prompted for authentication via pkexec
- The application reads and writes directly to your crontab, so be careful when editing manually
- Advanced mode supports all standard cron syntax (wildcards, ranges, lists, etc.)

## Building Packages

### Building RPM (Fedora/RHEL/CentOS)

Install build dependencies:
```bash
sudo dnf install rpm-build rpmdevtools python3-devel python3-setuptools
```

Build the package:
```bash
make rpm VERSION=1.0.0
```

The RPM will be in `~/rpmbuild/RPMS/noarch/`.

### Automated Builds via GitHub Actions

This repository uses GitHub Actions to automatically build packages:

1. Go to the **Actions** tab in the GitHub repository
2. Select **Build Packages and Create Release** workflow
3. Click **Run workflow**
4. Enter the version number (e.g., `1.0.0`)
5. Click **Run workflow**

The workflow will:
- Build RPM packages for Fedora/RHEL-based distributions
- Create a GitHub release with the version tag
- Upload all packages to the release
- Users can download directly from the [Releases page](https://github.com/Anarbb/tasker/releases)

**Note:** DEB packages are currently disabled in the workflow due to GTK4 compatibility issues on Ubuntu/Debian.

## Star History

<a href="https://www.star-history.com/#Anarbb/Tasker&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=Anarbb/Tasker&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=Anarbb/Tasker&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=Anarbb/Tasker&type=date&legend=top-left" />
 </picture>
</a>


## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0).

See the [LICENSE](LICENSE) file for details, or visit [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html).

Copyright (C) 2025 Anas Arbaoui

