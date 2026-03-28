#!/local/bin/perl

$utfil="./tmpfil";
$input1="";
$input2="";

print "\n Jeg skifter ut $input1 med $input2.\n\n";

open(FIND, "find .  -name \"*.html\" -print |") || 
    die "Kunne ikke kjøre find: $!\n";

$funnet=0;

while ($filename = <FIND>)
{
    #print "$filename \n";
    
    open(INNFIL,"<$filename");
    open(UTFIL,">$utfil")|| die "Kunne ikke aapne $utfil \n";;

    while(<INNFIL>)
    {	
	$linje=$_;

    }
    close (UTFIL);
    close (INNFIL);
    
    `mv $utfil $filename`;
    `chmod g+rxw $filename`;
    `chmod a+rx $filename`;
    
    $funnet=0;

}


