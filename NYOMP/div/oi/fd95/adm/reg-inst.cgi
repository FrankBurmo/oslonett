#!/local/bin/perl
#
# CGI-script for å registrere ny institusjon. Lager html-fil under
# directory'et data/ og legger til en ny linje i filen inst-index.txt

require "fd-lib.pl";

@fields = ("Nummer", "Institusjon", "Kategori", "Maskin");
@required = ("Institusjon", "Beskrivelse", "Kategori" );

@inputtags = ("Nummer", "Institusjon", "LogoURL", "ServerURL", "Altkategori");
@textareatags = ("Beskrivelse", "Deltagelse");
$annenkat = "Angitt nedenfor";	# Teksten som brukes for "annen kategori"

eval '&doit';		# bruker eval for å trap'e evt. runtime feil
&error("$@") if $@;
exit 0;



sub doit {

    print "Content-type: text/html\n\n";

    %input = &getinput;		# %input er fra nå av en global variabel

    $input{'Kategori'} = $input{'Kategori'} || $input{'Altkategori'};
    &assert;
    &register;
    exit 0;
}




sub assert {
    local(@mangler);

    foreach (@required) {
	push(@mangler, $_) unless $input{$_};
    }
    return unless @mangler;
    print &header("Registrering: for få felter utfylt");
    $" = "\n <li> ";
    print <<EOT;
Følgende felter mangler og må være utfylt:
<ul>
 <li> @mangler
</ul>
Gå tilbake til skjemaet, fyll ut de nødvendige feltene og registrer igjen.
EOT
    print &footer;
    exit 1;
}




sub register {
    local($filnavn);

    if ( $input{'Knapp'} != /^slett/i 
	&& length($input{'Altkategori'})
	&& $input{'Kategori'} ne $input{'Altkategori'} ) {
	&error(qq{Både feltet "Kategori" og "Egen kategori" er fylt ut. Sistnevnte skal kun brukes når man har valg "Angitt nedenfor" i kategori-feltet.});
    }


# Hvis ikke nummer er spesifisert må vi bruke neste ledige nummer...
    unless ($input{'Nummer'}) {
	$SIG{'ALRM'} = 'handletimeout'; # Må ikke blokkere uendelig hvis
	alarm($timeout);	    # filen ved en feil er låst permanent
	open(TELLER, "+<$instteller") || open(TELLER, ">$instteller") 
	    || &error("Kunne ikke åpne tellerfilen ($instteller)");
	flock(TELLER, $LOCK_EX);
	$SIG{'ALRM'} = 'IGNORE';  # Kan nå lese og oppdatere trygt
	$teller = <TELLER> || 0;  # Leser inn sist brukte registreringsnummer
	seek(TELLER, 0, 0);
	print TELLER ++$teller, "\n";

	flock(TELLER, $LOCK_UN);      # Frigir datafilen igjen
	close(TELLER);
	$input{'Nummer'} = $teller;   # Lagre reg.-telleren i global variabel
    }

# Vi åpner så indeks-filen og leser inn data om alle institusjonene
    system("cp $instindeks $instindeks.bak"); # Ta backup for sikkerhetsskyld
    $SIG{'ALRM'} = 'handletimeout'; # Må ikke blokkere uendelig hvis
    alarm($timeout);		    # filen ved en feil er låst permanent
    open(INDEX, "+<$instindeks") || open(INDEX, ">$instindex")
	|| &error("Kunne ikke åpne indeks-filen ($instindeks)");
    flock(INDEX, $LOCK_EX);
    $SIG{'ALRM'} = 'IGNORE';	# Kan nå lese og oppdatere trygt

    while(<INDEX>) {		# Leser inn gamle data i assosiativ array
	chop;
	@f{@instfields} = split($fieldsep);
	$entry{$f{'Nummer'}} = $_;
    }

    if ( $entry{$input{'Nummer'}} ) {
	# Ønsker å gjøre oppdatering for eksisterende institusjon
	@f{@instfields} = split($fieldsep, $entry{$input{'Nummer'}});
	&unauthorized($input{'Institusjon'}, $f{'Maskin'})
	    if ($f{'Maskin'} ne $ENV{'REMOTE_HOST'} &&
		$f{'Maskin'} ne $ENV{'REMOTE_ADDR'} &&
		crypt($input{'Passord'}, $masterpw) ne $masterpw);
    } else {
	# Gir feilmelding dersom man forsøker å slette ikke-eks. inst.
	&notfound if ( $input{'Knapp'} =~ /^slett/i );
    }

    if ($input{'Knapp'} =~ /^slett/i) {
	delete($entry{$input{'Nummer'}});
	$filename = sprintf("%s/inst%04d.html", $instdir, $input{'Nummer'});
	unlink($filename);
	rename("$filename.updateinfo", "$filename.backup");
	print &header("Institusjonen er slettet fra databasen");
	print <<EOT;

Tips dersom data ble slettet ved en feiltagelse:
<blockquote>
Følgende gjelder for de fleste web-browsere, ikke nødvendigvis for
alle: Dersom man velger "Back" eller tilsvarende for å komme til
forrige dokument, vil dette ha de gamle dataene intakt. I dette
skjemaet kan man trykke "Registrer..." for å gjenopprette de slettede
dataene.
</blockquote>

EOT
	print &footer;
    } else {
	$entry{$input{'Nummer'}} = join($fieldsep, @input{@fields});
	&writehtmlfile(%input) || &error("Kunne ikke lage ny HTML-fil");
	&regfeedback;
    }

    truncate(INDEX, 0);		# Skal skrive over gamle data
    seek(INDEX, 0, 0);
    print INDEX join("\n", values %entry); # Skriv data tilbake igjen
    print INDEX "\n" if scalar(values %entry);
    flock(INDEX, $LOCK_UN);	# Frigir datafilen igjen
    close(INDEX);
}



sub writehtmlfile {
# Skriver nå ut en ny HTML-fil under $instdir. Navnet
# er "inst<$input{'Nummer'}>.html". Returverdi: 0=kunne ikke lage fil, 1=OK
    local(%input) = @_;

    $filnavn = sprintf("$instdir/inst%04d.html",$input{'Nummer'});

    open(FILE, ">$filnavn") || return undef;
    print FILE &header($input{'Institusjon'});

    print FILE qq@<img alt="[$input{'Institusjon'}]" 
	src="$input{'LogoURL'}">\n<p>\n@ if $input{'LogoURL'};

    print FILE "$input{'Beskrivelse'}\n<p>\n";

    print FILE "<h2>Om deltagelsen til $input{'Institusjon'} i FD'95</h2>
$input{'Deltagelse'}\n<p>\n" if $input{'Deltagelse'};

    print FILE qq@
<blockquote>
 <center>
 <hr noshade size=2>
   Se også <a href="$input{'ServerURL'}">egne web-sider
   for $input{'Institusjon'}</a>
 <hr noshade size=2>
 </center>
</blockquote>
@ if $input{'ServerURL'};

    $inst = $input{'Institusjon'};
    $inst =~ s/([ \+\?\%])/sprintf("%%%02x",unpack("c",$1))/ge;
    print FILE <<EOT;
<h2>Arrangementer</h2>
Prøv også å <a href="$baseurl/finn-arr.cgi?Institusjon=$inst">søke
etter arrangementer i regi av $input{'Institusjon'}</a>.</h2>
EOT
    print FILE &footer;
    close FILE;

    open(REP, ">$filnavn.updateinfo") || return undef;
    print REP <<EOT;
<!-- Linjene nedenfor er automatisk generert av $0 og brukes dersom  -->
<!-- det skal gjøres oppdateringer. LINJENE SKAL IKKE ENDRES MANUELT -->

EOT
    for $field (@inputtags) {
	$value = $input{$field};
	print REP 
	    qq,<!-- replace $fieldsep(name\\s*=\\s*"?$field"?)$fieldsep with $fieldsep$fieldsep value="$input{$field}"$fieldsep -->\n,;
    }

    for $field (@textareatags) {
	$value = $input{$field};
	print REP qq,<!-- replace $fieldsep(name\\s*=\\s*"?$field"?\\s*[^>]*>)$fieldsep with $fieldsep$fieldsep$input{$field}$fieldsep -->\n,;
    }

    $input{'Kategori'} = $annenkat
	if $input{'Kategori'} eq $input{'Altkategori'};
    print REP
	qq,<!-- replace $fieldsep<option(.*$input{'Kategori'})$fieldsep with $fieldsep<option selected$fieldsep$fieldsep -->\n,;

    close REP;
    return 1;			# Returverdi OK
}




sub regfeedback {
    local($nyurl);

    $nyurl = sprintf("$insturl/inst%04d.html", $input{'Nummer'});
    print &header("Registrering av institusjon: tilbakemelding");
    print <<EOT;

"$input{'Institusjon'}" er nå registrert som
deltakerinstitusjon i Forskningsdagene '95.
<p>

De innsendte dataene er lagret i en egen <a href="$nyurl">
HTML-side for $input{'Institusjon'}</a>. <p>

<h2>NB!</h2>

 Dersom det skulle bli behov for å gjøre endringer må man oppgi
 registreringsnummeret. De registrerte dataene kan kun endres fra
 samme maskin som de nå er lagt inn fra (for å redusere mulighetene
 for uautoriserte oppdateringer i databasen).

<blockquote>
<center>
 <h1>Registreringsnummeret er $input{'Nummer'}</h1>
 <h3>Ta vare på dette nummeret for evt. senere oppdateringer!</h3>
</center>
</blockquote>

Registreringen er gjort fra $ENV{'REMOTE_HOST'}.

EOT
    print &footer;
}




sub unauthorized {
    local($inst,$maskin) = @_;

    print &header("Ikke autorisert til å gjøre oppdatering");
    print <<EOT;
Du har ikke anledning til å oppdatere eller slette data for
"$inst". Oppdateringer kan kun gjøres fra den maskinen
dataene opprinnelig ble registrert fra ($maskin).
EOT
    print &footer;
    exit 1;
}



sub notfound {
    print &header("Kan ikke slette uregistrert institusjon");
    print <<EOT;

Det er ikke registrert noen institusjon med registreringsnummer
$input{'Nummer'}. Det er derfor ikke aktuelt å gjøre noen
slette-operasjon.
EOT

    print &footer;
    exit 1;
}

