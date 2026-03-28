#!/local/bin/perl
# Lite skript for å finne neste/forrige side for en gitt Aftenposten-side.
# Scriptet kalles med URL ref.cgi/sidenummer/retning, der sidenummer er
# tre siffer og retning er "neste", "forrige", "next" eller "prev". 
# Eksempler: 
# 		ref.cgi/131/forrige
#		ref.cgi/110/neste
# Scriptet gjør "location:" til riktig side, nemlig den som numerisk kommer
# før/etter angitt side. Hvis neste/forrige side ikke finnes returneres 
# den siden man kom fra. Hvis denne ikke finnes, returneres siden 110.html.
# KGN, 30.9.95

# Kommenter bort neste to linjer for å bruke relativ adressering
$newsdir = "/home/frogner/www/me/ts/aft/nyheter";
$newsurl = "$ENV{'SERVER_URL'}/aftenposten/nyheter";

$DEFAULTPAGE = "110.html";

$page = $1 if $ENV{'PATH_INFO'} =~ s%^/(\d+)%%;
$dir = $1 if $ENV{'PATH_INFO'} =~ s%^/(\w+)%%;

# Velg $DEFAULTPAGE hvis sidenr. mangler
&gotopage($DEFAULTPAGE) unless defined $page;

$page .= ".html";

opendir(DIR, $newsdir) || &gotopage($page);
@files = sort readdir(DIR);
closedir(DIR);

# Må legge til et (tomt) filnavn for at siste navn skal kunne flyttes
# inn i $back1.
push(@files, "");

# Gjør lineært søk i @files for å finne plassering til $page i @files.
# $page trenger ikke være et eksisterende element i @files.
# Variablene $back0, $back1 og $back2 peker på de tre sist utleste 
# elementene. $back1 sammnelignes med ønsket side og man finner neste/
# forrige ved å se på $back2 og $back0 (evt. $back1 hvis $page ikke
# finnes i @files).
foreach (@files) {
    $back0 = $_;
    next unless $back0 =~ /^\d{3}\.html?$/i || $back0 eq "";
    if ($back1 ge $page) {	# Har funnet plassering til $page i @files
	if ($dir =~ /^prev|^forrige/i) {
	    $newpage = $back2;
	} elsif ($dir =~ /^next|^neste/i) {
	    $newpage = ( $back1 eq $page ) ? $back0 : $back1 ;
        }
	last;
    }
    $back2 = $back1;
    $back1 = $back0;
}

&gotopage($newpage) if length $newpage;

&gotopage($page) if $page eq $back1;

&gotopage($DEFAULTPAGE);

exit 0;


sub gotopage {
    # Gjør "Location:" til angitt side.
    local($pg) = $_[0];

    print "Location: $newsurl/$pg\n\n";
    exit 0;
}
