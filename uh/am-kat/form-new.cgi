#!/local/bin/perl

# The script is called with http://bla.bla.bla/bla/form-new.cgi/parameter

# %file maps parameter to file name extension
%file = (
	 'cd',		'cd',

	 'video',	'vhs',
	 'vhs',		'vhs',

	 'laser',	'laser',
	 'laserdisc',	'laser',

	 'spill',	'spill',
	 );

($param = $ENV{PATH_INFO}) =~ s!^/!!;
$param =~ tr/A-ZÆØÅ/a-zæøå/;
$choice = $file{$param} || "cd";

# ...then we go to the correct search form
print "Location: ";

print "$ENV{SERVER_URL}/uh/am-kat/form-new-$choice.html";
print "\n\n";

exit 0;
