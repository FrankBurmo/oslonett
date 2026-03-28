#!/usr/local/bin/perl5

$MAL = "retting-mal.html";

use CGI::Query;

($nr,$navn) = @query{'nr', 'navn'};

print "Content-Type: text/html\n\n";

if (open(MAL, $MAL)) {
    while (<MAL>) {
	s/\@FIRMA\@/$navn/o;
	s/\@FIRMANR\@/$nr/o;
	print;
    }
} else {
    print "<h1>$nr/$navn</h1>\n";
}
