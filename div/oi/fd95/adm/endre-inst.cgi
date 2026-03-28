#!/local/bin/perl

# CGI-script for å oppdatere informasjon lagret om en institusjon
# Programmet tar registreringsnummer som parameter og returnerer FORM
# med forhåndsutfylte felter for den ønskede institusjonen. Endringer
# kan så utføres og registreres på ny.

require "fd-lib.pl";

$reginst = "$basedir/adm/reg-inst.html";

print "Content-type: text/html\n\n";

%input = &getinput;

&error("For oppdatering av data må registreringsnummeret oppgis")
    unless $input{'Regnr'};

$instfile =  sprintf("%s/inst%04d.html.updateinfo", $instdir, $input{'Regnr'});

&error("Finner ingen registrering med dette nummeret ($input{'Regnr'})")
    unless -r $instfile;

open(INST, $instfile)
    || &error("Kan ikke åpne institusjonens HTML-fil ($instfil)");

$s = $fieldsep;			# pattern-match nedenfor blir ryddigere
while (<INST>) {
    if ( m/^<!--\s*replace $s([^$s]*)$s with $s([^$s]*)$s([^$s]*)$s\s*-->$/ ) {
	push(@orig, $1);
	push(@pre, $2);
	push(@post, $3);
    }
}
close(INST);

open(FORM, $reginst)
    || &error("Finner ikke HTML-filen med registreringsskjema ($reginst)");
while (<FORM>) {

    for $i ( $[ .. $#orig ) {
	s/$orig[$i]/$pre[$i]$1$post[$i]/;
    }
    s/(<input\s+type="?reset"?[^>]*>)/<input type="submit" name="Knapp" value="Slett denne fra databasen">\n$1/i;
    s/<!-- passord -->/<p><hr noshade size="1"><p>\nAdministrativt passord: <input type="password" name="Passord" size="50">/i if $input{'Admin'};
    print;
}
close(FORM);

exit 0;

