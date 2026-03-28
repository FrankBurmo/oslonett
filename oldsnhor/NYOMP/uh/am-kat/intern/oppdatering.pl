#!/local/bin/perl5

$KATALOG = '/local/www/uh/am-kat/intern/katalog.txt';
$BACKUPDIR = '/local/www/uh/am-kat/intern/backup';

sub quit;

$t = time;

close STDERR;			# pep støyer for mye, kaster stderr
foreach $newfile (@ARGV) {
    quit "Finner ikke filen $newfile, avbryter\n" unless -f $newfile;
    print "Leser inn nyheter fra $newfile...\n";
    open(F, "/local/bin/pep -gibm2iso $newfile |")
	|| quit "Kunne ikke utføre 'pep -gibm2iso $newfile': $!\n";
    push(@k, <F>);		# let large array grow huge
    close F;
}
print "Tilsammen ", $#k+1, " nye titler\n";

print "Bygger sorteringsnøkkel-tabell\n";
foreach (@k) {
    push(@sortkey, join(";",(split(/;/))[0,1]));
}

print "Sorteringsnøkkel-eksempel:\n",join("\t",@sortkey[$[..$[+75]),"\n"
    if $DEBUG;

print "Sorterer etter produkt+kategori\n";
@k2 = @k[sort bykey $[ .. $#k];
sub bykey { $sortkey[$a] cmp $sortkey[$b]; }

print "Finner indeks og antall for hver 'produkttype;kategori'\n";
foreach $i ( $[ .. $#k2 ) {
    $prodkat = join(";", (split(/;/, $k2[$i]))[0,1]);
    if ($prodkat ne $last) {
	$first{$prodkat} = $i;
	$last{$last} = $i - 1 if defined $last;
	$last = $prodkat;
    }
}
$last{$prodkat} = $#k2;

if ($DEBUG) {
# Test-utskrift: vis indekser for alle nye produkt;kategori
    foreach (sort keys %first) {
	printf "%40s %6d %6d\n", $_, $first{$_}, $last{$_};
    }
}

open(INNKAT, $KATALOG)
    || quit "Kunne ikke åpne katalogfilen $KATALOG: $!\n"; 
open(UTKAT, ">$KATALOG.new")
    || quit "Kunne ikke åpne katalogfilen $KATALOG.new: $!\n";
print "Leser inn gammel katalog...\n";
print "...og lagrer oppdatert katalogfil...\n";

undef $last;
while (<INNKAT>) {
    $prodkat = join(";", (split(/;/))[0,1]);
    $last = $prodkat unless defined $last;
    if ($prodkat ne $last) {
	print "Lagrer nye titler i $last (neste: $prodkat)\n"
	    if $DEBUG;
	print UTKAT @k2[$first{$last} .. $last{$last}]
	    if defined $first{$last} && defined $last{$last};
	$last = $prodkat;
    }
    print UTKAT $_;
}

close INNKAT;
close UTKAT;

print "Konsistens-sjekker ny katalog...\n";
open(KAT, "$KATALOG.new")
    || quit "Kunne ikke åpne katalogfilen $KATALOG.new: $!\n";
undef $last;
while (<KAT>) {
    $prodkat = join(";", (split(/;/))[0,1]);
    $last = $prodkat unless defined $last;
    if ($prodkat ne $last) {
	if ($count{$last}++) {
	    print "produkt;katalog '$last' er avbrutt av '$prodkat'\n";
	    $errcount++;
	}
	$last = $prodkat;
    }
}
quit "De $errcount feilene må rettes manuelt i katalog-filen $KATALOG.new\n"
    if $errcount;
print "Katalogen er konsistent.\n";

print "Tar backup av gammel katalog, bytter til ny\n";
@lt = localtime;
$lt[4]++;
$backup = sprintf("$BACKUPDIR/kat.%02d%02d%02d-%02d:%02d:%02d.txt",
		  @lt[reverse 0..5]);
rename ($KATALOG, $backup)
    || quit "Kunne ikke flytte gammel katalog til $backup\n";
rename ("$KATALOG.new", $KATALOG)
    || quit "Kunne ikke flytte ny katalog til $KATALOG.\nNB! Flytt gammel katalog tilbake fra backup manuelt! HASTER!\n";

&mkcatindex;

&mkitemindex;

$t = time - $t;
$m = int($t/60);
$s = $t - $m*60;
print "\nFerdig!\n";
printf "Total tid brukt på oppdateringen: %2d:%02d\n", $m, $s;
exit 0;



sub quit {
    print @_;
    exit 1;
}


sub mkcatindex {
    $| = 1;
    print "Bygger kategori-database for å gjøre effektive søk ";
    print "i kun én kategori...\n";

    open(K, $KATALOG) || quit "Kunne ikke åpne $KATALOG: $!\n";

    print "NB! Mens denne operasjonen pågår fungerer ikke søking.\n";
    print "    IKKE AVBRYT DENNE OPREASJONEN!\n";

    if ($DEBUG) {
	print "Finner alle kategorier, skriver '#' for hver 1000de tittel.\n";
	printf "%-30s %10s: %s\n","Kategori","Filpos","antall oppslag";
    }


    unlink "cat-index.pag";
    unlink "cat-index.dir";
    dbmopen(%index, "cat-index", 0664);

    $pos = tell(K);
    while (<K>) {
	if ($count++ > 1000) { print "#" if $DEBUG; $count-=1000; }
	$key = join(";",(split(/;/))[0,1]);

	$index{lc $key} = $pos if $key ne $lastkey;
	printf "\n%-30s %10s: ", $key, $pos if $DEBUG && $key ne $lastkey;
	$lastkey = $key;
	$pos = tell(K);
    }
    dbmclose (%index);
    print "\n" if $DEBUG;

    close K;
}


sub mkitemindex {
    $| = 1;
    print "Bygger tittel-database for å gjøre effektive tittel-oppslag\n";
    print "NB! Mens denne operasjonen pågår fungerer ikke hurtig-oppslag\n";
    print "    på tittel (sekvensielt søk brukes i stedet). IKKE AVBRYT!\n";
    open(K, $KATALOG) || quit "Kunne ikke åpne $KATALOG: $!\n";
    dbmopen(%index, "item-index", 0664);

    $pos = tell(K);
    while (<K>) {
	$key = (split(/;/))[2];
	$index{$key} = $pos;
	$pos = tell(K);
    }

    dbmclose (%index);
    close K;
}
