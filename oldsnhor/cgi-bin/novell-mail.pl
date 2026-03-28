#!/local/bin/perl -- -*-perl-*-


$mailprog = "/usr/ucb/mail";

print "Content-type: text/html\n\n";


# Get the input
read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});

# Split the name-value pairs
@pairs = split(/&/, $buffer);

foreach $pair (@pairs)
{
    ($name, $value) = split(/=/, $pair);

    # Un-Webify plus signs and %-encoding
    $value =~ tr/+/ /;
    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

    # Stop people from using subshells to execute commands
    # Not a big deal when using sendmail, but very important
    # when using UCB mail (aka mailx).
    # $value =~ s/~!/ ~!/g; 

    # Uncomment for debugging purposes
    # print "Setting $name to $value<P>";

    $FORM{$name} = $value;
}


&blank_response unless $FORM{'Str'};
&blank_response unless $FORM{'Navn'};
&blank_response unless $FORM{'Adresse'};
&blank_response unless $FORM{'Pnr'};
&blank_response unless $FORM{'Poststed'};


$mottager = "novfor@oslonett.no";


open(MAIL, "|$mailprog $mottager") || die "Greide ikke å åpne mail-programmet!\n";
print MAIL "Dette er informasjon som er blitt sendt automatisk ved hjelp av Novell Forums elektroniske registreringsskjema: \n\n";
print MAIL "      Ønske: $FORM{'Str'} \n";
print MAIL "       Navn: $FORM{'Navn'} \n";
print MAIL "    Adresse: $FORM{'Adresse'} \n";
print MAIL "     Postnr: $FORM{'Pnr'} $FORM{'Poststed'} \n";
print MAIL "      Firma: $FORM{'Firma'} \n";
print MAIL "      Email: $FORM{'Email'} \n";
print MAIL "     ID-fil: $FORM{'svar'} \n\n";
print MAIL " Kunden vil ha informasjon tilsendt som: $FORM{'infotype'}\n\n";
print MAIL "-----------------------------------------------------\n";
print MAIL "Server protocol: $ENV{'SERVER_PROTOCOL'}\n";
print MAIL "Remote host: $ENV{'REMOTE_HOST'}\n";
print MAIL "Remote IP address: $ENV{'REMOTE_ADDR'}\n";
print MAIL "-----------------------------------------------------\n";
close(MAIL);

# Make the person feel good for writing to us
print  "<title> Takk </title>\n";
print  "<H1> Takk </H1>\n";
print  "Du har registrert deg elektronisk hos Novell Forum, og vi har registrert følgende informasjon: <p>";
print  " <pre>       Navn: $FORM{'Navn'} \n";
print  "    Adresse: $FORM{'Adresse'} \n";
print  "     Postnr: $FORM{'Postnr'} $FORM{'Poststed'} \n";
print  "      Firma: $FORM{'Firma'} \n";
print  "     ID-fil: $FORM{'svar'} \n";
print  "      Ønske: $FORM{'Str'} \n";
print  "   </pre><p>";
print  " Du vil få eventuell informasjon tilsendt som: $FORM{'infotype'}<p>";
print "Tilbake til <A HREF=\"http://www.oslonett.no/home/novfor/\">Novell Forums's hjemmeside</A>.<P>";

# ------------------------------------------------------------
# subroutine blank_response
sub blank_response
{
    print "<title> Feilmelding </title>\n";
    print "<H1> Feilmelding </H1>\n";
    print "Registreringen din hadde blanke felter, og ble derfor ikke registrert.<p>";
    print "<A HREF=\"http://www.oslonett.no/home/novfor/novmail.htm\">Prøv en gang til</A>, eller ";
    print "returner til <A HREF=\"http://www.oslonett.no/home/novfor/\">Novell Forum's hjemmeside</A>.<P>";
    exit;
}


