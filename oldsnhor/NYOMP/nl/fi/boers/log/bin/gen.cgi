#!/local/bin/perl
#
# Genererer html-filoversikt fra dagens loggfil
#
# Dag Wigum, 6/12-95
#

$filnavn1 = "aksjelogg.dta";

open(STDERR, "/dev/null");

open(IN,"<$filnavn1") || die "Not able to open $filnavn1\n";



dbmopen(%MAININDEX,"aksjer",0664);

While (<IN>) {
    @TMP=split(/\#/);
    
    if (/aksje/,$TMP[0]) {
	@TICK = split(/\=/,$TMP[1]);
	$id = $TICK[1];

	#kurs = tid,bid,ask,price,volum

	$MAININDEX{$id}="tid=$TMP[2]+TMP[3]+TMP[4]+TMP[5]+TMP[6]";

    }

    elsif (/index/,$TMP[0]) {



