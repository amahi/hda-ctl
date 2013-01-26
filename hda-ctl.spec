%global rubyabi 1.9.1

Name:           hda-ctl
Version: 4.2.3
Release:        1

Summary:        hda-ctl is the Amahi HDA daemon.

Group:          System Environment/Daemons
License:        GPL
Source:         %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires: hda-platform >= 6.0.0
Requires: bind bind-utils caching-nameserver
Requires: sudo >= 1.7.2
Requires: dhcp mysql-server samba httpd
Requires: ruby(abi) = %{rubyabi}
Requires: monit perl-Authen-PAM fpaste
Requires: ruby-mysql ruby-libs ruby-augeas rubygem(bundler) rubygem(ruby-dbus)
Requires: perl-Authen-PAM perl-libwww-perl
Requires: cadaver php php-mysqlnd perl-URI filesystem rsync

%define debug_package %{nil}

%description
hda-ctl is the Amahi HDA daemon process.

%prep
%setup -q

make hda-ctl-hup

%build


%install
rm -rf %{buildroot}

mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_initrddir}
mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
mkdir -p %{buildroot}/var/cache
mkdir -p %{buildroot}%{_sysconfdir}/httpd/conf.d
mkdir -p %{buildroot}%{_sysconfdir}/sudoers.d
mkdir -p %{buildroot}/var/hda
mkdir -p %{buildroot}/usr/share/hda-ctl
mkdir -p %{buildroot}/etc/skel/Desktop
mkdir -p %{buildroot}/root/Desktop

install -m 755 -p hda-ctl hda-install %{buildroot}%{_bindir}
(cd %{buildroot}%{_bindir} && ln -sf hda-install hda-new-install)
install -m 755 -p hda-settings hda-alias hda-install-file %{buildroot}%{_bindir}
install -m 755 -p hda-register-apps hda-install-gem %{buildroot}%{_bindir}
install -m 755 -p hda-change-gw hda-change-dns amahi-installer hda-php-zone-change hda-fix-sudoers %{buildroot}%{_bindir}
# FIXME - remove after a while. added on Mon Feb 28 01:16:51 PST 2011
install -m 755 -p hda-upgrade-amahi5-to-amahi6 %{buildroot}%{_bindir}
install -m 4755 -p hda-ctl-hup %{buildroot}%{_bindir}
install -m 0440 -p hda-privs %{buildroot}%{_sysconfdir}/sudoers.d/amahi
install -p hda-ctl.initscript %{buildroot}%{_initrddir}/hda-ctl
install -p hda-ctl.sysconfig %{buildroot}%{_sysconfdir}/sysconfig/hda-ctl
install -p amahi-hda %{buildroot}/usr/share/hda-ctl/amahi-hda
install -p amahi-installer.initscript %{buildroot}%{_initrddir}/amahi-installer

rsync -Ca desktop-icons/ %{buildroot}/etc/skel/Desktop
rsync -Ca desktop-icons/ %{buildroot}/root/Desktop
rsync -Ca web-installer %{buildroot}/usr/share/hda-ctl/

# periodic updates
mkdir -p %{buildroot}%{_sysconfdir}/cron.hourly
install -m 700 -p hda-update %{buildroot}%{_sysconfdir}/cron.hourly

# base initialitation
rsync -Ca httpd %{buildroot}/usr/share/hda-ctl/

# calendar server non-destructive initialitation
mkdir -p %{buildroot}/var/hda/calendar
mkdir -p %{buildroot}/var/hda/calendar/logs
mkdir -p %{buildroot}/var/hda/calendar/html
mkdir -p %{buildroot}/var/hda/calendar/locks

# file server non-destructive initialization for later
rsync -Ca samba %{buildroot}/usr/share/hda-ctl/
mkdir -p %{buildroot}/var/hda/files/Backups
mkdir -p %{buildroot}/var/hda/files/Books
mkdir -p %{buildroot}/var/hda/files/Docs
mkdir -p %{buildroot}/var/hda/files/Movies
mkdir -p %{buildroot}/var/hda/files/Music
mkdir -p %{buildroot}/var/hda/files/Pictures
mkdir -p %{buildroot}/var/hda/files/Public

%clean
rm -rf %{buildroot}

%pre

%post
/sbin/chkconfig --add hda-ctl
/sbin/chkconfig --add amahi-installer

mkdir -p /var/hda/files

if [[ -e /var/cache/hda-ctl.cache ]]; then
    if grep -q yes /var/cache/hda-ctl.cache ; then
        (/usr/sbin/usermod -a -G users apache) || true

        # FIXME - added on 3/24/09, to be removed after 5/30/09
        # make the platform default
        (/bin/mv -f /etc/httpd/conf.d/04-platform.conf /etc/httpd/conf.d/01-platform.conf > /dev/null 2>&1) || true
        (/bin/rm -rf /var/hda/as > /dev/null 2>&1) || true
        (/bin/rm -rf /etc/httpd/conf.d/01-as.conf > /dev/null 2>&1) || true

        # FIXME: to be removed in the next major version of amahi 6.0
        INSUDOERS=`grep '^#includedir /etc/sudoers.d' /etc/sudoers`;
        if [ -z "$INSUDOERS" ]; then
            echo "#includedir /etc/sudoers.d" >> /etc/sudoers 
        fi
    fi
else
    (cd /var/hda/files/ && mkdir -p Backups Books Docs Movies Music Pictures Public && chown 500:100 . * && chmod 775 *)
fi

if [ -f %{_sysconfdir}/samba/smbpasswd ]; then
    mv -f %{_sysconfdir}/samba/smbpasswd /tmp/
fi
if [ -f %{_sysconfdir}/samba/smbusers ]; then
    mv -f %{_sysconfdir}/samba/smbusers /tmp/
fi
if [ -f %{_sysconfdir}/samba/secrets.tdb ]; then
    mv -f %{_sysconfdir}/samba/secrets.tdb /tmp/
fi

%preun

if [ "$1" = 0 ]; then
    # not an update, a complete uninstall
    /sbin/service hda-ctl stop > /dev/null 2>&1 || true
    /sbin/chkconfig --del hda-ctl
    /sbin/chkconfig --del amahi-installer
else
    # an update
    /sbin/service hda-ctl restart > /dev/null 2>&1 || true
fi

%files
%defattr(-,root,root,-)
%{_bindir}/amahi-installer
%{_bindir}/hda-alias
%{_bindir}/hda-change-dns
%{_bindir}/hda-change-gw
%{_bindir}/hda-ctl
%{_bindir}/hda-fix-sudoers
%{_bindir}/hda-install
%{_bindir}/hda-install-file
%{_bindir}/hda-install-gem
%{_bindir}/hda-new-install
%{_bindir}/hda-php-zone-change
%{_bindir}/hda-register-apps
%{_bindir}/hda-settings
%{_bindir}/hda-upgrade-amahi5-to-amahi6
%{_sysconfdir}/sysconfig/hda-ctl
%{_sysconfdir}/skel/Desktop
/root/Desktop/*
%{_sysconfdir}/cron.hourly/hda-update
%attr(0440, root, root)%{_sysconfdir}/sudoers.d/amahi
%ghost %attr(-, 500, 100) /var/hda/files
%attr(4755, root, root) %{_bindir}/hda-ctl-hup
%{_initrddir}/hda-ctl
%{_initrddir}/amahi-installer
/usr/share/hda-ctl/*
%attr(755, apache, apache) /var/hda/calendar

%changelog
* Sun Jan 13 2013 carlos puchol
- rename to hda-ctl and start on f18 port
* Sun Mar 11 2007 carlos puchol
- added hda.repo, and many other improvements
* Sat Mar 10 2007 carlos puchol
- add hda-install skeleton
* Sat Dec 09 2006 carlos puchol
- initial file
* Tue Feb 20 2006 carlos puchol
- add hda-ctl-hup, with uid
