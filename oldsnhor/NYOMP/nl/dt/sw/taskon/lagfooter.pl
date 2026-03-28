#!/local/bin/perl

$utfil="./tmpfil.html";


open(FIND, "find . -print |") || 
    die "Kunne ikke kjøre find: $!\n";

while ($filename = <FIND>)
{
    chop $filename;
    if(substr($filename,-4) eq "html")
    {
	print "$filename \n";
    
	open(INNFIL,"<$filename");
	open(UTFIL,">$utfil")|| die "Kunne ikke aapne $utfil \n";;

	while(<INNFIL>)
	{
	    if(/^apofooter/)
	    {
		print "\n Jeg fant apofooter! \n\n";
		print UTFIL "\n <a href=\"http://www.oslonett.no/NYOMP/index.html\"><img src=\"/gifs/on/home.gif\" alt=\"\[Oslonett Home\]\" border=0></a> \n";
		print UTFIL "<A HREF=\"/NYOMP/nl/dt/sw/taskon/index.html\"><iMG ALT=\"[Taskon Home]\" SRC=\"/NYOMP/nl/dt/sw/taskon/gifs/small-trans-logo.gif\" border=0></A>";
		print UTFIL "<hr> \n </body> \n </html>";
		goto UT;
	    }

	    $_=~ s/$input1/$input2/;
	    print UTFIL;
	}
UT:
	close (UTFIL);
	close (INNFIL);
    
	`mv $utfil $filename`;
	`chmod g+rxw $filename`;
	`chmod a+rx $filename`;
    }
}
SLUTT:
