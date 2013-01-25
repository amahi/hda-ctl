VERSION=4.2.3
ARCH=`uname -m`
RPMBUILDDIR=$(HOME)/rpmbuild

# SIGN=--sign

CFLAGS='-Wall'

all: rpm

dist: hdactl-hup
	(mkdir -p release && cd release && mkdir -p hdactl-$(VERSION))
	rsync -Ca hdactl hdactl-hup.c hdactl.spec hdactl.initscript hdactl.sysconfig hda-install \
	        debian hda-install-gem \
		amahi-hda httpd samba desktop-icons hdactl.sysconfig \
		hda-settings hda-register-apps hda-install-file hda-alias \
		hda-update hda-change-gw hda-change-dns amahi-installer.initscript \
		web-installer amahi-installer hda-php-zone-change hda-fix-sudoers \
		hda-upgrade-amahi5-to-amahi6 hda-privs networking.ubuntu \
		release/hdactl-$(VERSION)/
	(cd release && tar -czvf hdactl-$(VERSION).tar.gz hdactl-$(VERSION))
	(cd release && rm -rf hdactl-$(VERSION))
update-header:
	sed -i -e "s/version *= *\"[0-9.]*\"/version = \"$(VERSION)\"/" hdactl
	sed -i -e "s/version *= *\"[0-9.]*\"/version = \"$(VERSION)\"/" hda-install
	sed -i -e 's/^Version:\s*[0-9.]*\s*$$/Version: $(VERSION)/' hdactl.spec

rpm: update-header dist
	(cd release && rpmbuild $(SIGN) --target=$(ARCH) -ta hdactl-$(VERSION).tar.gz)
	mv $(RPMBUILDDIR)/RPMS/$(ARCH)/hdactl-$(VERSION)-*.$(ARCH).rpm release/
	mv $(RPMBUILDDIR)/SRPMS/hdactl-$(VERSION)-*.src.rpm release/

deb: update-header dist
	(cd release && ln -sf hdactl-$(VERSION).tar.gz hdactl_$(VERSION).orig.tar.gz)
	(cd release && tar -zxf hdactl_$(VERSION).orig.tar.gz)
#Commenting out until can figure out why debuild -S is not working	
	#(cd release/hdactl-$(VERSION)/debian && debuild -uc -us && debuild -S -uc -us)
	(cd release/hdactl-$(VERSION)/debian && debuild -uc -us)

install: rpm
	(cd release && sudo rpm -Uvh hdactl-$(VERSION)-*.$(ARCH).rpm)
