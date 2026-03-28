#!/usr/bin/perl

$url = $ENV{QUERY_STRING};
$url =~ s/%([\da-f][\da-f])/pack("C",hex($1))/gei;

print "Location: $url\n\n" if length $url;
&error unless length $url;
close(STDOUT);



sub error
{
    print "Status: 400 Bad Request\n\n";
}


