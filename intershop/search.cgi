#!/local/bin/perl5


# search.pl - søker gjennom kategori- og avdelingsdatabase for et firma. 
# Opprinnelig laget for InterShop (Ronny Sørensen)
#
# 1995 Kent Vilhelmsen
#


# Finn path, hvor html-treet starter, katalogfil og kategorinr. 

$path=$ENV{'PWD'};
$INDEX_ROOT="/local/www/sh/is/";

$KAT_FILE  = $index_root . "katalog/avdelingsbase.txt";
$PROD_FILE = $index_root . "katalog/produktbase.txt";
open(STDERR, "/dev/null");


# Neste linje virker kun for method="POST". Bør gi feilmelding hvis dette
# ikke er tilfelle eller bruke $kat = $ENV{'QUERY_STRING'};
# hvis method="GET".

read(STDIN, $buffer, $ENV{'CONTENT_LENGTH'});

@pairs = split(/&/, $buffer);

foreach $pair (@pairs)
{
    ($name, $value) = split(/=/, $pair);

    # Un-Webify plus signs and %-encoding
    $value =~ tr/+/ /;
    $value =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;

    # Stop people from using subshells to execute commands
    # Not a big deal when using sendmail, but very important
    # when using UCB mail (aka mailx).
    # $value =~ s/~!/ ~!/g; 

    # Uncomment for debugging purposes
    print "Setting $name to $value<P>";

    $FORM{$name} = $value;
}

print "Content-type: text/html\n\n"; 
$|=1;

$sokeord=$FORM{'text'};

&do_search;
&write_header;
&write_contents;
&write_footer;
exit 0;

#
# Her kommer etpar kommentarer til selve programstrukturen:
# Dermed skulle det hele være i orden til neste gang...

sub do_search {
    local($_, @KAT, @PRO);

    # OK, da raser vi gjennom databasen...
    return 0 if !open(KFIL,"<$KAT_FILE");
    return 0 if !open(PFIL,"<$PROD_FILE");
 
@TMP_KAT = <KFIL>;
@KAT = ();
$count = 0;
# Les gjennom kategori/avdelingsfilen for å sjekke om noen linjer må slås sammen
foreach (@TMP_KAT) {
    next if /^\s*$/;
    # Alle linjer skal slutte med $$. Hvis ikke, slå sammen denne og (de) neste
    # linje(r), til vi får avsluttet med $$.
    if (!/.*\$\$$/) {		
	$in=$in.$_;
	next;
    }	
    s/\$\$//;
    $in=$in.$_;
    $KAT[$count++] = $in;
    $in = "";			   
}

# Les inn alle produktene i en array og sørg for å fjerne dobbel-dollar bak hver av dem
@TMP_AVD = <PFIL>;
@PRO = ();
$count = 0;
foreach (@TMP_AVD) {
    next if /^\s*$/;
    # Alle linjer skal slutte med $$. Hvis ikke, slå sammen denne og (de) neste
    # linje(r), til vi får avsluttet med $$.
    if (!/.*\$\$$/) {		
	$in=$in.$_;
	next;
    }	
    s/\$\$//;
    $in=$in.$_;
    $PRO[$count++] = $in;
    $in = "";			   
}



    close(KFIL);
    close(PFIL);

    $kcount = $pcount = 0;
    foreach (@KAT) {
	$KFOUND[$kcount++] = $_ if /\b\Q$sokeord\E\b/i;
    }

    foreach (@PRO) {
	$PFOUND[$pcount++] = $_ if /\b\Q$sokeord\E\b/i;
    }
    
    # Sorter kategorier og produkter alfabetisk:
#    @SORTED = sort ( 



    close(KFIL);
    close(PFIL);

    return 1;
}


sub write_header {
    print qq!
<html> <head>
<title>RS intershop - sok</title>
</head>
<body bgcolor="#119955">
<table border="0" width="100%">
<tr>
<td valign="top">
<a href="index.html"><img src="gifs/rsi.gif" border=0></a>
</td>
<td valign=center>
<h1>Søkeresultat</h1>
</td>
</tr>
</table>

<hr size=2 noshade>
<table width="100%"  border="0">
<tr><td valign=top align=right>
<pre><a href="oversikt.cgi"><img src="gifs/oversikt.gif" border="0"></a><a href="soek.html"><img src=gifs/soek.gif border=0></a><a href="nyheter.html"><img src=gifs/nyheter.gif border=0></a>
</pre>
</td></tr>
</table>
    !;
    return;
}

sub write_contents {
    local($_);

    print "</blockquote>\n\n";

    print "<p><h2>Aktuelle produkter: </h2><p>\n<blockquote>\n";
    foreach $i (@PFOUND) {	   
	# Lag liste med URL og full pakke...
	@j = split(/\#/,$i);
	print "<a href=\"prodside.cgi\?$j[0]\">$j[1]</a><p>\n";
    }
    print "</blockquote>\n\n";

    return;
}


sub write_footer {
    print qq!
</body>
</html>
    !;
    return;
}














































