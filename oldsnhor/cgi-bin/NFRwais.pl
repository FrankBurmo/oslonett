#!/local/bin/perl
require "flush.pl";
#
# wais.pl -- WAIS search interface
#
# $Id$
#
# Tony Sanders <sanders@bsdi.com>, Nov 1993
#
# Example configuration (in local.conf):
#     map topdir wais.pl &do_wais($top, $path, $query, "database", "title")
#
# Modified to present the user "human-readable" titles, better instructions as well
# as the ability to do repeated searches after recieving results.
#
# by Eric Lease Morgan, NCSU Libraries, April 1994
# eric_morgan@ncsu.edu
# http://dewey.lib.ncsu.edu/staff/morgan/morgan.html
# To read more about this script try:
# http://dewey.lib.ncsu.edu/staff/morgan/son-of-wais.html


# where is your waiq binary?
$waisq = "/local/bin/waisq";

# where are your source files?
$waisd = "/local/www/wais";

# what database do you want to search?
$src = "NFR";

# what is the opening title you want to present to users
$openingTitle = "Let i Forskningsrådets informasjonsbase i WWW på Oslonett:";

# after searching, what to you want the title to be?
$closingTitle = "Let i Forskningsrådets informasjonsbase i WWW på Oslonett:";

# specify the path to add
# this is the same path your subtracted when you waisindexed
$toAdd = "/local/www/NYOMP";

# specify the leader to subtract
# again, this is the same string you added when you waisindexed
$toSubtract = "http://www.oslonett.no";

# who maintaines this service?
$maintainer = "<A HREF=http://www.oslonett.no/html/CommentForm.html>WebMaster@oslonett.no</A>";

# and when was it last modified.
$modified = "22. juni 1995 [MØ]";

# you shouldn't have to edit anything below this line, excpept if you want to change the help text

sub extractTitle {
  # get the string to munge
  $theFile = $headline;
  
  # parse out the file name
  $theFile =~ s/^.*$toSubtract//i;

  # concatonate the "toAdd" variable with the file name
  $theFile = $toAdd.$theFile;

  # open the file
  open( DATA, $theFile) || die "Can't open $theFile\n";

  # read the file and extract the title
  $linenum = 1;
  $foundtitle = 0;
#  $humanTitle = "(No title found in document, maybe a GIF file?) Call $maintainer.";
  $humanTitle = "$headline (antagelig et bilde)";
  while ( $line = <DATA>) {
    last if ($linenum > 5);
    $linenum++;
    if ($line =~ s/^.*<title>//i ) {
      chop( $line);
      $line =~ s!</title>.*$!!i;
      $humanTitle = $line;
      $humanTitle =~ s/^\s*//;
      $humanTitle =~ s/\s*$//;
      $foundtitle = 1;
      last;
    }
  }

  # close the file
  close (DATA);

  # return the final results
  return $humanTitle;
  }

sub send_index {
    print "Content-type: text/html\n\n";
    
    print "<HEAD>\n<TITLE>$openingTitle</TITLE>\n<ISINDEX></HEAD>\n";
    print "<BODY>\n<H2>", $openingTitle, "</H2>\n";
    print "<img src=/graphics/binoc.gif>\n";

    print "<p>";
    print "Dette er en søkbar indeks over Forskningsrådets informasjon hos Oslonett. ";
    print "Skriv inn et søkeutrykk, og trykk &lt;Enter&gt;.<P>";
    print "Siden dette er en WAIS database, kan du angi komplekse søkeuttrykk, for eksempel:<P>";
    print "<DL>";
    print "<DT><b>Høyre-hånds trunkering</b> (stemming) søk";
    print "<DD>Søket 'astro\\*' vil finne dokumenter som inneholder ordene";
    print " 'astronomi' så vel som 'astrofysikk'.<P>";
    print "<DT>Logiske '<b>And</b>' uttrykk";
    print "<DD>Søket 'hund AND katt' vil finne det logiske <B>snittet</b> av alle";
    print " dokumentene som inneholder ordene 'hund' og 'katt'. ";
    print "Bruken av ordet 'and' begrenser dermed søket.<p>";
    print "<DT>Logiske '<b>Or</b>' uttrykk";
    print "<DD>Søket 'kvitt or dobbelt' vil finne den logiske <B>unionen</b> av alle";
    print " dokumentene som inneholder ordene 'kvitt' eller 'dobbelt'. ";
    print "Bruken av ordet 'or' øker dermed søket.<p>";
    print "<DT>Logiske '<b>Not</b>' uttrykk";
    print "<DD>Søket 'industri not energi' vil finne alle dokumentene som inneholder";
    print " ordet 'industri', men <b>ekskluderer</b> de av disse som inneholder ordet 'energi'.";
    print "Bruken av ordet 'not' begrenser dermed søket.<p>";
    print "<DT><b>Nestede</b> logiske uttrykk";
    print "<DD>Søket '\\(industri AND energi\\) OR kvitt NOT dobbelt' vil finne unionen av alle";
    print " dokumentene som inneholder ordene 'industri' OG 'energi'. Så vil dokumenter inneholdende ordet 'kvitt' bli addert (union), og ";
    print " til slutt vil alle dokumentene inneholdende ordet 'dobbelt' bli ekskludert.";

    print "</DL>";
    print "Legg merke til at spesialtegn som '(' og '\*' må foranlediges av en '\\'.";
    print "<HR>";
    print "Denne WWW serveren er drevet av Oslonett A/S og vedlikeholdes av $maintainer. Dette søkesystemet ble sist modifisert $modified.<p>";
    print "<a href=http://www2.oslonett.no/div/oi/nfr/index.html><img alt=[NFR] src=http://www2.oslonett.no/div/oi/nfr/gifs/nfr-icon.gif></a>";
}


sub do_wais {
#    local($top, $path, $query, $src, $title) = @_;

    do { &'send_index; return; } unless defined @ARGV;
    local(@query) = @ARGV;
    local($pquery) = join(" ", @query);

    print "Content-type: text/html\n\n";
    &flush (STDOUT);


    open(WAISQ, "-|") || exec ("$waisq -c $waisd -f - -S $src.src -g @query 2>/dev/null");

    print "<HEAD>\n<TITLE>$closingTitle</TITLE>\n<ISINDEX></HEAD>\n";
    print "<BODY>\n<p><img alt=\"[Search Icon]\" src=/graphics/binoc.gif>\n<H2>", $closingTitle, "</H2>\n";
  

    print "Index \`$src\' contains the following\n";
    print "items relevant to \`$pquery\':<P>\n";
    print "<DL>\n";

    local($hits, $score, $headline, $lines, $bytes, $type, $date);
    while (<WAISQ>) {
        /:score\s+(\d+)/ && ($score = $1);
        /:number-of-lines\s+(\d+)/ && ($lines = $1);
        /:number-of-bytes\s+(\d+)/ && ($bytes = $1);
        /:type "(.*)"/ && ($type = $1);
        /:headline "(.*)"/ && ($headline = $1);         # XXX
        /:date "(\d+)"/ && ($date = $1, $hits++, &docdone);
    }
    close(WAISQ);
    print "</DL>\n";
    print "<HR>";
    print "This WWW server is maintained by $maintainer.<P>";
    print "<a href=http://www2.oslonett.no/div/oi/nfr/index.html><img alt=[NFR] src=http://www2.oslonett.no/div/oi/nfr/gifs/nfr-icon.gif></a>";
    if ($hits == 0) {
        print "Nothing found.\n";
    }
    print "</BODY>\n";
}

sub docdone {
    if ($headline =~ /Search produced no result/) {
        print "<HR>";
        print $headline, "<P>\n<PRE>";
# the following was &'safeopen
        open(WAISCAT, "$waisd/$src.cat") || die "$src.cat: $!";
        while (<WAISCAT>) {
            s#(Catalog for database:)\s+.*#$1 <A HREF="/$top/$src.src">$src.src</A>#;
            s#Headline:\s+(.*)#Headline: <A HREF="$1">$1</A>#;
            print;
        }
        close(WAISCAT);
        print "\n</PRE>\n";
    } else {
        $title = &extractTitle ($headline);
        print "<DT><A HREF=\"$headline\">$humanTitle</A>\n";
        print "<DD>Score: $score, #linjer: $lines, #tegn: $bytes\n";
    }
    $score = $headline = $lines = $bytes = $type = $date = '';
}

eval '&do_wais';

