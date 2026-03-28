#!/local/bin/perl

($ua, $ver) = ($ENV{HTTP_USER_AGENT} =~ m,([^/]+)/(\S+),);

$fname=$ARGV[0];


if ($ua eq "Mozilla" && $ver >= 1.1) {
    print "Location: http://www.oslonett.no/sp/sy/gifs/store/",$fname,".jpg\n\n";
} else {
    print "Location: http://www.oslonett.no/sp/sy/gifs/store/",$fname,".gif\n\n";
}
