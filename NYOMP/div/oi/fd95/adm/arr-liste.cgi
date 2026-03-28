#!/local/bin/perl5

require "fd-lib.pl";

print "Content-type: text/html\n\n";


open(FILE, $arrindeks) || &error("Kunne ikke åpne indeksfilen $arrindeks");
while (<FILE>) {
    chop;
    @entry{@arrfields} = split($fieldsep);
    push(@arr, sprintf("%-50s%4d     %s\n",
		       @entry{'Arrangement', 'Nummer', 'Maskin'}));
}
close(FILE);

sub lowcase { lc($a) cmp lc($b); }
@arr = sort lowcase @arr;

@arr = ( "  <b>Ingen arrangementer registrert</b>" ) unless @arr;

print &header("Liste over alle arrangementer");

printf("<pre>\n%-50s%6s   %s\n<hr noshade size=\"1\">\n",
       "Arrangement", "Reg.nr", "Maskin");
print @arr;
print "</pre>", &footer;

exit 0;
