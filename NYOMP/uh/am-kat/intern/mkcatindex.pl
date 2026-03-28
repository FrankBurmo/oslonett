#!/local/bin/perl5

$| = 1;
print "Finner alle kategorier, skriver '#' for hver 1000de tittel.\n\n";
printf "%-30s %10s: %s","Kategori","Filpos","antall oppslag";

open(K, "katalog.txt") || die $!;

unlink "cat-index.pag";
unlink "cat-index.dir";
dbmopen(%index, "cat-index", 0664);

$pos = tell(K);
while (<K>) {
    if ($count++ > 1000) { print "#"; $count-=1000; }
    $key = join(";",(split(/;/))[0,1]);

    $index{lc $key} = $pos if $key ne $lastkey;
    printf "\n%-30s %10s: ", $key, $pos if $key ne $lastkey;
    $lastkey = $key;
    $pos = tell(K);
}

dbmclose (%index);

close K;

print "\n\n";
