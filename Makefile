all:
	@echo "Nothing to build by default."

.PHONY: all rpm deb clean

VERSION ?= 1.0.0

rpm:
	mkdir -p /tmp/tasker-$(VERSION)
	cp -r *.py *.css *.desktop *.spec *.png debian setup.py README.md LICENSE /tmp/tasker-$(VERSION)/
	cd /tmp && tar czf tasker-$(VERSION).tar.gz tasker-$(VERSION)
	mkdir -p ~/rpmbuild/{SOURCES,SPECS,RPMS,SRPMS}
	cp /tmp/tasker-$(VERSION).tar.gz ~/rpmbuild/SOURCES/
	cp tasker.spec ~/rpmbuild/SPECS/
	sed -i 's/^Version: .*/Version: $(VERSION)/' ~/rpmbuild/SPECS/tasker.spec
	rpmbuild -ba ~/rpmbuild/SPECS/tasker.spec

deb:
	dch --newversion "$(VERSION)-1" --distribution ubuntu "Release $(VERSION)"
	dch --release ""
	dpkg-buildpackage -us -uc -b

clean:
	rm -rf build dist *.egg-info
	rm -rf debian/tasker
	rm -f ../*.deb ../*.dsc ../*.tar.gz ../*.changes
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

