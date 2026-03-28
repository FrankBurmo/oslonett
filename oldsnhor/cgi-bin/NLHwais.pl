#!/local/bin/perl
require "flush.pl";


# where is your waiq binary?
$waisq = "/local/bin/waisq";

# where are your source files?
$waisd = "/public/wais";

# what database do you want to search?
$src = "NLH";

# what is the opening title you want to present to users
$openingTitle = "Let i dokumentene til Norwegian Library House";

# after searching, what to you want the title to be?
$closingTitle = "Let i dokumentene til Norwegian Library House";

# specify the path to add
# this is the same path your subtracted when you waisindexed
$toAdd = "/home/hasle/b/paul/www_docs";

# specify the leader to subtract
# again, this is the same string you added when you waisindexed
$toSubtract = "http://www.oslonett.no/home/paul";

# who maintaines this service?
$maintainer = "<A HREF=http://www.oslonett.no/html/CommentForm.html>WebMaster@oslonett.no</A>";

# and when was it last modified.
$modified = "9. nov 1994 [SK]";

#
# file type map based on file extension, since all file types
# come back type URL
#

%filetype = (
'html', 'HTML fil',
'gif', 'GIF bilde',
'ps', 'Postscript fil',
'txt', 'Vanlig tekst fil',
'mpg', 'MPEG video',
);

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
#  $humanTitle = "$headline";
  ($humanTitle = $headline) =~ s%.*/%%;
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
    print "<img alt=\"\" src=/graphics/binoc.gif>\n";

    print "<p>";
    print "Dette er en søkbar indeks over <i>Norwegian Library House</i> sin informasjon hos Oslonett. ";
    print "Skriv inn et søkeutrykk, og trykk &lt;Enter&gt;.<P>";
    print "Siden dette er en WAIS database, kan du angi komplekse søkeuttrykk, for eksempel:<P>";
    print "<DL>";
    print "<DT><b>Høyre-hånds trunkering</b> (stemming) søk";
    print "<DD>Søket 'fisk\\*' vil finne dokumenter som inneholder ordene";
    print " 'fiske' så vel som 'fiskerier'.<P>";
    print "<DT>Logiske '<b>And</b>' uttrykk";
    print "<DD>Søket 'jordbruk AND fiske' vil finne det logiske <B>snittet</b> av alle";
    print " dokumentene som inneholder ordene 'jordbruk' og 'fiske'. ";
    print "Bruken av ordet 'and' begrenser dermed søket.<p>";
    print "<DT>Logiske '<b>Or</b>' uttrykk";
    print "<DD>Søket 'union or selvstendighet' vil finne den logiske <B>unionen</b> av alle";
    print " dokumentene som inneholder ordene 'union' eller 'selvstendighet'. ";
    print "Bruken av ordet 'or' øker dermed søket.<p>";
    print "<DT>Logiske '<b>Not</b>' uttrykk";
    print "<DD>Søket 'jordbruk not subsidier' vil finne alle dokumentene som inneholder";
    print " ordet 'jordbruk', men <b>ekskluderer</b> de av disse som inneholder ordet 'subsidier'.";
    print "Bruken av ordet 'not' begrenser dermed søket.<p>";
    print "<DT><b>Nestede</b> logiske uttrykk";
    print "<DD>Søket '\\(jordbruk AND fiske\\) OR hval NOT fredning' vil finne unionen av alle";
    print " dokumentene som inneholder ordene 'jordbruk' OG 'fiske'. Så vil dokumenter inneholdende ordet 'hval' bli addert (union), og ";
    print " til slutt vil alle dokumentene inneholdende ordet 'fredning' bli ekskludert.";

    print "</DL>";
    print "Legg merke til at spesialtegn som '(' og '\*' må foranlediges av en '\\'.";
    print "<HR>";
    print "Denne WWW serveren er drevet av Oslonett A/S og vedlikeholdes av $maintainer. Dette søkesystemet ble sist modifisert $modified.<p>";

    print "<a href=/home/paul/><img alt=\"[NLH]\" src=/graphics/NLH-icon.gif></a>";
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
    print "<BODY>\n<p><img alt=\"\" src=/graphics/binoc.gif>\n<H2>", $closingTitle, "</H2>\n";
  

    print "S&oslash;ket i WAIS basen \`$src\' ga disse klaffene\n";
    print "som relevante for: \`$pquery\':<P>\n";
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
    print "<a href=/home/paul/><img alt=\"[NLH]\" src=/graphics/NLH-icon.gif></a>";
    if ($hits == 0) {
        print"Nothing found.\n";
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
        $docname = $headline;
	$docname =~ s/\.([^.]*)$//;
	$extension= $1;
	$docname =~ s/\/([^\/]*)$//;
	$docname = $1;
        $title = &extractTitle ($headline);

        print "<DT><A HREF=\"$headline\">$humanTitle</A>\n";
        print "<DD>Score: $score, Linjer: $lines, Tegn: $bytes\n";
        print "<DD>Fil type:<B> $filetype{$extension}</B>\n";

    }
    $score = $headline = $lines = $bytes = $type = $date = '';
}

eval '&do_wais';

