#!/local/bin/perl5

require "lib.pl";

%input = &getinput;

&printheader("Lagre ny link i link-databasen");

print <<EOT;

<form method="POST" action="addlink.cgi">
Hvis du vil slette denne link'en, trykk på slette-knappen:
<input type="hidden" name="oldpattern" value="$input{pattern}">
<input type="hidden" name="pattern" value="$input{pattern}">
<input type="hidden" name="url" value="">
<input type="submit" value="Slett denne">
</form>
</font>

Dersom du vil endre link'en, fyll ut nytt søkemønster og/eller ny URL.
Trykk deretter på registreringsknappen:

<font size="+1">
<form method="POST" action="addlink.cgi">
<input type="hidden" name="oldpattern" value="$input{pattern}">
<dl>
<td> <b>Søkemønster</b> (firmanavn)
<dd> <input name="pattern" size="55" value="$input{pattern}">
<dt> <b>URL</b> (<em>NB! fullstendig URL, ikke relativ</em>)
<dd> <input name="url" size="55" value="$input{url}">
</dl>
<input type="submit" value="Registrer ny">
<input type="reset" value="Original-skjema">
</form>
EOT

&printfooter;

exit 0;
