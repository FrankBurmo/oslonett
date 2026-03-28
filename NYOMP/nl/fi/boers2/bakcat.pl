#!/local/bin/perl

umask 002;

$kat_file="oversikt.txt";


open(STDERR, "/dev/null");

open(FIL,"<$kat_file") || die "Not able to open $kat_file\n";


dbmopen(%KAT,"kategori",0664) || print "Content-type: text/html\n\nFoo";

	   
while (<FIL>) {
    $i='';
	$kat = $_;
	chop ($kat);
	$tmp = "";

	$_ = <FIL>;
	until (/\+/) {
	    chop ($_);
	    $tmp = $tmp."+".$_;
	    $_ = <FIL>;
	}
    while (length($KAT{$i.$kat})>1000) {
            $i++;
        }
	$KAT{$i.$kat} = $tmp;
	print "$i $kat = $tmp\n";
    }
    

dbmclose(%KAT);

close FIL;
	
