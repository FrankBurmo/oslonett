#!/local/bin/perl
# Script for å gjøre oppdateringer i FONO tittelbasen
#


require "../lib/tittellib.pl";


%input = &getinput; # returnerer data i (den globale) %input (key=feltnavn)

&assert if ($input{'Knapp'} =~ /^Oppdater/i);

&update;   # Gjør oppdatering eller sletting i databasen

exit 0;




sub assert {
# Sjekker om det finnes felter ut over de som er angitt i @fields og 
# keys(%skip), skriver i så fall en linje i feil-loggen.

    return;


    %dummy = %input;
    foreach $f ( @fields, keys %skip ) {
	undef ($dummy{$f});
    }

    while ( ($key, $val) = each %dummy )  {
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
	&printheader("Oppdatering av titteldata: for få felter utfylt");
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




sub update {

# Anvender flock(2) på datafilen

    local($record);

# Må ikke blokkere uendelig hvis filen ved en feil er låst permanent
    $SIG{'ALRM'} = 'handletimeout';
    alarm($timeout);

    open(FILE, "+<$datafile");
    flock(FILE, $LOCK_EX);

# Datafilen er nå låst, kan oppdatere trygt
    $SIG{'ALRM'} = 'IGNORE';

    system("cp $datafile $datafile.bak"); # Lag backup for sikkerhets skyld

    $kundeindeks = -1;
    while ( <FILE> ) {
	chop;
	push(@kunder, $_);
	$kundeindeks = $#kunder
	    if ( (split($fieldsep, $_))[0] == $input{'Tittelnr'});
    }
    $kundeindeks = @kunder if $kundeindeks == -1;

# Hvis ønsket kundenummer finnes i databasen, er $kundeindeks indeksen til
# denne posten. Hvis ikke er $kundeindeks lik høyeste brukte indeks + 1,
# slik at gjenopprettet post kan settes inn i posisjon $kundeindeks

    if ( $input{'Knapp'} =~ /^Slett/ ) {
	if ($kundeindeks == @kunder) {
	    &printheader("Ikke-eksisterende tittelnummer");
	    print <<EOT;
Tittelnummeret ($input{'Medlemsnr'}) som ønskes slettet
eksisterer ikke i databasen (allerede slettet?).<p>

 Eventuelle spørsmål kan rettes til <a href="mailto:$mailadr">$mailadr</a>.

EOT
            &printfooter;
            exit 0;
        }

	splice(@kunder, $kundeindeks, 1); # Ta ut aktuell kunde av array'en
	&printheader("Tilbakemelding: har slettet titteldata");
	print <<EOT;
Data om "$input{'Tittel'}" (medlem nr $input{'Tittelnr'}) er nå slettet fra
medlemsdatabasen. <p>

Dersom tittelen ble slettet ved et uhell, kan data gjenopprettes ved å
gå tilbake til skjemaet og velge "Send inn skjemaet" eller "Oppdater
databasen".
EOT

    } else {


	@old = split($fieldsep, $kunder[$kundeindeks]);
	for ( @fields ) { 
	    $old{$_} = shift(@old);
	}
        $input{'EndreDato'} = $old{'EndreDato'};

	$newrecord = '';

	for $f ( @fields ) {
	    push(@lines, sprintf("  <dt> <b>%s</b>\n  <dd> %s\n",
				 $fieldname{$f}, $input{$f}||"[ikke oppgitt]"))
		if ($input{$f} ne $old{$f});
            $input{'EndreDato'} = &dato if $f eq 'EndreDato';
	    $newrecord .= $input{$f} . $fieldsep;
	}
	chop($newrecord);	# Fjern siste forekomst av $fieldsep

	if (@lines) {
            $kunder[$kundeindeks] = $newrecord;
	    &printheader("Tilbakemelding: har oppdatert titteldata");
	    if ($kundeindeks == @kunder) {
		print <<EOT;
<blockquote>
<hr noshade size=2>
Data om denne tittelen er tidligere slettet men blir nå gjenopprettet.
<hr noshade size=2>
</blockquote>';
EOT
            }

	    print <<EOT;
Følgende nye data er lagt inn for tittelen "$input{'Tittel'}" (medlemsnr. $input{'Tittelnr'}):<p>
<dl>
@lines
</dl>
EOT
	} else {
	    &printheader("Tilbakemelding: ingen nye data oppgitt");
	    print "Ingen nye data er lagret for tittelen ";
	    print "\"$input{'Tittel'}\" (tittelnr. $input{'Tittelnr'})<p>\n";
	}
    }
    &printfooter;

# @kunder har her 1) fått fjernet, 2) fått oppdatert eller 3) ikke endret
# posten med ønsket kundenummer. Kan dermed skrive hele @kunder tilbake.

    truncate(FILE, 0);		# Skal skrive over gamle data
    seek(FILE, 0,0);		

    $" = "\n";
    print FILE "@kunder\n";	# Skriv ut alle kundene til fil

    flock(FILE, $LOCK_UN);	# Frigir datafilen igjen
    close(FILE);
}





