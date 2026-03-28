#!/local/bin/perl5

# Registrerer en ny stemme til navnet angitt i $ENV{QUERY_STRING}.
# Bruker flock() for å garantere at kun \'en bruker aksesserer filen samtidig:
#    Hvis filen allerede er låst av en annen bruker, blokkeres vår prosess
#    inntil 1) filen igjen blir ledig eller 2) maksimal ventetid ($TIMEOUT)
#    nås, da vekkes prosessen av SIGALRM og sender en feilmelding.

$DATAFIL        = '/local/www/sp/hballvm95/avstemning.data';
$KARANTENEFIL   = '/local/www/sp/hballvm95/karantene.data';
$KARANTENEDB	= '/local/www/sp/hballvm95/karantene';
$KARANTENETID	= 600;	# min. antall sekunder mellom stemmer fra samme maskin

$TIMEOUT        = 10;	# maks. # sekunder vi vil vente på tilgang til datafil
$LOCK_EX        = 2;	# exclusive file lock
$LOCK_UN        = 8;	# unlock file
$MAILADR	= 'www@sn.no';	# Send mail hit hvis filen er permanent låst

&avsluttet;

$SIG{'ALRM'} = 'handletimeout'; # Må ikke blokkere uendelig hvis...
alarm($TIMEOUT);		# ...filen ved en feil er låst permanent

open(SPILLERE, "+<$DATAFIL") || open(SPILLERE, ">$DATAFIL")
    || &error("Kunne ikke åpne filen $DATAFIL");

flock(SPILLERE, $LOCK_EX);	# Lås filen, blokker hvis allerede låst
$SIG{'ALRM'} = 'IGNORE';        # Kan nå lese og oppdatere trygt

# Oversetter + til SPC og %xx til char(hexcode xx)
($kandidat = $ENV{QUERY_STRING}) =~ s/\+/ /g;
$kandidat =~ s/%(..)/pack("c",hex($1))/ge;

# leser så inn avstemningsresultatet i %stemmer:
while (<SPILLERE>) {
    # Hopp over evt. blanke linjer (feil som kan oppstå ved manuell editering)
    next unless /\S/;
    chop;
    ($navn, $antall) = split(/%/);
    $stemmer{$navn} = $antall;
}

# Returnerer feilmelding hvis ikke navnet er gyldig
&error("Spilleren $kandidat er ikke registrert i databasen!")
    unless defined $stemmer{$kandidat};

# Åpner karantene-databasen
dbmopen(%sistestemme, $KARANTENEDB, 0644)
    || &error("Kan ikke åpne 'karantene-databasen'");
$akkurat_naa = time;

# Gir feilmelding hvis IP-adressen nylig har stemt
&i_karantene 
    unless $akkurat_naa > $KARANTENETID + $sistestemme{$ENV{REMOTE_ADDR}};

# Lagrer denne IP-adressen i sistestemme-tabellen
$sistestemme{$ENV{REMOTE_ADDR}} = time;
dbmclose(%sistestemme);

$stemmer{$kandidat}++;		# Antall stemmer økes med 1 for riktig spiller
truncate(SPILLERE, 0);		# Pass på å overskrive gammelt innhold
seek(SPILLERE, 0, 0);		# Gå til starten av filen igjen og skriv over
while (($key,$val) = each %stemmer) {
    print SPILLERE "$key%$val\n";
}
flock(SPILLERE, $LOCK_UN);      # Frigir datafilen igjen
close SPILLERE;

&header("Takk for at du var med på avstemningen");
print <<EOT;
<font size="+1">
Du stemte på $kandidat, hun har nå tilsammen $stemmer{$kandidat} stemmer. <p>


<center>
<h3><a href="/sp/hballvm95/bestespiller.cgi">Følg med hvordan det går videre med avstemningen.</a></h3>
</center>

Hvis du vil være med i trekningen om SN Internett pakker, fyller du ut
nok data i skjemaet under til at vi kan komme i kontakt med deg.
Resultater fra trekningen publiseres rett etter at VM er over.
<hr>
<form method="POST" action="trekkmeg.cgi">
<table border="0">
<dl>
<tr>
<td><dt>Navn:</td>
<td><dd><input name="Navn" size="45"></td>
<tr>
<td><dt>Adresse:</td>
<td><dd><input name="Adresse" size="45"></td>
<tr>
<td><dt>Postnr- og sted:</td>
<td><dd><input name="Postnrsted" size="45"></td>
<tr>
<td><dt>Telefon:</td>
<td><dd><input name="Telefon" size="45"></td>
<tr>
<td><dt>E-mail:</td>
<td><dd><input name="E-mail" size="45"></td>
</dl>
</table>
<input type="submit" value=" Ja, jeg vil være med i trekningen! ">
<input type="reset" value=" Nytt skjema ">
</form>
EOT

&footer;

exit 0;


sub error {
    local($msg) = $_[0];
    &header("Feilmelding");
    print "Programmet ble avbrutt med følgende feilmelding:\n";
    print "<blockquote><hr noshade>\n<h3>$msg</h3>\n<hr noshade>";
    print "</blockquote>\n";
    &footer;
    exit 0;

}


sub header {
    local($txt) = $_[0];

    print <<EOT;
Content-type: text/html

<html>
<head>
 <title>
  $txt
 </title>
</head>
<body background="/sp/hballvm95/img/vmlogo-bg.jpg">

<a href="/sp/hballvm95/">
<img alt="[Hjem]" src="/sp/hballvm95/img/vmikon.gif"
     border="0" align="right"></a>
<h1>$txt</h1>
EOT
}


sub footer {
    print <<EOT;
<address>
<hr size="1" noshade align="center" width="20%">
<center>
  <font size="-1">
  Disse sidene er laget for <a href="/"><img alt="SN Horisont" 
      border="0" src="/img/horisont.gif" align="absmiddle"></a>
  av <a href="/sn/">Schibsted Nett AS</a>. 
<a href="c.htm">Copyright &#169;</a> 1995.

</address>

</body>
</html>

EOT
}




sub handletimeout {
# Før flock() kalles setter vi opp en alarm som kaller denne prosedyren
# etter $TIMEOUT sekunder. Prosedyren returnerer altså feilmelding hvis
# forsøket på å flock'e ble gitt opp.

    &error(qq!Filen med avstemningsresultatet er låst av en annen
prosess. Forsøk igjen litt senere. Om problemet skulle være
vedvarende, ta kontakt med <a href="mailto:$MAILADR">$MAILADR</a>.!);

    &footer;
    exit 1;
}


sub avsluttet {

&header ("Avstemningen er avsluttet");
&footer;
exit;

}
sub i_karantene  {
    local($ventetid);

    $ventetid = $KARANTENETID - ($akkurat_naa - $sistestemme{$ENV{REMOTE_ADDR}});
    if ($ventetid > 60) {
	$ventetid = int($ventetid/60)+1 . " minutter";
    } else {
	$ventetid .= " sekunder";
    }

    &header("Det er allerede registrert en stemme fra din maskin");
    print <<EOT;

<h2>Du har ikke anledning til å stemme om igjen!</h2>

For å unngå juks er det ikke lov til å stemme flere ganger etter
hverandre. Hvis det er flere brukere på din maskin har du imidlertid
anledning til å stemme selv om en annen bruker nylig har stemt. Hvis
du ønsker å stemme, må du vente en stund før du også kan stemme. <p>

<h3>Tilbake til <a
href="/sp/hballvm95/bestespiller.cgi">avstemningsresultatet</a></h3>

EOT

    &footer;
    exit 1;
}
