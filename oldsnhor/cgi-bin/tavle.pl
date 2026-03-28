#!/local/bin/perl -- -*-perl-*-

$filnavn = "/local/www/TMP/oppslagstavle.html";
$tmpfil1 = "/local/www/TMP/tmpfil1.$$";


print "Content-type: text/html\n\n";

# Print a title and initial heading
print "<Head><Title>Takk</Title></Head>";
print "<Body><H1>Takk</H1>";

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

# If the comments are blank, then give a "blank form" response
&blank_response unless $FORM{'comments'};



open (FIL,">$tmpfil1");
&slettet_tavle unless open (FIL1,"<$filnavn");

while(<FIL1>)
{
    if(/^<!--her-->/)
    {
        print FIL "<!--her-->\n";
        print FIL "<p> <H2>$FORM{'overskrift'} $FORM{'dato'}</H2> \n";
        print FIL "$FORM{'comments'} <p>\n";
        print FIL "<b> $FORM{'navn'}</b><p>\n";
        print FIL "<a href= \"$FORM{adresse}\"> $FORM{tittel} </a>";
        print FIL "<p><hr>";
    }
    else
    {
        print FIL;
    }
}
close (FIL);
close (FIL1);
`mv $tmpfil1 $filnavn`;

# Make the person feel good for writing to us
print "Takk for at du ville legge inn denne beskjeden i <I>oppslagstavla til Regjeringskvartalets.</I>!<P>";

# ------------------------------------------------------------
# subroutine blank_response
sub blank_response
{
    print "Beskjeden din var blank og ble derfor ikke hengt opp";
    print "på Regjeringskvartalets elektroniske oppslagstavle. ";
    exit;
}

sub slettet_tavle
{
    open (TAVLE,">$filnavn");
    print TAVLE "<TITLE>Regjeringskvartalets elektroniske oppslagstavle</TITLE>\n";
    print TAVLE "<H1>Regjeringskvartalets elektroniske oppslagstavle</H1>\n";
    print TAVLE "<hr>\n";
    print TAVLE "<!--her-->\n";
    close (TAVLE);
    open (FIL1,"<$filnavn")
}

