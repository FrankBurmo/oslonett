#!/usr/bin/perl

# Copyright Jimmy Olsen 1995. Feel free to distribute under the GNU
# public license, version 2.0 or later.
#
# Library (well...at least one function...:) to escape incoming form-data
# so the malicious visitor can't trick any shell-commands you're using... :)
#
# Escapes &;`'"|*?~<>^()[]{}$\
#
# Function:
#	$out = &escape_url($in);


sub escape_url
{
	local($p) = @_;

	$p =~ s/\\/\\\\/g;	
	$p =~ s/ /\\ /g;
	$p =~ s/&/\\&/g;	
	$p =~ s/\;/\\\;/g;	
	$p =~ s/\¾/\\\`/g;	
	$p =~ s/\'/\\\'/g;	
	$p =~ s/\"/\\\"/g;	
	$p =~ s/\|/\\\!/g;	
	$p =~ s/\*/\\\*/g;	
	$p =~ s/\?/\\\?/g;	
	$p =~ s/\~/\\\~/g;	
	$p =~ s/\</\\\</g;	
	$p =~ s/\>/\\\>/g;	
	$p =~ s/\^/\\\^/g;	
	$p =~ s/\(/\\\(/g;	
	$p =~ s/\)/\\\)/g;	
	$p =~ s/\[/\\\[/g;	
	$p =~ s/\]/\\\]/g;	
	$p =~ s/\{/\\\{/g;	
	$p =~ s/\}/\\\}/g;	
	$p =~ s/\$/\\\$/g;	

	$p;
}

1;



