#!/local/bin/perl5

$DATAFIL	= '/local/www/sp/hballvm95/avstemning.data';
$GIF_LENGDE	= 350;
$HASH_LENGDE	= 45;
$HEIGHT		= 10;

open(SPILLERE, $DATAFIL) || &error("Kunne ikke åpne datafilen $DATAFIL");
while (<SPILLERE>) {
    ($spiller, $antall) = split(/%/);
    # bygger array'en @spiller som er slik at alfanumerisk sortering også gir
    # riktig numerisk sortering (ved like nr. sorteres alfabetisk etter navn).
    push(@spiller, sprintf("%010d %s", $antall, $spiller));
    $sum_stemmer += $antall;
    $maks_stemmer = $antall if $antall > $maks_stemmer;
}
close DATA;

$maks_stemmer = 1 if $maks_stemmer <= 0; # unngå div. by zero-feil

&header("Stem på beste norske spiller under sluttspillet i Håndball VM 1995");

print <<EOT;

PÅ SN Horisont kan du nå være med på å kåre den beste norske
spilleren under sluttspillet i damehåndball-VM 1995. Stemmene samles
inn fortløpende via Internett. For å sende inn din stemme velger du
bare et av navnene nedenfor og stemmen din blir talt med!<p>

Avstemningsresultatene nedenfor er basert på $sum_stemmer stemmer.
<p>
Etter at du har stemt, kan du velge om du vil være med i trekningen av
<a href="/sn/snnett.html">SN Internett pakker</a>! 
<p>Avstemningen er nå avsluttet. Mona Dahle vant suverent, gratulerer
til Mona! Takk også til alle som var med og stemte og gratulerer til
<a href="vinner.htm">vinneren av et SN Internett abonnement</a>!
EOT

# print-setningene ser litt hårete ut, 
# men så blir også dette 100% lynxable/mosaicable (inkl. grafikken):

print qq!<table border="2" cellpadding="4">\n<pre>\n!;
printf qq!<tr><td><font size="+1"><b>%-21s</b></font></td>!, "Spiller-navn";
print qq!<td><b> <font size="+1">Stemmer</font> </b></td>!;
print qq!<td><font size="+1"><b>Grafisk illustrasjon</b></font><br></td>!;
foreach (reverse sort @spiller) {
    ($antall, $navn) = ( /^0*(\d+)\s+(.+)/ );
    $urlnavn = $navn;
    $urlnavn =~ s/([^a-zA-Z0-9._ -])/sprintf("%%%%%02x",unpack("C",$1))/ge;
    $urlnavn =~ s/ /+/g;

    print "<tr>";
    printf(qq!<td><a href="stemmerpaa.cgi?$urlnavn">%-25s</td>!, $navn."</a>");
    printf(qq!<td align="right">%8d</td>!, $antall);
    printf(qq!<td><img alt="%s" !, 
	   '#' x int($HASH_LENGDE*$antall/$maks_stemmer));
    printf(qq!src="mkbar.cgi?%d" width="%d" height="$HEIGHT"><br></td>!,
	   $GIF_LENGDE*$antall/$maks_stemmer,$GIF_LENGDE*$antall/$maks_stemmer);
}
print "</pre></table>\n";

@t = localtime;
$t[4]++;			# map month from 0..11 to 1..12.
printf "<p>Automatisk generert %d.%d.%d, kl. %0d:%02d<p>\n",
    @t[3,4,5,2,1,0];

&footer;
exit 0;




sub error {
    local($msg) = $_[0];
    &header("Feilmelding");
    print "Programmet ble avbrutt med følgende feilmelding:\n";
    print "<blockquote><hr noshade>\n$msg\n<hr noshade></blockquote>\n";
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
<body background="/hballvm95/img/vmlogo-bg.jpg">

<a href="/hballvm95/">
<img alt="[Hjem]" src="/hballvm95/img/vmikon.gif"
     border="0" align="right"></a>
<h1 align="center">
  $txt
</h1>
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
