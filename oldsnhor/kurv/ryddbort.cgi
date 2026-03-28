#!/local/bin/perl5

require "lib.pl";
%input = &getinput;

open(FOO, ">$DATADIR/kurv-$input{id}.data")
	 || &error("Kunne ikke tømme handlekurven");
close FOO;

print "Location: http://www.sn.no/kurv/vis.cgi\n\n";

exit 0;
