#!/local/bin/perl -- -*-perl-*-
# ------------------------------------------------------------
# Form-mail.pl, by Reuven M. Lerner (reuven@the-tech.mit.edu).
#
# Last updated: March 14, 1994
#
# Form-mail provides a mechanism by which users of a World-
# Wide Web browser may submit comments to the webmasters
# (or anyone else) at a site.  It should be compatible with
# any CGI-compatible HTTP server.
# 
# Please read the README file that came with this distribution
# for further details.
# ------------------------------------------------------------

# ------------------------------------------------------------
# This package is Copyright 1994 by The Tech. 

# Form-mail is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2, or (at your option) any
# later version.

# Form-mail is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with Form-mail; see the file COPYING.  If not, write to the Free
# Software Foundation, 675 Mass Ave, Cambridge, MA 02139, USA.
# ------------------------------------------------------------

# Define fairly-constants

# This should match the mail program on your system.
$mailprog = '/usr/lib/sendmail';
 
# This should be set to the username or alias that runs your
# WWW server.
$recipient = 'jmfoto@jmfoto.no';

# Print out a content-type for HTTP/1.0 compatibility
print "Content-type: text/html\n\n";

# Print a title and initial heading
print "<Head><Title>Thank you</Title></Head>";
print "<Body><CENTER><H1>Thank you..</H1>";

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

# Now send mail to $recipient

open (MAIL, "|$mailprog $recipient") || die "Can't open $mailprog!\n";
print MAIL "From: $FORM{'username'} ($FORM{'realname'})\n";
print MAIL "Subject: Info Request\n\n";
print MAIL "$FORM{'SNAIL1'}";
print MAIL "$FORM{'SNAIL2'}";
print MAIL "\n\n";
print MAIL "$FORM{'theType'}";
print MAIL "$FORM{'comments'}";
print MAIL "\n\n";
print MAIL "Browser: $ENV{'HTTP_USER_AGENT'}\n";
print MAIL "Refer URL: $ENV{'HTTP_REFERER'}\n";
print MAIL "Server protocol: $ENV{'SERVER_PROTOCOL'}\n";
print MAIL "Remote host: $ENV{'REMOTE_HOST'}\n";
print MAIL "Remote IP address: $ENV{'REMOTE_ADDR'}\n";
print MAIL "SERVER_SOFTWARE: $ENV{'SERVER_SOFTWARE'}\n";
print MAIL "SERVER_NAME: $ENV{'SERVER_NAME'}\n";
print MAIL "GATEWAY_INTERFACE: $ENV{'GATEWAY_INTERFACE '}\n";
print MAIL "SERVER_PORT: $ENV{'SERVER_PORT'}\n";
print MAIL "REQUEST_METHOD: $ENV{'REQUEST_METHOD'}\n";
print MAIL "PATH_INFO: $ENV{'PATH_INFO'}\n";
print MAIL "PATH_TRANSLATED: $ENV{'PATH_TRANSLATED'}\n";
print MAIL "SCRIPT_NAME: $ENV{'SCRIPT_NAME'}\n";
print MAIL "QUERY_STRING: $ENV{'QUERY_STRING'}\n";
print MAIL "AUTH_TYPE: $ENV{'AUTH_TYPE'}\n";
print MAIL "REMOTE_USER: $ENV{'REMOTE_USER'}\n";
print MAIL "REMOTE_IDENT: $ENV{'REMOTE_IDENT'}\n";
print MAIL "CONTENT_TYPE: $ENV{'CONTENT_TYPE'}\n";
print MAIL "CONTENT_LENGTH: $ENV{'CONTENT_LENGTH'}\n";
close (MAIL);

# Make the person feel good for writing to us
print "<A HREF=\"./kart/menyen.map\"><IMG SRC=\"../galleri/menyen.gif\" BORDER=\"0\" ISMAP></A><P>";
print "Thank you $FORM{'realname'} taking the time to mail us..<br>";
print "This is what we're going to see:<p>";
print "From: $FORM{'username'} ($FORM{'realname'})<br>";
#print "Reply-to: $FORM{'username'} ($FORM{'realname'})<br>";
print "Subject: $FORM{'subject'}<p>";
print "$FORM{'comments'}<p>";
print "We will get back to you shortly.<BR>";
print "Now, please - just return to our <A HREF=\"http://www.sn.no/jmfoto/\">webpages</A>.<P>";
print "</CENTER></HTML>";

# ------------------------------------------------------------
# subroutine blank_response
sub blank_response
{
    print "Your comments appear to be blank, and thus were not sent ";
    print "to our webmasters. Please re-enter your comments, or ";
    print "return to our <A HREF=\"http://www.jmfoto.no/index.html/\">home page</A>.<P>";
    exit;
}



