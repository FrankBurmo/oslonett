#!/local/bin/perl5

$| = 1;

open(K, "katalog.txt") || die $!;

dbmopen(%index, "item-index", 0664);

$pos = tell(K);
while (<K>) {
    if ($count++ > 1000) { print "#"; $count-=1000; }
    $key = (split(/;/))[2];
    $index{$key} = $pos;
#    print "$key, $pos\n";
    $pos = tell(K);
}

dbmclose (%index);

close K;

