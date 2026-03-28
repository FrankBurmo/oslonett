#!/usr/bin/perl

use lib "/home/oslonett/perllib";
use mySSI;

# $Id: mailto.cgi,v 1.5 1998/08/05 12:28:59 steinar Exp $

use locale;
use POSIX qw(setlocale);

use URI::Escape;
use CGI;
my $cgi = new CGI;

my  $loc = POSIX::setlocale( &POSIX::LC_ALL, "no_NO" );
my %query;

my @keys = $cgi->param;
for (@keys) {
    $query{$_} = $cgi->param($_);
};

$query{subject} =~ s/\@NAVN\@/$query{Navn}/g;

my %CFG = ();
my $SEEN = 0;

## Options usually set by HTML hidden fields will not be echoed
## or sent in mail. Add 'to' or 'subject' if you want

my %dont_echo =  ( requiredfields,      1,
		   errortemplate,       1,
		   receipttemplate,     1,
		   printfpadding,       1,
		   mailtemplate,        1,
		   mailashtml,          1,
		   receiptstyle,        1,
		   errorstyle,          1,
		   receipturl,          1,
		   replyto,             1,
 	 	   cc,                  1,
 	 	   to,                  1,
 	 	   subject,             1,
   		   bcc,                 1 );

## Bootstrap. Read config file getting all other necessary options

 readConfig ('/home/oslonett/www/adm/mailto/mailto.cfg', \%CFG);

## Prepare 

 my @required_fields = split (/,/, $CFG{REQUIREDFIELDS});
 push @required_fields, split (/,/, $query{requiredfields}) 
    if $query{requiredfields};

## Check if all is well

 checkSanity();

## Multi select values returned in array ref, unpack if any

 handleMultiselect();

## Send the mail ..

 doMail();

## Oppdater fil ?

#doFileUpdate() if ($query{valencia} or $query{pass});

## And write receipt to the user

 doReceipt();

#########################
##
## Subroutines

sub readConfig {
 my $file = shift;
 my $cfg  = shift;
 my ($key,$val);

 open (C, $file) ||
   error ("Can't open config file: $file");

 while (<C>) {
  next 
   if /^(#| )/;
	 chomp;
 ($key,$val) = split(/=/,$_);
  $cfg->{$key} = $val;
 }
 close(C);

}

##

sub get_template_by_url {
    my $turl = shift;

#    use LWP::UserAgent;
#    use HTTP::Request;
#
#    my $ua = new LWP::UserAgent;
#    $ua->timeout(4);
#    $ua->agent("IS_mailto/1.0");
#    my $request = new HTTP::Request GET => $turl;
#    $response = $ua->request($request);
#    error ("Can't get at template on url $turl")
#      unless $response->is_success;
#    $response->content;

    "Not implemented";
}

sub error {
 my $mess = shift;
 my $tmpl;
 delete $query{errortemplate}
 if $SEEN;
 $SEEN = 1;
 if ($query{errortemplate}) {
     $tmpl = get_template_by_url ($query{errortemplate});
 } elsif ($CFG{ERRORTEMPLATE}) {
    local($/) = undef;
    open(E,$CFG{ERRORTEMPLATE}) || 
	die "Content-type: text/plain\n\nCan't open errortemplate";
    $tmpl = <E>;
    close (E);
 } else { die "Content-type: text/plain\n\nNo error template found";  }

    $tmpl = expand_inc($tmpl);
    $tmpl =~ s/\@MESSAGE\@/$mess/;
    $tmpl =~ s/\@ERRORSTYLE\@/$query{errorstyle} ? $query{errorstyle} 
                                                  : $CFG{ERRORSTYLE}/eg;
    $tmpl = expand_tmpl($tmpl);
    print "Content-type: text/html\n\n$tmpl";

    exit;
}
 
sub checkSanity {
    my $fields = "";

## Check security

    if($CFG{ALLOWEDREFERERS}) {
	my @list = split(/,/,$CFG{ALLOWEDREFERERS});
        my $match = 0;
        for (@list) {
         $match = 1
	     if( $ENV{HTTP_REFERER} =~ /^$_/);
        }
      error ("File $ENV{HTTP_REFERER} not allowed to access mailto script")
	  unless $match;
    }

    if($CFG{ALLOWEDCLIENTS}) {
	my @list = split(/,/,$CFG{ALLOWEDCLIENTS});
        my $match = 0;
        for (@list) {
         $match = 1
	     if( $ENV{REMOTE_HOST} =~ /$_$/ or
		 $ENV{REMOTE_ADDR} =~ /$_$/);
        }
    error ("HTTP client $ENV{REMOTE_HOST} not allowed to access mailto script")
	  unless $match;
    }

## Security ok, check fields

    for (@required_fields) {
      next
	if $query{$_};
      $fields .= "$_,";
    }

    chop($fields) 
	if $fields;
    error ("Missing fields from input:<p>$fields</p>")
	if $fields;


}

sub doFileUpdate {

    my $dir = "/home/steinar/www/sjk/mdl/turinfo/2001";

    my $sleep = 1;
    while (-f "$dir/.lock") {
	sleep ($sleep);
	$sleep = $sleep*2;
    }
    my $file = $query{pass} ? ".passnr" : ".paameldinger";
    system ("touch $dir/.lock");
    open F, ">>$dir/$file" ||
        error ("Kan ikke oppdatere liste over innmeldinger/passnr");
    my ($min,$h,$d,$m,$y) = (localtime)[1,2,3,4,5];
    $m++;
    $y+=1900;

    my @keys = $query{pass} ? ('Navn', 'Passnr','Instrument') :
	('Navn','Blir med','Deltar som','Følger korpsets reiseopplegg',
		'Reiser sammen med/deler rom med','Annen info');
    my $eq;

    printf F "%d-%02d-%02d-%02d:%02d", $y,$m,$d,$h,$min;
    for (@keys) {
#	$eq = uri_escape($_);
        $query{$_} =~ tr/\n\r/  /;
        printf F "¤$query{$_}";
    }
    printf F "\n";
    close (F);
    unlink ("$dir/.lock");
}

sub doMail {

    my ($tmpl,$body,$replyto,$from) = "";

    $from = $CFG{DEFAULTFROM} ? $CFG{DEFAULTFROM} : "";

    $replyto = $CFG{DEFAULTREPLYTO} ? $CFG{DEFAULTREPLYTO} : 
	($query{replyto} ? $query{replyto} : "");

    { 
	local($/) = undef;
        open (T, $CFG{MAILTEMPLATE}) ||
	   error ("Can't open mail template");
        $tmpl = <T>;
        close (T);
    }


    foreach (sort keys %query) {
     next 
	 if $dont_echo{$_};
     $query{$_} =~ s/(.{30})([^\w]+)/$1$2\n\t\t/g
         unless $query{mailashtml};

     $body .= $query{mailashtml} ? sprintf qq#<tr valign="top"><td>%s</td><td>$query{$_}</td></tr>\n#, my_unescape($_) :
        sprintf "%$CFG{PRINTFPADDING}s : %s\n", my_unescape($_), $query{$_};
    }

    $tmpl =~ s/\@FORMDATA\@/$body/;
    $tmpl = expand_tmpl($tmpl);

    open(MAIL, "| $CFG{SENDMAIL}") || error ("Can't start sendmail");
    print MAIL "To: $query{to}\n";
    print MAIL "Cc: $query{cc}\n"
	if $query{cc};
 
    print MAIL "Bcc: $query{bcc}\n"
	if $query{bcc};
    print MAIL "From: $from\n"
	if $from;
    print MAIL "Reply-to: $replyto\n"
	if $replyto;
    print MAIL "Subject: $query{subject}\n";

    print MAIL "\n";
    print MAIL $tmpl;
    close(MAIL);
}


sub doReceipt {
    my $tmpl = "";
    if ($query{receipturl}) {
	my $safe_query = "";
        if ($query{receipturl} =~ /\?\@QUERY\@/) {
	  foreach (sort keys %query) {
           next
	      if $dont_echo{$_};
           $safe_query .= uri_escape($_) . "=" . uri_escape($query{$_}) . "&"; 
         }
         chop($safe_query);
         $query{receipturl} =~ s/\@QUERY\@/$safe_query/;
        }

	print "Location: $query{receipturl}\n\n";
        exit;
    }

## Normal receipt

 if ($query{receipttemplate}) {
     $tmpl = get_template_by_url ($query{receipttemplate});
 } else {
     local ($/) = undef;
     open (T, $CFG{RECEIPTTEMPLATE}) ||
	 error ("Can't open receipt template");
     $tmpl = <T>;
     close (T);
 }

    my $body = "";
    foreach (keys %query) {
     next 
	 if $dont_echo{$_};

     $body .= sprintf qq#<tr valign="top"><td>%s</td><td>$query{$_}</td></tr>\n#, my_unescape($_);
    }

    $tmpl =~ s/\@FORMDATA\@/$body/;
    $tmpl =~ s/\@RECEIPTSTYLE\@/$query{receiptstyle} ? $query{receiptstyle} 
                                                  : $CFG{RECEIPTSTYLE}/eg;
    $tmpl = expand_tmpl($tmpl);
    print "Content-type: text/html\n\n$tmpl";
}

## Default macro expansions

sub expand_tmpl {
    my $tmpl = shift;

    $tmpl = expand_inc($tmpl);
    $tmpl=~ s/\@DATE\@/scalar localtime/eg;
    $tmpl=~ s/\@USER\@/$ENV{REMOTE_USER}/eg;
    $tmpl=~ s/\@TO\@/$query{to}/g;
    $tmpl=~ s/\@SUBJECT\@/$query{subject}/g;

    $tmpl;
}

sub my_unescape{
    my $str = shift;
    $str =~ s/\+/ /g;
    uri_unescape($str);
}

sub handleMultiselect{
    my ($values,$key);
    foreach $key (keys %query) {
    next
	unless ref $query{$key} eq "ARRAY";
    $values = "";
    for ( @{$query{$key}}) { $values .= "$_,";  };
    chop($values);
    $query{$key} = $values;

    }
}
__END__

=head1 NAME

 mailto.cgi - Customizable mail handler for HTML forms

=head1 VERSION

 $Revision: 1.5 $, $Date: 1998/08/05 12:28:59 $

=head1 SYNOPSIS

 <form metod="POST" action=".../cgi-bin/mailto.cgi">
 <input type="hidden" name="to" value="webmaster@yoursite.com">
 <input type="hidden" name="subject" value="Feedback">
 <input type="hidden" ....>
 Your form data goes here
 <input type="submit">
 </form>

=head1 DESCRIPTION

mailto.cgi is a Perl CGI script which can be used as action for any
HTML form in situations where you want the form data to be sent by
email to someone. The script accepts a lot of server-side and client-side
configuration options, which makes it a very flexible form backend.

You can use it with both the POST and GET methods. For HTML forms, you
will probably want to use the POST method though.

=head1 CLIENT-SIDE VERSUS SERVER-SIDE OPTIONS

The idea is to let the client have maximum control over layout and
interaction, without opening serious security breaches. The script will
run UNIX sendmail to send the mail, and if not carefully configured, it I<is>
possible to use the script to send anonymous mails over the Internet.

The client-side options let the user supply HTML templates and CSS
stylesheets used for receipts and error messages, whereas the server-side
settings control security aspects of using the script.

=head2 CLIENT-SIDE OPTIONS

You transmit your client-side settings to the script along with other 
form data. There may be situations where you allow the user to select
and set the options in the form, but in most cases you will probably
set the options in the containing HTML file using HTML hidden input fields
with proper B<name> and B<value> pairs. Here is the list of magic name
values (note that names are case sensitive):

=over 4

=item * to - mail recipient(s) [required]

 Any legal RFC822 address. Example

 <input type="hidden" name="to" 
       value="steinar@intervett.no,sales@site.com">

=item * subject - mail subject [required]

 Text which will be used to compose the subject field.

=item * cc - mail cc recipient(s) [optional]

 Any legal RFC822 address. 

=item * bcc - mail bcc recipient(s) [optional]

 Any legal RFC822 address. 

=item * replyto - Replyto address [optional]

 Any legal RFC822 address. The mail will be sent using the uid of
the user running the CGI script, which is the uid of the user running
the httpd process. By supplying a replyto address, any conforming
mail client should offer the user the option to use this address
when sending replies.

=item * errorstyle - URL to CSS stylesheet used in error messages 

 Error messages are formatted according to an HTML template specified
in the server-side config file. However, using CSS, the user can insert
a style-sheet in this template by transmitting the URL to the stylesheet
in this option. See below for CSS class names used by the default 
error-template.

=item * receiptstyle - URL to CSS stylesheet used in receipt

 In the same way, the user can exercise fine control over the layout
and formatting of the standard receipt. See below for CSS class names
used by the default receipt-template.

=item * errortemplate - URL to alternative error-template

 If you don't like the format of the default error-template (even if you
modify it with your own style-sheet), you can supply an alternate 
HTML template using this option. See below for macro names you can
use to have things inserted in the template.

=item * receipttemplate - URL to alternative receipt-template

 In the samme as for error messages, you can supply your own
HTML template used for the receipt. See below for macro names.

=item * mailtemplate - URL to alternative mail template

 This template will override the default server template used
when composing mail. This can be an HTML template, causing the
mail to be sent as inline HTML in the mail body. However, as the
script will be able to do better formatting with HTML, you should
also set the option 'mailashtml' if the mail template is an
HTML file. 

=item * mailashtml - Send HTML mail

 See above. Set it to anything different from NIL if you want to send
HTML mail. If not set, the form data will be formatted as plain text
when inserted into the current mail template.

=item * requiredfields - Comma separated list with user fields

 Using this option, you can tell the script which user fields are 
required before accepting the form and sending the mail. Example:

 <input type="hidden" name="requiredfields" 
       value="name,address,email">

The script will format an error message and send to the browser if
any of the required fields are left blank or not set in the form at all.

=item * receipturl - Receipt handled by this URL

 If form data is accepted and the mail sent, the script will format a
receipt and output to the browser. However, you can override this by
supplying a URL to something which should handle the receipt. This
can be a script or a static page according to what you want. If this
option is used, the script will use the HTTP Location header to
do the redirection of the receipt.

A nice feature is that you can have all the form data sent to this
alternate receipt script as well. To do that, you must specify a
"magic" query string in the URL, like this:

 <input type="hidden" name="receipturl" 
       value="myreceipt.cgi?@QUERY@">

The script will then receive the whole form in the query-string as
name/value pairs, properly URL-encoded.

=item * printfpadding - A number > 0 

 When sending plain-text mail, the script will right-align the name
of each field in the HTML form, using this number as the minimum
length.

=back

=head2 SERVER-SIDE CONFIGURATION

The only way to supply server-side configuration data, is to modify
the default configuration file or modify the script to use another
one. The format of the configuration file is lines looking like this

 name=value

Lines beginning with '#' or white-space are ignored. Recognized 
configuration settings are:

=over 4

=item * ERRORTEMPLATE=filename

 Default error template

=item * MAILTEMPLATE=filename

 Default template used when composing mail. 

=item * RECEIPTTEMPLATE=filename

 Default template used in receipt. 

=item * ERRORSTYLE=url

 URL to default CSS style-sheet to be inserted in error template

=item * RECEIPTSTYLE=url

 URL to default CSS style-sheet to be inserted in receipt template

=item * SENDMAIL=path to UNIX sendmail

 The script will open a pipe to sendmail to send the mail. The right
hand side should contain full path to the sendmail program, possibly
with proper options depending on your system.

=item * REQUIREDFIELDS=comma separated list of field names

 Should possibly be "to,subject". Note that the client-side option
'requiredfields' add fields to this list, it will not override the
server-side setting.

=item * ALLOWEDCLIENTS=comma separated list of host name endings

 Use IP adresses or DNS domain names or both to specify client
host name addresses allowed to connect to the script. Note that
subtext matching will be used. Example:

 ALLOWEDCLIENTS=intervett.no,.com

This accepts connections from all hosts within the intervett.no 
domain as well as all .com hosts.

Note that this functionality relies solely of the information
available in the REMOTE_ADDR and REMOTE_HOST CGI variables. If you
connect to the script through a firewall, the script will read
the address of the firewall, not the address of the originating
HTTP client.

=item * ALLOWEDREFERERS=comma separated list of allowed referers

 If you want to make sure that only HTML forms at certain places
are allowed to use the script as action-handler, the script can use
the HTTP_REFERER CGI variable as matching against this list. 
Matching is done subtext wise from left to right. Example:

 ALLOWEDREFERERS=http://www.intervett.no/prod,http://www.infostream

All files residing within the 'prod' hierarchy at www.intervett.no
are allowed to use the script. Also, any file at any webserver
with address www.infostream.* are allowed to use the script.

=item * DEFAULTFROM=RFC822 address

 Use this to set the From: header in the outgoing mail.

=item * DEFAULTREPLYTO=RFC822 address

 Use this to set the Reply-to: header in the outgoing mail.

=back

=head2 MACRO EXPANSIONS

 All HTML and text templates can contain some common magic macro names
which will be expanded upon execution. In addition, some templates have 
their own macro names only applicable for that context.

=head3 Common macros

=over 8

=item * @DATE@

 Current date and time

=item * @USER@

 Name of remote user if Basic Authentication is used

=item * @TO@

  To: address in mail

=item * @SUBJECT@

 Mail subject

=back

=head3 Context specific macros

=over 8

=item * @ERRORSTYLE@ [error template]

 URL to stylesheet used for errors will be substitued, either set
in server configuration file or specified by the user using HTML
hidden fields (see explanation earlier).

=item * @MESSAGE@ [error-template]

 Error message will be substituted.

=item * @RECEIPTSTYLE@ [receipt-template]

 URL to stylesheet used for receipts will be substitued.

=item * @FORMDATA@ [mail-template and receipt-template]

 Name/value pairs will be formatted in a table-like manner

=back

=head1 REQUIREMENTS

Needs CGI::Query and URI::Escape, both usually part of any 
Perl distribution with WWW modules included.

=head1 AUTHOR

Steinar Kjærnsrød E<lt>steinar@intervett.no>

=head1 COPYRIGHT

© InfoStream AS, 1998

=cut
