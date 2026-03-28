#!/local/bin/perl


# search.cgi
#
# Dag Wigum, 16.11.95
#
# Søker gjennom annonsebasen, og skriver ut resultatet
#

$kat_file="resultatdb.txt";
$teller=0;
$date = "DATE";

# Neste linje virker kun for method="POST". Bør gi feilmelding hvis dette
# ikke er tilfelle eller bruke $kat = $ENV{'QUERY_STRING'};
# hvis method="GET".

read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});

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

$top=$FORM{"ord"};

$FORM{"ord"} =~ s/\*/.*/g;
$FORM{"ord"} =~ s/\?/.?/g;
$FORM{"ord"} =~ s/\s+\bELLER\b\s+/\\b|\\b/ig;
$FORM{"ord"} =~ s/\bog\b/OG/;
$FORM{"ord"} =~ s/[øØ]/[øØ]/g;
$FORM{"ord"} =~ s/[æÆ]/[æÆ]/g;
$FORM{"ord"} =~ s/[åÅ]/[åÅ]/g;
$FORM{"ord"} =~ s/^\s+//;
$FORM{"ord"} =~ s/\s+$//;


%NAMEINDEX = ("BIL1","BIL (A-I)","BIL2","BIL (J-N)","BIL3","BIL (O-Å)","BIL4","BIL DIVERSE","BAAT","BÅT-FLY","BYMSE","MOTOR FORSKJELLIG","EBOLIG","BOLIGEIENDOM","EFRITID","FRITIDSEIENDOM","ELEIE","LEIEMARKEDET","EFORS","EIENDOM FORSKJELLIG","ENAERING","NÆRINGSEIENDOM","HUS","HUS-HJEM-HOBBY","REISER","REISER","HELSE","HELSE","UNDERHOLDNING","UNDERHOLDNING","UNDERVISNING","UNDERVISNING","SPORT","SPORT","PERSON","PERSONLIG","KUNN","KUNNGJØRING","BYGG","BYGG-ANLEGG","REKLAME","REKLAME-MARKEDSFØRING","DATA","DATA-TELE-KONTOR","FORSIKRING","FORSIKRING-ØKONOMI","FORR","FORR.-DRIFT-UTSTYR","TRANSPORT","TRANSPORT","STILLING","STILLING");

$sok=$FORM{"ord"};

open(STDERR, "/dev/null");

open(FIL,"<$kat_file") || die "Not able to open $kat_file\n";

dbmopen(%KEYINDEX,"key",0664) || print "Content-type: text/html\n\nFoo";

dbmopen(%MAININDEX,"oppslag",0664) || print "Content-type: text/html\n\nFoo";


# Lag title-tag...

$title = "Aftenposten - Annonser";

# Lag body-tag...
$body_tag = "<body BGCOLOR=\"#ffffee\" TEXT=\"#000000\"
           LINK=\"#0000ff\" VLINK=\"#aa0000\" ALINK=\"#aa0000\">";


&header;

&spesifikk;


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
<h3>Resultat av søk på : $top</h3>

</center>

";

    return;
}

sub spesifikk{

# Endring av KG: søk i "Alle kategorier" virket ikke lenger,
# dette fikser problemet:
    if ($FORM{kategori} eq "ALLE") {
	@TAB = keys %KEYINDEX;
    } else {
	@TAB=split(/,/,$FORM{kategori});
    }

    foreach $t (@TAB) {

	undef($i);


	while (defined($KEYINDEX{$i.$t})) {
	    @TMP = split(/,/,$KEYINDEX{$i.$t});

	    foreach $_ (@TMP) {
		$tmp = $MAININDEX{$_};
		@FELT = split(/<br>/,$tmp);
		@a = split(/\#/,shift(@FELT));
		
		@b=split(/=/,$a[1]);
		@k=split(/=/,$a[0]);
		if ($k[1] = $t) {
		    $string="<center><h3>$NAMEINDEX{$t}</h3><center><br>$b[1]<br>";
		    foreach $l (@FELT) {
			$string=$string.$l;
		    }
		    $found="true";
		    @PAR=split(/\s*\bOG\b\s*/,$sok);
		    foreach $p (@PAR) {
			$found = "false" unless $string =~ /\b$p\b/i;
		    }
		    if ($found eq "true") {
			$funnet="ja";
			$teller++;
			$FUNNET[$teller] = $string;
		    }
		}

		$i++;

	    }
	}
    }
    if ($funnet eq "ja") {
	print "<b>Dato: $MAININDEX{$date}<br>Antall treff = $teller</b><p><hr>\n";

	@FUNNET = sort(@FUNNET);

	foreach $_ (@FUNNET) {
	    print "<blockquote><blockquote>\n";
	    print $_;
	    print "</blockquote></blockquote><hr>\n";
	}
    }
    else {
	print "<center><h3>Ingen treff</h3></center>";
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


	
