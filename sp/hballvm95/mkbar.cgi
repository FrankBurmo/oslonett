#!/local/bin/perl5
# Program returns gif image containong color bar of length $ENV{QUERY_STRING}

$ENV{PATH} .= ':/local/x11/bin/pbm';	# where pbm progs are found
$COLOR = '\#b00';	# select color in format #rgb, each in 0..f (hex)
$HEIGHT = 10;
$| = 1;			# have to flush IO operations before calling system()

$ENV{QUERY_STRING} = 1 unless $ENV{QUERY_STRING} > 0;	# length defaults to 1
open(STDERR, '>/dev/null');	# discard noisy status messages from pbmprogs

print "Content-type: image/gif\n\n";
system("ppmmake $COLOR $ENV{QUERY_STRING} $HEIGHT | ppmtogif");

exit 0;
