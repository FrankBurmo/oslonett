#!/local/bin/perl5

# programmet finner forrige eller neste artikkel, kalles med to argumenter:
# artikkelens fil-navn og "forrige" eller "neste":
# Eksempel:
#
#	ref.cgi/960208-01.html/neste
#	ref.cgi/960208-01.html/forrige
#
# Programmet gjør 'location:' til riktig side (neste/forrige i rekken)
# kgn, 8.2.96

$basedir = '/local/www/newsdesk/html';
$url = 'http://www.sn.no/newsdesk/html';

$DEFAULTPAGE = "index.html";

$page = $1 if $ENV{'PATH_INFO'} =~ s%^/(\d+-\d+.html)%%;
$dir = $1 if $ENV{'PATH_INFO'} =~ s%^/(\w+)%%;

# Velg $DEFAULTPAGE hvis sidenr. mangler
&gotopage($DEFAULTPAGE) unless defined $page;

opendir(DIR, $basedir) || &gotopage($page);
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
    next unless $back0 =~ /^\d{6}-\d{2}\.html?$/i || $back0 eq "";
    last if ($back1 ge $page);
    $back2 = $back1;
    $back1 = $back0;
}
# Har funnet plassering til $page i @files
if ($dir =~ /^prev|^forrige/i) {
    $newpage = $back2;
} elsif ($dir =~ /^next|^neste/i) {
    $newpage = ( $back1 eq $page ) ? $back0 : $back1 ;
}

&gotopage($newpage) if length $newpage;

&gotopage($page) if $page eq $back1;

&gotopage($DEFAULTPAGE);

exit 0;


sub gotopage {
    # Gjør "Location:" til angitt side.
    local($pg) = $_[0];

    print "Location: $url/$pg\n\n";
    exit 0;
}
