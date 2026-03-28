#!/local/bin/perl5

print "Content-type: text/html\n\n";
print "<h2>Your global cookies \@$ENV{SERVER_NAME} are:</h1>\n\n";
$kaker = $ENV{HTTP_COOKIE} || "(none)";
print $kaker,"\n";

exit 0;
