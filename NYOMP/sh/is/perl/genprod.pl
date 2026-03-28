#!/usr/local/bin/perl
#genprod.pl: Generer html-sider fra en produktdatabase og en avdelingsdatabase
#
#
#Scriptet skal lage enten - en avdelingsside
#                   eller - en produktside
#
#
#Kallet kommer fra en navigeringsknapp, og angir hva vi skal lage side om
#
#Avdelingsside
#Vi skal generere en avdelingsside  med riktig header, produktliste 
#og footer. Vi får informasjon om dette fra avdelingsbasen
#
#Header angir hvor vi er, og har også navigeringsikoner til andre 
#avdelingssider. Vi får produktene fra produktbasen.
#
#Produktliste er greit.
#
#Footer er standard på alle.
#
#
#Produktside
#Vi skal generere en produktside med: Produktnavn, bilde, beskrivende tekst 
#og navigeringsknapper til hovedside og forrige side. Nederst har vi standard 
#footer.


$PRODFILE = "/home/frogner/www/NYOMP/sh/is/katalog/produktbase.txt";


open(STDERR, "/dev/null");


open(PROD, "<$PROD") || die "can't open input file $PRODFILE\n";

finn indeksnr



	


    while (<PROD>)
    {
	if (/$indeksnr.*/) {
	    ($nr,$varenr,$navn,$bilde,$beskriv,$pris)=split(/#/o);
							    print "<tr><td>$navn</td><td>$pris</td><td>Legg i kurven</td></tr>";
							}
	}
