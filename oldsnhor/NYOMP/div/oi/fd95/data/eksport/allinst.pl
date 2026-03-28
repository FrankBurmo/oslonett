#!/local/bin/perl5

$top = "/local/www/div/oi/fd95/data/inst";

open(IDX, "$top/inst-indeks.txt") || die;

while (<IDX>) {
    @record = split("`");
    push(@key, $record[1]);	# institusjonens navn
    push(@nr, $record[0]);	# registreringsnummer
    $inst{$record[0]} = $record[1];
}


sub alpha { $key[$a] cmp $key[$b]; }

@nr = @nr[sort alpha $[ .. $#key];
@key = @key[sort alpha $[ .. $#key];

foreach (@nr) {
    print STDERR "Skriver data for $inst{$_}...\n";
    system(sprintf("inst.pl $top/inst%04d.html.updateinfo", $_));
    next if $inst{$_} eq "Universitetet i Oslo"; # forhåndsformattert prog.
    system("allarr.pl '$inst{$_}'");
}


close IDX;

