#!/bin/bash
# Install build dependencies for Tasker

set -e

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    DISTRO=$ID
else
    echo "Error: Cannot detect distribution"
    exit 1
fi

echo "Detected distribution: $DISTRO"
echo ""

case "$DISTRO" in
    fedora|rhel|centos|rocky|almalinux)
        echo "Installing RPM build dependencies..."
        sudo dnf install -y \
          rpm-build \
          rpmdevtools \
          python3-devel \
          python3-setuptools \
          python3-gobject \
          gtk4 \
          polkit
        
        echo ""
        echo "Build dependencies installed successfully!"
        echo ""
        echo "To build the RPM, run:"
        echo "  make VERSION=1.0.0 rpm"
        echo ""
        echo "Or manually:"
        echo "  rpmdev-setuptree"
        echo "  rpmbuild -ba tasker.spec"
        ;;
    
    ubuntu|debian|pop|linuxmint)
        echo "Installing DEB build dependencies..."
        sudo apt-get update
        sudo apt-get install -y \
          build-essential \
          devscripts \
          debhelper \
          dh-python \
          python3-all \
          python3-setuptools \
          python3-gi \
          libgtk-4-1 \
          policykit-1
        
        echo ""
        echo "Build dependencies installed successfully!"
        echo ""
        echo "To build the DEB package, run:"
        echo "  make VERSION=1.0.0 deb"
        echo ""
        echo "Or manually:"
        echo "  dpkg-buildpackage -us -uc -b"
        ;;
    
    *)
        echo "Error: Unsupported distribution: $DISTRO"
        echo "Supported distributions: Fedora, RHEL, CentOS, Rocky, AlmaLinux, Ubuntu, Debian, Pop!_OS, Linux Mint"
        exit 1
        ;;
esac
