Name:          mumudvb
Version:       2.1.0
Release:       6%{?dist}
Summary:       A dvb multicast streamer

License:       GPLv2
URL:           http://www.mumudvb.net
Source0:       https://github.com/braice/MuMuDVB/archive/%{version}.zip
Source1:       mumudvb@.service

Patch0:        Fix-compiling-with-kernels-4.14.patch

# We could add CAM support, but we would need to package dvb-apps, and it's kinda unmaintained
#BuildRequires: libucsi.so()(64bit) libdvben50221.so()(64bit) linuxtv-dvb-apps-devel
#Requires:      libucsi.so()(64bit) libdvben50221.so()(64bit)
BuildRequires: asciidoc gettext-devel autoconf automake
BuildRequires: systemd

%description


%prep
%autosetup -n MuMuDVB-%{version} -p1

%pre
getent group mumudvb >/dev/null || groupadd -r mumudvb
getent passwd mumudvb >/dev/null || \
useradd -r -g mumudvb -G video -d /dev/null -s /sbin/nologin \
   -c "MuMuDVB Service User" mumudvb
exit 0

%build
autoreconf -i -f
%configure
make %{?_smp_mflags}
make doc


%install
install -m 0755 -d %{buildroot}%{_sysconfdir}/%{name}
install -m 0644 -D scripts/debian/etc/default/mumudvb %{buildroot}%{_sysconfdir}/sysconfig/%{name}
install -m 0644 -D %{SOURCE1} %{buildroot}%{_unitdir}/%{name}@.service
install -d %{buildroot}%{_docdir}/%{name}
install -t %{buildroot}%{_docdir}/%{name}/ doc/html/*
%make_install


%files
%{_bindir}/%{name}
%config %attr(-, root, mumudvb) %{_sysconfdir}/sysconfig/%{name}
%config %attr(-, root, root) %{_unitdir}/%{name}@.service
%config %attr(-, root, mumudvb) %{_sysconfdir}/%{name}
%doc %{_docdir}/%{name}

%changelog
* Fri Dec 15 2017 Anatole Denis <natolumin@rezel.net> - 2.1.0-6
- Fix building with kernels 4.14+
* Thu Mar 16 2017 Anatole Denis <natolumin@rezel.net> - 2.1.0-5
- Setup RuntimeDirectory in the service file
* Mon Mar 13 2017 Anatole Denis <natolumin@rezel.net> - 2.1.0-4
- Revert use of systemd-sysusers (not in el7)
* Sun Mar 12 2017 Anatole Denis <natolumin@rezel.net> - 2.1.0-3
- Tweaked user/group parameters
* Sun Mar 12 2017 Anatole Denis <natolumin@rezel.net> - 2.1.0-2
- Add mumudvb to the video group
* Sun Mar 12 2017 Anatole Denis <natolumin@rezel.net> - 2.1.0-1
- Version bump to 2.1
* Fri Nov 20 2015 Anatole Denis <anatole@rezel.net>
- First packaging for centos
