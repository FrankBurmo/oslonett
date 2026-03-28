#!/local/bin/perl



require "lib/tittellib.pl";

%input = &getinput;

&printheader ("FONO: Bestilling");


print<<EOT;

Du har angitt at du vil bestille følgende tittel mot postoppkrav:
<p>
<center>

        <table cellspacing=5 border=5 cellpadding=2>
        <tr><th align=left>Tittel</th><th align=left>Artist</th>
            <th align=left>Label</th>
            <th align=left>Kat.nr</th>
            <th align=left>Pris</th></tr>
    <tr><td>$input{'Tittel'}</td><td>$input{'Artist'}</td>
    <td>$input{'Label'}</td>
    <td>$input{'Kat.nr'}</td><td>$input{'Pris'}</td></tr\
>

        </table>
</center>

<p>
Fyll nå ut navn og adresse. Du bør også <a href="/fono/beting.htm">lese våre
betingelser</a>.
<p>
<form method="POST" action="/cgi-bin/mailit">
<input type="hidden" name="mailto" value="steinar@a.sn.no,majorst@sn.no">
<input type="hidden" name="subject" value="FONO: Bestilling - $input{'Kat.nr'}">
<input type="hidden" name="Label" value="$input{'Label'}">
<input type="hidden" name="Tittel" value="$input{'Tittel'}">
<input type="hidden" name="Artist" value="$input{'Artist'}">
<input type="hidden" name="Kat.nr" value="$input{'Kat.nr'}">
<input type="hidden" name="Pris" value="$input{'Pris'}">
<pre>

Navn	    : <input name="Navn" size=40>
Adresse     : <input name="Adresse" size=40> 
Postnr      : <input name="Postnummer" size=6> Poststed : <input name="Poststed" size=20>
Evt. EPost  : <input name="EPost" size=40>
Telefon     : <input name="Telefon" size=10> Fax : <input name="Fax" size=10>
</pre>
<input type="submit" value="Send bestilling">
</form>

EOT
&printfooter;




