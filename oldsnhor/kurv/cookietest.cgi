#!/local/bin/perl5

print "Set-Cookie: newcookie=$ENV{QUERY_STRING}; path=/kurv\n"
    if length $ENV{QUERY_STRING};
print "Content-type: text/html\n\n";
print "<font size=\"+1\">\n";

foreach (split(/;\s*/, $ENV{HTTP_COOKIE})) {
    print $_, "<br>\n";

}
exit 0;
