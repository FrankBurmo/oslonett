#!/local/bin/perl5

require "lib.pl";

%input = &getinput;

$input{id} = $1 if $ENV{HTTP_COOKIE} =~ /kurvid=(\d+)/;

# For intershop er default å ha med bestillingsskjema:
$input{skjema} = 1 if $sistebutikk eq 'intershop' && ! length $input{skjema};

open(KURV, "$DATADIR/kurv-$input{id}.data")
    || &ingenkurv;

$header = ($input{skjema}) ? "Bestillingsskjema" : "Innhold i handlekurven";
&header($header,$sistebutikk);

print <<EOT if $input{skjema};
Vil du bestille varene i handlekurven (med de angitte antallene), fyll
ut skjemaet nedenfor.

Feltene som er satt med <b>uthevet skrift</b> må fylles ut.
Det er spesielt viktig at elektronisk post-adresse fylles ut riktig
fordi det vil bli sendt en mail til denne adressen som så må besvares
for at bestillingen skal være gyldig.

<h3>Innhold i handlekurven</h3>
EOT

while (<KURV>) {
    chop;
    s!^/+!!;
    ($id, $antall) = ( /^(.+)\s+(\d+)$/ );
    $vareantall{$id} += $antall;
}

$ext = '-empty' unless $vareantall{$id} ||
    !length $butikkinfo{$sistebutikk.'-secondaryimg-empty'};

$secondaryimg = qq!<img align="right" alt="" border="0" 
    src="$butikkinfo{$sistebutikk.'-secondaryimg' . $ext}">!
    if length $butikkinfo{$sistebutikk.'-secondaryimg' . $ext};

print <<EOT;

$secondaryimg
<table border="2" width="75%">
<tr>

<td><font size="+1">Butikk</font></td>
<td><font size="+1">Produkt</font></td>
<td colspan="2" align="center"><font size="+1">Antall</font></td>

<td align="center"><font size="+1">Pris</font></td>
<td align="center"><font size="+1">Sum</font><br></td>
<tr>

EOT


    foreach $id (sort keys %vareantall) {
	($butikk, $varenr) = split(m!/!, $id, 2);
	%info = &vareinfo($butikk, $varenr);
	$visited{$butikk} = 1;

	$antall = $vareantall{$id};
	$sum = sprintf "%.2f", $antall * $info{pris};
	$pris = sprintf "%.2f", $info{pris};
	$html20 .= qq{
<td><a href="$butikkinfo{$butikk."-url"}">$butikk</a></td>
<td><a href="$info{'url'}">$info{'navn'}</a> </td>
<td align="right">
<a href="/kurv/nyttantall.cgi?vareid=$id&id=$input{id}">$antall</a>
</td>
<td align="center">
<a href="/kurv/nyttantall.cgi?vareid=$id&id=$input{id}&antall=0">Fjern</a>
</td>
<td align="right">$pris </td>
<td align="right">$sum <br></td>
<tr>
};
	$textline = sprintf("%-25s %-40s %5d %10.2f %10.2f\n",
			    $id, $info{navn}, $antall, $pris, $sum);
	$text .= $textline;
	$textline =~ s/\"/&#34;/g;
	chop($textline);
	$linjenr++;
	$html .= qq{<input type="hidden" name="linje$linjenr" value="$textline">\n};
	$sumsum += $sum;
    }
$text .= sprintf("%-79s%10.2f\n","SUM:",$sumsum);

$sumsum = sprintf "%.2f", $sumsum;
$mva = sprintf "%.2f", $sumsum*0.22/1.22;
print <<EOT;
$html20
<tr>
<tr>
<td colspan="5">Sum:</td>
<td align="right">$sumsum<br></td>
<tr>
<td colspan="5">Hvorav m.v.a.:</td>
<td align="right">$mva</td>
</table>
<p>
EOT

print <<EOT;

<b><a href="ryddbort.cgi?id=$input{id}">Tøm hele handlekurven</a></b><p>

Hvert produktnavn ovenfor er en link til mer informasjon om produktet.
Du kan endre antall for hver vare ved å trykke på tallet som står
etter produktnavnet.<p>

EOT

    if (! $input{skjema}) {
	print <<EOT;

Når du ønsker å bestille varene i kurven, trykker du her for å få frem
bestillings-skjemaet:
<pre></tt><h3><a href="$ENV{SCRIPT_NAME}?skjema=1">Vis bestillingsskjema</a>                <a href="ryddbort.cgi?id=$input{id}">Tøm hele handlekurven</a></h3><tt></pre>

EOT
 
   } else {
# 24.1.96 - kommenterte bort muligheten for å fjerne skjema igjen 
# for å spare litt plass i web-siden
#       print "<pre></tt><h3>\n";
#       print "Hvis du ikke ønsker å bestille ennå kan du skjule ";
#       print "bestillingsskjemaet for å få en mer oversiktlig side:";
#print qq!<a href="$ENV{SCRIPT_NAME}?skjema=0">Skjul bestillingsskjema</a>!;

# print "</h3><tt></pre>\n";

print <<EOT;

</form>

<form method="POST" action="bestill.cgi">
<input type="hidden" name="id" value="$input{id}">
<input type="hidden" name="ref" value="$input{ref}">
$html

<table border="0" cellpadding="0">
<dl>

<tr>
<dt><td><font size="+1"><b>Navn:</b></font></td>
<dd><td><input name="navn" size="55"></td>

<tr>
<dt><td><font size="+1">Firma:</font></td>
<dd><td><input name="firma" size="55"</td>

<tr>
<dt><td><font size="+1"><b>Adresse:</b></font></td>
<dd><td><input name="adresse" size="55"</td>

<tr>
<dt><td><font size="+1"><b>Postnr og -sted</b>:</font></td>
<dd><td><input name="postnr" size="6">
<input name="poststed" size="46"></td>

<tr>
<dt><td><font size="+1">Telefon:</font></td>
<dd><td><input name="telefon" size="15"</td>

<tr>
<dt><td><font size="+1">Telefaks:</font></td>
<dd><td><input name="telefaks" size="15"</td>

<tr>
<dt><td><font size="+1"><b>E-post:</b></font></td>
<dd><td><input name="e-post" size="30"</td>

<tr>
<dt><td><font size="+1">Kommentar:</font></td>
<dd><td><textarea name="kommentar" cols="55" rows="2"></textarea></td>

<tr>
<dt>
<dd>
<td colspan="2">
Hvis det er behov for å angi størrelse, farge eller andre detaljer for
noen av de bestilte produktene, kan du gjøre det i kommentar-feltet.
Andre kommentarer til selve bestillingen kan du også fylle inn her.
</td>

<tr>
</dl>
</table>
<input type="submit" value=" Send bestilling ">
<input type="reset" value=" Nytt skjema ">

EOT

print join("<p>\n\n", @tillegg{keys %visited});

print <<EOT;
<p>

</form>

</body>
</html>
EOT
}

exit 0;


sub ingenkurv {
    &error("Finner ikke igjen handlekurven din ($input{id})")
	if length $input{id};

    ($ua, $ver) = ($ENV{HTTP_USER_AGENT} =~ m,([^/]+)/(\S+),);
    $notnetscape = "Handlekurvsystemet er foreløpig avhengig av at man bruker Netscape. Generalisering av systemet kommer om kort tid, følg med!<p>I mellomtiden kan du forsøke å bestille ved å sende e-mail til butikken..."
	unless $ua eq 'Mozilla' && $ver >= 1.1;

    &header("Du har ikke fått med deg noen handlekurv");

    print <<EOT;

Du får ikke med deg noen handlekurv før du har bruk for det. Når du
tar med deg den første varen får du også med deg en handlekurv.
<p>

$notnetscape
EOT


    exit 0;
}
