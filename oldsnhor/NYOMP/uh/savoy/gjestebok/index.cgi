#!/local/bin/perl -- -*-perl-*-

$filnavn = "tavle.html";
$toppfil = "toppconfig.html";
$bunnfil = "bunnconfig.html";


print "Content-type: text/html\n\n";

&slettet_tavle unless open (FIL1,"<$filnavn");

while(<FIL1>)
{
 print;
}

close (FIL1);

sub slettet_tavle
{
    open (TAVLE,">$filnavn");
    open (TOPP,"<$toppfil");
    while(<TOPP>)
      {
	print TAVLE;
      }
    close TOPP;
    print TAVLE "<center> \n<font size=+2>\n<a href=\"nyttinnlegg.html\">";
    print TAVLE "New Message!</a></font>\n</center>\n<hr>\n";
    print TAVLE "\n<!--her-->\n";
    open (BUNN,"<$bunnfil");
    while(<BUNN>)
      {
	print TAVLE;
      }
    close BUNN;
    close (TAVLE);
    open (FIL1,"<$filnavn");

}

