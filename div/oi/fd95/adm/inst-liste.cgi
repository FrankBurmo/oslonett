#!/local/bin/perl

require "fd-lib.pl";

print "Content-type: text/html\n\n";


open(FILE, $instindeks) || &error("Kunne ikke åpne indeksfilen $instindeks");
while (<FILE>) {
    chop;
    @entry{@instfields} = split($fieldsep);
    push(@inst, sprintf("%-50s%4d     %s\n",
		       @entry{'Institusjon', 'Nummer', 'Maskin'}));
}
close(FILE);

@inst = sort @inst;

@inst = ( "  <b>Ingen institusjoner registrert</b>" ) unless @inst;

print &header("Liste over alle institusjoner");

printf("<pre>\n%-50s%6s   %s\n<hr noshade size=\"1\">\n",
       "Institusjon", "Reg.nr", "Maskin");
print @inst;
print "</pre>", &footer;

exit 0;
