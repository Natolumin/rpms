Name:           ulogd
Version:        2.0.7
Release:        1%{?dist}
Summary:        Netfilter userspace logging daemon

License:        GPLv2
URL:            https://www.netfilter.org/projects/ulogd/
Source0:        https://www.netfilter.org/projects/ulogd/files/ulogd-%{version}.tar.bz2

Source10:       ulogd.service
Source11:       ulogd.logrotate
Source12:       ulogd_socket.te

BuildRequires:  libnetfilter_log-devel >= 1.0.0
BuildRequires:  libnetfilter_conntrack-devel >= 1.0.2
# nfacct is not required and not packaged for centos
%bcond_with nfacct
%if %{with nfacct}
BuildRequires:  libnetfilter_acct-devel >= 1.0.1
BuildRequires:  libmnl-devel >= 1.0.3
%endif
BuildRequires:  libnfnetlink >= 1.0.1

Requires:       systemd

BuildRequires: selinux-policy-devel, checkpolicy
Requires(post): policycoreutils
Requires(preun): policycoreutils
Requires(postun): policycoreutils

%description
ulogd is a userspace logging daemon for netfilter/iptables related logging. This
includes per-packet logging of security violations, per-packet logging for
accounting, per-flow logging and flexible user-defined accounting.


# Output plugins:
%package output-postgresql
Summary:        PostgreSQL output plugin for ulogd
BuildRequires:  postgresql-devel
%description output-postgresql
PostgreSQL output plugin for ulogd

%package output-mysql
Summary:        MySQL output plugin for ulogd
BuildRequires:  mysql-devel
%description output-mysql
MySQL output plugin for ulogd

%package output-dbi
Summary:        DBI output plugin for ulogd
BuildRequires:  libdbi-devel
%description output-dbi
DBI output plugin for ulogd

%package output-json
Summary:        JSON output plugin for ulogd
BuildRequires:  pkgconfig(jansson)
%description output-json
JSON output plugin for ulogd

%package output-sqlite
Summary:        SQLITE3 output plugin for ulogd
BuildRequires:  pkgconfig(sqlite3)
%description output-sqlite
SQLITE output plugin for ulogd

%package output-pcap
Summary:        PCAP output plugin for ulogd
BuildRequires:  libpcap-devel
%description output-pcap
PCAP output plugin for ulogd

%prep
%setup -q


%build
%configure --enable-nfacct=%{?with_nfacct:on}%{!?with_nfacct:off} --enable-static=no --with-dbi-lib=%{_libdir}/ --with-pgsql=yes --with-mysql=yes --with-sqlite=yes --with-pcap=yes --with-jansson=yes

# Default configuration taken from gentoo. Maybe ship a proper config file with the RPM ?
sed -i -e "s|/var/log/ulogd_|%{_localstatedir}/log/%{name}/|g" -e 's|/tmp|/run|g' -e "s|/var/log/ulogd.log|%{_localstatedir}/log/%{name}/ulogd.log|" ulogd.conf.in
%if 0%{!?with_nfacct:1}
sed -i -e '/ulogd_inpflow_NFACCT.so/d' ulogd.conf.in
%endif

make %{?_smp_mflags}
cp %{SOURCE12} . && make -f %{_datadir}/selinux/devel/Makefile

%install
%make_install
#enable-static=no is currently broken
rm -f %{buildroot}%{_libdir}/ulogd/*.la

install -pD -m0644 ulogd_socket.pp %{buildroot}%{_datadir}/selinux/packages/ulogd_socket.pp

install -pD -m0644 %{SOURCE10} %{buildroot}%{_unitdir}/%{name}.service
install -pD -m0644 %{SOURCE11} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -pD ulogd.conf %{buildroot}/%{_sysconfdir}/ulogd.conf
install -d %{buildroot}%{_localstatedir}/log/%{name}/

%preun
if [ "$1" -lt "1" ]; then
semodule -r ulogd_socket
fi
%systemd_preun %{name}.service
%post
if [ "$1" -le "1" ]; then
semodule -i %{_datadir}/selinux/packages/ulogd_socket.pp
fi
%systemd_post %{name}.service
%postun
if [ "$1" -ge "1" ]; then
semodule -i %{_datadir}/selinux/packages/ulogd_socket.pp
fi
%systemd_postun_with_restart %{name}.service

%files
%doc %{_mandir}
%{_libdir}/ulogd/ulogd_inppkt_*.so
%{_libdir}/ulogd/ulogd_inpflow_NFCT.so
%if %{with nfacct}
%{_libdir}/ulogd/ulogd_inpflow_NFACCT.so
%endif
%{_libdir}/ulogd/ulogd_raw2packet_BASE.so
%{_libdir}/ulogd/ulogd_filter_*.so
# builtin output modes
%{_libdir}/ulogd/ulogd_output_OPRINT.so
%{_libdir}/ulogd/ulogd_output_GPRINT.so
%{_libdir}/ulogd/ulogd_output_XML.so
%{_libdir}/ulogd/ulogd_output_NACCT.so
%{_libdir}/ulogd/ulogd_output_LOGEMU.so
%{_libdir}/ulogd/ulogd_output_SYSLOG.so
%{_libdir}/ulogd/ulogd_output_GRAPHITE.so

%{_sbindir}/ulogd

%{_unitdir}/ulogd.service
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config %{_sysconfdir}/logrotate.d/%{name}

%dir %{_localstatedir}/log/%{name}

# SELinux module for recent kernels
%{_datadir}/selinux/packages/ulogd_socket.pp

%files output-pcap
%{_libdir}/ulogd/ulogd_output_PCAP.so
%files output-sqlite
%{_libdir}/ulogd/ulogd_output_SQLITE3.so
%files output-postgresql
%{_libdir}/ulogd/ulogd_output_PGSQL.so
%files output-mysql
%{_libdir}/ulogd/ulogd_output_MYSQL.so
%files output-dbi
%{_libdir}/ulogd/ulogd_output_DBI.so
%files output-json
%{_libdir}/ulogd/ulogd_output_JSON.so

%changelog
* Fri Apr 27 2018 Anatole Denis <natolumin@rezel.net> - 2.0.7-1
- Version bump to 2.0.7
* Sat Apr 15 2017 Anatole Denis <natolumin@rezel.net> - 2.0.5-5
- Add additional SELinux policy module for recent kernels
* Sat Mar 11 2017 Anatole Denis <natolumin@rezel.net> - 2.0.5-4
- Use Type=simple service (SELinux prevents writing pidfile)
* Fri Mar 10 2017 Anatole Denis <natolumin@rezel.net> - 2.0.5-2
- Fix logfiles paths
* Wed Feb 15 2017 Anatole Denis <anatole@rezel.net> - 2.0.5-1
- Initial packaging
