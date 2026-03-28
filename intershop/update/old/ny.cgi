#!/local/bin/perl5


# Ny.cgi - legger inn nye produkter i produktbasen
# Opprinnelig laget for InterShop (Ronny Sørensen)
#
# 1995 Dag Wigum (modifisert utgave av search.cgi hos samme butikk)
#


# Finn path, hvor html-treet starter, katalogfil og kategorinr. 

$path=$ENV{'PWD'};
$INDEX_ROOT="/local/www/sh/is/";

$PROD_FILE = join("",$index_root,"katalog/produktbase.txt");
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

$pnr=$FORM{'pnr'};
$navn=$FORM{'navn'};
$pris=$FORM{'pris'};
$beskriv=$FORM{'beskriv'};

&do_enter;
&write_header;
&write_contents;
&write_footer;
exit 0;

#
# Her kommer etpar kommentarer til selve programstrukturen:
# Dermed skulle det hele være i orden til neste gang...

sub do_enter {
    local($_, @KAT, @PRO);

    # OK, da raser vi gjennom databasen...
    return 0 if !open(PFIL,"<$PROD_FILE");

	while <PFIL> do {
		@TMP=split(/#/);
		if ($TMP[0] < $pnr) {
			TMP[0] = 

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
<a href="index.html"><img src="../gifs/rsi.gif" border=0></a>
</td>
<td valign=center>
<h1>Søkeresultat</h1>
</td>
</tr>
</table>

<hr size=2 noshade>
<table width="100%"  border="0">
<tr><td valign=top align=right>
<pre><a href="../oversikt.cgi"><img src="../gifs/oversikt.gif" border="0"></a><a href="../soek.html"><img src=../gifs/soek.gif border=0></a><a href="../nyheter.html"><img src=../gifs/nyheter.gif border=0></a>
</pre>
</td></tr>
</table>
    !;
    return;
}

sub write_contents {
    local($_);

    print "</blockquote>\n\n";

    print "<p><h2>Aktuelle produkter for endring: </h2><p>\n<blockquote>\n";
    foreach $i (@PFOUND) {	   
	# Lag liste med URL og full pakke...
	@j = split(/\#/,$i);
	print "<a href=\"update.cgi\?$j[0]\">$j[1]</a><p>\n";
    }
    print $kcount;
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














































