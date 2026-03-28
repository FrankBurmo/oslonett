#!/local/bin/perl5

$ANNDB    = "/local/etc/www/internsoek/log.txt";

%input = &getinput;

open (DB, ">> $ANNDB") || die "Kan ikke åpne annonsør DB\n";

$tim = time;

printf (DB "%s %% %s %% %s %% %s %% %s %% %s %% %ld\n", $input{URL}, $input{TITTEL}, $input{INGRESS}, $input{IKONURL}, $input{KNR}, $input{FURL}, $tim);

close (DB);

print<<EOT;
Content-type: text/html

<html>
<head>
 <title>OK</title>
</head>
<body bgcolor="#ffffff">
<h1>$input{TITTEL}: OK</h1>

Veiviseren er nå oppdatert med en ny annonsør. <a href="http://www.sn.no/innhold/soek.cgi?alfabetisk=a-zæøåÆØÅ&tokolonner=ja">Sjekk selv!</a>
</body>
</html>

EOT

sub getinput {
# Return %input array, associating input names with input values
# Also builds global array @datanames, giving original order of input
# field names.
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

        $value =~ s/\s+/ /g;
        $input{$name} = $value;
    }
    %input;                     # returnerer den assosiative array'en
}





