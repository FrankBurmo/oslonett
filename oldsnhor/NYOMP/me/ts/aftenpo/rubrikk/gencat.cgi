#!/local/bin/perl


# gencat.cgi
#
# Dag Wigum, 16.11.95
#
# Genererer en htmlfil med annonsene for en kategori
# oppdatert 26.1.96
#

$kat_file="resultatdb.txt";


# Neste linje virker kun for method="GET". Bør gi feilmelding hvis dette
# ikke er tilfelle eller bruke read(STDIN, $kat, $ENV{'CONTENT_LENGTH'}
# hvis method="POST".

$kat = $ENV{'QUERY_STRING'};


$date = "DATE";


open(STDERR, "/dev/null");

open(FIL,"<$kat_file") || die "Not able to open $kat_file\n";

dbmopen(%KEYINDEX,"key",0664) || print "Content-type: text/html\n\nFoo";

dbmopen(%MAININDEX,"oppslag",0664) || print "Content-type: text/html\n\nFoo";

%NAMEINDEX = ("BIL1","BIL (A-I)","BIL2","BIL (J-N)","BIL3","BIL (O-Å)","BIL4","BIL DIVERSE","BAAT","BÅT-FLY","BYMSE","MOTOR FORSKJELLIG","EBOLIG","BOLIGEIENDOM","EFRITID","FRITIDSEIENDOM","ELEIE","LEIEMARKEDET","EFORS","EIENDOM FORSKJELLIG","ENAERING","NÆRINGSEIENDOM","HUS","HUS-HJEM-HOBBY","REISER","REISER","HELSE","HELSE","UNDERHOLDNING","UNDERHOLDNING","UNDERVISNING","UNDERVISNING","SPORT","SPORT","PERSON","PERSONLIG","KUNN","KUNNGJØRING","BYGG","BYGG-ANLEGG","REKLAME","REKLAME-MARKEDSFØRING","DATA","DATA-TELE-KONTOR","FORSIKRING","FORSIKRING-ØKONOMI","FORR","FORR.-DRIFT-UTSTYR","TRANSPORT","TRANSPORT","STILLING","STILLING");


# Lag title-tag...

$title = "Aftenposten - Annonser";

# Lag body-tag...
$body_tag = "<body BGCOLOR=\"#ffffee\" TEXT=\"#000000\"
           LINK=\"#0000ff\" VLINK=\"#aa0000\" ALINK=\"#aa0000\">";


&header;
&katalog;
&footer;

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

<center>
<!------------------- Standard header -------------------------->     
<A HREF=\"../banner/rubr_u.map\">
<IMG WIDTH=454 HEIGHT=65 ALT=\"Aftenposten - Annonser\" 
SRC=\"../banner/rubr_u.gif\" ISMAP border=0></A><BR><BR>

	    <h3>$NAMEINDEX{$kat} - $MAININDEX{$date}</h3>
</center>


";

    return;
}

sub katalog{


    while (defined($KEYINDEX{$i.$kat})) {
	@TMP = split(/,/,$KEYINDEX{$i.$kat});

	foreach $_ (@TMP) {
	    $tmp = $MAININDEX{$_};
	    @FELT = split(/<br>/,$tmp);
	    $funnet="ja";
	    @A = split(/\#/,shift(@FELT));
	    
	    @B=split(/=/,$A[1]);
	    
	    $FUNNET[$teller] = "<b>$B[1]</b><br>";
	    foreach $b (@FELT) {
		$FUNNET[$teller] = $FUNNET[$teller].$b;
	    }
	    $teller++;
	}

	$i++;


	@FUNNET = sort(@FUNNET);

	foreach $_ (@FUNNET) {
	    print "<hr><blockquote><blockquote>\n";
	    print $_;
	    print "</blockquote></blockquote>\n";
	}

    }
    return;
}


sub footer {

    print "
<!---- KNAPPERAD + tekstversjon-------->
<center>

<font size=\"-1\">
<a href=\"../hjemme/innhold.htm\">[Innhold]</a> <a 
href=\"../info/hjelp/index.htm\">[Info]</a> <a href=\"../index.htm\">[Aftenposten 
hjemmeside]</a> <a href=\"index.htm\">[Annonser hovedside]</a>
</center>
</font>

</body>
</html>

";

    return;
}



dbmclose(%MAININDEX);
dbmclose(%KEYINDEX);
close FIL;


	
