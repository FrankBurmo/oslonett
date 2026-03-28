#!/local/bin/perl
# Script for å laste kundebasen fra fil i argv(1)
#

require "../lib/medllib.pl";

$dump = shift;
$bak  = $datafile . ".bak";  #Backup

`cp $datafile $bak`;
# open(MDL, ">$datafile");
open(DMP, "$dump") || die "Kan ikke åpne dumpfilen $dump\n";

($sec, $min, $hour, $mday, $mon, $year, $wday, $yday) = localtime;
$mon++;
$idag = sprintf ("%2.2d%2.2d%2.2d %2.2d:%2.2d:%2.2d", $year,$mon,$mday,$hour,$min,$sec);


$nr = 0;
$div ="";
while (<DMP>) {

($nvn,$kontakt,$adr,$pnr,$psted,$tlf,$fax,$email,$url) = split(/%/);
next unless $nvn;
$nr++;
@rec = 
    ($nvn,$kontakt,$adr,$pnr,$psted );

$record="";
  for (@rec) { $record .= "$_\;";
  }
chop ($record);
print "$record\n";
}
#close (MDL);
close (DMP);




