#!/usr/bin/perl

# Program for å vise resultatene fra ski-vm '96

$CONFIG = '/home/steinar/frogner/NYOMP/sp/hego/ski-nm96/resultat-config.txt';

$SEPARATOR = ';';

%input = &getinput;

open(CONF, $CONFIG) || &error("Kunne ikke lese konfigurasjonsfilen $CONFIG");
while (<CONF>) {
    ($kode, $resfil, $header, $footer) = split(/;/);
    last if $kode eq $input{renn};
}
close CONF;

&error("Ukjent rennkode") if $kode ne $input{renn};

open(RESULTAT, $resfil) || &error("Kunne ikke lese resultatfilen $resfil");
while (<RESULTAT>) {
    chop;
#    s/^\s*;\s*//; # alle linjer begynner med et semikolon (feil i dataformat)
    s/\s*:\s*$//;
    
    # Må fylle inn kolonnen med plassering dersom denne mangler fordi man ved 
    # søk kun viser treff-linjene (og da må kolonne 0 vise riktig plassering).
    # NB! Antar her at plasseringen alltid er oppgitt i kolonne null!

    @tmp = split(/$SEPARATOR/);
    $tmp[0] = $lastcol0 unless $tmp[0] =~ /\S/;
    $tmpline = join($SEPARATOR, @tmp);
    push(@resultat, $tmpline);
    $lastcol0 = $tmp[0];

    # Finner maks. lengde av hver kolonne for å kunne formattere pent
    # for klienter som ikke støtter tabeller
    @tmp = split(/$SEPARATOR/);
    next if $#tmp < 1;
    foreach $i ($[ .. $#tmp) {
	$maxlen{$i} = length $tmp[$i] if length $tmp[$i] > $maxlen{$i};
    }
}
close RESULTAT;

# $maxlen{$i} inneholder maks lengde av kolonne nr. $i, brukes
# for å formattere pent også uten tabell-støtte

print "Content-type: text/html\n\n";

open(HEADER, $header);
while (<HEADER>) {
    print;
}
close HEADER;

$h1 = shift(@resultat);
print <<EOT;
<h1>$h1</h1>

<font size="+1">
<form action="resultat.cgi" method="POST">
<input type="hidden" name="renn" value="$input{renn}">
Søk etter deltager eller klubb:
<input name="soek" size="20">
<input type="submit" value=" Søk ">
</form>
</font>
EOT
    print "Søk etter '$input{soek}' ga følgende treff:" if (length $input{name});

    print "<table><pre>";

foreach $reslinje (@resultat) {
    $colno = 0;
    next if $line && length $input{soek} && $reslinje !~ /$input{soek}/i;
    print "<tr><br>";
    foreach $kolonne (split(/$SEPARATOR/, $reslinje)) {
	$pre = $post = "";
	if ($line == 0) {
	    $pre = qq!<b><font size="+1">!;
	    $post = qq!</font></b>!;
	}
	if ($kolonne =~ /^[\d,.\s]+$/) {
	    printf qq!<td align="right">$pre%$maxlen{$colno++}s$post </td>!, $kolonne;
	} else {
	    printf "<td>$pre%-$maxlen{$colno++}s$post </td>", $kolonne;
	}
    }
    $line++;
}
print qq!<tr><br><td><font size="+1">Ingen treff for søkeuttrykket '$input{soek}'</font></td>!
    if $line == 1 && length $input{soek};
print "</pre></table>\n";


open(FOOTER, $footer);
while (<FOOTER>) {
    print;
}
close FOOTER;
exit 0;





sub getinput {
# Return %input array, associating input names with input values
# Also builds global array @datanames, giving original order of input
# field names.
    local($i, $name, $value, $data, @data, %input);

    if ($ENV{'REQUEST_METHOD'} eq "GET") {
        $data = $ENV{'QUERY_STRING'};
    } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
        while (read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'})) {
	    $data .= $buffer;
	}
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
        push(@datanames, $name);
        $input{$name} = $value;
    }
    %input;                     # returnerer den assosiative array'en
}

sub error {
# returns HTML error message and exits program
    local($msg) = $_[0];

    print "Content-type: text/html\n\n";
    print "<h1>$msg</h1>";

    exit 1;
}

