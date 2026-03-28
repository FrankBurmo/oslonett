#!/local/bin/perl -- -*-perl-*-

$filnavn = "tavle.html";
$tmpfil1 = "tmpfil1.$$";
$toppfil = "toppconfig.html";
$bunnfil = "bunnconfig.html";

$mailprog = '/usr/ucb/mail -s "Innlegg: Savoys gjestebok"';
$recipient = 'arneom@a.sn.no,SAVOYEMAIL@aol.com,oddstad@a.sn.no';

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

# If the comments are blank, then give a "blank form" response
&blank_response unless $FORM{'comments'};

$date=`date`;

open (FIL,">$tmpfil1");
open (FIL1,"<$filnavn");

while(<FIL1>)
{
    if(/.*<!--her-->/)
    {
	print FIL "<!--her-->\n";
        print FIL "<p> <H2>$FORM{'overskrift'}</H2> \n";
	print FIL "$FORM{'comments'} <p>\n";
	print FIL "<b> $FORM{'navn'}, $FORM{'email'}</b><p>\n";
        print FIL "Hostname: $ENV{'REMOTE_HOST'} $date\n";
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

open (MAIL, "|$mailprog $recipient") || die "Can't open $mailprog!\n";
print MAIL " Dette er en kopi av et innlegg som nettop ble lagt inn i Savoys elektroniske gjestebok:\n\n";
print MAIL "$FORM{'overskrift'} $date \n";
print MAIL "$FORM{'comments'}\n";
print MAIL " $FORM{'navn'}, $FORM{'email'}\n";
print MAIL "Hostname: $ENV{'REMOTE_HOST'}\n";
close (MAIL);


# Make the person feel good for writing to us
open (TOPP,"<$toppfil");
while(<TOPP>)
  {
	print;
  }
close TOPP;
print "<center><p><font size=+2>Thank you for leaving a message in Savoys guestbook!</font><P>";
print "Return to the <A HREF=\"/savoy/gjestebok/\">guestbook.</A>.<center><P>";
print "</body></html>\n";


# ------------------------------------------------------------
# subroutine blank_response
sub blank_response
{
    open (TOPP,"<$toppfil");
    while(<TOPP>)
    {
	print;
    }
    close TOPP;
    print "<center><font size=+2><b>Your message was empty!</b></font><p>";
    print "<a href=\"nyttinnlegg.html\"> Try again</a>, or ";
    print "return to <A HREF=\"/savoy/\">Savoys frontpage.</A></center><P>";
    print "</body></html>\n\n";
    exit;
}


