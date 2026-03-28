#!/local/bin/perl5
# returnerer HTML form med ferdig utfylte felter

require "lib.pl";
print "Content-type: text/html\n\n";

&getinput;

open(FILE, $input{file}) || &error("Kan ikke åpne filen $input{file}");

while (<FILE>) {
    chop;
    ($name, $value) = split(": ", $_, 2);
    $name =~ tr/A-ZÆØÅ/a-zæøå/;
    $input{$name} = $value;
}

$leserbrev = $input{leserbrev};
$leserbrev =~ s/<p>\s*/\n\n/g;
$leserbrev =~ s/<br>\s*/\n/g;

$svar = $input{svar};
$svar =~ s/<p>\s*/\n\n/g;
$svar =~ s/<br>\s*/\n/g;


$revdato = &dato;

if ($input{publiseres} =~ /^ja/i) {
    $pubja = "checked";
} elsif ($input{publiseres} =~ /mail/i ) {
    $pubmail = "checked";
} else {
    $pubnei = "checked";
}

print &header("Besvare innkommende leserbrev");

print <<EOT;

Fra denne siden kan man
<ol>
<li> redigere innkommende spørsmål eller tilbakemeldinger
<li> besvare innkommende spørsmål eller kommentere tilbakemeldinger
</ol>

Bruk gjerne feltet for signatur nederst på siden - og husk å angi om
teksten skal publiseres eller ei.

<form method="POST" action="$topurl/intern/redinn.cgi">
<center>
<table border="6" cellpadding="4">
<tr>
<td>
<h2>Overskrift:</h2>
<input name="Overskrift" size="65" value="$input{overskrift}">

<h2>Leserbrev:</h2>

<textarea name="leserbrev" rows="15" cols="80">$leserbrev</textarea>
<p>

<table border="0">
<td><b>Avsender</b>:</td><td> <input name="navn" size="65" value="$input{navn}"><br></td>
<tr>
<td><b>E-post</b>:</td><td> <input name="epost" size="65" value="$input{epost}"></td>
</table>

</td>
<tr>
<td>

<h2>Redaksjonelle tillegg - svar, kommentarer, etc.</h2>

<textarea name="Svar" rows="10" cols="80">$svar</textarea><p>
Signatur: <input name="signatur" size="40" value=$input{signatur}><p>

Skal legges synlig i world wide web?

<blockquote>
<input type="radio" name="publiseres" value="ja,mail" $pubja> Ja, og send email<br>
<input type="radio" name="publiseres" value="nei,mail" $pubmail> Nei, men send email<br>
<input type="radio" name="publiseres" value="nei" $pubnei> Nei, og ikke send email<br>
</blockquote>

(Elektroinsk post sendes kun hvis det er angitt en mail-adresse.)
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
	print qq!<input type="hidden" name="besvart" value="">!;
	print qq!<input type="hidden" name="sendny" value="">!;
    }

print <<EOT;
<tr>
<td>
<table border="0">
<td>Registreringsdato:</td><td>       $input{regdato}<br></td>
<tr>
<td>Siste oppdateringsdato:</td><td>  $input{revdato}<br></td>
</table>

</td>
<tr>
<td align="center">
<input type="hidden" name="regdato" value="$input{regdato}">
<input type="hidden" name="revdato" value="$revdato">
<input type="hidden" name="file" value="$input{file}">
<input type="hidden" name="ref" value="$input{ref}">

<input type="submit" value="Oppdater"> 
<input type="reset" value="Nytt skjema">
</td>
</table>
</center>
EOT


exit 0;

