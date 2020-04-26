Name:          inspircd
Version:       3.6.0
Release:       1%{?dist}
Summary:       A modular Internet Relay Chat server written in C++

Group:         Applications/Communications
License:       GPLv2
URL:           http://www.inspircd.org/
Source0:       https://github.com/inspircd/inspircd/archive/v%{version}.tar.gz
Source1:       inspircd.service
Source2:       inspircd.logrotate

BuildRequires: make, tar, gcc-c++
BuildRequires: perl
BuildRequires: perl(Getopt::Long)
%if 0%{?fedora} > 30
BuildRequires: systemd-rpm-macros
%else
BuildRequires: systemd
%endif

# For default modules
BuildRequires: gnutls-devel, openssl-devel
Requires:      systemd

%package ssl-gnutls
Summary:       GNUTLS ssl module for inspircd
Requires:      inspircd == %{version}-%{release}
# automatic dependencies are somehow broken for inspircd modules
Requires:      gnutls
%description ssl-gnutls
Provides an SSL module linking against gnutls
%package ssl-openssl
Summary:       OpenSSL ssl module for inspircd
Requires:      inspircd == %{version}-%{release}
# automatic dependencies are somehow broken for inspircd modules
Requires:      openssl-libs
%description ssl-openssl
Provides an SSL module linking against openssl

%description
InspIRCd is a project created to provide a stable IRCd which provides a
vast number of features in a modularized form. By keeping the
functionality of the main core to a minimum, yet providing a highly
featured module API, we hope to increase the stability and speed of our
project and make it customizable to the needs of many users. InspIRCd is
released to the public domain under GPL so that you may benefit from our
work. The project is written from scratch, avoiding the inherent
instability and security problems found in many other more "heavyweight"
IRCd distributions.

%pre
getent group %{name} >/dev/null || groupadd -r %{name}
getent passwd %{name} >/dev/null || \
useradd -r -g %{name} -d %{_libdir}/%{name}/ -s /sbin/nologin -c \
"InspIRCd service user" %{name}
exit 0

%prep
%autosetup -n inspircd-%{version}


%build
# Enable extra modules
./configure --enable-extras=m_ssl_gnutls.cpp,m_ssl_openssl.cpp,m_sslrehashsignal.cpp,m_regex_posix.cpp,m_regex_stdlib.cpp
./configure --disable-interactive \
    --disable-auto-extras \
    --distribution-label %{dist} \
    --system \
    --prefix=%{_libdir}/%{name} \
    --config-dir=%{_sysconfdir}/%{name} \
    --module-dir=%{_libdir}/%{name}/modules \
    --log-dir=%{_localstatedir}/log/%{name} \
    --data-dir=%{_localstatedir}/run/%{name} \
    --binary-dir=%{_sbindir} \
    --example-dir=%{_docdir}/%{name}-%{version}/examples \
    --uid $(id -u) \
    --gid $(id -g) \

INSPIRCD_DISABLE_RPATH=1 make %{?_smp_mflags}


%install
%make_install

rm -f %{buildroot}%{_sbindir}/inspircd-genssl
rm -f %{buildroot}%{_datadir}/inspircd/.gdbargs

# systemd service
install -pD -m0644 %{SOURCE1} %{buildroot}%{_unitdir}/%{name}.service
install -pD -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# Log,PID directory
mkdir -p %{buildroot}%{_localstatedir}/log/%{name}/


%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%files
%doc %{_docdir}/%{name}-%{version}/examples
%doc README.md
%doc %{_mandir}/man1/*
# Original perlscript wrapper and service file
%doc %{_datadir}/inspircd
# Capabilities for the executable
%attr(754, %{name}, %{name}) %caps(CAP_NET_BIND_SERVICE=ep) %{_sbindir}/%{name}

%config %{_sysconfdir}/logrotate.d/%{name}

%{_unitdir}/%{name}.service

%dir %attr(775, %{name}, %{name}) %{_localstatedir}/log/%{name}

# Modules, but exclude modules with external deps to their own package
%attr (755, %{name}, %{name}) %{_libdir}/%{name}/modules/*.so
%exclude %{_libdir}/%{name}/modules/m_ssl_*.so

%files ssl-gnutls
%attr (755, %{name}, %{name}) %{_libdir}/%{name}/modules/m_ssl_gnutls.so
%files ssl-openssl
%attr (755, %{name}, %{name}) %{_libdir}/%{name}/modules/m_ssl_openssl.so

%changelog
* Sun Apr 26 2020 Anatole denis <natolumin@rezel.net> - 3.6.0-1
- Version bump

* Sat Apr 25 2020 Anatole Denis <natolumin@rezel.net> - 2.0.29-1
- Version bump

* Sat Sep 28 2019 Anatole Denis <natolumin@rezel.net> - 2.0.28-1
- Version bump

* Wed Jul 24 2019 Anatole Denis <natolumin@rezel.net> - 3.2.0-1
- Major version changes

* Sat Dec 29 2018 Anatole Denis <natolumin@rezel.net> - 2.0.27-1
- Version bump

* Tue Nov 06 2018 Anatole Denis <natolumin@rezel.net> - 2.0.26-2
- Add compile-time options to enable SHA256 for gnutls and ECDHE for openssl

* Sun May 13 2018 Anatole Denis <natolumin@rezel.net> - 2.0.26-1
- Version bump

* Mon Nov 13 2017 Anatole Denis <natolumin@rezel.net> - 2.0.25-1
- Version bump

* Wed Sep 13 2017 Anatole Denis <natolumin@rezel.net> - 2.0.24-3
- Rebuild for CentOS 7.4/openssl 1.0.2

* Sun May 21 2017 Anatole Denis <natolumin@rezel.net> - 2.0.24-2
- fix logrotate matching

* Fri May 19 2017 Anatole Denis <natolumin@rezel.net> - 2.0.24-1
- Version bump to 2.0.24

* Thu Mar 23 2017 Anatole Denis <natolumin@rezel.net> - 2.0.23-7
- Add logrotate file

* Thu Mar 23 2017 Anatole Denis <natolumin@rezel.net> - 2.0.23-6
- Modularize build to separate ssl modules from core

* Sun Oct 09 2016 Anatole Denis <natolumin@rezel.net>
- Add patch to sanitize server gecos in m_httpd_stats

* Mon Sep 26 2016 Anatole Denis <natolumin@rezel.net>
- Remove patch and use systemd mechanisms to work around it

* Thu Sep 08 2016 Anatole Denis <natolumin@rezel.net>
- Don't restart the server on upgrades, since most upgrades will only need to
reload some specific modules
- Change file mode to avoid capability elevation to CAP_NET_BIND_SERVICE

* Sun Sep 04 2016 Anatole Denis <natolumin@rezel.net> - 2.0.23
- Version bump to 2.0.23

* Mon Aug 15 2016 Anatole Denis <natolumin@rezel.net> - 2.0.22
- Version bump to 2.0.22
- Add a WorkingDirectory to service file so that the current directory can be written to

* Mon Jul 18 2016 Anatole Denis <natolumin@rezel.net>
- Add CAP_NET_BIND_SERVICE to the inspircd binary, allowing it to bind to low ports

* Wed Feb 24 2016 Anatole Denis <natolumin@rezel.net>
- Fix nonexistent PID directory (/var/run is a symlink to /run, which is handled
by systemd and is a tmpfs)

* Tue Feb 23 2016 Anatole Denis <natolumin@rezel.net> - 2.0.21
- Version bump

* Tue Sep 29 2015 Anatole Denis <natolumin@rezel.net> - 2.0.20
- Cleanup service file

* Tue Jul 21 2015 Richard Bradfield <bradfirj@fstab.me> - 2.0.20
- Initial package for Copr testing
