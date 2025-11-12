%define name tasker
%define version 1.0.0
%define release 1

Summary: A simple GTK4 GUI for managing cron jobs
Name: %{name}
Version: %{version}
Release: %{release}%{?dist}
License: GPLv3+
Group: Applications/System
Source0: %{name}-%{version}.tar.gz
BuildArch: noarch
BuildRequires: python3-devel
BuildRequires: python3-setuptools
Requires: python3 >= 3.10
Requires: python3-gobject >= 3.42.0
Requires: gtk4
Requires: polkit

%description
Tasker is a simple GTK4 GUI for managing cron jobs on Linux. It provides
an easy-to-use interface for creating, editing, and deleting scheduled tasks
without needing to edit crontab files manually.

%prep
%setup -q

%build
python3 setup.py build

%install
python3 setup.py install --root=%{buildroot} --optimize=1

# Fix shebang in the installed script
%py3_shebang_fix %{buildroot}%{_bindir}/tasker

# Install desktop file
mkdir -p %{buildroot}%{_datadir}/applications
install -m 644 me.arbaoui.tasker.desktop %{buildroot}%{_datadir}/applications/

# Install icon
mkdir -p %{buildroot}%{_datadir}/icons/hicolor/48x48/apps
install -m 644 icon.png %{buildroot}%{_datadir}/icons/hicolor/48x48/apps/tasker.png

# Install CSS (setup.py should handle this, but ensure directory exists)
mkdir -p %{buildroot}%{_datadir}/tasker

%files
%{python3_sitelib}/main.py
%{python3_sitelib}/cron_manager.py
%{python3_sitelib}/task_dialog.py
%{python3_sitelib}/__pycache__/main.*.pyc
%{python3_sitelib}/__pycache__/cron_manager.*.pyc
%{python3_sitelib}/__pycache__/task_dialog.*.pyc
%{python3_sitelib}/tasker-*.egg-info
%{_bindir}/tasker
%{_datadir}/applications/me.arbaoui.tasker.desktop
%{_datadir}/tasker/ui.css
%{_datadir}/icons/hicolor/48x48/apps/tasker.png
%doc README.md LICENSE

%defattr(-,root,root,-)

%changelog
* Wed Nov 12 2025 Anas Arbaoui <anas@arbaoui.me> - 1.0.0-1
- Initial release

