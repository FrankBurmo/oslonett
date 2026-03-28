#!/local/bin/perl5

require "lib.pl";

&printheader("Administrasjon av link-database");

print <<EOT;

Nedenfor er listen over alle linkene i link-databasen. Link'ene i
høyre kolonne peker til riktig web-side (som angitt av URL'en) slik at
man enkelt kan sjekke at link'en peker til riktig sted.<p>

Link\'ene i venstre kolonne peker til et program som kan brukes til å
endre eller fjerne eksisterende linker. Hvis du vil legge inn ny link
må du fylle inn <a href="#nylink">skjemaet nederst på siden</a>.<p>

<center>
<pre>
<table border="2">
<tr><td><font size="+2">Søkemønster</font></td><td><font size="+2">URL<br></font></td>
EOT

open(BASE, $BASE) || &error("Kan ikke lese linkdatabasen: $BASE");
@base = <BASE>;
close BASE;

foreach (sort @base) {
    chop;
($pattern, $url) = split(/%/);
($escpattern = $pattern)=~ s/([ &+?])/sprintf("%%%2X",unpack("c",$1))/ge;
($escurl = $url)	=~ s/([ &+?])/sprintf("%%%2X",unpack("c",$1))/ge;
print qq{<tr><td><a href="linkform.cgi?pattern=$escpattern&url=$escurl">};
print qq{$pattern</a></td>};
print qq{<td><a href="$url">$url</a><br></td>};
}

print <<EOT;
</table>
</pre>
</center>
<hr>
<a name="nylink"><h2>Registrere ny link</h2></a>
For å legge inn ny link, fyll ut feltene nedenfor:

<form method="POST" action="addlink.cgi">
<dl>
    <td> <b>Søkemønster</b> (firmanavn)
    <dd> <input name="pattern" size="55">
    <dt> <b>URL</b> (<b>NB!</b> ikke relativ men fullstendig URL, f.eks.
    <em>http://www.sn.no/ettellerannet</em> eller
    <em>/home/bladetne/ettellerannet</em>)
    <dd> <input name="url" size="55">
</dl>
<input type="submit" value="Registrer ny">
<input type="reset" value="Slett feltene">
</form>
<hr>

<h2>Oppdatering av artikler</h2>

Når databasen er oppdatert kan du kjøre oppdatering av alle artiklene.
Dette tar litt tid (i størrelsesorden et minutt eller to).

<center>
<h3><em>Ikke kjør dette programmet med mindre<br>
du er sikker på at du er klar til å gjøre det:</em></h3>

    <h3><a href="/me/ts/ne/autolink/update.cgi">$ENV{SERVER_URL}/me/ts/ne/autolink/update.cgi</a></h3>
</center>

EOT

&printfooter;
exit 0;
