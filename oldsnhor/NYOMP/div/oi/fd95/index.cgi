#!/local/bin/perl

($client, $version) = ($ENV{'HTTP_USER_AGENT'} =~ m#([^/]*)/(\S+)#);
$tables = 0;
$tables = 1 if $client eq "Mozilla" && $version >=1.1;
$talbes = 1 if $client eq "Arena";

print("Location: http://www.oslonett.no/forskdag95/",
      ($tables) ? "index2.html\n\n" : "index.html\n\n");

exit 0;
