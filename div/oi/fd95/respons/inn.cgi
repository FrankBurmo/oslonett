#!/local/bin/perl5

$ENV{IFS} = " ";
$ENV{PATH} = "/local/bin:/usr/bin:/bin/.";

require "intern/fd-lib.pl";

print "Content-type: text/html\n\n";

&getinput;

$input{'regdato'} = &dato;
$maskin{'maskin'} = $ENV{REMOTE_HOST} || $ENV{REMOTE_ADDR} || "[ukjent]";
push(@names, "maskin", "regdato");

&noinput unless ($input{overskrift} || $input{kommentar});

$input{base} =~ s/\W//g;	# unngå brysomme filnavn...
$teller = &uniquenumber("$intdir/$input{base}count.txt");
$filnavn = sprintf("%s/%sreg%05d.txt", $intdir, $input{base}, $teller);

open(FILE, ">$filnavn") || &error("Kunne ikke åpne filen '$filnavn'");
foreach (@names) {
    print FILE "$_: $input{$_}\n";
}
close(FILE);

print &header("Kvittering: Har registrert spørsmål/kommentar");

print <<EOT;

Følgende innsendt(e) spørsmål eller kommentar(er) samt tilhørende
adresse-informasjon er nå registrert hos oss:

<center>
<table border="6" cellpadding="4">
<tr>
<td colspan="2" align="center"><font size="5"><b>Tilbakemelding</b><br></font></td>
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
    print &header("Ingen melding sendt med");

    print <<EOT;

Det er ikke oversendt noen melding fordi du ikke har fylt ut noen av
feltene "overskrift" eller "kommentar/spørsmål".<p>

Gå tilbake til skjemaet og fyll ut disse feltene (og evt. andre
felter). Forsøk deretter å registrere på nytt.<p>

EOT

    print &footer;
    exit 0;
}
