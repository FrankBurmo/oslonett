#!/local/bin/perl -- -*-perl-*-

# ------------------------------------------------------------

# Form-mail.pl, by Reuven M. Lerner (reuven@the-tech.mit.edu).
# This is a rewrite of a program that was trashed by our power
# surge in the middle of February 1994.

# ------------------------------------------------------------

# Bugs and other fixes

# March 1, 1994 (Reuven)
# Fixed security hole that could result from people
# executing subshells
# ------------------------------------------------------------

# Define fairly-constants
$mailprog = '/usr/ucb/mail -s "A comment about the World Cup 1994 WWW Server."';
$recipient = 'webmaster@www.worldcup.com';

# Print out what we need
print "Content-type: text/html\n\n";
print "<h2><a href=/index.html><img align=middle src=/wc94/images/head.WC.small.gif></a> World Cup 1994 WWW Server Comment Form</h2>";
print "<p><hr><p>";
print "<Head><Title>Thank you</Title></Head>";
print "<Body><H1>Thank you for your comments.</H1>";

# Get the input
read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});

# Split the name-value pairs
@pairs = split(/&/, $buffer);

foreach $pair (@pairs)
{
    ($name, $value) = split(/=/, $pair);
    $value =~ tr/+/ /;
    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

    # Stop people from using subshells to execute commands
    $value =~ s/~!/ ~!/g; 

    # Uncomment for debugging purposes
    # print "Setting $name to $value<P>";

    $FORM{$name} = $value;
}

# Now send mail to $recipient

open (MAIL, "|$mailprog $recipient") || die "Can't open $mailprog!\n";
print MAIL "\n\n$FORM{'username'}\n";
print MAIL "$FORM{'realname'}\n";
print MAIL "$FORM{'phonenum'}\n";

print MAIL "sent the following comment about the WorldCup 1994 WWW Server:\n\n";
print MAIL  "------------------------------------------------------------\n\n";
print MAIL "$FORM{'comments'}\n";
print MAIL "\n------------------------------------------------------------\n\n";
print MAIL "Remote host: $ENV{'REMOTE_HOST'}\n";
print MAIL "Remote IP address: $ENV{'REMOTE_ADDR'}\n";
close (MAIL);


print "<P>";
print "<ul><li>Return to the <A HREF=\"/wc94/index.html\">World Cup 1994 WWW Server</A>, if you want.</ul><P><hr>";
print "<p>Your comments have been forwarded to <b>webmaster@www.worldcup.com.</b>";
