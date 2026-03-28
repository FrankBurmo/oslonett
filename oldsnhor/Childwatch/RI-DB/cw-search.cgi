#!/local/bin/perl5

$DB = "/home/frogner/www/Childwatch/RI-DB/DATABASE";
$DEFAULT_FORMAT = "very short";  # full/raw/short/very short
$DEFAULT_FOCUS  = "all";         # all/research/doc/computer
#$CONVENTION     = "/Childwatch/convention.html";
$CONVENTIONDIR   = "/Childwatch/convention";


$HEADER = <<"---";
<title>Childwatch - Database on R&amp;I on Children's Rights</title>
<h3 align=center>
<font size=+2>D</font>ATABASE ON
<font size=+2>R</font>ESEARCH AND
<font size=+2>I</font>NFORMATION ON
<font size=+2>C</font>HILDREN'S
<font size=+2>R</font>IGHTS
</h3>

<hr>
---

$TRAILER = <<"---";
<!-- common signature found in signature.html -->
<hr>
<a href="/Childwatch/RI-DB/index.html"><img src="/Childwatch/img/ridb.gif" alt="[Database on R&I]"></a>
<a href="/Childwatch/index.html"><img src="/Childwatch/img/back2.gif" alt="[Childwatch Home]"></a>
---


&split_query($ENV{QUERY_STRING});  # splits into the %query array

# First we extract the 'format' and the 'focus' attributes

$format = lc($query{'format'}) || $DEFAULT_FORMAT;
delete $query{'format'};

$focus  = lc($query{'focus'})  || $DEFAULT_FOCUS;
delete $query{'focus'};

$research_focus = 0;
$doc_focus = 0;
$computer_focus = 0;
if ($focus eq "research") {
    $research_focus = 1;
} elsif ($focus eq "doc") {
    $doc_focus = 1;
} elsif ($focus eq "computer") {
    $computer_focus = 1;
} elsif ($focus eq "all") {
    $research_focus = 1;
    $doc_focus = 1;
    $computer_focus = 1;
} else {
    print "Content-type: text/html\n\n";
    print $HEADER;
    print "Illegal focus!\n";
    exit;
}
    

# Need to define the 'match' subroutine based on the content of %query;
unless (keys %query) {
    print "Content-type: text/html\n\n";
    print $HEADER;
    print "No query!\n";
    exit;
}

# Look for the 'searchtype' attribute
$or = 1;
$or = 0 if lc($query{'searchtype'}) eq "and";
delete $query{'searchtype'};

# Look for the 'showcode' attribute.  Only used for debugging.
$showcode = 0;
$showcode = 1 if lc($query{'showcode'}) eq "yes";
delete $query{'showcode'};

# Generate the search procedure

%regmatch_key = ('areas-of-research' => 1, 'projects' => 1, 'subject-areas' => 1);
%boolean_key  = ('computerized' => 1, 'collection' => 1,
                 'public' => 1, 'private' => 1,
		 'on-line-access' => 1);

$code = "sub match {\n";
foreach $key (keys %query) {
    foreach $val (split (/\0/, $query{$key})) {
	next unless length $val;
        if ($key eq "free") {
	    $val = quotemeta $val;

	    my($expr_started) = 0;  # flag used for "and" search

	    # Make free-text search work for coded fields
	    for $area (keys %areas) {
		if ($areas{$area} =~ /$val/i) {
		    # this area contains the free text string
		    if ($or) {
			$code .= qq{  return 1 if \$freetext =~ /\\b$area\\b/;\n} if $or;
		    } else {
			$code .= qq{  return 0 if\n}  unless $expr_started;
			$code .= qq{ &&\n} if $expr_started;
		        $code .= qq{\t\$freetext !~ /\\b$area\\b/};
			$expr_started = 1;
		    }
		}
	    }
	    for $hold (keys %holdings) {
		if ($holdings{$hold} =~ /$val/i) {
		    # this area contains the free text string
		    if ($or) {
			$code .= qq{  return 1 if \$freetext =~ /\\b$hold\\b/;\n} if $or;
		    } else {
			$code .= qq{  return 0 if\n}  unless $expr_started;
			$code .= qq{ &&\n} if $expr_started;
		        $code .= qq{\t\$freetext !~ /\\b$hold\\b/};
			$expr_started = 1;
		    }
		}
	    }
	    if ($or) {
		$code .= qq{  return 1 if \$freetext =~ /$val/i;\n};
	    } else {
		$code .= qq{  return 0 if\n} unless $expr_started;
		$code .= qq{ &&\n} if $expr_started;
		$code .= qq{\t\$freetext !~ /$val/i;\n};
		$expr_started = 1;
	    }
	} elsif ($boolean_key{$key}) {
	    $val = 0 if lc($val) eq "no" || lc($val) eq "false";
	    # $code .= qq{  # $key: or=$or, $val=$val\n};
	    if ($or) {
	        $code .= qq{  return 1 if \$val{'$key'};\n}  if  $val;
	        $code .= qq{  return 1 if !\$val{'$key'};\n} if  !$val;
            } else {
	        $code .= qq{  return 0 if !\$val{'$key'};\n} if  $val;
	        $code .= qq{  return 0 if \$val{'$key'};\n}  if  !$val;
            }
	} elsif ($regmatch_key{$key}) {
	    $val = quotemeta $val;
	    $code .= qq{  return 1 if \$val{'$key'} =~ /$val/i;\n} if $or;
	    $code .= qq{  return 0 if \$val{'$key'} !~ /$val/i;\n} if !$or;
	} else {
	    $code .= qq{  return 1 if lc(\$val{'$key'}) eq lc("$val");\n} if $or;
	    $code .= qq{  return 0 if lc(\$val{'$key'}) ne lc("$val");\n} if !$or;
	}
    }
}
$code .= qq{  0;\n} if $or;
$code .= qq{  1;\n} if !$or;
$code .= "}\n";
if ($showcode) {
    print "Content-type: text/plain\n\n";
    print $code;
    exit;
}
eval $code;
if ($@) {
     print "Content-type: text/plain\n\n";
     print "Searchprocedure does not work:\n\n$@\n\n";
     print "$code\n";
     exit;
}
$code = undef;

# Find the right Content/type
if ($format eq "raw") {
    print "Content-type: text/plain\n\n";
} else {
    print "Content-type: text/html\n\n";
    print $HEADER;
}

# Present the search parameters
if (!defined $query{'id'}) {
    $first = 1;
    $lastkey = "";
    print "<b>Search for:</b> ";
    foreach $key (keys %query) {
	foreach $val (split (/\0/, $query{$key})) {
	    next unless length $val;
	    if ($first) {
		$first = 0;
	    } else {
		print " <b>or</b> "  if $or;
		print " <b>and</b> " if !$or;
	    }
	    if ($key ne $lastkey) {
		my $k = $key;
		$k =~ s/-/ /;
		print "\u$k =";
	    }
	    $lastkey = $key;
	    if ($key eq 'areas-of-research' || $key eq 'subject-areas') {
		my($h) = split(/\./, $val);
		$val = "$val $area_heading{$h}: $areas{$val}";
	    }
	    print " $val ";
	}
    }
    print "\n\n";
}


open(DB) || die "Can't open database\n";

$id = undef;
%val = ();
$freetext = "";

$count = 0;
while (<DB>) {
    if (/^id:\s*(.*)/) {
	# a new entry is found
	$newid = $1;
	if (defined($id)) {
	    if (&match) {
		$count++;
                if ($format eq "very short") {
		    push(@collect,
			 [$id, @val{'name', 'institution', 'englishname', 'country'}]);
		} else {
		    &out;
		}
	    }
	}
	$id = $newid;
	%val = ();
	$freetext = "";
	$val{'id'} = $id;
    } elsif (/^(\w[^:]*):\s*(.*)/) {
	$val{$1} = $2;
	$freetext .= "$2 ";
    } elsif (/^$/) {
	# ignore blank lines
    } else {
	warn "DB corrupt at line $.\n";
    }
}

if ($format eq "very short") {
    $country = "";
    for (sort { $a->[4] cmp $b->[4] || $a->[1] cmp $b->[1] } @collect) {
	if ($_->[4] ne $country) {
	    print "</ul>\n" if $country ne "";
	    $country = $_->[4];
	    print "<h3>$country</h3>\n";
	    print "<ul>\n";
	}
	print qq{<li> <b><a href="$ENV{SCRIPT_NAME}?id=$_->[0]&format=full&focus=$focus">$_->[1]</a></b>};
        print qq{, $_->[2]\n} if $_->[2];
	print qq{<br>($_->[3])\n} if length($_->[3]) && $_->[3] ne $_->[1];
    }
    print "</ul>\n" if $country ne "";
    print "</dl>\n";
}

if ($count == 0) {
    print qq(<img src="/Childwatch/img/warning.gif" alt=""><br> Nothing found!\n);
} elsif ($count > 1) {
    print "<i>$count entries found in the database.</i>\n"
}

print $TRAILER;

sub out
{
    local($_);
    if ($format eq 'raw') {
	&rawout;
	return;
    }
    print "<a href=\"$ENV{SCRIPT_NAME}?id=$id&format=full&focus=$focus\">\n"
	if $format ne "full";

    $val{'name'} = $val{'englishname'} || "[No name]"
	unless length $val{'name'};
    $val{'englishname'} = $val{'name'} unless length $val{'englishname'};
    $val{'name'} .= " $val{'acronym'}" if $val{'acronym'};
    $val{'englishname'} .= " $val{'englishacronym'}" if $val{'englishacronym'};
    if ($format eq "very short") {
	print "<dt><b>$val{'name'}</b>";
    } else {
	print "<h2>$val{'name'}</h2>\n";
    }
    print "</a>\n\n" if $format ne "full";

    if ($format eq "very short") {
	print " <dd> $val{'englishname'}\n"
	    unless $val{'name'} eq $val{'englishname'};
	return;
    }

    $br = 0;
    unless ($val{'name'} eq $val{'englishname'}) {
	print "($val{'englishname'})\n";
	$br = 1;
    }
    if ($val{'institution'}) {
	print "<br>" if $br;
	print "$val{'institution'}\n";
	$br = 1;
    }
    if ($val{'address'}) {
	print "<br>" if $br;
	print "$val{'address'}\n";
	$br = 1;
    }
    print "<br>" if $br;
    print "$val{'postalcode'}\n";
    print "<br>$val{'country'}\n";
    present("Location", $val{'location'});

    print "<p><b>Phone:</b> $val{'telephone'}";
    print ", <b>Fax:</b> $val{'fax'}" if defined $val{'fax'};
    print ", <b>Telex:</b> $val{'telex'}" if defined $val{'telex'};
    if (defined $val{'e-mail'}) {
	if ($val{'e-mail'} =~ /@/) {
	    print qq{<br><b>E-mail:</b> <a href="mailto:$val{'e-mail'}">$val{'e-mail'}</a>};
	} else {
	    print qq{<br><b>E-mail:</b> $val{'e-mail'}};
	}
    }
    present("Director", $val{'director'}, 1);

    print "\n";
    return if $format eq "short";

    # Type of organization
    print "<p>This is a ";
    if ($val{'public'}) {
	print "public";
	print "/" if $val{'private'};
    }
    print "private" if $val{'private'};
    print " ";
    $_ = $val{'type'};
    if (defined $org_types{$_}) {
	print $org_types{$_};
    } elsif (defined $_ && length $_) {
	print $_;
    } else {
	print "organization";
    }
    print ".\n";

    # Scope of activites
    print "Scope of activites are $val{'scope-of-activities'}.\n"
	if defined $val{'scope-of-activities'};

    # Research section
    if ($research_focus) {
	print qq{<a name="research"><h2><img src="/Childwatch/img/research.gif" alt=""> Research activities</h2></a>\n};

	present("Contact",  $val{'contact'}, 1);

	# Projects
	if (defined $val{'projects'}) {
	    print "<h3>Major ongoing projects</h3>\n";
	    print "<ul>\n";
	    $_ = $val{'projects'};
	    s/-/<li>/g;
	    print "$_\n";
	    print "</ul>\n";
	}

	# Areas of research
	if (defined $val{'areas-of-research'}) {
	    print "<h3>Areas of research</h3>\n";
	    present_area($val{'areas-of-research'});
	}

	# Other topics
	if (defined $val{'other-topics'}) {
	    print "<h3>Other topics of special interest</h3>\n";
	    my $t = $val{'other-topics'};
	    $t =~ s/&/<li>/g;
	    print "<ul><li>$t</ul>\n\n";
	}
    }

    if ($doc_focus && $val{'collection'} eq "yes") {
	print qq{<a name="doc"><h2><img src="/Childwatch/img/document.gif" alt=""> Library/Documentation activites</h2></a>\n};

	present("Contact", $val{'documentalists'}, 1);

	# Document types
	if (defined $val{'holdings'}) {
	    print "<h3>Types of documentation</h3>\n";
	    my $t = $val{'holdings'};
            $t =~ s/(\w{2})/<li>$1/;
	    $t =~ s/\b([A-Z])\b/<li>$holdings{$1}/g;
	    print "<ul><li>$t</ul>\n\n";
	}

	present("Scope", $val{'geographical-scope'}, 1);
	present("Size", $val{'size-of-collection'});
	present("Languages", $val{'languages-of-collection'});

	# Subject areas
	if (defined $val{'subject-areas'}) {
	    print "<h3>Areas of documentation</h3>\n";
	    present_area($val{'subject-areas'});
	}

	# services
	if (defined $val{'services'}) {
	    print "<h3>Services offered</h3>\n";
	    my $t = $val{'services'};
	    $t =~ s/(-?\d+)(F?)/<li>$service_types{$1} $fees{$2}/g;
	    $t =~ s/-\s/<li>/g;
	    print "<ul>$t</ul>\n\n";
	}
	present("Accession lists:", $val{'accession-lists'}, 1);
	present("Other products:", $val{'other-products'});
    }


    if ($computer_focus && $val{'computerized'} eq "yes") {
	print qq{<a name="computer"><h2><img src="/Childwatch/img/computer.gif" alt=""> Computerized databases</h2></a>\n};

	present("Computers", $val{'computers'}, 1);
	present("Operating systems", $val{'operating-systems'});

	if ($val{'on-line-access'} eq "yes") {
	    print "<h3>On-line access to database</h3>\n";
	    present("Database host or service", $val{'database'}, 1);
	    present("Search languages used", $val{'search-languages'});
	    present("Dialogue languages used", $val{'dialogue-languages'});
	    # on line help
	    present("Access hours", $val{'access-hours'});
	    present("Access address", $val{'access-address'});
	    present("Protocol", $val{'protocol'});
	}
    }

    #print qq{<p><hr align=left width="25%">\n};
    if (!$research_focus) {
	print qq{<a href="$ENV{SCRIPT_NAME}?id=$id&format=full&focus=research"><img src="/Childwatch/img/research.gif" alt="[RESEARCH]"> Research Activites</a><br>};
    }
    if (!$doc_focus && $val{'collection'} eq "yes") {
	print qq{<a href="$ENV{SCRIPT_NAME}?id=$id&format=full&focus=doc"><img src="/Childwatch/img/document.gif" alt="[DOCUMENTATION]"> Library/Documentation activites</a><br>};
    }
    if (!$computer_focus && $val{'computerized'} eq "yes") {
	print qq{<a href="$ENV{SCRIPT_NAME}?id=$id&format=full&focus=computer"><img src="/Childwatch/img/computer.gif" alt="[COMPUTER]"> Computerized databases </a><br>};
    }
    if ($focus ne "all" &&
        (!$research_focus ||
            ($research_focus &&
                ($val{'computerized'} eq "yes" ||
                 $val{'collection'} eq "yes")))) {
        print qq{<a href="$ENV{SCRIPT_NAME}?id=$id&format=full&focus=all"><img src="/Childwatch/img/all.gif" alt="[ALL]"> Show all information</a>};
    }
    print "<p>\n";
}

sub present
{
    my($head,$val, $first) = @_;
    $present_first = 1 if $first;
    return unless defined $val;
    print "<p>"  if $present_first;
    print "<br>" if !$present_first;
    $present_first = 0;
    print "<b>$head:</b> $val\n";
}
sub present_area
{
    print "<dl><dd>\n";
    my $lastcat = "";
    foreach (split(' ', $_[0])) {
	my($cat) = /^(\w+)\./;
	if ($cat ne $lastcat) {
	    print "</ul>\n" if $lastcat ne "";
	    print "<b>$area_heading{$cat}</b>\n<ul>\n";
	    $lastcat = $cat;
	}
	my($area) = $areas{$_};
	$area =~ s/(articles?\s(\d+))/<a href="$CONVENTIONDIR\/art$2.html">$1<\/a>/i;
	print "<li> $area\n";
    }
    print "</ul></dl>\n\n";
}

sub rawout
{
    print "id = $id\n";
    for (sort keys %val) {
	print "$_: $val{$_}\n";
    }
    print "\n";
}

BEGIN {

%org_types = 
(
 1 => "child research institute",
 2 => "child research unit/project within an institution",
 3 => "university department wholly concerned with children",
 4 => "university department partially concerned with children",
 5 => "research policy institution/organization",
);

%service_types =
(
 1 => "documentation centre open to public",
-1 => "documentation centre not open to public",
 2 =>"document loan",
 3 =>"database searches in-house",
 4 =>"database searches on-line",
 5 => "bibliographical abstracts",
 6 => "photocopying",
 7 => "selective dissemination of information",
 8 => "inter-library loans",
 9 => "research",
);

%fees =
(
"F" => "<b>[fees]</b>",
""  => "",
);

%areas =
(
"I.1"    => "definition of the child (Article 1)",
"I.2"    => "non-discrimination (Article 2)",
"I.3"    => "best interests of the child (Article 3) ",
"I.4"    => "life, survival and development (Article 6)",
"I.5"    => "views of the child (Article 12)",
"II.1"   => "name and nationality (Article 7)",
"II.2"   => "preservation of identity (Article 8)",
"II.3"   => "freedom of expression (Article 13)",
"II.4"   => "information, access to (Article 17)",
"II.5"   => "freedom of thought, conscience and religion (Article 14) ",
"II.6"   => "freedom of association and of peaceful assembly (Article 15)",
"II.7"   => "privacy (Article 16)",
"II.8"   => "torture or other cruel, inhuman or degrading treatment or punishment (Article 37 a)",
"III.1"  => "parental guidance and the child's evolving capacities (Article 5)",
"III.2"  => "parental responsibilities (Article 18, §1-2)",
"III.3"  => "separation from parent(s) (Article 9)",
"III.4"  => "family reunification (Article 10)",
"III.5"  => "recovery of maintenance for the child (Article 27, §4)",
"III.6"  => "children deprived of their family environment (Article 20)",
"III.7"  => "adoption (Article 21)",
"III.8"  => "illicit transfer and non-return of children abroad (Article 11)",
"III.9"  => "abuse and neglect (Article 19)",
"III.10" => "periodic review of placement (Article 25)",
"IV.1"   => "life, survival and development (Article 6, §2)",
"IV.2"   => "disabled children (Article 23)",
"IV.3"   => "health and health care services (Article 24)",
"IV.4"   => "social security and child care services (Articles 26, 18, §2)",
"IV.5"   => "standard of living (Article 27, §1-3)",
"V.1"    => "education (Article 28)",
"V.2"    => "aims of education (Article 29)",
"V.3"    => "leisure, recreation and cultural activities (Article 31)",
"VI.1"   => "refugee children (Article 22) ",
"VI.2"   => "children in armed conflicts (Article 38)",
"VI.3"   => "administration of juvenile justice (Article 40)",
"VI.4"   => "children deprived of their liberty (Article 37 b,c,d)",
"VI.5"   => "sentencing of juveniles (in particular the prohibition of capital punishment and life imprisonment) (Article 37a)",
"VI.6"   => "recovery and social reintegration (Article 39)",
"VI.7"   => "economic exploitation (including child labour) (Article 32)",
"VI.8"   => "drug abuse (Article 33)",
"VI.9"   => "sexual exploitation and sexual abuse (Article 34)",
"VI.10"  => "other forms of exploitation (Article 36)",
"VI.11"  => "sale, trafficking and abduction (Article 35)",
"VI.12"  => "children belonging to a minority or indigenous group (Article 30)",
"VII.1"  => "monitoring children's rights (Articles 43,44,45)",
"VII.2"  => "legislation on children (Article 4)",
 );

%area_heading = (
"I"   => "General principles",
"II"  => "Civil Rights and freedoms",
"III" => "Family environment and alternative care",
"IV"  => "Basic health and welfare",
"V"   => "Education, leisure and cultural activities",
"VI"  => "Special protection measures",
"VII" => "Other subjects",
);

%holdings = (
"M" => "monographs",
"P" => "periodicals",
"N" => "newspapers/clippings",
"R" => "reports",
"G" => "gray literature",
"D" => "doctoral dissertations",
"V" => "videos",
"A" => "audios",
"S" => "statistical data",
);

}; #--- BEGIN

sub split_query     # updates the %query array
{
    local($query) = shift;
    local($name, $value);
    for (split(/&/, $query)) {
        s/\+/ /g;
	($name, $value) = split(/=/, $_);
        ($name, $value) = ("isindex", $name) unless defined $value;
        $name  =~ s/%([\da-f][\da-f])/pack("C",hex($1))/gei;
        $value =~ s/%([\da-f][\da-f])/pack("C",hex($1))/gei;

        unless (defined $query{$name})  { $query{$name} = $value }
        else { $query{$name} = $query{$name} . "\0" . $value }

    }
}
