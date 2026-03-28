#!/local/bin/perl

($ua, $ver) = ($ENV{HTTP_USER_AGENT} =~ m,([^/]+)/(\S+),);

if ($ua eq "Mozilla" && $ver >= 1.1) {
    print "Location: /nl/mes/nv/r96/ginfo.html\n\n";
} else {
    print "Location: /nl/mes/nv/r96/ginfo2.html\n\n";
}
