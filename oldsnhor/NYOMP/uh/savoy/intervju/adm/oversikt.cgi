#!/local/bin/perl5

require "/local/www/data/vg/include/include.pl";

$top = "/local/www/data/intervju";

opendir(DIR, $top) || &error("Kunne ikke åpne directory $top");
@dirs = grep(-d && !/^\./ && -r "$_.info", readdir(DIR));
closedir(DIR);

&header("Oversikt over alle intervjuer");

if (@dirs) {
    print "<pre>\n";
    printf "%-55s %-8s%s\n\n", "Tittel", "  Dato";

    foreach $dir (@dirs) {
	open(INFO, "$dir.info") || next;
	undef %info;
	while (<INFO>) {
	    last unless /\S/;	# blank line separates headers form body
	    ($key, $val) = ($1, $2) if /^([^:\s]+)\s*:\s*(.+)/;
	    $info{lc $key} = $val;
	}
	close INFO;
	printf("<a href=\"spm.cgi/$dir\">%-55s     %-8s\n",
	       $info{'tittel'}."</a>", $info{'dato'});
    }
    print "</pre>\n\n";
    print "For å se nærmere på ett intervju, bruk en av linkene overnfor.<p>\n";
} else {
    print "<h2>Ingen registrerte intervjuer</h2>\n";
}

print qq!For å gjøre et <a href="nyttintervju.html">nytt intervju</a> må du !;
print "bruke et eget skjema.\n";

print &footer;

exit 0;

sub header {
    local($txt) = $_[0];

    return if $HEADER++;
    &top($txt);
    print "<title>$txt</title>\n";
    &std_header;
    print qq!<h1><tt><font size="+5">$txt</font></tt></h1>\n\n!;
}


sub error {
    local($msg) = $_[0];

    &header("Feilmelding");

    print "Programmet ble avbrutt med følgende feilmelding:\n\n<blockquote>\n";
    print qq!<hr size="2" noshade>\n<font size="+1"><b>$msg</b></font>\n!;
    print qq!<hr size="2" noshade>\n</blockquote>\n!;
    &std_footer;
    exit 0;
}

