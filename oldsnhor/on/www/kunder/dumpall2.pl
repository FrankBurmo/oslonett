#!/local/bin/perl
# Program for å dumpe innholdet av web-kundedatabasen
# Skriver en tekstfil til standard ut med data om alle kundene

require 'kundelib.pl';

open(IDX, "ON-kundedata.txt") || die $!;

$ind="    ";

while (<IDX>) {
    @f{@fields} = split('"');
    next if $f{'Annonsetype'} =~ /ennå ikke avklart/i;
    print "--- $f{'Firma'} ---\n\n";
    foreach $name (@fields) {
	print "$name:\n$ind";
	$f{$name} =~ s/(.{50,70})\s/$1\n$ind/g;
	print $f{$name},"\n";
    }
    print "\n\n";
}
close IDX;
