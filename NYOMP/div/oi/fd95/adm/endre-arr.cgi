#!/local/bin/perl

# CGI-script for å oppdatere informasjon lagret om et arrangement.
# Programmet tar registreringsnummer som parameter og returnerer FORM
# med forhåndsutfylte felter for det ønskede arrangementet. Endringer 
# kan så utføres og registreres på ny.

require "fd-lib.pl";

$regarr = "$basedir/adm/reg-arr.html";

print "Content-type: text/html\n\n";

%input = &getinput;

&error("For oppdatering av data må registreringsnummeret oppgis")
    unless $input{'Regnr'};

$arrfile =  sprintf("%s/arr%04d.html.updateinfo", $arrdir, $input{'Regnr'});

&error("Finner ingen registrering med dette nummeret ($input{'Regnr'})")
    unless -r $arrfile;

open(ARR, $arrfile)
    || &error("Kan ikke åpne arrangementets HTML-fil ($instfil)");
while (<ARR>) {
    if ( m/^<!--\s*replace $fieldsep([^$fieldsep]*)$fieldsep with $fieldsep([^$fieldsep]*)$fieldsep([^$fieldsep]*)$fieldsep\s*-->$/ ) {
	push(@orig, $1);
	push(@pre, $2);
	push(@post, $3);
    }
}
close(ARR);

open(FORM, $regarr)
    || &error("Finner ikke HTML-filen med registreringsskjema ($regarr)");
while (<FORM>) {
    for $i ( $[ .. $#orig ) {
	s/$orig[$i]/$pre[$i]$1$post[$i]/gi;
    }
    s/(<input\s+type="?reset"?)/<input type="submit" name="Knapp" value="Slett denne fra databasen">\n$1/i;
    s/<!-- passord -->/<p><hr noshade size="1"><p>\nAdministrativt passord: <input type="password" name="Passord" size="50">/i if $input{'Admin'};
    print;
}
close(FORM);

exit 0;

