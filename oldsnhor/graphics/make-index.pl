#!/usr/local/bin/perl -w

print "<TITLE>Images</TITLE><H1>Image index</H1>
";

for (<*.gif>,<*.xbm>,<people/*.gif>) {
    print "<h2>$_</h2><img src=$_> <a href=$_><img src=internal-gopher-image alt=\"GET IT!\"></a>\n";
}

require "ctime.pl";
print "<hr>Made by '$0' at ";
print &ctime(time);
