#!/local/bin/perl


# update.pl
#
# Dag Wigum, 30.12.95
#
# Legger inn riktig topp og bunn i delphis sider
#

$filnavn=$ARGV[0];
$tmpfil="tmpfil.dta";
$top="top.html";
$header="header.html";
$meny="meny.html";
$footer="footer.html";


open(STDERR, "/dev/null");

open(FIL,"<$filnavn") || die "can't open input file $filnavn\n";
open(TOP,"<$top") || die "can't open input file $top\n";
open(HEADER,"<$header") || die "can't open input file $head\n";
open(MENY,"<$meny") || die "can't open input file $meny\n";
open(FOOTER,"<$footer") || die "can't open input file $footer\n";
open(TMP,">$tmpfil") || die "can't open input file $tmpfil\n";



@body=<FIL>;
@top=<TOP>;
@header=<HEADER>;
@meny=<MENY>;
@footer=<FOOTER>;

#print @body;

foreach $i (@body) {
    if ($i=~/top\.htm/) {
	print TMP @top;
    }
    elsif ($i=~/header\.htm/) {
	print TMP @header;
    }
    elsif ($i=~/meny\.htm/) {
	print TMP @meny;
    }
    elsif ($i=~/footer\.htm/) {
	print TMP @footer;
    }
    else {
	print TMP $i;
    }
}

system("cp $filnavn original/.;mv $tmpfil $filnavn;chmod 755 $filnavn");



close FIL,TOP,HEADER,MENY,FOOTER;
close TMP;

	
