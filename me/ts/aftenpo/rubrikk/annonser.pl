#!/local/bin/perl

# annonser.pl
#
# Dag Wigum, 15.11.95
#
# Leser igjennom annonsefilen fra Aftenposten, og strukturerer denne.
#

umask 002;

$this_program_name=$ENV{'SCRIPT_NAME'};
$kat_file=$ARGV[0];
$kode_file="kodedb.txt";
$res_file="resultatdb.txt";

open(STDERR, "/dev/null");

open(FIL,"<$kat_file") || die "Not able to open $kat_file\n";
open(KODE,"<$kode_file") || die "Not able to open $kode_file\n";
open(OUT,">$res_file") || die "Not able to open $res_file\n";


while (<KODE>) {
    @m=split(/#/);
    $KODE{"$m[0]"}="$m[1]";
}


%REFINDEX = ("BAR","BIL1","BLN","BIL2","BLR","BIL2","BAM","BIL1","BAU","BIL1","BBM","BIL1","BCI","BIL1","BDA","BIL1","BDI","BIL1","BFI","BIL1","BFO","BIL1","BHO","BIL1","BLA","BIL2","BMA","BIL2","BME","BIL2","BMI","BIL2","BNI","BIL2","BOP","BIL3","BPE","BIL3","BRE","BIL3","BSU","BIL3","BSZ","BIL3","BTO","BIL3","BVL","BIL3","BVW","BIL3","BSA","BIL3","BVO","BIL3","BAN","BIL4","BHY","BIL1","BJA","BIL2","BPO","BIL3","BSK","BIL3","BCH","BIL1","BJE","BIL2","BDE","BIL1","BKI","BIL2","B01","BIL4","B04","BIL4","B15","BIL4","BAB","BIL4","BAD","BIL4","BAF","BIL4","BAH","BIL4","BAK","BIL4","Å","BAAT","B03","BYMSE","B05","BYMSE","B06","BYMSE","B07","BYMSE","B08","BYMSE","B09","BYMSE","B10","BYMSE","B11","BYMSE","B12","BYMSE","B13","BYMSE","B14","BYMSE","B16","BYMSE","B17","BYMSE","B18","BYMSE","E04","EBOLIG","E05","EBOLIG","E06","EBOLIG","E07","EBOLIG","E08","EBOLIG","E09","EBOLIG","E10","EBOLIG","E11","EBOLIG","E12","EBOLIG","E13","EBOLIG","E14","EBOLIG","E15","EBOLIG","E24","EBOLIG","L10","EBOLIG","R","EFRITID","E19","EFRITID","E20","EFRITID","E21","EFRITID","E23","EFRITID","E24","EFRITID","E22","EFRITID","E17","ELEIE","L03","ELEIE","L04","ELEIE","E18","ELEIE","L06","ELEIE","L07","ELEIE","E01","EFORS","E02","EFORS","E03","EFORS","E16","EFORS","E25","EFORS","L01","EFORS","L02","EFORS","L08","EFORS","L09","EFORS","L11","EFORS","N01","ENAERING","N02","ENAERING","N03","ENAERING","N04","ENAERING","N05","ENAERING","N06","ENAERING","N07","ENAERING","H","HUS","A","HUS","R","REISER","P","HELSE","C","UNDERHOLDNING","U","UNDERVISNING","X","SPORT","T","PERSON","K03","PERSON","K01","KUNN","K02","KUNN","K04","KUNN","Y","BYGG","V","BYGG","M","REKLAME","O","DATA","Ø","FORSIKRING","F","FORR","G","TRANSPORT","S","STILLING");

#    foreach $k ( %REFINDEX) { print "$k\n"; if ($i++ == 1) { print "\n"; $i -= 2;}}
#    exit 0;
unlink 'key.dir', 'key.pag', 'oppslag.dir', 'oppslag.pag';

dbmopen(%KEYINDEX,"key",0664);


%KEYINDEX = ("BIL","0","BAAT","0","EBOLIG","0","EFRITID","0","ELEIE","0","EFORS","0","ENAERING","0","HUS","0","REISER","0","HELSE","0","UNDERHOLDNING","0","UNDERVISNING","0","SPORT","0","PERSON","0","KUNN","0","BYGG","0","REKLAME","0","DATA","0","FORSIKRING","0","FORR","0","TRANSPORT","0","STILLING","0");

dbmopen(%ANTALLINDEX,"antall",0664);

%ANTALLINDEX = ("BIL","0","BAAT","0","EBOLIG","0","EFRITID","0","ELEIE","0","EFORS","0","ENAERING","0","HUS","0","REISER","0","HELSE","0","UNDERHOLDNING","0","UNDERVISNING","0","SPORT","0","PERSON","0","KUNN","0","BYGG","0","REKLAME","0","DATA","0","FORSIKRING","0","FORR","0","TRANSPORT","0","STILLING","0");


dbmopen(%MAININDEX,"oppslag",0664);

    foreach $key (%MAININDEX) {
	delete $MAININDEX{$key};
    }



&katalog;



sub katalog{

    $teller = 0;


while (<FIL>) {

    if (/startfile/) {
	@TMP = split(/\></);
	$tmp = substr($TMP[1],0,17);
	print OUT "$tmp<br>\n";
    }
    elsif (/start_date/) {
	@TMP = split(/\></);
	$tmp = substr($TMP[0],12,19);
	$MAININDEX{"DATE"} = "$tmp\n";
    }
    elsif (/class=/) {
	$teller++;
	$i='';
	@TMP = split(/\></);
	$tmp = substr($TMP[6],10,100);
	$antall = substr($TMP[5],11,2);
	$hkat = substr($TMP[3],8,3);
	$kat = $hkat;
	$hkat =~ s/H\d+/H/;
	$hkat =~ s/P\d+/P/;
	$hkat =~ s/U\d+/U/;
	$hkat =~ s/V\d+/V/;
	$hkat =~ s/R\d+/R/;
	$hkat =~ s/Y\d+/Y/;
	$hkat =~ s/C\d+/C/;
	$hkat =~ s/F\d+/F/;
	$hkat =~ s/O\d+/O/;
	$hkat =~ s/M\d+/M/;
	$hkat =~ s/G\d+/G/;
	$hkat =~ s/S\d+/S/;
	$key = $REFINDEX{$hkat};
	while (length($KEYINDEX{$i.$key})>1000) {
	    $i++;
	}
	$KEYINDEX{$i.$key} = $KEYINDEX{$i.$key} . "$teller,";
	$ANTALLINDEX{$key}++;
	&uc($KODE{$kat});
	&tegnsett($tmp);
	$string = "Kategori=$kat#Kat_tekst=$KODE{$kat}#Antall=$antall#<br>$tmp<br>";

	$a = <FIL>;
	until ($a=~/endtext/) {
	    $string = $string . "$a<br>";
	    $a = <FIL>;
	}
	$MAININDEX{"$teller"} = $string;
    }
    else {
	print OUT;
    }
}

    return;
}
   

sub uc {
    $_[0] =~ tr/a-zæøå/A-ZÆØÅ/;
}

sub tegnsett {
    $_[0] =~ tr/”/ø/;
}


dbmclose(%MAININDEX);
dbmclose(%KEYINDEX);
dbmclose(%ANTALLINDEX);

close FIL, OUT;


	
