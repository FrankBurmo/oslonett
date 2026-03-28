#!/local/bin/perl5

require "/local/www/data/vg/include/include.pl";

$top = "/local/www/data/intervju";

%input = &getinput;

open(F, ">$input{'filename'}")
    || &error("Kunne ikke skrive til filen $input{'filename'}");
foreach (keys %input) {
    $input{$_} =~ s/\n/<br>/g;
    $input{$_} =~ s/\r//g;
    print F "$_:\t$input{$_}\n";
}
close F;

open(I, "+<$input{'int_name'}.info")
    || &error("Kan ikke åpne filen $input{'int_name'}");
#Skip header lines
while (<I>) {
    last unless /\S/;
}
while (<I>) {
    if ($_ == $input{'nummer'}) {
	$alleredebesvart = 1;
	last;
    }
}

unless ($alleredebesvart) {
    seek(I, 0, 2);		# seek end of file
    print I "$input{'nummer'}\n"; # write number
}
close I;

&header("Har oppdatert data");

print "Spørsmål nummer $input{'nummer'} er nå besvart.<p>\n\n";
print qq!Tilbake til <a href="spm.cgi/$input{'int_name'}">intervjuoversikten</a>, \n!;
print qq!eller se på <a href="/cgi-bin/intervju/$input{'int_name'}">det ferdige !;
print "intervjuet</a>.\n";

&std_footer;

exit 0;





sub header {
    local($txt) = $_[0];

    return if $HEADER++;

    &top($txt);

    print "<title>$txt</title>\n";
    &std_header;
    print qq!<h1><tt><font size="+5">$txt</font></tt></h1>\n\n!;
}


sub error {
    local($msg) = $_[0];

    &header("Feilmelding");

    print "Programmet ble avbrutt med følgende feilmelding:\n\n<blockquote>\n";
    print qq!<hr size="2" noshade>\n<font size="+1"><b>$msg</b></font>\n!;
    print qq!<hr size="2" noshade>\n</blockquote>\n!;
    &std_footer;
    exit 0;
}


sub getinput {
# Leser inn data (med method GET eller POST) og plasserer dem i en
# assosiativ array, der nøklene i array'en er feltnavnene

    local($i, $name, $value, $data, @data, %input);

    if ($ENV{'REQUEST_METHOD'} eq "GET") {
        $data = $ENV{'QUERY_STRING'};
    } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
        read(STDIN, $data, $ENV{'CONTENT_LENGTH'});
    } else {
        return;
    }

    # Del opp input-data i felter ved alle forekomster av '&'.
    @data = split(/&/, $data);

    for $i (0 .. $#data) {

        # Pluss oversettes til SPC
        $data[$i] =~ tr/+/ /;

        # Alt til venstre for første "=" er feltnavn, resten er felt-verdi
        ($name, $value) = split(/=/, $data[$i], 2);

        # Erstatt forekomster av %<hexkode> med tilsvarende tegn
        $name =~ s/%(..)/pack("c",hex($1))/ge;
        $value =~ s/%(..)/pack("c",hex($1))/ge;

        # En/flere forekomster av whitespace i $value oversettes til SPC

        $input{$name} =  $value; # assosier verdi med feltnavn...
    }
    return %input;
}

