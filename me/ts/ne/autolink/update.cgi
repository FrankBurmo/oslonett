#!/local/bin/perl5

require "lib.pl";

$TOP	= '/local/www/me/ts/ne/red/utg';
$PATH	= "$TOP/[0-9][0-9]*";
$FIND	= '/local/gnu/bin/find';

$| = 1;
&printheader("Automatisk oppdatering av tidligere artikler");

open(BASE, $BASE) || &error("Kan ikke åpne link-databasen");
while (<BASE>) {
    chop;
    ($pattern, $url) = split(/%/);
    $pattern =~ s/ /\\s+/g;
    $link{$pattern} = $url;
}
close BASE;

# Don't change any links that are untouched since last update
#$newlink{'Eiendoms-Consult'} = '/home/bladetne/megler/ec/eiencons.htm';
#$newlink{Meglerforum} = '/home/bladetne/megler/meglerfo/meglerfo.htm';

%newlink = %link;
@newlinkkeys = keys %newlink;
#foreach (@newlinkkeys) {
#    print "$_<br>\n";
#}


open(FIND, "$FIND $PATH -name *.html -print |")
    || &error("Kan ikke kjøre 'find'");
@allfiles = <FIND>;
close FIND;

undef $/;			# read whole files deliberately

print $#allfiles+1, " filer skal sjekkes. Oppdaterer nå...<br>\n";
$tid = time;
print qq{<font size="-1"><blockquote>\n};
foreach (@allfiles) {
    $finishcount++;
    chop;
    $in = $_;
    $out = $in . ".new";
    $orig .= ".orig";

    ($dir = $in) =~ s!/[^/]+$!!;
    $dir =~ s!^$TOP/!!;
    if ($dir ne $lastdir) {
	print "Ferdig med utgave '$dir'. ";
	printf("%d fil%s sjekket, %d fil%s gjenstår...<br>\n",
	       $x = $finishcount - $lastfinishcount, $x != 1?"er":"",
	       $y = $#allfiles + 1 - $finishcount, $y != 1?"er":"");
	$lastfinishcount = $finishcount;
	$lastdir = $dir;
    }
    $count = 0;
    open(FILE, $orig) || open(FILE, $in) || &error("Kan ikke lese fil: $in");
    $a = <FILE>;
    close FILE;

    foreach $pattern (@newlinkkeys) {
	$url = $newlink{$pattern};
	$c = $a =~ s/(<a[^>]+>)?\b($pattern)\b(<\/a>)?/<a href="$newlink{$pattern}">$2<\/a>/i;
	$count += $c;
	$count{$pattern} += $c if $c;
    }
    
    if ($count) {
	($url = $out) =~ s!/local/www!!;
	push(@updated, "<a href=\"$url\">$ENV{SERVER_URL}$url</a> (<b>$count</b>)<br>\n");
	open(OUT, ">$out") || &error("Kan ikke skrive ny fil: $out");
	print OUT $a;
	close OUT || &error("Feil ved lukking av filen $out");
	rename($out, $in)
	    || print "<b>ADVARSEL:</b> Kunne ikke lagre $in<br>\n";
    }
}

print "</blockquote></font>\n";
$tid = time - $tid;
print $#updated+1, " av disse filene ble oppdatert med nye/endrede ";
print "link'er.<p>\nKonverteringen tok tilsammen $tid sekunder<p>\n";

print qq!<center><table border="4">\n<pre>\n!;
print qq!<tr><td colspan="2" align="center"><font size="+2">!;
print qq!Fordeling av linker som ble brukt</font></td><br>!;
foreach (keys %count) {
    push(@usedlinks, sprintf("%6d %s", 1e+6 - $count{$_}, $_));
}
foreach (sort @usedlinks) {
    $_ =~ s/\s*\d+\s+//;
    printf qq!<tr><td width="350"><a href="$link{$_}">%-45s</td>!, $_. "</a>";
    printf qq!<td align="right" width="40">%6d</td><br>!, $count{$_};
    $sum += $count{$_};
}
printf "<tr><td><b>%-41s</b></td>", "Tilsammen";
printf qq!<td align="right">%6d</td><br>!, $sum;
print "</pre></table></center>\n";

print "<p>Følgende artikler ble endret (antall nye linker i parentes):<br>";
print "<blockquote>\n@updated\n</blockquote>\n";

&printfooter;

exit 0;
