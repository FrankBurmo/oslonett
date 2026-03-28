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


&blank_response unless $FORM{'navn'};
&blank_response unless $FORM{'adresse'};
&blank_response unless $FORM{'pnr'};
&blank_response unless $FORM{'poststed'};


$mottager = "robbi.nash@kelly.no";


open(MAIL, "|$mailprog $mottager") || die "Greide ikke å åpne mail-programmet!\n";
print MAIL "Dette er en mail som er blitt sendt automatisk fra KELLYs informasjonsbestillingsprogram i WWW. Nedenfor finner du hvilke tjenester avsender ønsker informasjon om, sammen med kontaktinformasjon: \n\n";
print MAIL "      Firma: $FORM{'firma'} \n";
print MAIL "       Navn: $FORM{'navn'} \n";
print MAIL "    Adresse: $FORM{'adresse'} \n";
print MAIL "     Postnr: $FORM{'pnr'} $FORM{'poststed'} \n";
print MAIL "      Email: $FORM{'email'} \n";
print MAIL "    Telefon: $FORM{'telefon'} \n\n";
print MAIL "  Vikartype: $FORM{'tjeneste'} \n\n";
print MAIL "-----------------------------------------------------\n";
print MAIL "Server protocol: $ENV{'SERVER_PROTOCOL'}\n";
print MAIL "Remote host: $ENV{'REMOTE_HOST'}\n";
print MAIL "Remote IP address: $ENV{'REMOTE_ADDR'}\n";
print MAIL "-----------------------------------------------------\n";
close(MAIL);

# Make the person feel good for writing to us
print  "<title>KELLY: Takk </title>\n";
print  "<body bgcolor=#e0f0e0 text=#006600>\n";
print  "<H1> Takk </H1>\n";
print  "Du har nå bestilt informasjon fra KELLY. Følgende informasjon er blitt sendt: <p>";
print  " <pre>       Navn: $FORM{'navn'} \n";
print  "      Firma: $FORM{'firma'} \n";
print  "    Adresse: $FORM{'adresse'} \n";
print  "     Postnr: $FORM{'postnr'} $FORM{'poststed'} \n";
print  "      Email: $FORM{'email'} \n";
print  "    Telefon: $FORM{'telefon'} \n\n";
print  "  Vikartype: $FORM{'tjeneste'} \n\n";
print  "   </pre><p>";
print "Tilbake til <A HREF=\"http://www.kelly.no/kelly/\">KELLYs hjemmeside</A>.<P>";

# ------------------------------------------------------------
# subroutine blank_response
sub blank_response
{
    print "<title>KELLY: Feilmelding </title>\n";
    print  "<body bgcolor=#e0f0e0 text=#006600>\n";
    print "<H1> Feilmelding </H1>\n";
    print "Registreringen din hadde blanke felter, og ble derfor ikke registrert.<p>";
    print "<A HREF=\"http://www.kelly.no/kelly/bestilling.html\">Prøv en gang til</A>, eller ";
    print "returner til <A HREF=\"http://www.kelly.no/kelly/\">KELLYs hjemmeside</A>.<P>";
    exit;
}


