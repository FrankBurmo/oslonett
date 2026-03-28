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
$waisd = "/local/lib/wais/wais-sources";

# what database do you want to search?
$src = "world-factbook93";

# what is the opening title you want to present to users
$openingTitle = "Search Hewlett Packard WWW information at Oslonett Inc:";

# after searching, what to you want the title to be?
$closingTitle = "Search Hewlett Packard WWW data at Oslonett Inc:";

# specify the path to add
# this is the same path your subtracted when you waisindexed
$toAdd = "/public/www/";

# specify the leader to subtract
# again, this is the same string you added when you waisindexed
$toSubtract = "http://www.oslonett.no/";

# who maintaines this service?
$maintainer = "<A HREF=http://www.oslonett.no/html/CommentForm.html>WebMaster@oslonett.no</A>";

# and when was it last modified.
$modified = "May 9, 1994 [SK]";

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
  $humanTitle = "$headline";
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
    print "This is an index of some of the the information on this WWW server. ";
    print "To use this function, simply enter a query.<P>";
    print "Since this is a WAIS index, you can enter complex queries. For example:<P>";
    print "<DL>";
    print "<DT><b>Right-hand truncation</b> (stemming) queries";
    print "<DD>The query 'astro*' will find documents containing the words";
    print " 'astronomy' as well as 'astrophysics'.<P>";
    print "<DT>Boolean '<b>And</b>' queries";
    print "<DD>The query 'red and blue' will find the <B>intersection</b> of all";
    print " the documents containing the words 'red', and 'blue'.";
    print "The use of 'and' limits your retrieval.<p>";
    print "<DT>Boolean '<b>Or</b>' queries";
    print "<DD>The query 'red or blue' will find the <B>union</b> of all the";
    print " documents containing the words 'red' and 'blue'.";
    print "The use of 'or' increases your retrieval.<p>";
    print "<DT>Boolean '<b>Not</b>' queries";
    print "<DD>The query 'red not green' will find the all the documents containing";
    print " the word 'red', and <b>excluding</b> the documents containing the word 'green'.";
    print "The use of 'not' limits your retrieval.<p>";
    print "<DT><b>Nested</b> Boolean queries";
    print "<DD>The query '(red and green) or blue not pink' will find the union of all";
    print " the documents containing the words 'red', and 'green'. It will then add (union)";
    print " all decuments containing the word 'blue'. Finally, it will exclude all documents";
    print " containing the word 'pink'";
    print "</DL>";
    print "<HR>";
    print "This WWW server is maintained by $maintainer, and it was last modified on $modified.<p>";
    print "<a href=/html/adv/HP/HP.html><img alt=[HP] src=/html/adv/HP/hp.gif></a>";
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
    print "<a href=/html/adv/HP/HP.html><img alt=[HP] src=/html/adv/HP/hp.gif></a>";
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
        print "<DD>Score: $score, Lines: $lines, Bytes: $bytes\n";
    }
    $score = $headline = $lines = $bytes = $type = $date = '';
}

eval '&do_wais';

