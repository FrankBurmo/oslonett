#!/usr/bin/perl

print "Content-type: text/html\n\n";
open I, "ls -1 |";
while (<I>) {
    chop;
  print qq|<p><img src="$_" alt="$_"></p>\n|;
}

close I;
