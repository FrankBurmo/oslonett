#!/usr/bin/perl

while (<>) {
	s/\.\s/ /g;
	s%((http|ftp|gopher)://([^ \t,])+)(|\s|,)%<a href=$1>$1</a>$4%gi;
	s//./g;

	print;
}
