#!/local/bin/perl5

$INFILE = 'annonsebase.txt';
$OUTFILE = 'markedsbase.txt';
$SEPARATOR = "\t";
@keys = ('status','omr','type');

open(IN, $INFILE) || die;
open(OUT, ">$OUTFILE") || die;

LINE:
while (<IN>) {
    chop;
    @a = split(/$SEPARATOR/);
    next if $#a < 0;		# skip empty lines
    if ($#a == 0) {		# one field means new status/place/type
	push(@tmp, $_);
	$newplace = 1;
	next;
    }
    if ($newplace) {
	$newplace = 0;
	@field{'type'} = @tmp if $#tmp == 0;
	@field{'omr','type'} = @tmp if $#tmp == 1;
	@field{'status','omr','type'} = @tmp if $#tmp == 2;

# Generell, alternativ kode for de tre foregående linjer
#	@field{splice(@keys, $#keys-$#tmp, $#tmp+1)} = @tmp;

	@tmp = ();
    }
    $line = join($SEPARATOR, @field{@keys}, $_);
    print OUT "$line\n";
}

close IN;
close OUT;

exit 0;

