#!/local/bin/perl

$utfilnavn = "./tmpfil";

open(FIND, "find .  -name \"*.html\" -print |") || 
    die "Kunne ikke kjøre find: $!\n";

print " OVERSIKT OVER KALL PÅ WAISSCRIPT \n\n";

while ($filename = <FIND>)
{
    ($title,$ext)=split(/./);
    open(UTFIL,">$utfilnavn");
    open(INNFIL,"<$filename");

    print UTFIL "<html>\n";
    print UTFIL "<head>\n";
    print UTFIL "<title>Hotelloversikt: $title</title>\n";
    print UTFIL "</head>\n";
    print UTFIL "<body bgcolor=0000aa text=fed0a7 vlink=#fed0a7 link=#fed0a7 alink=#fed0a7>\n";



    while(<INNFIL>)
    {
	print UTFIL;
    }

    print UTFIL "</body></html>\n";
    close (UTFIL);
    close (INNFIL);
    `mv $utfilnavn $filename`;
}

