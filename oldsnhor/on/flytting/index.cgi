#!/usr/bin/perl

($client, $version) = ($ENV{'HTTP_USER_AGENT'} =~ m,([^/]*)/(\S+),);
$tables = 0;
$tables = 1 if $client eq "Mozilla" && $version >=1.1;
$tables = 1 if $client eq "Arena";

$directory = $ENV{'SCRIPT_NAME'};
$directory =~ s,/[^/]*$,/,;

print("Location: $ENV{'SERVER_URL'}$directory",
      ($tables) ? "index2.html\n\n" : "index.html\n\n");

exit 0;
