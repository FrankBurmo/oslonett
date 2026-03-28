#!/local/bin/perl5

require "lib.pl";

&header("Bestilling");

print <<EOT;

<form method="POST" action="sendbestilling.cgi">

<dl>
<table border="0" cellpadding="0">

<tr>
<td><dt><b>Navn:</b></td>
<td><dd><input name="navn" size="55"></td>

<tr>
<td><dt><b>Firma:</b></td>
<td><dd><input name="firma" size="55"</td>

<tr>
<td><dt><b>Adresse:</b></td>
<td><dd><input name="adresse" size="55"</td>

<tr>
<td><dt><b>Postnr og -sted:</b></td>
<td><dd><input name="postnr" size="6">
<input name="poststed" size="46"></td>

<tr>
<td><dt><b>Telefon:</b></td>
<td><dd><input name="telefon" size="15"</td>

<tr>
<td><dt><b>Telefaks:</b></td>
<td><dd><input name="telefaks" size="15"</td>

<tr>
<td><dt><b>E-post:</b></td>
<td><dd><input name="e-post" size="30"</td>

<tr>
</table>
</dl>

<input type="submit" value=" Send bestilling ">
</form>

</body>
</html>
EOT

exit 0;
