#!/local/bin/perl

$norsk = "http://www.oslonett.no/uh/am-kat/form-nor.html";
$engelsk = "http://www.oslonett.no/uh/am-kat/form-eng.html";

print "Location: ";

print( ($ENV{'REMOTE_HOST'} !~ /\.no$/) ? $engelsk : $norsk);
print "\n\n";

exit 0;
