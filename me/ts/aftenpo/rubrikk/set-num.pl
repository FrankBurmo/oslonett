#!/local/bin/perl


# set-num.pl
#
# Dag Wigum, 19.1.96
#
# Skriver inn antall for hver annonsekategori
#

$tmp_file = "tmp.html";

dbmopen(%ANTALLINDEX,"antall",0664) || print "Content-type: text/html\n\nFoo";

for ($i=1; $i<=4; $i++) {
    
    $annonse_file = "a$i.htm";

    open(AFIL,"<$annonse_file") || die "Not able to open $annonse_file\n";
    open(TMP,">$tmp_file") || die "Not able to open $tmp_file\n";

    while (<AFIL>) {

	print TMP;

	if (/cat=/) {
	    @LINJE=split(/\#/);
	    @CAT=split(/=/,$LINJE[1]);
	    $tall=$ANTALLINDEX{$CAT[1]}-1;
	    if ($tall<0) {
		$tall = 0;
	    }

	    print TMP "<td align=center><a href=\"gencat.cgi?$CAT[1]\">$LINJE[2]</a><br>[Antall: $tall]</td>\n";
	    $_ = <AFIL>;
	}     
    }

    close AFIL, TMP;

    system("mv $tmp_file $annonse_file");
    system("chmod 775 $annonse_file");

}


dbmclose(%ANTALLINDEX);



	
