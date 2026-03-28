#!/local/bin/perl
# Script for å ta imot registrering av (mulig) ny annonsør fra HTML FORM
# KGN, 16.6.95. Sist endret: 6.7.95
#
# Oppdaterer filen angitt av $datafile med informasjon fra de innleste
# feltene. Format for datafilen er:
#  - _en_ post pr. linje
#  - felter pr. linje som angitt i @fields, adskilt med $fieldsep
#
# Bruker dessuten filen angitt av $counterfile for å lagre sist
# brukte kundenummer. Kundenummeret økes med 1 for hver registrering.
# Etter sletting vil datafilen ikke ha poster for hvert kundenummer.
# Etter gjenoppretting vil datafilen ha gjenopprettet kundenummer
# sist i filen (rekkefølgen er altså vilkårlig).
#
# Følgende feilsituasjoner logges (til filen angitt av $errlogfile):
#
# - Forekommende felter i FORM som ikke er angitt i @fields. Dette
#   indikerer skrivefeil i HTML FORM.
# - Ventetid utover $timeout sekunder for å få tilgang til datafilen.
#   (En annen prosess blokkerer datafilen ved en feil.)

require "kundelib.pl";

%input = &getinput;
# returnerer data i (den globale) %input (key=feltnavn)

&assert;   # returnerer HTML-kode og avslutter hvis for få felter er fylt ut

&register; # foretar selve registreringen i datafilen

&feedback; # returnerer HTML-kode med tilbakemelding til brukeren

exit 0;





sub assert {
# Sjekker at et minimum (angitt i @required) av felter er fylt ut
# før registrering kan foretas. Avbryter scriptet med feilmeldin
# hvis kravet ikke er tilfredsstilt.
# Sjekker om det finnes felter ut over de som er angitt i @fields og 
# keys(%skip), skriver i så fall en linje i feil-loggen.

    %inputfields = %input;
    foreach $f ( @fields, keys %skip ) {
	undef ($inputfields{$f});
    }

    while ( ($key, $val) = each %inputfields )  {
	push(@ukjent, $key) if $val;
    }

    &logerror("Ukjent(e) felt(er) fra FORM: " . join(", ", @ukjent))
	if @ukjent;
	
# Sjekker at et minimum av felter (de som er angitt i @required) er 
# utfylt, returnerer feilmelding og avslutter hvis >= 1 felt mangler.
    local($i, @mangler);

    for $i ( @required ) {
	push(@mangler, $i) if ( $input{$i} !~ /\S/ );
    }

    if ( @mangler ) {
	$" = "\n <li> ";	# La print lage <li>-entries bak kulissene
	&printheader("Kunderegistrering: for få felter utfylt");
	print <<EOT;
Følgende felter mangler og må være utfylt:

<hr noshade size=1>
<ul>
<li> @mangler
</ul>
<hr noshade size=1>
Registreringen er ikke utført, gå tilbake og fullfør utfyllingen.
EOT
        &printfooter;

        exit 1;
    }
}



sub register {
# Anvender flock(2) på datafilen, registrerer dataene inneholdt
# i %input i filen og frigir datafilen igjen. 

    local($record);

# Må ikke blokkere uendelig hvis filen ved en feil er låst permanent
    $SIG{'ALRM'} = 'handletimeout';
    alarm($timeout);

    open(FILE, ">>$datafile");
    flock(FILE, $LOCK_EX);
    seek(FILE, 0, 2);	# I tilfelle andre har skrevet mens vi har ventet

# Datafilen er nå låst, kan oppdatere trygt
    $SIG{'ALRM'} = 'IGNORE';
    open(COUNTER, "+<$counterfile");
    $counter = <COUNTER> || 0;	# Leser inn sist brukte kundenummer
    $input{'Kundenr'} = ++$counter;
    $input{'RegDato'} = &dato;
    $input{'EndreDato'} = &dato;
    $record = '';
    for $f ( @fields ) {
	$record .= $input{$f} . $fieldsep;
    }
    chop($record);		# Kast siste forekomst av $fieldsep
    print FILE "$record\n";

    seek(COUNTER, 0, 0);	# Ønsker å skrive over gammelt nummer
    print COUNTER $counter;	# Skriver tilbake kundenummeret
    close COUNTER;

    flock(FILE, $LOCK_UN);	# Frigir datafilen igjen
    close(FILE);
}



sub feedback {
# Returnerer HTML-kode med tilbakemelding om at alt gikk bra
    local($i);

    &printheader("Kunderegistrering: tilbakemelding");

    print "Vi har registrert følgende informasjon om denne kunden:\n";
    print "<hr noshade size=1>\n<dl>\n";

    for $f ( @fields ) {
	printf "  <dt> <b>%s</b>\n  <dd> %s\n",
	$fieldname{$f}, $input{$f}||"[ikke oppgitt]";
    }
    print <<EOT;
</dl>

<p>
<hr noshade size=1>
<p>

Dersom dataene ovenfor skulle være feil kan du slette denne
registreringen, gå tilbake til skjemaet, rette opp feilen(e)
og gjøre en ny registrering.
<form method="POST" action="$endrescript">
<input type="hidden" name="Kundenr" value="$counter">
<input type="hidden" name="Firma" value="$input{'Firma'}">
<input type="submit" name="Knapp" value="Slett denne kunden">
</form>

EOT
    &printfooter;
}



