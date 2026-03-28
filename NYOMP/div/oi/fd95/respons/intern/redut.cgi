#!/local/bin/perl5
# returnerer HTML form med ferdig utfylte felter

require "fd-lib.pl";
print "Content-type: text/html\n\n";

&getinput;

open(FILE, $input{file}) || &error("Kan ikke åpne filen $input{file}");

while (<FILE>) {
    chop;
    ($name, $value) = split(": ", $_, 2);
    $name =~ tr/A-ZÆØÅ/a-zæøå/;
    $input{$name} = $value;
}

($kommentar = $input{kommentar}) =~ s/(.{45,63})\s/$1\n/g;
    
($svar = $input{svar}) =~ s/(.{45,63})\s/$1\n/g;

$revdato = &dato;

if ($input{publiseres} =~ /^ja/i) {
    $pubja = "checked";
} elsif ($input{publiseres} =~ /mail/i ) {
    $pubmail = "checked";
} else {
    $pubnei = "checked";
}

print &header("Besvare innkommende forespørsel");
print <<EOT;

Fra denne siden kan man
<ol>
<li> redigere innkommende spørsmål eller tilbakemeldinger
<li> besvare innkommende spørsmål eller kommentere tilbakemeldinger
</ol>

Bruk gjerne feltet for signatur nederst på siden - og husk å angi om
teksten skal publiseres eller ei.

<form method="POST" action="$baseurl/intern/redinn.cgi">
<center>
<table border="6" cellpadding="4">
<tr>
<td>
<h2>Om avsender (faste felter):</h2>
<pre>
Firma:		$input{firma}
Navn:		$input{navn}
Stilling:	$input{stilling}
Adresse:	$input{adresse}
Postnr/-sted:   $input{postnummer} $input{poststed}
Evt. E-Post:    $input{epost}
Telefon:        $input{telefon}           Telefax: $input{telefax}

Registreringsdato:       $input{regdato}
Siste oppdateringsdato:  $input{revdato}

Innsendt spørsmål kun til internt bruk (ikke web): $input{intern}
Ønsker å være anonym ved evt. web-publisering:     $input{anonym}

</pre>
</td>
<tr>
<td>

<h2>Overskrift:</h2>
<input name="Overskrift" size="65" value="$input{overskrift}">

<h2>Kommentarer:</h2>

<textarea name="Kommentar" rows="10" cols="65">$kommentar</textarea>
</td>
<tr>
<td>

<h2>Redaksjonelle tillegg - svar, kommentarer, etc.</h2>

<textarea name="Svar" rows="10" cols="65">$svar</textarea><p>
Signatur: <input name="signatur" size="40" value=$input{signatur}><p>

Skal legges synlig i world wide web?
<blockquote>
EOT

if ($input{intern} =~ /^nei$/i) {
    print(qq!<input type="radio" name="publiseres" 
	  value="ja,mail" $pubja> Ja, og send email<br>!);
} else {
    print "<em>[Innsender ønsker ikke svaret publisert i WWW]</em><p>";
}

print <<EOT;
<input type="radio" name="publiseres" value="nei,mail" $pubmail> Nei, men send email<br>
<input type="radio" name="publiseres" value="nei" $pubnei> Nei, og ikke send email<br>
</td>
EOT


    if (length $input{'besvart'} ) {
	print "<tr><td>\n";
	print "<p>Det er allerede sendt svar pr. e-post til denne brukeren<br>\n";
	print "Om det likevel skal sendes ny mail, sett en markering her:\n";
	print qq!<input type="hidden" name="besvart" value="ja">!;
	print qq!<input type="hidden" name="sendny" value="">!;
	print qq!<input type="checkbox" name="sendny" value="ja">\n!;
	print "</td>\n";
    } else {
	print qq!<input type="hidden" name="besvart" value="ja">!;
	print qq!<input type="hidden" name="sendny" value="">!;
    }

print <<EOT;
<tr>
<td align="center">
<input type="hidden" name="firma" value="$input{firma}">
<input type="hidden" name="navn" value="$input{navn}">
<input type="hidden" name="stilling" value="$input{stilling}">
<input type="hidden" name="adresse" value="$input{adresse}">
<input type="hidden" name="postnummer" value="$input{postnummer}">
<input type="hidden" name="poststed" value="$input{poststed}">
<input type="hidden" name="epost" value="$input{epost}">
<input type="hidden" name="telefon" value="$input{telefon}">
<input type="hidden" name="fax" value="$input{fax}">
<input type="hidden" name="regdato" value="$input{regdato}">
<input type="hidden" name="revdato" value="$revdato">
<input type="hidden" name="intern" value="$input{intern}">
<input type="hidden" name="anonym" value="$input{anonym}">
<input type="hidden" name="file" value="$input{file}">

<input type="submit" value="Oppdater"> 
<input type="reset" value="Nytt skjema">
</td>
</table>
</center>
EOT


exit 0;

