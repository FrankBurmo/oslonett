#!/local/bin/perl5

$dir   = "/local/www/marked/eiendom";

print "Content-type: text/html

";

chdir $dir or die "Can't chdir: $!";

form() unless $ENV{QUERY_STRING};

# Split the query string
for (split(/&/, $ENV{QUERY_STRING})) {
	($name, $val) = split(/=/, $_);
        $val =~ s/\+/ /g;
        $val =~ s/%([\da-f][\da-f])/pack("C",hex($1))/gei;
	next unless length $val;
	$query{$name} = $val;
	if ($name eq "type") {
	    $ok_type{$val} = 1;
	}
	if ($name eq "eierform") {
	    $ok_eierform{$val} = 1;
	}
}
print "<html><head><title>Resultat av søk</title></head><body bgcolor=ffffff>";
print "<h1>Søkeresultat</h1>\n\n";

open(DB, "DB") or die "Can't open DB: $!\n";

print "<table border>\n";
print "<tr><th>Tittel<th>Type<th>Eierform<th>m²<th>Rom<th>Pris</tr>\n";
$count = 0;
while (<DB>) {
    ($url,$type,$eierform,$size,$rooms,$price, $title) = split(/:/, $_);
    $price =~ s/[ \.]//g;
    if (defined %ok_type) {
	next unless $ok_type{$type};
    }
    if (defined %ok_eierform) {
	next unless $ok_eierform{$eierform};
    }
    if (defined $query{"price-max"}) {
	next if $price > $query{"price-max"};
    }
    if (defined $query{"price-min"}) {
	next if $price < $query{"price-min"};
    }

    $count++;
    print qq{<tr><tr><td><a href="$url">$title</a><td>$type<td>$eierform<td>$size<td>$rooms<td>$price</tr>\n};
}
print "</table>\n";
print "<p>$count treff\n";
print "</body></html>";


sub form
{
    print "<html><title>Søkeside</title><body bgcolor=ffffff>
<h1>Søk blandt annonserte eiendommer</h1>\n";
    if (open(DB, "DB")) {
	my %seen_type;
	my %seen_eierform;
	while (<DB>) {
	    my($url,$type,$eierform) = split(/:/, $_);
	    $seen_type{$type}++;
	    $seen_eierform{$eierform}++;
	}
	close(DB);

	# Make the form
	print <<"EOT";

Her kan du søke ut de eiendomene du har interesse for. Fyll ut
søkekriteriene nedenfor. Du kan også registrere en epost adresse.
Denne adressen vil motta salgsoppgaver etterhvert som eiendommer som
oppfyller søkekriteriene registreres.

EOT
	print qq{<form action="$ENV{SCRIPT_NAME}" method="GET">\n};
	print "<table>\n";
	print "<tr><td><b>Område:</b></td><td><input name=area size=20>
<select name=area>
<option> [ Velg her ]
<option> Oslo
<option> - Oslo vest
<option> - Oslo øst
<option> - Oslo nord
<option> - Sentrum
<option> - Gamlebyen
<option> - Vidern
<option> - Groruddalen
<option> Bergen
<option> Trondheim
<option> Tromsø
</select>
</td></tr>\n";
	range("Pris", "price", 7);
	range("Boareal", "size", undef, "m²");
	range("Antall rom", "rooms");
	if (keys %seen_type > 1) {
	    print "<tr><td><b>Boligtype:</b></td><td>\n";
	    foreach (sort keys %seen_type) {
		print qq{ <input type=checkbox name=type value="$_"> $_\n};
	    }
	    print "</td></tr>\n";
	}
	if (keys %seen_eierform > 1) {
	    print "<tr><td><b>Eierform:</b></td><td>\n";
	    foreach (sort keys %seen_eierform) {
		print qq{ <input type=checkbox name=eierform value="$_"> $_\n};
	    }
	    print "</td></tr>\n";
	}
	print "</table>\n\n";
	
	print qq{<p><input type=submit value="Søk...">\n};


	print qq{<p><b>Epost:</b> <input name=email>\n};

	print "</form></body></html>\n";


    } else {
	print "No database to search in\n";
    }
    exit 0;
}

sub range
{
    my($prompt, $type, $size, $unit) = @_;
    $size = 3 unless $size;
    print qq{<tr><td><b>$prompt:</b><td><input name=$type-min size=$size> - <input name=$type-max size=$size> $unit</tr>\n};
}
