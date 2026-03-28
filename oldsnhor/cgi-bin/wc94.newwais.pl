#!/local/bin/perl
#
# newwais.pl -- WAIS search interface
#
# from wais.pl
#
# Tony Sanders <sanders@bsdi.com>, Nov 1993
#
# Example configuration (in local.conf):
#     map topdir wais.pl &do_wais($top, $path, $query, "database", "title")
#
# this script uses a sneaky feature of Mosaic that interpretes a 
# single text input form with the name 'isindex' (case sensitive) to
# the same as a <ISINDEX>.  On non-mosaic clients, you wind up with an
# additional query
#
# Note that I know even less about perl than the other two people
# who hacked this, so feel free to send hate mail to pjh@netcom.com
# if I did something really bad (or if there is a better way of
# grabbing the filename off the end of a path.
#

require 'ctime.pl';

$waisq = "/local/bin/waisq";
$waisd = "/www/htdocs/wc94/wais-sources";
$src = "wc94";
$title = "WC'94";

#
# file type map based on file extension, since all file types
# come back type URL
#

%filetype = (
'html', 'HTML File',
'gif', 'GIF Image',
'ps', 'Postscript File',
'txt', 'Plain Text File',
);

#
# code
# 

sub send_index {
    print "Content-type: text/html\n\n";
    
    print "<HEAD>\n<TITLE>Index of ", $title, "</TITLE>\n</HEAD>\n";
    print "<BODY>\n<H1>", $title, "</H1>\n";

    print "This is an index of the information on this server. Please\n";
    print "type a query in the search dialog.\n<P>";
    print "You may use compound searches, such as: <CODE>environment AND cgi</CODE>\n";
    print "<ISINDEX>";
}

sub do_wais {
#    local($top, $path, $query, $src, $title) = @_;


    do { &'send_index; return; } unless defined @ARGV;
    local(@query) = @ARGV;
    local($pquery) = join(" ", @query);

#
# grab a wais source if there is one
#

    local($test) = $ENV{'PATH_INFO'};
    if ($test)
    {
	$test =~ s/\///;
        $src = $test;
        $title = $test;
    }

    print "Content-type: text/html\n\n";

    $ENV{'HOME'} = "/";
	
    open(WAISQ, "-|") || exec ($waisq, "-c", $waisd,
                                "-f", "-", "-S", "$src.src", "-g", @query);

    print "<HEAD>\n<TITLE>Search of ", $title, "</TITLE>\n</HEAD>\n";
    print "<BODY>\n<H1>", $title, "</H1>\n";

    print "<HR><FORM method=\"GET\" action=\"/cgi-bin/newwais.pl/$src\">\n";
    print "Enter keyword(s):\n";
    print "<input name=\"isindex\" value=\"@query\" size=30></FORM><HR>\n";

    print "$title contains the following\n";
    print "items relevant to <B>\`$pquery\':</B><P>\n";
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
            s#(Catalog for database:)\s+.*#$1 <STRONG>$src</STRONG>#;
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
        print "<DT><B>$hits: </B><A HREF=\"$headline\">$docname</A>\n";
        print "<DD>Score:<B> $score </B> Lines:<B> $lines </B> \
                   Bytes:<B> $bytes</B>\n";
        print "<DD>File Type:<B> $filetype{$extension}</B>\n";
    }
    $score = $headline = $lines = $bytes = $type = $date = '';
}

eval '&do_wais';
