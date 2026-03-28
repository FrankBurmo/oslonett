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


&blank_response unless $FORM{'Navn'};
&blank_response unless $FORM{'Adresse'};
&blank_response unless $FORM{'Pnr'};
&blank_response unless $FORM{'Poststed'};
&blank_response unless $FORM{'artbra'};
&blank_response unless $FORM{'strukbra'};
&blank_response unless $FORM{'grafikknivaa'};

$mottager = "arneom@oslonett.no,serief@oslonett.no";


open(MAIL, "|$mailprog $mottager") || die "Greide ikke å åpne mail-programmet!\n";
print MAIL "Dette er informasjon som er blitt sendt automatisk ved hjelp av GOALs elektroniske ratingsystem: \n\n";

print MAIL "  INFORMASJON OM AVSENDER! \n\n";
print MAIL "       Navn: $FORM{'Navn'} \n";
print MAIL "    Adresse: $FORM{'Adresse'} \n";
print MAIL "     Postnr: $FORM{'Pnr'} $FORM{'Poststed'} \n";
print MAIL "      Email: $FORM{'Email'} \n";
print MAIL "    Telefon: $FORM{'telefon'} \n";
print MAIL "      Alder: $FORM{'Alder'} \n\n";

print MAIL "           SPØRSMÅL!\n\n ";
print MAIL "Hva synes du om artiklene i GOAL?: $FORM{'artbra'}\n";
print MAIL "Kommentarer: $FORM{'arttekst'}\n\n";
print MAIL "Hvordan synes du informasjonen er strukturert?: $FORM{'strukbra'}\n";
print MAIL "Kommentarer: $FORM{'struktekst'}\n\n";
print MAIL "Hva synes du om grafikkbruken i GOAL?: $FORM{'grafikknivaa'}\n";
print MAIL "Kvalitet: $FORM{'grafikkkvalitet'}\n\n";
print MAIL "Hva synes du om muligheten til å søke blant artiklene?: $FORM{'sokbra'}\n";
print MAIL "Kommentarer: $FORM{'soktekst'}\n\n";
print MAIL "Hvor ofte kjøper du papirversjonen av GOAL?: $FORM{'papir'}\n\n";
print MAIL "Hvordan liker du å lese om fotball på WWW?: $FORM{'fotballwww'}\n\n";
print MAIL "Føler du at Internettversjonen av GOAL vil kunne føre til at du ikke kjøper papirversjonen av GOAL?: $FORM{'konkurent'}\n";

print MAIL "-----------------------------------------------------\n";
print MAIL "Server protocol: $ENV{'SERVER_PROTOCOL'}\n";
print MAIL "Remote host: $ENV{'REMOTE_HOST'}\n";
print MAIL "Remote IP address: $ENV{'REMOTE_ADDR'}\n";
print MAIL "-----------------------------------------------------\n";
close(MAIL);

# Make the person feel good for writing to us
print  "<title> Takk </title>\n";

print "<body bgcolor=#503060 text=#ffffff link=#ffffaa vlink=#ffffaa>
<hr><center><a href=\"/me/ts/goal/\"><img alt=\"\" src=\"/me/ts/goal/gifs/goal_200.gif\" width=150 border=0></a></center><hr>\n\n";

print  "<H1> Takk </H1>\n";
print "Takk for at du tok deg tid til å evaluere GOAL. Du er nå med i trekningen av en fotballvideo. Vinnerene vil bli lagt ut på evalueringssiden.<p>\n";
print "Tilbake til <A HREF=\"http://www.oslonett.no/me/ts/goal\">GOALs hjemmeside</A>.<P>";

# ------------------------------------------------------------
# subroutine blank_response
sub blank_response
{
    print "<title> Feilmelding </title>\n";
    print "<body bgcolor=#503060 text=#ffffff link=#ffffaa vlink=#ffffaa>
<hr><center><a href=\"/me/ts/goal/\"><img alt=\"\" src=\"/me/ts/goal/gifs/goal_200.gif\" width=150 border=0></a></center><hr>\n\n";
    print "<H1> Feilmelding </H1>\n";
    print "Registreringen din hadde blanke felter, og ble derfor ikke registrert.<p>";
    print "<A HREF=\"http://www.oslonett.no/me/ts/goal/rating.html\">Prøv en gang til</A>, eller ";
    print "returner til <A HREF=\"http://www.oslonett.no/me/ts/goal/\">GOALs hjemmeside</A>.<P>";
    exit;
}


