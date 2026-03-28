#!/local/bin/perl5

require "lib.pl";

%input = &getinput;

&error("Søkemønster ikke angitt, forsøk igjen")
    unless length $input{pattern};

$input{pattern}	=~ s/%/&#37;/g;
$input{url}	=~ s/%/&#37;/g;

open(BASE, $BASE) || &error("Kunne ikke lese link-databasen: $BASE");
while (<BASE>) {
    chop;
    ($pattern, $url) = split(/%/);
    $link{$pattern} = $url;
}
close BASE;

delete $link{$input{oldpattern}} if length $input{oldpattern};
$link{$input{pattern}} = $input{url} if length $input{url};

open(BASE, ">$BASE")
    || &error("Kunne ikke skrive til link-databasen $BASE (open failed)");
foreach (keys %link) {
    print BASE "$_%$link{$_}\n";
}
close BASE
    || &error("Kunne ikke skrive til link-databasen $BASE (open failed)");

print "Location: $ENV{SERVER_URL}/me/ts/ne/autolink/linkadm.cgi\n\n";

exit 0;
