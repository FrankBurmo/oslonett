#!/local/bin/perl -- -*-perl-*-


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

print "Content-type: text/html\n\n";
print "<Head><Title>Bestilling av CD'er fra Akers Mic</Title></Head>";
print "<Body BACKGROUND=\"/div/DEMO/bg2.gif\" rgb=\"#ff00ff\" TEXT=\"#FFFF00\" LINK=\"#00FF7F\" VLINK=\"#38B0DE\" ALINK=\"#0077FF\">\n";
print "<center><IMG SRC=/div/DEMO/topp20.gif></center>\n";
print "<center><H1>Bestilling av CD'er fra Akers Mic</H1></center>";

#XXX: Presenter bestilte CDer

if($ENV{'HTTP_COOKIE'} =~ /id=/)
{
    # trekk ut $id og $pin fra cookie
    foreach $pair (split(/\s*;\s*/, $ENV{'HTTP_COOKIE'})) {
	($key,$val) = split(/=/, $pair, 2);
	$id  = $val if $key eq "id";
	$pin = $val if $key eq "pin";
    }

    print <<"EOT";

<pre>
<FORM method="POST"  ACTION="https://www2.oslonett.no/div/DEMO/bestilling.cgi">
Kundenr: <INPUT TYPE=text NAME=id MAXLENGTH=65 SIZE=5 value=$id>
Pinkode: <INPUT TYPE=password NAME=pin MAXLENGTH=65 SIZE=5 value=$pin>
</pre>

EOT

} else {

    print "Du er nå inne i selve bestillingsskjemaet. Siden du ikke har vært elektronisk kunde hos oss før, må du taste inn navn, adresse, emailadresse og Visakortnummer, så vil du få CD'ene tilsendt i posten.<p>\n\n";
    print "<FORM method=\"POST\"  ACTION=\"https://www2.oslonett.no/div/DEMO/foerstebestilling.cgi\">\n";
    print "<pre>\n";
    print "Kundenavn     : <INPUT TYPE=text NAME=navn MAXLENGTH=65 SIZE=65>\n";
    print "Adresse       : <INPUT TYPE=TEXT NAME=adresse MAXLENGTH=65 SIZE=65>\n";
    print "Postnummer    : <INPUT TYPE=TEXT NAME=postnummer MAXLENGTH=5 SIZE=5> Poststed : <INPUT TYPE=text NAME=poststed MAXLENGTH=30 SIZE=30>\n";

    print "Email         : <INPUT TYPE=TEXT NAME=email MAXLENGTH=50 SIZE=50>\n";
    print "Visakortnummer: <INPUT TYPE=TEXT NAME=visakortnummer MAXLENGTH=50 SIZE=50>\n"; 
    print "</pre>\n";
}

print "<INPUT TYPE=\"hidden\" NAME=\"cd1\" VALUE=\"$FORM{'cd1'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd2\" VALUE=\"$FORM{'cd2'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd3\" VALUE=\"$FORM{'cd3'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd4\" VALUE=\"$FORM{'cd4'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd5\" VALUE=\"$FORM{'cd5'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd6\" VALUE=\"$FORM{'cd6'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd7\" VALUE=\"$FORM{'cd7'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd8\" VALUE=\"$FORM{'cd8'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd9\" VALUE=\"$FORM{'cd9'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd10\" VALUE=\"$FORM{'cd10'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd11\" VALUE=\"$FORM{'cd11'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd12\" VALUE=\"$FORM{'cd12'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd13\" VALUE=\"$FORM{'cd13'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd14\" VALUE=\"$FORM{'cd14'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd15\" VALUE=\"$FORM{'cd15'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd16\" VALUE=\"$FORM{'cd16'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd17\" VALUE=\"$FORM{'cd17'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd18\" VALUE=\"$FORM{'cd18'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd19\" VALUE=\"$FORM{'cd19'}\">\n";
print "<INPUT TYPE=\"hidden\" NAME=\"cd20\" VALUE=\"$FORM{'cd20'}\">\n";

print "<p>\n<hr>\nVi har registrert en bestilling på følgende CD'er:<br>\n<dl>\n";
if($FORM{'cd1'}){print "<dt> Jackson, Michael \n<dd>History - Past, Present And \n";}
if($FORM{'cd2'}){print "<dt> Bjørk\n<dd>Post\n";} 
if($FORM{'cd3'}){print "<dt> Morrison, Van\n<dd> Days Like This\n";}
if($FORM{'cd4'}){print "<dt> Pink Floyd\n<dd> P.U.L.S.E. - Live \n";}
if($FORM{'cd5'}){print "<dt> Hofseth, Bendik \n<dd> Metamorphoses\n";}
if($FORM{'cd6'}){print "<dt> Deep Forest \n<dd> Boheme\n";}
if($FORM{'cd7'}){print "<dt> Secret Garden\n<dd> Songs From A Secret Garden \n";}
if($FORM{'cd8'}){print "<dt> Creedence Clearwater Revival\n<dd> 36 Greatest Hits\n";}
if($FORM{'cd9'}){print "<dt> Bon Jovi\n<dd> These Days\n";}
if($FORM{'cd10'}){print "<dt> Kaspers Orkester, Bo\n<dd> På Hotell\n";}
if($FORM{'cd11'}){print "<dt> King, Diana\n<dd> Tougher Than Love\n";}
if($FORM{'cd12'}){print "<dt> Connells, The \n<dd> Ring \n";}
if($FORM{'cd13'}){print "<dt> Stewart, Rod \n<dd> A Spanner In The Works \n";}
if($FORM{'cd14'}){print "<dt> Dylan, Bob\n<dd> MTV Unplugged \n";}
if($FORM{'cd15'}){print "<dt> John, Elton\n<dd> Made In England \n";}
if($FORM{'cd16'}){print "<dt> Marsalis, Wynton & Ellis Marsalis \n<dd> Joe Cool`s Blues\n";}
if($FORM{'cd17'}){print "<dt> Lennox, Annie\n<dd> Medusa \n";}
if($FORM{'cd18'}){print "<dt> Hancock, Herbie\n<dd> Dis Is Da Drum \n";}
if($FORM{'cd19'}){print "<dt> DIVERSE ARTISTER \n<dd> Definitive Summerhits 3 \n";}
if($FORM{'cd20'}){print "<dt> DANCE / SOUL\n<dd> Freezone 2: Variations On A \n";}
print "</dl><hr>\n\n";

print "\n<input type=submit value=\"Bekreft bestilling\">\n";

#print  "<p>Remote host: $ENV{'REMOTE_HOST'}<p>\n";
#print  "Remote IP address: $ENV{'REMOTE_ADDR'}<p>\n";
print "</FORM>\n";
print "</body>\n";
print "</html>\n"
