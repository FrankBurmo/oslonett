#!/local/bin/perl

$serverURL = "http://www.oslonett.no/";

$debugLOG = "/tmp/log";
$DEBUG = 0;     # set to 1 to turn on debugging code

# Specify the "first hit anchor" to be used with hiliting,
# should match up with anchor value in "kidofwais.pl". See &hilite.
# Also need to add </A> to end of hit to end anchor.
$anchor = ' name="first_hit"';

# who maintains this service?
$maintainer = '<a href="mailto:webmaster@oslonett.no">webmaster@oslonett.no</a>';

# you shouldn't have to edit anything below this line

sub send_file {
    print "Location: /$partial_name\n\n";
}


sub prepare_matching_program {
    # prepare the query word matching patterns (will use eval on this to
    # hopefully make it faster). Creates "$match_terms" and initializes
    # "$looking_for_first" to "on" (=1). This sets up the terms that we will
    # search and substitute for, adding BOLD tags around. The bold tags we
    # add are <B > ... </B >. <B > was chosen (with cap and space between B
    # and >) so as to be unlikely to be the same as any of the original BOLD
    # tags in the document. This enables us, on the "first match", to find
    # the position in the string of the "first match" and add the anchor tag
    # in front of that (so the document is positioned to the first hit when
    # presented to the user).
    local($searchterm);
    $looking_for_first = 1;
    $match_terms = "{study;\n";
    foreach $searchterm (@query) {
        # remove parens, quotes, words: and or not
        $searchterm =~ tr/\(\)\'\"//d;

        $searchterm =~ /^and$/i && next;
        $searchterm =~ /^or$/i  && next;
        $searchterm =~ /^not$/i && next;
        $searchterm =~ /^\s*$/  && next;

        $searchterm =~ /^.+\*$/ && $searchterm =~ tr/*//d &&
          ($match_terms .=
            "\$matched = 1 if s!\\b($searchterm)!<b><blink>\$1</b></blink>!ig;\n")
                        && next;
        #default case
        $searchterm =~ tr/*//d;
        $match_terms .=
        "\$matched = 1 if s!\\b($searchterm)\\b!<blink><b>\$1</b></blink>!ig;\n";
    } #end foreach searchterm
    $match_terms .= "}";
    $DEBUG && print LOG "$match_terms\n";
    return;
}


sub hilite {
        # Search for the query words and place BOLD tags around each if found.
        # If the "first hit" in this document, put in the "first_hit" anchor.
        # Also need to add </A> to end of hit to end anchor.
        local($_) = @_;         # text to hilite
        local($position,$end_position);
        $matched = 0;
        eval ($match_terms);    # do the matching/replacing
        if ($looking_for_first && $matched) { # something matched for the 1st
                $looking_for_first = 0;       # time, try to place an anchor
                $position = index( $_, "<blink><b>" );
                                # put anchor text into string if above found
                if ($position >= 0) {
                    # If text that has been bolded first is already within a
                    # <a> .., </a> construct, then we can't put another such
                    # construct around it. So instead stick the "name=" string
                    # into the <a ...> construct that is already there. If it
                    # already has a name= clause, not sure which will be
                    # recognized.
                    if ($end_gt && $in_anchor) {
                        $end_gt = "$anchor>";
                    } elsif (! $in_anchor) {
                        substr($_, $position, 0) = "<A $anchor>";
                        $end_position = index( $_, "</b></blink>", $position);
                        ($end_position >= 0) &&
                                (substr($_, $end_position + 13, 0) = "</A>");
                    }
                }
        }
        &print_it ( $_ );
        return;
}

sub print_it {  # This routine does the actual "printing" of the document
        local($to_print) = @_;
        if ($end_gt) {
                print "$end_gt$to_print";
                $end_gt = "";
        } else {
                print $to_print;
        }
}

sub process_file {

    # if 'PATH_INFO'/'PATH_TRANSLATED' has a non-null value, then
    # 'PATH_TRANSLATED' should be the fully qualified path to the file to
    # to be hilited. If these environment variables are null, then someone
    # has constructed an incorrect url
    $partial_name = $ENV{'PATH_INFO'};
    $full_name    = $ENV{'PATH_TRANSLATED'};
    if ($partial_name eq "") {
        print "Content-type: text/html\n\n";
        print "<head><title>Ulovlig URL angitt</title></head>\n";
        print "<body><h2>Ulovlig URL angitt</H2>\n";
        print "<p>";
        print "This script has been referenced by an incorrect url. Please ";
        print "contact $maintainer if you have any questions.<p>\n";
        print "<A HREF=\"$serverURL\">Main page for this server.</A></BODY>\n";
        return;
    }
    $partial_name = substr($partial_name,1); # remove beginning slash
    TYPE: for ($partial_name) {
        /.htm$/        && do { $type = 'html'; $ok = 1; last TYPE };
        /.html$/        && do { $type = 'html'; $ok = 1; last TYPE };
        /.txt$/         && do { $type = 'text'; $ok = 1; last TYPE };
        /.TEXT$/        && do { $type = 'text'; $ok = 1; last TYPE };
        $ok = 0;
    }

    do { &send_file; return; } unless defined @ARGV; # nothing to hilite
        # probably can't try to hilite without messing up file unless html/txt
    do { &send_file; return; } unless $ok;

    local(@query) = @ARGV;
    local($pquery) = join(" ", @query);
    # NCSA's HTTPD puts backslashes in front of "funny" or "dangerous"
    # characters in the input supplied thru argv. In the case of search terms
    # for WAIS, this can screw up the search (parens and "*" get backslashed
    # and then don't work correctly). So remove the backslashes, AND the
    # potentially "dangerous" characters ( ; ` ! ).
    $pquery =~ tr/!\;\`\\//d;           # just in case, get rid of ;`! and \
    @query = split(' ',$pquery);        # and recreate query word array

    # DEBUG code - write stuff into file
    $DEBUG && do { open (LOG, ">>$debugLOG") || die "can't open log";};

    &prepare_matching_program;  # create $match_terms string

    # just send file if there are no words left to hilite
    do { &send_file; return; } if ($match_terms eq "{study;\n}");

    # start the html document to "return"
    print "Content-type: text/html\n\n";

    $DEBUG && select (LOG); # write rest of stuff to file for DEBUG

    # try and open file for reading
    open (FP, "$full_name") || print "File $full_name can't be read. Please con
tact $maintainer." && return;

    if ($type eq 'text') {      # Start document for "text"
        print "<HEAD><TITLE>File: $partial_name</TITLE></HEAD>\n";
        print "<BODY><p>\n<PRE>";
    }

    local($in_tag,$skip_till_endtag,$endtag,$line_left);
    $in_tag = 0;
    $skip_till_endtag = $in_anchor = 0;
    $endtag = $end_gt = "";
    READ_LINE: while (<FP>) {
        $line_left = $_;
        PROCESS_LINE: for ($line_left) {

                ($line_left eq "") && next READ_LINE;   # nothing left of this
                                                        # paragraph
                $skip_till_endtag && $line_left =~ /$endtag/i && do {
                           $line_left = $';
                           &print_it ( "$`$endtag" );
                           $skip_till_endtag = 0;
                           $endtag = "";
                           redo PROCESS_LINE;
                        };
                $skip_till_endtag && do {  # endtag must be in next paragraph
                           &print_it ( $line_left );
                           next READ_LINE;
                        };
                ! $in_tag && $line_left =~ /</  && do {
                           $line_left = $';
                           &hilite($`) if ($` ne "");
                           &print_it ( "<" );
                           if ($line_left =~
                                 /^(PLAINTEXT|XMP|LISTING|TITLE)/i) {
                                $line_left = $';
                                $endtag = "</$1";
                                &print_it ( $1 );
                                $skip_till_endtag = 1;
                           } else {
                                ($line_left =~ /^\/A/i) && ($in_anchor = 0);
                                ($line_left =~ /^A\s+/i) && ($in_anchor = 1);
                                $in_tag = 1;
                           }
                           redo PROCESS_LINE;
                        };
                $in_tag   && $line_left =~ />/  && do {
                           $line_left = $';
                           &print_it ( $` );
                           $end_gt = ">";
                           $in_tag = 0;
                           redo PROCESS_LINE;
                        };
                $in_tag   && do {       # ending ">" must be in next paragraph
                           &print_it ( $line_left );
                           next READ_LINE;
                        };
                &hilite($line_left);  # default case: hilite rest of paragraph
                next READ_LINE;
        } # end line_left foreach
    }
    print $end_gt if $end_gt; # print out "leftover >" if there is one
    close(FP);

    print "\n</PRE>\n</BODY>\n" if ($type eq 'text'); # end document for "text"
    return;
}

open (STDERR,"> /dev/null");
eval '&process_file';


