#!/local/bin/perl

$utfil="./tmpfil.html";

open(FIND, "find .  -name \"*.html\" -print |") || 
    die "Kunne ikke kjøre find: $!\n";

print " OVERSIKT OVER KALL PÅ WAISSCRIPT \n\n";

while ($filename = <FIND>)
{
    
    open(INNFIL,"<$filename");
    open(UTFIL,">$utfil")|| die "Kunne ikke aapne $utfil \n";

    while(<INNFIL>)
    {
	if(/.*\/cgi-bin\/.*/)
	{
	    
		if(!/.*imagemap.*/)
		{
		    if(/.*wais.*/)
		    {
			print "FILNAVN: $filename";
			print "GAMMEL LINJE: $_";
			$_=~ s#/cgi-bin/#http://www.oslonett.no/cgi-bin/#g;
			print "NYLINJE: $_ \n\n";
		    }
		}
	}
    }

    close (INNFIL);
    close (UTFIL);
    
}

