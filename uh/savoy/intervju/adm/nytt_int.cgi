#!/local/bin/perl5

require "/local/www/data/vg/include/include.pl";

%input = &getinput;

&error("Du må fylle ut feltet 'Intervjutittel'")
    unless length $input{'tittel'};
&error("Du må fylle ut feltet 'Kort-tittel' med bokstavene a-z, punktum ('.') eller '_'")
    if $input{'dir'} =~ /[^a-zA-Z._]/ || !length $input{'dir'};
&error("Du må fylle ut feltet 'Dato'")
    unless length $input{'dato'};

unless (-d $input{'dir'}) {
    # lag nytt dir
    mkdir($input{'dir'}, 0775) || &error("Kunne ikke lage nytt directory $input{'dir'}");
}

$input{'intro'} =~ s/[\r\n]+/ /g;

open(INFO, ">$input{'dir'}.info") || &error("Kunne ikke skrive filen '$input{'dir'}.info'");
foreach (keys %input) {
    print INFO "$_:\t$input{$_}\n";
}
print INFO "\n";	# separate headers from body
close INFO;

&header("Har registrert nytt intervju");

print <<EOT;

Dersom du har registrert gale opplysninger, kan du skrive over denne
regsitreringen ved å oppgi samme kort-tittel én gang til.<p>

Tilbake til <a href="oversikt.cgi">oversikten over alle intervjuene</a>.
EOT

&std_footer;

exit 0;









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

