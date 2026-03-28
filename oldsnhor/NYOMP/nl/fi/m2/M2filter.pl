#!/local/bin/perl5

# Leser inn filen som skal legges til basen
$innfil = $ARGV[0];
$dbfil  = "m2base.txt"; 

open(INNFIL,"<$innfil") || error("Fikk ikke åpnet inputfilen $innfil");
open(BASE,">$dbfil") || error("Fikk ikke åpnet databasefilen $dbfil");

$count=0;
$DB = ();
# Først leser vi inn hele innfilen i et array, og legger på skilletegn og terminering
foreach $_ (<INNFIL>) {
    if (/^\s+(\S+)\s+(.+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)/) {

	$kode = $1; $adr  = $2; $komm = $3; $dist = $4; $areal= $5; $takst= $6;

	# Fjern trailing mellomrom efter adresse
	$adr =~ s/(\s*)$//g;

	# Dropp de som ikke har adressefelt
	if ($adr ne "") {
	    # Generer array
	    $line = join('#',$kode,$adr,$komm,$dist,$areal,$takst)."\$\$";
	    
	    $DB[$count] = $line;
	    
	    $line = "";
	    $count++;
	}
    }
}

print "Leste inn $count poster\n";

# Skriv til databasefil (lager backup f;rst)
$BACKUPFILE = "m2base.txt.bak";
system("cp $dbfil ./$BACKUPFILE");
system("chmod 770 $BACKUPFILE");

foreach $_ (@DB) {
    print BASE $_."\n";
}

close(INNFIL);
close(BASE);

exit(0);

