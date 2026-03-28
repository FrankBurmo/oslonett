#!/local/bin/perl5

require "lib.pl";

$mailprog = "/usr/lib/sendmail -t";
$admaddr = "kgn\@oslonett.no";

print "Content-type: text/html\n\n";

&getinput;

&error("Ingen fil angitt, kan ikke gjøre registrering") 
    unless length $input{file};

print &header("Kvittering: Har registrert leserbrev med evt. svar");

&sendmail if ($input{'publiseres'} =~ /mail/i
	      && ( length $input{'sendny'} || ! length $input{'besvart'}));

open(FILE, ">$input{file}")
    || &error("Kunne ikke åpne filen $input{file}");
foreach (@names) {
    print FILE "$_: $input{$_}\n";
}
close(FILE);

print <<EOT;

Følgende data er nå lagret:

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

Tilbake til <a href="redliste.cgi">den interne redaksjonslisten</a>...
EOT


print &footer;

exit 0;


sub sendmail {
    if (! length $input{epost}) {
	print <<EOT;
<hr size="2" noshade>
Ønsker å sende mail, men ingen mottageradresse er angitt!
<hr size="2" noshade>
EOT
        return;
    }

    open(MAIL, "|$mailprog") || &error("Failed to start $mailprog");

    print MAIL "To: $input{epost}\n";
    print MAIL "Reply-to: $admaddr\n";
    print MAIL "Subject: Svar på innsendt leserbrev til GOAL\n";
    print MAIL "\n";		# End of headers

    $overskr = &rearrange($input{'overskrift'});

    $brev = $input{leserbrev};
    $brev =~ s/<br>\s*/\n/ig;
    $brev =~ s/\&gt;/>/ig;
    $brev =~ s/\&lt;/</ig;
    $brev =~ s/\&amp;/&/ig;

    $svar = $input{svar};
    $svar =~ s/<br>\s*/\n/ig;
    $svar =~ s/\&gt;/>/ig;
    $svar =~ s/\&lt;/</ig;
    $svar =~ s/\&amp;/&/ig;

    print MAIL <<EOT;
Denne meldingen er automatisk generert av programmet
$0.

Ditt innsendte leserbrev til GOAL er nå besvart, se nedenfor.
Eventuelle spørsmål om denne tjenesten kan rettes til $admaddr.

-----Spørsmål/kommentar, datert $input{'regdato'}:

$overskr

$brev

     $input{'navn'}, <$input{'epost'}>

-----Svar:

$svar

$input{'signatur'}

EOT
    close MAIL;
    push(@names, "besvart") unless defined($input{besvart});
    $input{'besvart'} = "ja";
    print "Har sendt spørsmål/kommentar og svar pr. mail til $input{'epost'}.<p>\n";
}

sub rearrange {
    local(@a) = @_;

    foreach ( $[ .. $#a ) {
	$a[$_] =~ s/(.{50,75})\s+/$1\n/g;
    }
    return @a;
}
