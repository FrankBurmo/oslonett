#!/local/bin/perl5

$top = "/local/www/div/oi/fd95/data/arr";
$arr = shift @ARGV;

open(IDX, "$top/arr-indeks.txt") || die;

while (<IDX>) {
    @record = split("`");
    $inst = $record[4];
    next unless $inst eq $arr;
    push(@key, $record[3] . $record[1]); # dato + tittel
    push(@nr, $record[0]);	# registreringsnummer
}


sub alpha { $key[$a] cmp $key[$b]; }

@nr = @nr[sort alpha $[ .. $#key];
@key = @key[sort alpha $[ .. $#key];

foreach (@nr) {
    system(sprintf("arr.pl $top/arr%04d.html.updateinfo", $_));
}

close IDX;

