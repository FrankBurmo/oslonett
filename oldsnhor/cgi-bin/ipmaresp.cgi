#!/usr/bin/perl

# Terminate headers
print "Content-type: text/html\n\n"; 

# Where is the email program?
$mail_prog = "/usr/lib/sendmail";
$mail_opts = "-t";

# See if the user sent an HTTP_FROM header. Many clients don't these days.
$http_from = $ENV{"HTTP_FROM"}; 

# See which method they used to access this form. If they used POST, then
# read the input from STDIN. If they used GET, use the query string. 

# Which method is used is determined by the HTML in the form.
if($ENV{'REQUEST_METHOD'} eq "GET") {
  $buffer = $ENV{'QUERY_STRING'};
  if($buffer eq "")  {
    print "<TITLE>Feil - bruk HTML</TITLE>\n";
    print "<H1 align=center>Vennligst bruk HTML-skjemaet</H1>\n";
    print "Du har sendt en foresp&oslash;rsel uten &aring; bruke riktig skjema.<br>";
    print "Vennligst bruk service-skjemaet til dette.\n";
    exit(1);
  }
}  else  {
  read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});
} 

# Split pairs by the ampersand which divides variables
@pairs = split(/&/, $buffer);
# Create an array, indexed by the variable name, that contains all the values
foreach $pair (@pairs)
{
# Each variable is structured "name1=value1", so split it on those lines
  ($name, $value) = split(/=/, $pair); 

# Decode the value (+ is a space, and %xx in hex is an encoded character)
  $value =~ tr/+/ /;
  $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
# Create an array indexed by names and put the value in
	if($form{$name} eq "")
	{
		$form{$name} = $value;
	}
	else
	{
		$form{$name} = "$form{$name}, $value";
	}
} 

$mailto = $form{'mailto'};
if($mailto eq "") { $mailto = "ottoh\@oslonett.no" }
$replyto = $form{'replyto'};
if($replyto eq "") { $replyto = "ottoh\@oslonett.no" }
$subject = $form{'subject'};
if($subject eq "") { $subject = "IPMA Admin-distribution response" }
$callform = $form{'callform'};
if($callform eq "") { $subject = "adminlist.html" }

$firstname = $form{'firstname'};
$lastname = $form{'lastname'};
$company = $form{'company'};
$ipmana = $form{'ipmana'};
$address1 = $form{'address1'};
$city = $form{'city'};
$postcode = $form{'postcode'};
$country = $form{'country'};
$tel = $form{'tel'};
$fax = $form{'fax'};
$email = $form{'email'};
$checkbox = $form{'checkbox'};

$sig = $form{'sig'};

$fail = "";

if($firstname eq "") {
    $fail = "first name";
}
elsif($lastname eq "") {
    $fail = "last name";
}
elsif($ipmana eq "") {
    $fail = "IPMA National Association";
}
elsif($email eq "") {
    $fail = "email-address";
}

if($fail) {
    print <<ENDOFTEXT ;
<HEAD>
<TITLE>IPMA: Unable to comply</TITLE>
</HEAD>
<BODY BGCOLOR="#ffffff">
<P><table border=0 width=580 cellpadding=5>
<tr><td>
<A HREF="index.html"><IMG SRC="gfx/rorliten.gif" ALIGN="MIDDLE" WIDTH=100 HEIGHT=98 BORDER="0"></A>
</td><td align=center valign=middle><FONT SIZE="+3">Unable to comply</FONT>
</td></tr>
</table>
<table border=0 width=580 cellpadding=5>
<tr><td>
<HR SIZE="1" WIDTH="580" ALIGN="LEFT">
<P><FONT SIZE="+1">Your request could not be handled, because you have
not filled out <CITE>$fail</CITE>.
</FONT></P>
<strong>The following fields are mandatory:</strong>
<P><strong><ul>
<li>First Name
<li>Last Name
<li>IPMA National Association
<li>E-Mail
</ul></strong></P>
<P><font size=-1><b>Go back to: <a href="$callform">$subject</a></b></font></P>
</td></tr>
<tr><td>
<HR WIDTH=580 ALIGN=left SIZE=1>
<CENTER><FONT SIZE=-1>
<A HREF="../ipma/index.html">IPMA Homepage</a>
 - <A HREF="#top">Top of Page</A>
 - <A HREF="index.html">Frontpage</A>
 - <A HREF="stream1.html">Stream 1</A>
 - <A HREF="stream2.html">Stream 2</A>
 - <A HREF="regform.html">Registration Form</A>
</FONT></CENTER>
<HR WIDTH=580 ALIGN=left SIZE=1>
<a href="http://www.design.idg.no/"><IMG  vspace=5  WIDTH=14 HEIGHT=18 SRC="gfx/id_ikon.gif" alt="Inter\@ktiv Design as" border=0></a>
</td></tr>
</table></P>
</BODY>
</HTML>
ENDOFTEXT
    exit(1);
} 

# Open the mail command, or print an error.
open (MAIL, "|$mail_prog $mail_opts $mailto") || die "Could not open $mail_prog"; 
# Send the feedback. If the user had an HTTP_FROM variable, use that in 
# the from line. If not, use the one he gave in the form.
if($http_from)
  { print MAIL "From: $http_from\n"; }
else
  { print MAIL "From: $email\n"; } 

print MAIL <<ENDOFTEXT ;
Cc: $email
Reply-to: $replyto
Subject: $subject

IPMA response from "$firstname $lastname" <$email>:

------------------------------------------------------------

ENDOFTEXT
print MAIL "Name:				$lastname, $firstname\n";
if($company)	{ print MAIL "Company:			$company\n"; }
print MAIL "IPMA National Association:	$ipmana\n";
if($address1)	{ print MAIL "Address:			$address1\n"; }
if($city)	{ print MAIL "City:				$city\n"; }
if($postcode)	{ print MAIL "Postal Code:			$postcode\n"; }
if($country)	{ print MAIL "Country:			$country\n"; }
if($tel)	{ print MAIL "Telephone:			$tel\n"; }
if($fax)	{ print MAIL "Fax:				$fax\n"; }

if($checkbox)	{ print MAIL "\nValues selected for $subject:\n$checkbox\n"; }

print MAIL "\n------------------------------------------------------------\n";
close (MAIL); 

print <<ENDOFTEXT ;
<HEAD>
<TITLE>IPMA: Thank you for your request</TITLE>
</HEAD>
<BODY BGCOLOR="#ffffff">
<P><table border=0 width=580 cellpadding=5>
<tr><td>
<A HREF="index.html"><IMG SRC="gfx/rorliten.gif" ALIGN=MIDDLE WIDTH=100 HEIGHT=98 BORDER=0></A>
</td><td align=center valign=middle><FONT SIZE="+3">Thank you for your request</FONT>
</td></tr>
</table>
<table border=0 width=580 cellpadding=5>
<tr><td>
<HR SIZE="1" WIDTH="580" ALIGN="LEFT">
<P><FONT SIZE="+1">Thank you for your request, $firstname $lastname.</P>
<P>We have registered your input wich has been mailed
you as confirmation of receipt.</FONT></P>
</td></tr>
<tr><td>
<HR WIDTH=580 ALIGN=left SIZE=1>
<CENTER><FONT SIZE=-1>
<A HREF="../ipma/index.html">IPMA Homepage</a>
 - <A HREF="#top">Top of Page</A>
 - <A HREF="index.html">Frontpage</A>
 - <A HREF="stream1.html">Stream 1</A>
 - <A HREF="stream2.html">Stream 2</A>
 - <A HREF="regform.html">Registration Form</A>
</FONT></CENTER>
<HR WIDTH=580 ALIGN=left SIZE=1>
<a href="http://www.design.idg.no/"><IMG  vspace=5  WIDTH=14 HEIGHT=18 SRC="gfx/id_ikon.gif" alt="Inter\@ktiv Design as" border=0></a>
</td></tr>
</table></P>
</BODY>
</HTML>
ENDOFTEXT
exit(0);
