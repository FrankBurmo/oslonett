#!/local/bin/perl -- -*-perl-*-

$inputfil = "/home/frogner/www/rl/op/whats.html";

print "Content-type: text/html\n\n";


print "<Head><Title>What's up in Oslo</Title></Head>";
print "<body><center><H1>What's up in Oslo</H1></center>";

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
&blank_response unless $FORM{'dato'};

if(!open (INNFIL,"<$inputfil"))
{
    print "<p> Søkefilen kunne ikke åpnes! <p>\n";
    print "<p> Returner til Oslonetts <A HREF=\"/http://www.oslonett.no/\">hjemmeside</A>\n";
    exit;
}

$funnet=0;
$dato=$FORM{'dato'};
print "<p><b> You are now searching for events the $FORM{'dato'}.july. </b><p>\n";
$nestedato=$FORM{'dato'}+1;

while(<INNFIL>)
{
    if(/^<b>.*\b$dato\D/)
    {
	$funnet=1;
	print;
    }
    elsif(/^<b>.*\b$nestedato\D/)
    {
	$funnet=0;
    }
    elsif($funnet==1)
    {
	print;
    }
}

print "</body>\n";

sub blank_response
{
    print "Du førte ikke inn en dato i datofeltet, og det var derfor";
    print " ikke mulig å søke i mengden av begivenheter i Oslo.";
    print "<p> Returner til Oslonett's <A HREF=\"/http://www.oslonett.no/\">hjemmeside</A>.<P>";
    exit;
}



