#!/local/bin/perl

$utfil="./tmpfil.html";
$input1="<img src=\"/NYOMP/UH_kent/Underh_inv.gif\" alt=\"[Underholdning]\">";
$input2="<a href=\"/NYOMP/info.html\"><img src=\"/NYOMP/UH_kent/Underh_inv.gif\" alt=\"[Underholdning]\"></a>";

print "\n Jeg skifter ut $input1 med $input2.\n\n";

open(FIND, "find .  -name index.html -print |") || 
    die "Kunne ikke kjøre find: $!\n";
while ($filename = <FIND>)
{
    print "$filename \n";
    
    open(INNFIL,"<$filename");
    open(UTFIL,">$utfil")|| die "Kunne ikke aapne $utfil \n";;

    while(<INNFIL>)
    {
	if(/.*<img src=\"\/NYOM.*/)
	{
	    print UTFIL "$input2\n";
	}
	else {print UTFIL;}
    }
    close (UTFIL);
    close (INNFIL);
    
    `mv $utfil $filename`;
    `chmod g+rxw $filename`;
    `chmod a+rx $filename`;
}
