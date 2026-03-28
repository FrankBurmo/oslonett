#!/local/bin/perl

($ua, $ver) = ($ENV{HTTP_USER_AGENT} =~ m,([^/]+)/(\S+),);

if ($ua eq "Mozilla" && $ver >= 1.1) {
    print "Location: /sp/sy/kat/priser-ns.html\n\n";
} else {
    print "Location: /sp/sy/kat/priser.html\n\n";
}
