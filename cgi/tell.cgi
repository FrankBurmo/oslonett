#!/usr/bin/perl

use lib "/home/oslonett/perllib";
use mySSI;
use locale;

use CGI;

my $cgi = new CGI;
my $url = $cgi->param("url");
my $tmpl;

{
  local($/) = undef;
  open T, "/home/oslonett/adm/tell.tmpl";
  $tmpl = <T>;
  close T; 
}

 $tmpl = expand_inc($tmpl);
 $tmpl =~ s/\@URL\@/$url/g;

 print "Content-type: text/html\n\n$tmpl";
