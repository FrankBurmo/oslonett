#!/local/bin/perl

$ENV{QUERY_STRING} =~ s/^[^=]*=//;
$ENV{QUERY_STRING} =~ s/\+/ /g;
$ENV{QUERY_STRING} =~ s/%(..)/pack("c",hex($1))/ge;

($gr, $art) = split(m:/:, $ENV{QUERY_STRING});
$gr =~ s/%(..)/pack("c",hex($1))/ge;

open(REF, "$gr/$art");
$/='';
$a=<REF>;
close REF;

if ($a !~ /\npublished:/) {
    open(REF, ">>$gr/$art");
    print REF "published: yes\n";
    close REF;
}

$gr =~ s!(["% &?/])!sprintf("%%%02X",unpack("c",$1))!ge;
print "Location: http://www.aftenposten.no/simon/redaksjon.cgi/$gr/$art\n\n";
exit 0;
