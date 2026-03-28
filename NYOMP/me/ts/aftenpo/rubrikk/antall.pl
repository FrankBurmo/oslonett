#!/local/bin/perl


# antall.pl
#
# Dag Wigum, 19.1.96
#
# Skriver ut antall for hver annonsekategori
#


dbmopen(%ANTALLINDEX,"antall",0664) || print "Content-type: text/html\n\nFoo";

foreach $_ (%ANTALLINDEX) {
    print "$_ = $ANTALLINDEX{$_}\n";
    $total = $total + $ANTALLINDEX{$_};
}

print " total = $total\n";

dbmclose(%ANTALLINDEX);



	
