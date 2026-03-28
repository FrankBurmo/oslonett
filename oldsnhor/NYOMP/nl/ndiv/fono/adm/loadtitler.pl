#!/local/bin/perl
# Script for å laste titler fra fil i argv(1)
#

require "../lib/tittellib.pl";

$dump = shift;
$bak  = $datafile . ".bak";  #Backup
`cp $datafile $bak`;

## Les inn genredata
open(GEN, "$genredata") || die "Kan ikke åpne genrefil $genredata\n";
while (<GEN>) {
    chop ($_);
    $isgen{$_}++;
}
close (GEN);

# og åpne for skriving igjen:

open(GEN, ">>$genredata") || die "Kan ikke åpne genrefil $genredata\n";

#Artister
open(ART, "$artistdata") || die "Kan ikke åpne artistfil $artistdata\n";
while (<ART>) {
    chop ($_);
    $isart{$_} = 1;
    }

close (ART);

# .. for skriving

open(ART, ">>$artistdata") || die "Kan ikke åpne artistfil $artistdata\n";

open(TIT, ">$datafile") || die "Kan ikke åpne  $datafile\n";

open(DMP, "$dump") || die "Kan ikke åpne dumpfilen $dump\n";

$nr = 0;
$div ="";

($sec, $min, $hour, $mday, $mon, $year, $wday, $yday) = localtime;
$mon++;
$idag = sprintf ("%2.2d%2.2d%2.2d %2.2d:%2.2d:%2.2d", $year,$mon,$mday,$hour,$min,$sec);

while (<DMP>) {

    $nr++;
    ($mdl,$artist,$tit,$genre,$knr, $aar,$pris) = split(/;/);


if (!$isart{$artist}) {
    $isart{$artist} = 1;
    print ART "$artist\n";
   }

if (!$isgen{$genre}) {
    $isgen{$genre} = 1;
    print GEN "$genre\n";
   }

@rec = 
    ($nr,"$idag","$idag",$mdl,$artist,$tit,$genre,$knr,$aar,$pris);

$record="";
  for (@rec) { $record .= "$_\"";
  }
chop ($record);
print TIT "$record";
}

print "$nr linjer prosessert\n";
close (MDL);
close (DMP);
close (ART);
close (GEN);
close(TIT);




