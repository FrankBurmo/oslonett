#!/usr/local/bin/perl
#vareinfo.pl: Generer html-sider fra en produktdatabase
#
#
#Scriptet returnerer navn, pris og url på en gitt vare
#
#
#Kallet kommer fra bestillingssystemet
#


$path=$ENV{'PWD'};
$index_root="/local/www/sh/is/";
$this_program_name="vareinfo.cgi";
$kat_file=join("",$index_root,"katalog/produktbase.txt");
$header_dir="header/";
$footer_dir="footer/";
$funnet=0;

$indeksnr = $ARGV[0];


open(STDERR, "/dev/null");

open(PROD, "<$kat_file") || die "can't open input file $PRODFILE\n";

while (<PROD>)
    {
	if (/^$indeksnr\b/) {
	    chop;
	    $funnet=1;
	    ($nr,$navn,$pris)=split(/\#/o);

	    print "Navn : $navn\n";
	    print "Pris : $pris\n";
	    print "URL : /sh/is/prodside.cgi?$nr\n";

	}
    }

if ($funnet==0) {
    print "fant ikke ønsket vare\n";
}

close(PROD);
