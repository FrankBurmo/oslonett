#!/local/bin/perl
# Program for å dumpe innholdet av web-kundedatabasen
# Skriver en postscriptfil for hver kunde til området ./tmp/
# Filene får navn kundeNNN.ps

require 'kundelib.pl';

mkdir("tmp", 0775) unless ( -e tmp);

$ENV{'REQUEST_METHOD'} = 'GET';

open(IDX, "ON-kundedata.txt") || die $!;

while (<IDX>) {
    @f{@fields} = split('"');
    $type{$f{'Kundenr'}} = $f{'Annonsetype'};
}
close IDX;

foreach $kundenr (1 .. 220) {
#    next if $type{$kundenr} =~ /ennå ikke avklart/i;
    print "Kunde nr. $kundenr... ";
    $ENV{'QUERY_STRING'} = "format=psfil&Kundenr=$kundenr";
    $filnavn = sprintf("tmp/kunde%03d.ps", $kundenr);
    system("finnkunde.cgi | tail +3 > $filnavn");
    $h = `head $filnavn`;
    if ( $h =~ /^<html>/ ) {
	print "finnes ikke\n";
	unlink("$filnavn");
    } else {
	print "OK\n";
    }
}
