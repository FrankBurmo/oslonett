#!/local/bin/perl

$utfil="./tmpfil.html";
$input1=$ARGV[0];
$input2=$ARGV[$#ARGV];

print "\n Jeg skifter ut $input1 med $input2.\n\n";

open(FIND, "find .  -name index.html -print |") || 
    die "Kunne ikke kjøre find: $!\n";

while ($filename = <FIND>)
{
    print "$filename \n";
    
    open(INNFIL,"<$filename");
    open(UTFIL,">$utfil")|| die "Kunne ikke aapne $utfil \n";;

    $skrivut=0;
    while(<INNFIL>)
    {
	#$_=~ s/$input1/$input2/;
	if(/^<!--        -->/)
	{
	    $skrivut++;
	}
	if(/^\<\/body\>/)
	{
	    $skrivut=0;
	}
	if($skrivut<2)
	{
		print UTFIL;
	}  
    }
    close (UTFIL);
    close (INNFIL);
    
    `mv $utfil $filename`;
    `chmod g+rxw $filename`;
    `chmod a+rx $filename`;
}

