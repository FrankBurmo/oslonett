#!/local/bin/perl


# oversikt.cgi
#
# Dag Wigum, 15.11.95
# - og endel modifikasjoner av Kent Vilhelmsen 28.11.1995 og 18.12.1995
# Leser igjennom avdelingsbasen, og lager en innholdsfortegnelse.
#
# NEW! Hver linje i avdelingsbasen må avsluttes med dobbelt-dollar, $$!!!


# Finn path, hvor html-treet starter, katalogfil og kategorinr. 

$path=$ENV{'PWD'};
$index_root="/local/www/sh/is/";

$URL_PATH	= "/sh/is";

$this_program_name=$ENV{'SCRIPT_NAME'};
$kat_file=join("",$index_root,"katalog/avdelingsbase.txt");
$prod_file=join("",$index_root,"katalog/produktbase.txt");
$header_dir="header/";
$footer_dir="footer/";

# open(STDERR, "/dev/null");

# Les inn katalogfil
open(FIL,"<$kat_file") || die "Not able to open $kat_file\n";
open(PROD_FILE,"<$prod_file") || die "Not able to open $prod_file\n";
 
@TMP_KAT = <FIL>;
@KATALOG = {};
$count=0;
# Les gjennom kategori/avdelingsfilen for å sjekke om noen linjer må slås sammen
foreach (@TMP_KAT) {
    next if /^\s*$/;
    # Alle linjer skal slutte med $$. Hvis ikke, slå sammen denne og (de) neste
    # linje(r), til vi får avsluttet med $$.
    if (!/.*\$\$$/) {		
	$in=$in.$_;
	next;
    }	
    s/\$\$//;
    $in=$in.$_;
    $KATALOG[$count++] = $in;
    $in = "";			   
}




# Lag title-tag...
$title = ("Oversikt");

# Lag body-tag...
$body_tag = "<body bgcolor=\"#ffffbb\" link=\"#ff2000\" vlink=\"#ff2000\" >";

&header;
&table;
&footer;


##
## Genererer header utifra kategoriparameter...
##

sub header {

    print "Content-type: text/html\n\n";
    print "
<html>
<head>
<title>
$title
</title>
</head>

$body_tag

<hr size=\"1\" noshade>
<table border=\"0\" width=\"100%\">
<tr>
<td valign=\"top\" align=\"left\">
<a href=\"$URL_PATH/index.html\"><img src=\"$URL_PATH/gifs/rsi.gif\" border=\"0\"></a>
</td>

<td valign=\"bottom\" align=\"right\">\n";

    print "
<br>
<a href=\"$URL_PATH/oversikt.cgi\"><img src=\"$URL_PATH/gifs/oversikt.gif\" border=\"0\"></a><a href=\"$URL_PATH/soek.html\"><img src=\"$URL_PATH/gifs/soek.gif\" border=\"0\"></a><a href=\"$URL_PATH/nyheter.html\"><img src=\"$URL_PATH/gifs/nyheter.gif\" border=\"0\"></a>
</td>
</tr>
</table>

<hr size=2 noshade>


";


    return;
}

#
#Genererer listen av produktkategorier
#
sub table {

    print "<ul>";
foreach $_ (@KATALOG) {
    @TMP = split(/\#/);
    if (/^(\d)\#/) {
	print "</ul><a href=\"genpage.cgi?$TMP[0].1.1\">$TMP[1]</a><ul>";
	$hkat=$TMP[0];
    }
    if (/^($hkat).(\d+)\#/) {
	print "<li><a href=\"genpage.cgi?$TMP[0].1\">$TMP[1]</a><br>";
	$ukat=$TMP[0]
    }
    if (/^($ukat).(\d+)\#/) {
	print "<blockquote><a href=\"genpage.cgi?$TMP[0]\">$TMP[1]</a></blockquote>";
    }
}

print"</ul>";


    return;
}



#
# Genererer footeren til produktsiden, gitt kategoriparameter
#

sub footer {

    print "
<br><br>
<p>
<table border=\"0\" width=\"100%\">
<tr>
<td align=\"left\">
<a href=\"menu.map\"><img src=\"$URL_PATH/gifs/big_button.gif\" border=\"0\" ismap></a>
</td>
</tr>
</table><p>
<address>
<font size=\"-1\">
Schibsted Nett AS</address>

</body>
</html>

";

    return;
}






exit(0);



