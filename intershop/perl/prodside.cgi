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

$path=$ENV{'PWD'};
$index_root="/local/www/sh/is/";
$this_program_name="genpage.cgi";
$kat_file=join("",$index_root,"katalog/produktbase.txt");
$header_dir="header/";
$footer_dir="footer/";
$funnet=0;

$indeksnr = $ARGV[0];


open(STDERR, "/dev/null");

open(PROD, "<$kat_file") || die "can't open input file $PRODFILE\n";

print "Content-type: text/html\n\n";

while (<PROD>)
    {
	if (/^$indeksnr/) {
	    $funnet=1;
	    ($nr,$navn,$pris,$bilde)=split(/\#/o);

	    print "
<html>
<head>
<title>Produktsside: $navn</title>
</head>
<body bgcolor=\"\#ffffbb\" link=\"\#ff2000\" vlink=\"\#ff2000\">
<hr size=\"1\" noshade>
<table border=\"0\" width=100% align=\"right\">
<tr>
<td valign=\"top\" align=\"left\">
<a href=\"index.html\"><img src=\"gifs/rsi.gif\" border=\"0\"></a>
</td>
<td>
<br>
<a href=\"info.html\"><img src=\"gifs/inf.gif\" border=\"0\"></a><a href=\"oversikt.html\"><img src=\"gifs/oversikt.gif\" border=\"0\"></a><a href=\"soek.html\"><img src=\"gifs/soek.gif\" border=\"0\"></a><a href=\"nyheter.html\"><img src=\"gifs/nyheter.gif\" border=\"0\"></a>
</td>
</tr>
</table>
";

	    if ($bilde eq " ") {
		print "<img src=\"prodgifs/$bilde.gif\" align=left alt=\"\">";
	    }

	    print "
<h1>$navn</h1>
$beskriv
<h2>Pris:</h2>
$pris <p>
<a href=\"\">legg i kurven<\/a>
    
<p>
<table border=\"0\" width=\"100%\">
<tr>
<td align=\"left\">
<a href=\"\"><img src=\"gifs/big_button.gif\" border=\"0\"></a>
</td>
</tr>
</table><p>
<address>
<font size=\"-1\">
Oslonett AS</address>

</body></html>

";

}
}

if ($funnet=0) {
    print "fant ikke";
}

close(PROD);
