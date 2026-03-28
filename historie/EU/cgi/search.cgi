#!/usr/bin/perl 

use lib "/home/steinar/perllib";
use mySSI;
use locale;
use POSIX qw(setlocale);
my  $loc = POSIX::setlocale( &POSIX::LC_ALL, "no_NO" );

use CGI;

my $cgi = new CGI;

my $newslist = ""; my $newsfiles = 0;
my $imgteller = 0; my $imglist = "";
my $linkteller = 0; my $linklist = "";

my $query;
my @pars = $cgi->param;

for (@pars) {
 $query{$_} = $cgi->param($_);
}

# Dekod søk

my $search_exp = $query{string};

if (not $query{string} =~ /^"/) {
    $query{string} =~ s/ OR /\|/ig;
    my @words = split /\s+/, $query{string};
    $search_exp = "";
    for (@words) {
	$search_exp .= "$_|";
    }
    $search_exp =~ s/\|{2,}//g;
    chop ($search_exp);
    $query{string} = $search_exp;
    $query{string} =~ s/\|/ OR /g;

} 
#    error ("$search_exp : $query{string}"); exit;
$query{string} =~ s/\"//g; 
$search_exp =~ s/\"//g; 
 use URI::Escape;
 use File::Find;
 use File::Basename;

 my $nfiles = 0;
 my $slist = "";

## CONFIG SEKSJON - endre her for en annen installasjon
##
# 1:
# Hvilke filendelser skal vi lete etter? Må være tekstfiler for at søk skal 
# virke. Regexpet må avpasses etter suffixlisten, disse to tingene brukes
# på forskjellige måter, derfor ligger de både i en array og i et regexp
 my @suffixes = ('.html','.htm','.txt');
 my $sufregexp = '^(\.htm|\.html|\.txt)$';

# 2:
# Ønsker vi å hoppe over spesielle filer, angis de i dette regexpet
   my $skiplist = '\/ssi|index\.html|\/gifs|\/img|css|\/js\/|\#';
   $skiplist .= '|\/News\/' unless $query{topdir} eq 'News';

# 3:
# Start for rekursjonen
 my $top     = "/home/oslonett/www/historie/EU";
 my $root = $top;

 my $addquery = "";

  if ($query{topdir}){
      $top = $top . "/" . $query{topdir};
      $addquery = "&amp;topdir=$query{topdir}";
  }





# 4:
# URL tilsvarende toppen $top
 my $topurl = '';

# 5:
# Hvordan skal søkebegrepet utheves i teksten:
 my $startuthev = '<span class="sokmatch">';
 my $stoputhev  = '</span>';

##
## END CONFIG ##

## Er vi i state 2, dvs. klikk på en av filene i trefflisten?
## (show_results gjør selv exit)

 show_results ()
    if $query{path};

# Nei, state 1 - let etter treff:

# 1. HTML filer
 

 File::Find::find(\&subst, "$top");

$slist = "<p>Ingen filtreff</p>"
    unless $nfiles;


 $/ = undef;
 open (I,"$root/search.tmpl") ||
    error ("Kan ikke åpne malfil $root/search.tmpl for søk");

 my $tmpl = <I>;
 $tmpl = expand_inc($tmpl);
 close (I);

# Flett inn stoff og skriv ut

$tmpl =~ s/\@STRING\@/$query{string}/g;
$tmpl =~ s/\@LIST\@/$slist/;
$tmpl =~ s/\@N\@/$nfiles/;
$tmpl =~ s/\@SOURCE\@/$query{source}/;

print "Content-type: text/html\n\n$tmpl";

####################
##
## Subroutines


# HTML søk

 sub subst { 

    local($_);
    my $filename = $File::Find::name;
    my $file;

# Split path i tre komponenter

    my ($name,$path,$suffix) = fileparse($filename,@suffixes);
    

## Er dette en fil vi skal se videre på, eller hoppe over?

    if ($filename =~ /$skiplist/o or not $suffix =~ /$sufregexp/o) {
        return;
    } 

## Så får vi sjekke om søkeuttrykket matcher innholdet

    { 
     local($/) = undef;
     open (F,$filename) || die "Can't open $name";
     $file = <F>;
     close(F);
    }
#    $file =~ /<body\s+.*?>((.|\n)*)<\/body>/mi;
#    $body = $1 ? $1 : $file;
    $body = $file;
    if ($body =~ /$search_exp/i) {
        $url = path_to_url($filename);
	$file =~ /<title>((.|\n)*?)<\/title>/mi;
        $title = $1 ? $1 : $url;
#	$slist .= sprintf "<a href=\"/cgi/sok.cgi?path=$url&amp;string=%s$addquery#hit\">%s</a>\n<br />\n",  uri_escape($query{string}), $title;
	$slist .= sprintf qq|<a href="$url">%s</a>\n<br />\n|,  $title;
	$nfiles++;
    }
}

# Hjelperutine

sub path_to_url {
    my $path = shift;

    $path =~ s%/home/oslonett/www%%;

    return "$path";

}

sub url_to_path {

    my $url = shift;
    
    return ($top . "$url");
}

sub show_results {

    print "Location: http://priv.infostream.no/oslonett/historie/EU/cgi/search.cgi$query{path}\n\n";
    exit;

    local($/) = undef;
    my $path = url_to_path($query{path});

    $dirname = dirname ($query{path});

    open (F, $path);
    my $content = <F>;
    close (F);
    $content =~ s%(<body\s+.*>(.|\n)*)($query{string})((.|\n)*</body>)%$1$2<a name="hit">$startuthev$3$stoputhev</a>$4%mig;
    $content =~ s%(<body\s+.*>(.|\n)*)($query{string})((.|\n)*</body>)%$1$2<a name="hit">$3</a>$4%mig;
    $content = expand_inc($content);


 print qq#Content-type: text/html\n\n<base href="http://$ENV{SERVER_NAME}$topurl$dirname/">\n$content#;
    exit;
}

sub error {
    my $m = shift;
    print "Content-type: text/plain\n\n$m";
    exit;
}
