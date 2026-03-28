#!/local/bin/perl

# kode.pl
#
# Dag Wigum, 27.11.95
#




$this_program_name=$ENV{'SCRIPT_NAME'};

$kat_file = "kodeskjema.txt";
$res_file = "kodedb.txt";

open(STDERR, "/dev/null");

open(FIL,"<$kat_file") || die "Not able to open $kat_file\n";
open(OUT,">$res_file") || die "Not able to open $res_file\n";


while (<FIL>) {
    @TMP = split(/#/);
    @TMP2 = split(/\s+/);
    print OUT "$TMP2[1]#$TMP[1]\n";
}


close FIL, OUT;


	
