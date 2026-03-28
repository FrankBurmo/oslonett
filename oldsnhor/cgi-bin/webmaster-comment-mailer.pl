#/local/bin/perl -- -*-perl-*-

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
$mailprog = '/usr/ucb/mail';
$recipient = 'hassan@Eng.Sun.COM';

# Print out what we need
print "Content-type: text/html\n\n";
print "<Head><Title>Thank you</Title></Head>";
print "<Body><H1>Thank you</H1>";

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
print MAIL "$FORM{'username'} ($FORM{'realname'}) sent the following\n";
print MAIL "comment about the ripple WWW server:\n\n";
print MAIL  "------------------------------------------------------------\n";
print MAIL "$FORM{'comments'}";
print MAIL "\n------------------------------------------------------------\n";
print MAIL "Remote host: $ENV{'REMOTE_HOST'}\n";
print MAIL "Remote IP address: $ENV{'REMOTE_ADDR'}\n";
close (MAIL);


print "Thank you for your comments!<P>";
print "Return to our <A HREF=\"/\">home page</A>, if you want.<P>";
