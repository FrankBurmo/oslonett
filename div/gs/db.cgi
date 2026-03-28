#!/local/bin/perl5

# Dette er WWW grensesnittet mot Sybase til EuroCalls Gule Sider. Skriptet
# benytter sybperl som gir tilgang til Sybase sitt DB-Library.
#
# © 1995 Schibsted Nett AS, Gisle Aas
#
# $Id: db.cgi,v 1.13 1996/01/19 15:37:03 aas Exp $

# Sørger for å få ut headere så tidlig som mulig.  Dette hjelper hvis
# det senere oppstår en feil i koden under.
BEGIN {
    local($|) = 1;

    ($ua, $ver) = ($ENV{HTTP_USER_AGENT} =~ m,([^/]+)/(\S+),);
    $SERVERPUSH = ($ua eq "Mozilla" && $ver >= 1.1);
    $SERVERPUSH = 0;  # Dette var allikevel ikke noen god ide
    $boundary="XyZZy$$";

    if ($SERVERPUSH) {
	print "Content-type: multipart/x-mixed-replace;boundary=$boundary

--$boundary
Content-Type: text/html\n\n";
    } else {
	print "Content-Type: text/html\n\n";
    }

    # Dette trengs for at sybperl skal finne Sybase sin "interface" fil
    $ENV{SYBASE} = "/home/frogner/www2/sybase";
}

# Dette er den enkleste måten å få perl til å håndtere Æ, Ø, Å riktig.
# Det virker fint på SunOS4, men man må sikkert finne en annen verdi
# for LC_CTYPE hvis man kjører det på en annen maskintype.
use POSIX;
setlocale(LC_CTYPE, "iso_8859_1");


# Konfigurering av diverse som man kanskje vil ønske å endre en gang i blandt

$DEBUG          = 0;
$FORCE_GLOB     = 1;            # inital maching for every string
$COLOR          = 'bgcolor="#ffffff"';
$LOGO           = 'gifs/guleeurocall_150.gif';
$SEARCH_TRAILER = "trailer-s.html";
$PRES_TRAILER   = "trailer-p.html";
$ERROR_TRAILER  = "trailer-e.html";
$RETTELSE       = 1;

# Sjekk om vi vi egentlig ikke skal kjøre fordi databasen er under
# vedlikehold
&dbdown if -f "/local/www/div/gs/DBDOWN";

# Desverre er det enklest å hardkode hvor vi finner bibliotekene vi vil bruke
use lib "/local/www/div/gs/lib";
use CGI::Query;

$DEBUG = 1 if $query{'debug'};
$GsSQL::SQL_AS_HTML = 1 if $DEBUG;

# Først avgjør vi om vi skal gjøre et enkelt oppslag eller om det er snakk
# om et virkelig søk.
if (defined $query{'nr'}) {
    $nr = $query{'nr'};

    # Direkte oppslag på ett enkelt firma.
    require GsSQL;
    import GsSQL qw(sql);

    $a = sql("
SELECT firma.navn, navn2,
       gateadr, postadr, postnr, poststed.navn,
       info, infolang
  FROM firma, poststed
 WHERE firma.postnr = poststed.nr
   AND firma.nr = '$nr'
")->[0];
    my($navn, $navn2,
       $gateadr, $postadr, $postnr, $poststed,
       $info, $infolang) = @$a;

    if (defined $navn2) {
	$navn = $navn2;
    } else {
	capitalize($navn);
    }
    my $capnavn = cap_font($navn, 5);

    print <<EOT;
<html>
<head>
 <title>Eurocalls Gule Sider - $navn</title>
</head>
<body $COLOR>
<img align=right alt="" src="$LOGO">
<p>$capnavn
EOT
    print "<blockquote>\n";
    $adr = "";
    $besok = "";
    if (defined $postadr) {
	capitalize_addr($postadr);
	$adr .= "$postadr\n";
	if (defined $gateadr) {
	    capitalize_addr($gateadr);
	    $besok = $gateadr;
	    # Når vi både har postadresse og gateadresse så vil vi oppleve
	    # at gateadressens postnr finnes i parentes på slutten av adressen
	    if ($besok =~ s/\s*\((\d+)\)\s*$//) {
		my $nr = $1;
		if ($nr != $postnr) {
		    my $sted = sql("SELECT navn FROM poststed WHERE nr = $nr")
			->[0][0];
		    capitalize($sted);
		    $besok .= ", $nr $sted";
		}
	    }
	}
    } elsif (defined $gateadr) {
	capitalize_addr($gateadr);
	$adr .= "$gateadr\n";
    }
    capitalize($poststed);
    $adr .= sprintf " %04d %s", $postnr, $poststed;
    $adr .= "\n\n<b>Besøksadresse:</b> $besok" if length $besok;
    $adr =~ s/\n/<br>/g;
    print "<font size=+1>$adr<hr>\n";
    print "<p>\n";

    #my(%type) =
    #  (
    #   T => "Telefon",
    #   F => "Telefaks",
    #   M => "Mobil",
    #   E => "E-Post",
    #   X => "E-Post (X.400)",
    #   U => "URL",
    #  );

    my $no = 0;
    sql("SELECT type, nr FROM nettadr WHERE firma = '$nr'",
       sub {
	   my($type, $nr) = @_;
	   if ($type eq "U") {
	       $nr = qq{<a href="$nr">$nr</a>};
	   } elsif ($type eq "E") {
	       $nr = qq{<a href="mailto:$nr">$nr</a>};
           }
	   push(@{$nettadr{$type}}, $nr);
       });
    @x = grep(defined $_, @{$nettadr{'T'}},
	                  map("$_ (mobil)" ,@{$nettadr{'M'}}));
    print "<table cellspacing=0>\n";
    if (@x) {
	print "<tr><td valign=top><b>Telefon: </b></td><td>";
	print join("<br>", map{ s/(\d\d)/$1 /g; $_} @x);
	print "</td></tr>\n";
    }
    @x = grep(defined $_, @{$nettadr{'F'}});
    if (@x) {
	print "<tr><td valig=top><b>Telefaks: </b></td><td>";
	print join("<br>", map{ s/(\d\d)/$1 /g; $_} @x);
	print "</td></tr>\n";
    }
    @x = grep(defined $_, @{$nettadr{'E'}}, @{$nettadr{'X'}});
    if (@x) {
	print "<tr><td valig=top><b>E-Post: </b></td><td>";
	print join("<br>", @x);
	print "</td></tr>\n";
    }
    @x = grep(defined $_, @{$nettadr{'U'}});
    if (@x) {
	print "<tr><td valign=top><b>URL: </b></td><td>";
	print join("<br>", @x);
	print "</td></tr>\n";
    }
    print "</table>\n";
    print "</font>\n";
    
    $info = $infolang if defined $infolang;

## AUTO URL linking
    if (defined $info) {
        $info =~ s%((http|ftp|gopher)://(\S+[\w/]))(\.?[\s,<])%<a href=$1>$1</a>$4%gi;
        $info =~ s%(\S+\@\S+)%<a href=mailto:$1>$1</a>%gi;
	print "<pre>$info</pre>\n";
    }

    my @ord = ();
    sql("SELECT stikkord.ord
FROM stikkord, stikkreg
WHERE stikkord.nr = stikkreg.ord
  AND firma = '$nr'",

	sub{  push(@ord, shift)	}
       );
    if (@ord) {
	print "<p><b>Stikkord:</b> ", join(", ", @ord), "\n";
    }
    print "</blockquote>\n";
    if ($RETTELSE) {
	($unavn = $navn) =~ s/([\x00-\x20"#%;<>?{}|\\\\^~`\[\]\x7F-\xFF])/sprintf("%%%02X", ord $1)/ge;
	print qq{<p><a href="retting.cgi?nr=$nr&navn=$unavn">Skal noe av dette endres?</a>\n};
    }
    if (open(T, $PRES_TRAILER)) {
	print while <T>;
    }
    print "</body></html>\n";
    exit;
}


#--------------------------------------------------------------------------
# Her begynner vi hvis vi virkelig skal lage et søk mot databasen.

print "<html>\n<head>\n <title>Eurocalls Gule Sider - avansert søk</title>\n";
print "</head>\n<body $COLOR>\n";
print qq{<img align=right alt="" src="$LOGO">\n};
# Skal søke etter firma basert på søkekriteriene som er gitt.  Aller først
# begynner vi med å konstruere en passende SQL setning.

($postnr, $poststed, $firmanavn, $stikkord) = 
  @query{'postnr', 'poststed', 'firmanavn', 'stikkord'};

$sql_pre = "SELECT firma.nr, firma.navn, navn2,
       gateadr, postadr, postnr, poststed.navn
";
push(@used_tables, "firma", "poststed");
$sql = "WHERE firma.postnr = poststed.nr
";

# Prosesser postnr
if (length $postnr) {
    $postnr =~ s/(\d)[+,\s]+(\d)/$1,$2/g;
    $postnr =~ s/\s+//g;
    @postnr = ();
    @interval = ();
  POSTNR:
    for (split(',', $postnr)) {
	next if /[^\d\-]/;  # illegal chars in spec
	if (/-/) {
	    ($min, $max) = split('-', $_);
	    if ($min == $max) {
		push(@postnr, $min);
		next POSTNR;
	    }
	    if (length $min && length $max) {
		if ($min > $max) {
		    # swap values
		    my $tmp = $min;
		    $min = $max;
		    $max = $tmp;
		}
		push(@interval, "postnr BETWEEN $min AND $max");
	    } elsif (length $min) {
		push(@interval, "postnr >= $min");
	    } elsif (length $max) {
		push(@interval, "postnr <= $max");
	    }
	} else {
	    next POSTNR unless length $_;
	    push(@postnr, $_);
	}
    }
    # Lets construct some SQL
    if (@postnr) {
	push(@interval, "postnr IN (" . join(",", @postnr) . ")");
    }
    $postnr = join(" OR ", @interval);
    $sql .= "  AND ($postnr)\n" if length $postnr;
}

if ($firmanavn !~ /^\s*$/) {
    my $tree = parse($firmanavn);
    simplify_syntax($tree);
    $firmanavn = gen_sql($tree, "firma.navn");
    $sql .= "  AND $firmanavn\n";
}

if ($poststed !~ /^\s*$/) {
    my $tree = parse($poststed);
    simplify_syntax($tree);
    $poststed = gen_sql($tree, "poststed.navn");
    $sql .= "  AND $poststed\n";
}

if ($stikkord !~ /^\s*$/) {
    my $tree = parse($stikkord);
    simplify_syntax($tree);
    $stikkord = gen_sql($tree, "stikkord.ord");
    $sql .= "  AND $stikkord\n";
}

 $sql .= "ORDER BY firma.navn\n";


if ($SERVERPUSH) {
    local($|) = 1;
    print "<h1>Sender søket til databasen</h1><pre>$sql</pre>
<h3>Straks tilbake med svar....</h3>
";
    print "\n--$boundary\nContent-Type: text/html\n\n";
    sleep(2);
}

# OK, det var det.  Nå prøver vi å koble opp mot databasen:
require GsSQL;
import GsSQL qw(sql);

$rowcount = $query{'rowcount'} || 20;
# Hardkoding av maksimum og minimumsverdier
$rowcount = 500 if $rowcount > 500;
$rowcount = 5 if $rowcount < 5;

# Nå sendes søket til databasen
$count = 0;
sql("set rowcount $rowcount
SELECT DISTINCT 
      firma.nr, firma.navn, navn2, gateadr, postadr, postnr, poststed.navn
 FROM " . join(", ", @used_tables) . "
$sql",

sub  # Denne kalles for hver rad som returneres
{
    my($nr, $navn, $navn2, $gateadr, $postadr, $postnr, $poststed) = @_;
    $nr =~ s/\s+$//;

    unless ($count++) {
	local($|) = 1;
	print "<h1>" . cap_font("Søkeresultat",6) . "</h1>\n";
	print "<ol>\n";
    }

    if (defined $navn2) {
	$navn = $navn2;
    } else {
	capitalize($navn);
    }
    print qq{<li><a href="db.cgi?nr=$nr"><b>$navn</b></a>};
    if (0 && defined $gateadr) {
	capitalize_addr($gateadr);
	print " $gateadr,";
    }
    if (0 && defined $postadr) {
	capitalize_addr($postadr);
	print " $postadr,";
    }
    capitalize($poststed);
    printf " %04d %s\n", $postnr, $poststed;
});
print "</ul>" if $count;

if ($count == 0) {
    print <<"EOT";
<h1>Søket gav ingen treff</h1>

Det er ingen firmaoppføringer i EuroCalls database som oppfyller de
søkekriteriene du har oppgitt.

EOT
} elsif ($count == $rowcount) {
    print "<p><i><b>NB!</b> Søket avbrutt etter $count treff</i>\n";
} else {
    print "<p><i>$count treff</i>\n";
}
if (open(T, $SEARCH_TRAILER)) {
   print while <T>;
}
print "</body></html>\n";
exit;


sub dbdown
{
    print <<"EOT";
<h1>Databasen er under vedlikehold</h1>

Tjenesten er desverre ikke tilgjengelig.  Snart tilbake!

EOT
    exit;
}



sub error
{
    my($msg, @more) = @_;
    print qq{<img align=right alt="" src="$LOGO">\n};
    print "<h1>$msg</h1>\n";
    print "@more\n";
    if (open(T, $ERROR_TRAILER)) {
       print while <T>;
    }
    exit;
}


sub capitalize
{
    $_[0] =~ s/\b(an?s|edb|)\b/\U$1/g;           # forkortelser
    $_[0] =~ s/\b(\w)/\U$1/g;
    $_[0] =~ s/\b(I|På|Og|For|Mot|Av)\b/\L$1/g;  # småord
    $_[0] =~ s/(\w)'(\w)\b/$1'\L$2/g;            # engelsk genitiv
}

sub capitalize_addr
{
    $_[0] =~ s/\b(\w)/\U$1/g;
    $_[0] =~ s/\b(I|På|Og)\b/\L$1/g;  # småord
    $_[0] =~ s/\Bv\.\s/veien /;
    $_[0] =~ s/\Bg\.\s/gata /;
    $_[0] =~ s/\sV\.?\s/ vei /;
    $_[0] =~ s/\sG\.?\s/ gate /;
    $_[0] =~ s/\bPb\.?\s/Postboks /;
}

sub cap_font   # Netscape HTML kode for å sette fontstørrelser og slikt
{
    my($text, $size) = @_;
    my $big = $size + 1;
    $text =~ s/([A-ZÆØÅ0-9\/]+)/<FONT SIZE=$big>$1<\/FONT>/g;
    $text =~ s/([a-zæøå\-']+)/<font size=$size>\U$1\E<\/font>/g;  #' #emacs
    $text;
}

# The following routines (parse/simplify_syntax/print_syntax/gen_sql)
# all operate on a syntax tree that contains nodes like this:
#
#   ["AND",  R, R, ...]
#   ["OR",   R, R, ...]
#   ["CAT",  R, R]
#   ["NOT",  R]
#   ["EXP",  R]
#   ["EQ",   S]
#   ["LIKE", S]
#   ["NEQ",  S]
#   ["NLIKE",S]
#
# Where "R" is a reference to a new node and "S" is a scalar argument
#
# parse() returns a tree where "AND"/"OR" nodes only contain 2 sub nodes,
# and never returns "NEQ" and "NLIKE" nodes. simplify_syntax() introduce
# these features:
#   ["OR", R, ["OR", R, ["OR", ...]]]  ===>  ["OR", R, R, R,...]
#   same for subsequent AND nodes
#   ["NOT" ["EQ", S]]                  ===>  ["NEQ", S]
#   ["NOT" ["LIKE", S]]                ===>  ["NLIKE", S]


# This routine generates SQL statements from a syntax tree.  It should
# be called with 2 argument; a reference to the top node of the tree, and
# a field value that spesify which field to generate code against.

sub gen_sql
{
    my($node, $field, $level) = @_;
    $level = 0 unless defined $level;
    my $nl = "\n" . (" " x ($level * 2 + 7));
    my $code;
    my($type, @children) = @$node;
    if ($type eq "OR") {
	if ($field eq "stikkord.ord") {
	    $code = "$nl(";
	    my @simpleargs = ();
	    my $first = 1;
	    for (@children) {
		$ctype = $_->[0];
		if ($ctype =~ /^N?(EQ|LIKE)$/) {
		    push(@simpleargs, $_);
		} else {
		    # Hvis vi genererer SQL av denne formen, som etter det
		    # jeg kan se er helt passende, så starter Sybase på et
		    # søk som den aldri blir ferdig med.  Derfor lager vi
		    # heller en feilmelding med det samme:
		    error("Expression too complex");
		    $code .= "${nl}OR " unless $first;
		    $code .= gen_simple_or($field,$nl,@simpleargs)
		      if @simpleargs;
		    $code .= "${nl}OR " if !$first || @simpleargs;
		    $code .= gen_sql($_, $field, $level+1);
		    @simpleargs = ();
		    $first = 0;
		}
	    }
	    if (@simpleargs) {
		$code .= "${nl}OR " unless $first;
		$code .= gen_simple_or($field,$nl,@simpleargs);
	    }
	    $code .= ")";
	} else {
	    $code = "$nl(" .
	      join("${nl}OR ",
		   map {gen_sql($_, $field, $level+1)} @children) .
		     "$nl)";
	}
    } elsif ($type eq "AND" || $type eq "CAT") {
	$code = "$nl(" .
                join("${nl}AND ",
                     map {gen_sql($_, $field, $level+1)} @children) .
                "$nl)";
    } elsif ($type eq "NOT") {
	$code = "${nl}NOT " . gen_sql($children[0], $field, $level+1);
    } elsif ($type eq "EXP") {
	$code = "$nl(" . gen_sql($children[0], $field, $level+1) . "$nl)";
    } else {  # must be EQ/LIKE/NEQ/NLIKE
	my $searchstring = $children[0];
	$searchstring =~ s/'/''/g;  #' # make it a suitable as sql string
	my $op;
	$op = "="    if $type =~ /EQ$/;
	$op = "LIKE" if $type =~ /LIKE$/;
	my $neg = "";
	$neg = "NOT " if $type =~ /^N/;
	if ($field eq "stikkord.ord") {
	    my($sr,$so) = new_stikk_tables();
	    $code = "$nl(firma.nr = $sr.firma AND $sr.ord = $so.nr AND" .
	      "$nl $neg$so.ord $op '$searchstring')";
	} else {
	    $code = "$nl$neg$field $op '$searchstring'";
	}
    }
    $code;
}

sub gen_simple_or
{
    my($field, $nl, @args) = @_;
    my($sr, $so) = new_stikk_tables();
    my $code = "$nl  (firma.nr = $sr.firma AND $sr.ord = $so.nr $nl AND ( ";
    $code .= join("$nl    OR ", map {
	my($type, $searchstring) = @$_;
	$searchstring =~ s/'/''/g;  #' # make it a suitable as sql string
	my $op;
	$op = "="    if $type =~ /EQ$/;
	$op = "LIKE" if $type =~ /LIKE$/;
	my $neg = "";
	$neg = "NOT " if $type =~ /^N/;
	"$neg$so.ord $op '$searchstring'";
      } @args);
    $code .= "$nl ))";
    $code;
}

sub new_stikk_tables
{
    $fieldno++;
    push(@used_tables, "stikkreg sr$fieldno",
	               "stikkord so$fieldno");
    ("sr$fieldno", "so$fieldno");
}


# The following code rearrange a syntax tree so that the representation
# is simpler, without semantics changes.

sub simplify_syntax
{
    my($node) = @_;
    return unless defined $node;
    return unless ref($node);
    my($type, @children) = @$node;

    if ($type eq "EXP") {
	# remove rendundant "EXP" nodes
	my $childtype = $children[0][0];  # there can only be one child
	if ($childtype =~ /^(EXP|NOT|EQ|LIKE)$/) {
	    @$node = @{$children[0]};
	    simplify_syntax($node);
	    return;
	}
    }

    if ($type eq "NOT") {
	# fold ("NOT" "EQ") to "NEQ" and ("NOT" "LIKE") to "NLIKE"
	my $childtype = $children[0][0];  # there can only be one child
	if ($childtype eq "EQ" || $childtype eq "LIKE") {
	    @$node = @{$children[0]};
	    $node->[0] = "N" . $node->[0];
	    return;  # we are at the bottom of the tree
	}
    }

    if ($type eq "OR" || $type eq "AND") {
	# fold subsequent "OR" or "AND" nodes
	my $lastchild = pop(@children);
	while (ref($lastchild) && $lastchild->[0] eq $type) {
	    shift(@$lastchild);
	    push(@children, @$lastchild);
	    $lastchild = pop(@children);
	}
	push(@children, $lastchild);
	@$node = ($type, @children);
    }

    # let's try if we can simplify our children
    for (@children) {
	simplify_syntax($_);
    }
}



# The following code implements a simple recursive descent parser for
# the following language:
#
#    expr   ::= <term>
#               <term> ["and"] <expr>
#               <term> "or" <expr>
#    term   ::= <factor>
#               "not" <factor>
#    factor ::= <searchstring>
#               "(" <expr> ")"
#
# Each "nonterminal" in the gramar is represented by a function below.
# Tokens are read from the global array @tokens.  The current token to
# consider is always found in the $token global variable.

BEGIN {
    @tokens = ();     # tokens
    $token  = undef;  # current token
}

sub parse
{
    my $input = shift;

    # Allow alternative representation for and/or/not
    $input =~ s/&+/ and /g;
    $input =~ s/\|+/ or /g;
    $input =~ s/!/ not /g;
    $input =~ s/\sog\s/ and /gi;
    $input =~ s/\seller\s/ or /gi;
    $input =~ s/\bikkj?e\s/not /gi;

    @tokens = map  { s/^\s+//; s/\s+$//; $_ }   # strip leading/trailing space
	      grep { !/^\s*$/ }                 # remove all space tokens
              split( /(\(|\)|\b(?:and|or|not)\b)/, $input);
    #print "TOKENS: ", join(", ", map { "'$_'" } @tokens), "\n";

    my $expr;
    $token = shift(@tokens);
    eval {
	$expr = expr();
	die "Too many )'s" if defined $token;
    };
    if ($@) {
	$@ =~ s/\s+at\s+.*//;
	error("Syntaks feil", $@);
	$expr = undef;
    }
    $expr;
}

sub expr
{
    die "Empty expression" unless defined $token;
    my $x = term();
    return $x unless defined $token;
    return $x if $token eq ")";
    
    if (lc($token) eq "and") {
	$token = shift(@tokens);
	$x = ["AND", $x, expr()];
    } elsif (lc($token) eq "or") {
	$token = shift(@tokens);
	$x = ["OR", $x, expr()];
    } else {
	$x = ["CAT", $x, expr()];
    }
    $x;
}

sub term
{
    my $x;
    if (lc($token) eq "not") {
	$token = shift(@tokens);
	$x = ["NOT", factor()];
    } else {
	$x = factor();
    }
    $x;
}

sub factor
{
    my $x;
    if ($token eq "(") {
	$token = shift(@tokens);
	$x = ["EXP", expr()];
	die "Missing )" if !defined($token) or $token ne ")";
	$token = shift(@tokens);
    } else {
	die "Syntax error (and)" if lc($token) eq "and";
	die "Syntax error (or)"  if lc($token) eq "or";
	die "Syntax error (not)" if lc($token) eq "not";
	die "Empty factor" if $token eq ")";

	my $op = "EQ";

	$token =~ s/\s+/ /g;
	if ($token =~ /[*%_?\[\]]/) {  # glob
	    $token =~ s/\*/%/g;
	    $token =~ s/\?/_/g;
	    $op = "LIKE";
	} elsif ($FORCE_GLOB) {
	    # we just make it
	    $op = "LIKE";
	    $token .= "%";
	}

	$x = [$op, lc $token];
	$token = shift(@tokens);
    }
    $x;
}

# End of parser

#__END__

# The following procedure pretty-prints a syntax tree on STDOUT.  It is
# useful for debugging.

sub print_syntax
{
    my($node, $level) = @_;
    $level = 0 unless defined $level;
    return unless defined $node;
    print " " x ($level * 2);
    my($type, @children) = @$node;
    print "$type";
    my $nl = 0;
    my $child;
    for $child (@children) {
	if (ref $child) {
	    print "\n" unless $nl;
	    $nl = 1;
	    print_syntax($child, $level+1);
	} else {
	    print " $child";
	}
    }
    print "\n" unless $nl;
}


