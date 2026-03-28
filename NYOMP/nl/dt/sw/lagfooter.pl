#!/local/bin/perl

$utfil="./tmpfil.html";
$url=$ARGV[0];
$gif=$ARGV[$#ARGV];

$skifte="*.html";

print "\n Jeg lager footer med: \n URL = $url \n icon = $gif \n\n";

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
		print UTFIL "\n <a href=\"$url\"><img src=\"$gif\" alt=\"\[Home\]\" border=0></a> \n";
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
