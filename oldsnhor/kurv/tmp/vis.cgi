#!/local/bin/perl5

$DATADIR = "/local/www/kurv/kunder";

%butikkinfo = (
	       "intershop-vareurl",	"/local/www/sh/is/perl/vareinfo.pl",
	       "intershop-url",		"/local/www/sh/is/",
	       );

print "Content-type: text/html\n\n";
&header;

%input = &getinput;

$input{id} = $1 if $ENV{HTTP_COOKIE} =~ /kurvid=(\d+)/;

open(KURV, "$DATADIR/kurv-$input{id}.data")
    || &error("Finner ikke igjen handlekurven din ($input{id})");


print <<EOT;
<form method="POST" action="/kurv/bestill.cgi">
<input type="hidden" name="id" value="$input{id}">
<input type="hidden" name="ref" value="$input{ref}">

<table border="2">
<tr>

<td><font size="+1">Butikk</font></td>
<td><font size="+1">Produkt</font></td>
<td><font size="+1">Antall</font></td>
<td><font size="+1">Pris</font></td>
<td><font size="+1">Sum</font></td>
<tr>

EOT


    while (<KURV>) {
	chop;
	s!^/+!!;
	($id, $antall) = ( /^(.+)\s+(\d+)$/ );
	$vareantall{$id} += $antall;
    }

    foreach $id (sort keys %vareantall) {
	($butikk, $varenr) = split(m!/!, $id, 2);
	%info = &vareinfo($butikk, $varenr);

	$antall = $vareantall{$id};
	$sum = $antall * $info{pris};
	print <<EOT;
<td><a href="/sh/is/">$butikk</a> </td>
<td><a href="$info{'url'}">$info{'navn'}</a> </td>
<td align="center">$antall </td>
<td align="right">$info{pris} </td>
<td align="right">$sum </td>
<tr>

EOT
    }
print <<EOT;
</table>
<p>

Du vil kunne endre antall for hver vare. Velger du 0, fjernes denne
varen fra kurven ved neste rekalkulering. For produkter hvor størrelse
farge etc. må oppgis gjøres dette først i bestillingsskjemaet.<p>

Vil du bestille varene ovenfor (med de angitte antallene), trykk her: <input type="submit" value=" Bestill ">
</form>
EOT

exit 0;


sub vareinfo {
    local($butikk, $varenr) = @_;
    local(%info);
    $varenr =~ s/([;\"!&\'\`*?$~])/\\$1/g;
    open(VARE, "/local/www/sh/is/perl/vareinfo.pl $varenr| ") || &error("Finner ikke vareinfo");
    while (<VARE>) {
	next unless /:/;
	$info{lc $1} = $2 if /^([^\s:]+)\s*:\s*(.+)\s*$/;
    }
    close VARE;
    return %info;
}




sub getinput {
# Return %input array, associating input names with input values
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

        $input{$name} = $value;
    }
    %input;                     # returnerer den assosiative array'en
}



sub error {
# returns HTML error message and exits program
    local($msg) = $_[0];

    print "Content-type: text/html\n\n";
    print <<EOT;
<html>
<head>
<title>$msg</title>
</head>
<body bgcolor="#ffffff">
<h1>Feilmelding</h1>

Programmet ble avbrutt med følgende feilmelding:
<center>
<font size="+2">
$msg
</font>
</center>
EOT
    exit 1;
}


sub header {
    print <<EOT;

<html>
<head>
<title>
Innhold i handlekurv
</title>
</head>

<body bgcolor="#ffffbb" link="#ff2000" vlink="#ff2000" >

<h1>Innhold i handlekurv</h1>
<a href="/sh/is/index.html"><img src="/sh/is/gifs/rsi.gif" border="0"></a>

EOT
}
