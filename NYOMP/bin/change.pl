#!/local/bin/perl

$utfil="./tmpfil.html";
$input1="http://www2.oslonett.no/cgi-bin";
$input2="http://www.oslonett.no/cgi-bin";

print "\n Jeg skifter ut $input1 med $input2.\n\n";

open(FIND, "find .  -name \"*.map\" -print |") || 
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
	$_=~ s/$input1/$input2/g;
	print UTFIL;
	if($linje=~ /$input1/)
	{
	    $funnet=1;
	    print "$filename \n";
	}
    }
    close (UTFIL);
    close (INNFIL);
    
    if($funnet==1)
    {
	chop $filename;
	$backup=$filename.".bak";
	print "TEST: $backup\n";
	`cp $filename $backup`;
    }
    `mv $utfil $filename`;
    `chmod g+rxw $filename`;
    `chmod a+rx $filename`;
    
    $funnet=0;

}


