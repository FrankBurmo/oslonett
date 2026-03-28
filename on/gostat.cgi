#!/local/bin/perl5

$| = 1;

$golog ='/home/frogner/www2/netsite/httpd-80/logs/go-log';

open(STDERR, ">/dev/null");	# don't print error messages from eval

print "Content-type: text/html\n\n";

%input = &getinput;

$count = `grep $input{ann} $golog | wc -l`;
$count =~ tr/0-9//cd;

$vgcount = 'counter(go-vg)';
$aftcount = 'counter(go-aft)';

if (length $input{ann}) {
$vgcount = ($input{ann} =~/vg*/) ? "counter(go-vg)=$count" : $vgcount;
$aftcount = ($input{ann} =~/aftenpo*/) ? "counter(go-aft)=$count" : $aftcount;
}
if (length $input{Logg}){
print "<pre>\n";
system ("/local/gnu/bin/grep -B 1 -A 4 $input{ann} $golog");
} else
{
print <<EOT;
<html>
<head>
 <title>GO statistikk fra SNs forside</title>
</head>
<body bgcolor="#ffffff">
<h1>GO statistikk fra SNs forside</h1>
Hopp til Aftenposten og VG fra Schibsted Netts forside logges. I skjemaet
under må du klikke på Oppdater knappen for begge avisene for å få de siste
tallene. Tallene som står i skjemaet når det kommer opp, viser tallene slik
de var siste gang noen klikket Oppdater.
<p>
Tellerne begynte å løpe søndag 12. november 1995.

<table border=1>
<tr><td><form method="POST" action="gostat.cgi">
<input type=hidden name=ann value="vg.no">
<tr><th>Annonsør</th><th>Antall hopp</th><th>Klikk for å oppdatere</th><th>Vis logg</th></tr>
<tr><th><img src="/graphics/vg.gif"></th> <th><img src="/webcount/num.cgi/$vgcount"></th><th><input type=submit value="Oppdater"></th><th><input name=Logg type=submit value="Logg"></th></tr></form></td></tr>
<tr><td><form method="POST" action="gostat.cgi">
<input type=hidden name=ann value="aftenposten">
<tr><th><img src="/graphics/nya3.gif"></th> <th><img src="/webcount/num.cgi/$aftcount"></th><th><input type=submit value="Oppdater"></th><th><input name=Logg type=submit value="Logg"></th></tr>
</form>
</td></tr>
</table>
<p>
<hr size=1 noshade width=30% align=left>
<address>
(C)opyright Schibsted Nett AS, 1995
</body>
</html>
EOT
};
exit 0;

sub getinput {
# Return %input array, associating input names with input values
# Also builds global array @datanames, giving original order of input
# field names.
    local($i, $name, $value, $data, @data, %input);

    if ($ENV{'REQUEST_METHOD'} eq "GET") {
        $data = $ENV{'QUERY_STRING'};
    } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
        read(STDIN, $data, $ENV{'CONTENT_LENGTH'});
    } else {
        return;
    }

    # Del opp input-data i felter ved alle forekomster av '&'.
    @data = split(/&/, $data);

    for $i (0 .. $#data) {

        # Pluss oversettes til SPC
        $data[$i] =~ tr/+/ /;

        # Alt til venstre for første "=" er feltnavn, resten er felt-verdi
        ($name, $value) = split(/=/, $data[$i], 2);

        # Erstatt forekomster av %<hexkode> med tilsvarende tegn
        $name =~ s/%(..)/pack("c",hex($1))/ge;
        $value =~ s/%(..)/pack("c",hex($1))/ge;

        $value =~ s/\s+/ /g;
        $input{$name} = $value;
    }
    %input;                     # returnerer den assosiative array'en
}





