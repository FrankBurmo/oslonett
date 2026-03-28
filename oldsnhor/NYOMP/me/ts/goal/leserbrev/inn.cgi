#!/local/bin/perl5

$ENV{IFS} = " ";
$ENV{PATH} = "/local/bin:/usr/bin:/bin/.";

require "intern/lib.pl";

print "Content-type: text/html\n\n";

&getinput;

$input{'regdato'} = &dato;
$input{'maskin'} = $ENV{REMOTE_HOST} || $ENV{REMOTE_ADDR} || "[ukjent]";
push(@names, "maskin", "regdato");

&noinput unless ($input{overskrift} || $input{leserbrev});

$teller = &uniquenumber($tellerfil);
$filnavn = sprintf("%s/brev%05d.txt", $intdir, $teller);

open(FILE, ">$filnavn") || &error("Kunne ikke åpne filen '$filnavn'");
foreach (@names) {
    print FILE "$_: $input{$_}\n";
}
close(FILE);

print &header("Kvittering: Har registrert leserbrev");

print <<EOT;

<h2>Takk for innsendt leserbrev</h2>

Brevet ditt er nå oversendt redaksjonen. Når redaksjonen har svart på
brevet eller publisert det uten kommentar får du beskjed pr.
elektronisk post dersom du har oppgitt en e-post-adresse.
<p>

Kopi av det mottatte leserbrevet er gjengitt nedenfor:

<center>
<table border="6" cellpadding="4">
<tr>
<td colspan="2" align="center"><font size="5"><b>Leserbrev</b><br></font></td>
<dl>
EOT
foreach (@names) {
    next unless length $input{$_};
    $name = $_;

    substr($name,0,1) =~ tr/a-zæøå/A-ZÆØÅ/;

    printf("<dt><tr>\n<td><b>%s:</b></td>\n", $name);
    printf("<dd><td>%s</td>\n", $input{$_});
    print "</tr>\n";
}
print <<EOT;
</dl>
</table>
</center>
<p>

Meldingen er nå oversendt redaksjonen. Hvis den publiseres i WWW og
hvis du oppga en e-post-adresse ovenfor, får du automatisk en kopi av
svaret.

EOT
print &footer;

exit 0;



sub noinput {
    print &header("Ingen tekst sendt");

    print <<EOT;

Det er ikke oversendt noe leserbrev fordi du ikke har fylt ut noen av
feltene "overskrift" eller "leserbrev".<p>

Gå tilbake til skjemaet og forsøk igjen.<p>

EOT

    print &footer;
    exit 0;
}
