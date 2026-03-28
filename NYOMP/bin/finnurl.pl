#!/local/bin/perl

open(FIND, "find .  -name \"*.html\" -print |") || 
    die "Kunne ikke kjøre find: $!\n";

print " OVERSIKT OVER KALL PÅ WAISSCRIPT \n\n";

while ($filename = <FIND>)
{
    
    open(INNFIL,"<$filename");

    while(<INNFIL>)
    {
	if(/.*\/html\/adv\/.*/)
	{
	    print "FILNAVN: $filename";
	}
    }

    close (INNFIL);
}

