#!/local/bin/perl
#
# CGI-script for å registrere nytt arrangement. Lager html-fil under
# directory'et data/ og legger til en ny linje i filen arr-index.txt

require "fd-lib.pl";

%fieldname = ("Arrangement", "Arrangementets tittel",
	      "Beskrivelse", "Kort beskrivelse av arrangementet",
	      "Sted", "Sted",
	      "Dato", "Dato",
	      "Klokkeslett", "Klokkeslett",
	      "Institusjon", "Arrangør-institusjon",
	      "Kontakt", "Kontaktperson for påmelding",
	      "Pris", "Pris",
	      "Maalgruppe", "Målgruppe(r)",
	      "Fylke", "Fylke",
	      "Beliggenhet", "Beliggenhet" );	       

@required = ("Arrangement", "Sted", "Dato", "Institusjon",
	     "Beskrivelse");

@inputtags = ("Nummer", "Arrangement", "Sted", "Klokkeslett", "Kontakt",
	      "Pris","Maalgruppe", "Instnummer", "Institusjon", "Beliggenhet");
@textareas = ("Beskrivelse");


eval '&doit';		# Bruker eval for å trap'e evt. runtime feil
&error("$@") if $@;
exit 0;



sub doit {

    print "Content-type: text/html\n\n";

    %input = &getinput;		# %input er fra nå av en global variabel
    $input{'Dato'} = join($datosep, sort(split($datosep, $input{'Dato'})));

    %input = &instlookup(%input);

    &assert(%input);
    &register;
    exit 0;
}



sub instlookup {
    local (%input) = @_;
    local (%entry, @matches);

    return %input unless $input{'Institusjon'} || $input{'Instnummer'};

    open(FILE, "$instindeks")
	|| &error("Kunne ikke åpne indeksfilen ($instindeks)");
    while (<FILE>) {
	@entry{@instfields} = split($fieldsep);
	push(@matches, $_)
	    if ( ($entry{'Nummer'} == $input{'Instnummer'})
		|| (!$input{'Instnummer'}
		    && $entry{'Institusjon'} =~ /$input{'Institusjon'}/i) );
    }
    close(FILE);

    if (! @matches ) {
	print &header("Tilbakemelding: Oppgitt arrangør-institusjon er ikke registrert");
	print <<EOT;

Den medsendte angivelsen av institusjonsnavn/-nummer passer ikke med
noen av de registrerte institusjonene. P.g.a. at hvert arrangement
skal ha en kryssreferanse til arrangør-institusjonen må institusjonen
være registrert på forhånd. <p>

Hvis institusjonen ikke er registrert må det først gjøres. Bruk <a
href="reg-inst.html">registreringsskjemaet for nye
deltakerinstitusjoner</a> og gå deretter tilbake til skjemaet for
registrering av arrangementer.<p>

Dersom institusjonen allerede er regsitrert kan det være en skrivefeil
i det innleste institusjonsnavnet. Se på <a
href="$baseurl/finn-inst.cgi?Institusjon=.*">listen over registrerte
institusjoner</a> og gå tilbake til skjemaet og rett evt. skrivefeil.
EOT
        print &footer;
	exit 0;
    } elsif ( @matches > 1 ) {
	print &header("Tilbakemelding: Oppgitt annonsørnavn er ikke unikt");
	print <<EOT;

Den medsendte angivelsen av institusjonsnavn er ikke entydig. P.g.a.
at hvert arrangement skal ha en kryssreferanse til
arrangør-institusjonen må institusjonen være registrert på forhånd.<p>

Følgende deltakerinstitusjoner passer med det angitte navnet:
<ul>
EOT
        for (@matches) {
	    @entry{@instfields} = split($fieldsep);
	    print " <li> $entry{'Institusjon'}, registreringsnummer: $entry{'Nummer'}\n";
	}

	print <<EOT;

</ul>
Gjør derfor angivelsen mer spesifikk, f.eks. ved å fylle inn
registreringsnummeret i tillegg eller i stedet for institusjonsnavnet.<p>

EOT
        print &footer;
	exit 0;
    }
    @entry{@instfields} = split($fieldsep, pop(@matches));
    $input{'Institusjon'} = $entry{'Institusjon'};
    $input{'Instnummer'} = $entry{'Nummer'};
    %input;
}



sub assert {
    local(%input) = @_;
    local(@mangler);

    foreach (@required) {
	push(@mangler, $fieldname{$_}) unless $input{$_};
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
    local(%entry, @f, $teller);

    unless ($input{'Nummer'}) {
# Hvis ikke nummer er spesifisert skal vi gjøre en ny-registrering.
# Leser da inn sist brukte nummer, øker med 1, og skriver tilbake nytt nr.

	$SIG{'ALRM'} = 'handletimeout'; # Må ikke blokkere uendelig hvis
	alarm($timeout);	    # filen ved en feil er låst permanent

	open(TELLER, "+<$arrteller") || open(TELLER, ">$arrteller") 
	    || &error("Kunne ikke åpne tellerfilen ($arrteller)");
	flock(TELLER, $LOCK_EX);
	$SIG{'ALRM'} = 'IGNORE';	# Kan nå lese og oppdatere trygt
	$teller = <TELLER> || 0;  # Leser inn sist brukte registreringsnummer
	seek(TELLER, 0, 0);
	print TELLER ++$teller, "\n";

	flock(TELLER, $LOCK_UN);      # Frigir datafilen igjen
	close(TELLER);
	$input{'Nummer'} = $teller;   # Lagre reg.-telleren i global variabel
    }

    $SIG{'ALRM'} = 'handletimeout'; # Må ikke blokkere uendelig hvis
    alarm($timeout);                # filen ved en feil er låst permanent

    system("cp $arrindeks $arrindeks.bak");
    open(INDEX, "+<$arrindeks") || open(INDEX, ">$arrindeks")
        || &error("Kunne ikke åpne indeks-filen ($arrindeks)");
    flock(INDEX, $LOCK_EX);
    $SIG{'ALRM'} = 'IGNORE';    # Kan nå lese og oppdatere trygt

    while(<INDEX>) {            # Leser inn gamle data i assosiativ array
        chop;
        @f{@arrfields} = split($fieldsep);
        $entry{$f{'Nummer'}} = $_;
    }

    if ( $entry{$input{'Nummer'}} ) {
        # Ønsker å gjøre oppdatering el. sletting for eksisterende arrangement
        @f{@arrfields} = split($fieldsep, $entry{$input{'Nummer'}});
        &unauthorized($input{'Arrangement'}, $f{'Maskin'})
            if ($f{'Maskin'} ne $ENV{'REMOTE_HOST'} &&
		$f{'Maskin'} ne $ENV{'REMOTE_ADDR'} &&
		crypt($input{'Passord'}, $masterpw) ne $masterpw);
    } else {
        # Gir feilmelding dersom man forsøker å slette ikke-eks. inst.
        &notfound if ( $input{'Knapp'} =~ /^slett/i );
    }

    if ($input{'Knapp'} =~ /^slett/i) {
        delete($entry{$input{'Nummer'}});

	$filename = sprintf("%s/arr%04d.html", $arrdir, $input{'Nummer'});
	unlink($filename);
	rename("$filename.updateinfo", "$filename.backup");

        print &header("Arrangementet er slettet fra databasen");
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
        $entry{$input{'Nummer'}} = join($fieldsep, @input{@arrfields});
        &writehtmlfile(%input) || &error("Kunne ikke lage ny HTML-fil");
        &regfeedback;
	print &footer;
    }

    truncate(INDEX, 0);         # Skal skrive over gamle data
    seek(INDEX, 0, 0);
    print INDEX join("\n", values %entry); # Skriv data tilbake igjen
    print INDEX "\n" if (scalar values %entry);
    flock(INDEX, $LOCK_UN);     # Frigir datafilen igjen
    close(INDEX);
}



sub writehtmlfile {
# Skriver nå ut en HTML-fil under navnet $arrdir. Navnet er
# "arr<$input{'Nummer'}>.html. Returverdi: 0=kunne ikke lage fil, 1=OK
    local(%input) = @_;
    local($field, $nummer, $filnavn);

# Skriver nå ut en ny HTML-fil under $arrdir.
# Navnet er "arr<$input{'Nummer'}>.html"

    $filnavn = sprintf("$arrdir/arr%04d.html",$input{'Nummer'});

    open(FILE, ">$filnavn") || return undef;
    print FILE &header($input{'Arrangement'});

    $nummer = sprintf("%04d", $input{'Instnummer'});
    print FILE <<EOT;

<dl>	

  <dt> <b>Arramngementets tittel:</b>
  <dd> $input{'Arrangement'}

  <dt> <b>Nærmere beskrivelse av arrangementet:</b>
  <dd> $input{'Beskrivelse'}

  <dt> <b>Sted:</b>
  <dd> $input{'Sted'}

  <dt> <b>Dato:</b>
  <dd> $input{'Dato'}

  <dt> <b>Klokkeslett:</b>
  <dd> $input{'Klokkeslett'}

  <dt> <b>Arrangør:</b>
  <dd> <a href="$insturl/inst$nummer.html">$input{'Institusjon'}</a>
EOT
    print FILE "  <dt> <b>Målgruppe:</b>\n      <dd> $input{'Maalgruppe'}\n"
	if $input{'Maalgruppe'};
    print FILE "  <dt> <b>Påmelding:</b>\n      <dd> $input{'Kontakt'}\n"
	if $input{'Kontakt'};
    print FILE "  <dt> <b>Pris:</b>\n      <dd> $input{'Pris'}\n"
	if $input{'Pris'};
    print FILE "  <dt> <b>Fylke:</b>\n      <dd> $input{'Fylke'}\n";
    print FILE "  <dt> <b>Beliggenhet:</b>\n      <dd> $input{'Beliggenhet'}\n"
	  if $input{'Beliggenhet'};
    print FILE "</dl>\n";
    print FILE &footer;
    close FILE;

# Skriver så ut felter for å forenkle forhåndsutfylling ved evt. oppdatering

    open(REP, ">$filnavn.updateinfo") || return undef;

    print REP <<EOT;
<!-- Linjene nedenfor er automatisk generert av $0 og brukes dersom  -->
<!-- det skal gjøres oppdateringer. LINJENE SKAL IKKE ENDRES MANUELT -->
EOT

    for $field (@inputtags) {
	print REP
	    qq,<!-- replace $fieldsep(name\\s*=\\s*"?$field"?)$fieldsep with $fieldsep$fieldsep value="$input{$field}"$fieldsep -->\n,;
    }

    for $field (@textareas) {
	print REP qq,<!-- replace $fieldsep(name\\s*=\\s*"?$field"?\\s*[^>]*>)$fieldsep with $fieldsep$fieldsep$input{$field}$fieldsep -->\n,;
    }

    print REP
	qq,<!-- replace $fieldsep<option(.*$input{'Fylke'})$fieldsep with $fieldsep<option selected$fieldsep$fieldsep -->\n,;

    for $date ( split($datosep, $input{'Dato'}) ) {
	print REP
	    qq,<!-- replace $fieldsep(name\\s*=\\s*"?Dato"?\\s+value\\s*=\\s*"?$date"?)\\s*>$fieldsep with $fieldsep$fieldsep checked>$fieldsep -->\n,;
    }
    close REP;

    return 1;			# returverdi som angir OK
}



sub regfeedback {
    local($nyurl);

    $nyurl = sprintf("$arrurl/arr%04d.html", $input{'Nummer'});
    print &header("Registrering av arrangement: tilbakemelding");
$neste = $input{'Nummer'}+1;
    print <<EOT;

"$input{'Arrangement'}" er nå registrert som
ett av arrangementene under Forskningsdagene '95.
<p>

De innsendte dataene er lagret i en egen <a href="$nyurl"> HTML-side
for arrangementet</a>. <p>

<h2>NB!</h2>

 Dersom det skulle bli behov for å gjøre endringer må man oppgi
 registreringsnummeret. De registrerte dataene kan kun endres fra
 samme maskin som de nå er lagt inn fra (for å redusere mulighetene
 for uautoriserte oppdateringer i databasen).

<blockquote>
 <h1>Registreringsnummeret er $input{'Nummer'}</h1>
 <h3>Ta vare på dette nummeret for evt. senere oppdateringer!</h3>
</blockquote>

Registreringen er gjort fra maskinen $ENV{'REMOTE_HOST'}.
<p>
EOT


}



sub notfound {
    print &header("Kan ikke slette uregistrert arranement");
    print <<EOT;

Det er ikke registrert noe arrangement med registreringsnummer
$input{'Nummer'}. Det er derfor ikke aktuelt å gjøre noen
slette-operasjon.
EOT

    print &footer;
    exit 1;
}


sub unauthorized {
    local($arr,$maskin) = @_;

    print &header("Ikke autorisert til å gjøre oppdatering");
    print <<EOT;
Du har ikke anledning til å oppdatere eller slette data for
"$arr". Oppdateringer kan kun gjøres fra den maskinen
    dataene opprinnelig ble registrert fra ($maskin). 
Din maskins navn/adresse: $ENV{'REMOTE_HOST'}/$ENV{'REMOTE_ADDR'}.
EOT
    print &footer;
    exit 1;
}

