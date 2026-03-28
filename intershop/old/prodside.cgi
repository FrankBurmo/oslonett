#!/usr/local/bin/perl
#prodside.pl: Generer html-sider fra en produktdatabase
#
#
#Scriptet skal lage en produktside
#
#
#Kallet kommer fra et produkt i en produktlist
#
#
#Produktside
#Vi skal generere en produktside med: Produktnavn, bilde, beskrivende tekst 
#og navigeringsknapper til hovedside og forrige side. Nederst har vi standard 
#footer.

$KURV_HENT	= "/kurv/hent.cgi";
$KURV_DIR	= "/local/www/kurv/kunder";
$KURV_INNHOLD	= "/local/www/kurv/innhold.pl";

$NOCHECKGIF	= "/sh/is/gifs/kurv.gif";
$CHECKGIF	= "/sh/is/gifs/fullkurv.gif";
$NOCHECKTXT	= "Legg varen i kurven";
$CHECKTXT       = "Varen er i kurven";
$BUTIKK_ID	= "intershop";
$URL_PATH	= "/sh/is";

#foreach ( split(/\n/, `$KURV_INNHOLD $id` ) ) {
#    $ikurv{ $_ } = 1 if s!/intershop/!!;
#}
$gifimg = $ikurv{$nr} ? $CHECKGIF : $NOCHECKGIF;
$kurvetxt = $ikurv{$nr} ? $CHECKTXT : $NOCHECKTXT;

$path=$ENV{'PWD'};
$index_root="/local/www/sh/is/";

$kat_file=join("",$index_root,"katalog/produktbase.txt");
$header_dir="header/";
$footer_dir="footer/";
$funnet=0;

$indeksnr = $ARGV[0];

# Finn ut hvilken side som kalte oss opp
$callerpage = $1 if $indeksnr =~ /(.+)\..+$/;

# open(STDERR, "/dev/null");

open(PROD_FIL, "<$kat_file") || die "can't open input file $kat_file\n";

# Les inn alle produktene i en array og sørg for å fjerne dobbel-dollar bak hver av dem
# (dette kan avgjort gjøres mer effektivt :)
@TMP_AVD = <PROD_FIL>;
@PROD = (); 
$count=0;
foreach (@TMP_AVD) {
    next if /^\s*$/;
    # Alle linjer skal slutte med $$. Hvis ikke, slå sammen denne og (de) neste
    # linje(r), til vi får avsluttet med $$.
    if (!/.*\$\$$/) {		
	$in=$in.$_;
	next;
    }	
    s/\$\$//;
    $in=$in.$_;
    $PROD[$count++] = $in;
    $in = "";			   
}

print "Content-type: text/html\n\n";

foreach (@PROD)
    {
	if (/^$indeksnr\#/) {
	    $funnet=1;
	    ($pnr,$navn,$pris,$tekst,$bilde)=split(/\#/o);
	    # Endring 27.12.95 - kent vilhelmsen -
	    # Jeg har innført pnr som er _hele_ produktnummeret...
	    @NR=split(/\./o,$pnr);
	    $nr=pop(@NR);
	    # $nr = $pnr;

	    # Trenger å kunne dekode handlekurv-id hvis man skal vise 
	    # i kurv/ikke i kurv
	    $id = $1 if $ENV{HTTP_COOKIE} =~ /kurvid=(\d+)/;

	    foreach ( split(/\n/, `$KURV_INNHOLD $id` ) ) {
		$ikurv{ $_ } = 1 if s!/intershop/!!;
	    }

	    $gifimg = $ikurv{$pnr} ? $CHECKGIF : $NOCHECKGIF;
	    $kurvetxt = $ikurv{$pnr} ? $CHECKTXT : $NOCHECKTXT;

	    print "
<html>
<head>
<title>Produktsside: $navn ($nr/$id)</title>
</head>
<body bgcolor=\"\#ffffbb\" link=\"\#ff2000\" vlink=\"\#ff2000\">
<hr size=\"1\" noshade>
<table border=\"0\" width=100%>
<tr>
<td valign=\"top\" align=\"left\">
<a href=\"/sh/is/index.html\"><img src=\"/sh/is/gifs/rsi.gif\" border=\"0\" alt=\"InterShop\"><br>[til forsiden]</a>
</td>
<td valign=center>
<h1>Produktside</h1>
</td>
<tr>
<td colspan=2 align=left valign=top>
<hr size=1 noshade>
<br>
<a href=\"/sh/is/oversikt.cgi\"><img src=\"/sh/is/gifs/oversikt.gif\" border=\"0\" alt=\"Oversikt\"></a><a href=\"/sh/is/soek.html\"><img src=\"/sh/is/gifs/soek.gif\" border=\"0\" alt=\"Søk\"></a><a href=\"/sh/is/nyheter.html\"><img src=\"/sh/is/gifs/nyheter.gif\" border=\"0\" alt=\"Nyheter\"></a>
</td>
</tr>
</table>    
<p>
<table border=\"0\">
<tr>
<td align=\"top\">
<h1>$navn</h1>
$beskriv
<h2>Pris: $pris </h2>
Varenr: $nr<p>
$tekst <p>
<a href=\"$KURV_HENT/$BUTIKK_ID/$pnr?ref=$ENV{SCRIPT_NAME}%3F$pnr\"><img src=\"$gifimg\" border=\"0\" alt=\"\"><p>$kurvetxt<\/a>
<p>
<a href=/sh/is/genpage.cgi?$callerpage><img src=\"/sh/is/gifs/home.gif\" border=\"0\"></a>
</td>
";

	    if ($bilde ne "") {
		print "<td valign=\"top\"><img src=\"/sh/is/katalog/images/$bilde\" border=\"0\" alt=\"\"></td>";
	    }

	    print "
</tr>
</table>    
<p>
<table border=\"0\" width=\"100%\">
<tr>
<td align=\"left\">
<a href=\"/sh/is/menu.map\"><img src=\"/sh/is/gifs/big_button.gif\" border=\"0\" ismap></a>
</td>
</tr>
</table><p>
<address>
<hr>
<table border=0 width=100%>
<tr><td align=center>
<a href=\"/\">
 <img alt=\"[SN Horisont]\" src=\"/img/horisont.gif\" border=0></a></td>
<td align=center><a href=\"/sn/\"><img alt=\"[SchibstedNett AS]\" src=\"/img/snikon.gif\" border=0></a></td></tr>
</table>
</adress>

</body></html>

";
	    exit;
	}
    }

if ($funnet=0) {
    print "fant ikke";
}

close(PROD_FIL);
