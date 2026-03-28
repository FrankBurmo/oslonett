#!/local/bin/perl

umask 002;

$kat_file="/home/frogner/www/NYOMP/nl/fi/boers2/oversikt.txt";


open(STDERR, "/dev/null");

open(FIL,"<$kat_file") || die "Not able to open $kat_file\n";


dbmopen(%KAT,"kategori",0664) || print "Content-type: text/html\n\nFoo";

	   
while (<FIL>) {
	$kat = $_;
	chop ($kat);
	$tmp = "";

	$_ = <FIL>;
	until (/\+/) {
	    chop ($_);
	    $tmp = $tmp."+".$_;
	    $_ = <FIL>;
	}

	$KAT{$kat} = $tmp;
#	print "$kat = $tmp\n";
    }
    

dbmclose(%KAT);

close FIL;
	
