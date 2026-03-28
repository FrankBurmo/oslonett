#!/local/bin/perl

print "\nAngit utgave-directory på formed dddd (f.eks. "9540"): ";
$dir = <> || "xyzzy";

print "regexp: ";
$soek = <STDIN>;
chop($soek);

while (<>) {
    if (m,<title>(.+)</title>,) {
	$tittel = $1;
	print "  <li> <a href=\"/me/ts/cw/utg/$dir/$ARGV\">$tittel</a>\n"
	    if ($tittel =~ /$soek/i);
    }
}

    

