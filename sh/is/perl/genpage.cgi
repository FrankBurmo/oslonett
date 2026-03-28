#!/local/bin/perl


#
# Finn path, hvor html-treet starter, katalogfil og kategorinr. 
#
$path=$ENV{'PWD'};
$index_root="/local/www/sh/is/";

$basket="http:\/\/www.oslonett.no/sh/is/kurv/kurv.html";

$this_program_name="genpage.cgi";
$kat_file=join("",$index_root,"katalog/avdelingsbase.txt");
$prod_file=join("",$index_root,"katalog/produktbase.txt");
$header_dir="header/";
$footer_dir="footer/";


$kat = $ARGV[0];

# 1. underkategori
$_=$kat;
/^(\d+.\d+)/;
$ukat = $1;

# Hvor dypt er treet?
@KAT = split(/\./,$kat);
$depth=scalar(@KAT);

if ($depth = 4) {
    $uukat=$kat;
} else {
    $_=$kat;
    /^(\d+.\d+.\d+)/;
    $uukat = $1;
}


# Hvilken hovedkategori skal vi ha? (utheves grafisk med inntrykket knapp)
$hkat=$KAT[0];

open(STDERR, "/dev/null");

# Les inn katalogfil
open(FIL,"<$kat_file") || die "Not able to open $kat_file\n";
open(PROD_FILE,"<$prod_file") || die "Not able to open $prod_file\n";
 
@KATALOG=<FIL>;

# Les inn alle aktuelle kategorier 

$count1=$count2=$count3=0;

foreach $_ (@KATALOG) {
    # Hovedkategoriene:
    if (/^(\d)\#/) {
	$HOVEDKAT[$count1++]=$_;
    }
    if (/^($hkat).(\d+)\#/) {
	$UNDERKAT[$count2++]=$_;
    }
    if (/^($ukat).(\d+)\#/) {
	$UNDERUNDERKAT[$count3++]=$_;
    }
}



# Lag referanse til alle hovedikonene - husk at et ikon skal utheves!
$count=0;
foreach $_ (@HOVEDKAT) {
    chop;
    @TMP = split(/\#/);
    $par=$TMP[0];
    $TMP[1]=~ tr/a-z/A-Z/;
    $TMP[1]=~ tr/זרו/ֶ״ֵ/;

    if ($par eq $hkat) {
	# Uthev dette ikonet spesielt
	$HOVED_IKONER[$count] = join("", "<a href=\"", $this_program_name, "\?", $count+1, ".1.1","\"><img src\=\"gifs\/$TMP[3]i.gif", "\" border=0></a>");
	$k_navn=$TMP[1];
    } else {			
	$HOVED_IKONER[$count] = join("", "<a href=\"", $this_program_name, "\?", $count+1, ".1.1","\"><img src\=\"gifs\/$TMP[3].gif", "\" border=0></a>");
    }
    $count++;
}




# Lag referanse til alle underkategoriene
$count=0;
foreach $_ (@UNDERKAT) {
    chop;
    @TMP = split(/\#/);
    $par=$TMP[0];
    $TMP[1]=~ tr/a-z/A-Z/;
    $TMP[1]=~ tr/זרו/ֶ״ֵ/;

    # Vi mו fremheve den kategorien vi er i spesielt. 

    if ($par eq $ukat) {
	$U_LINJE[$count++] = join("", "<img src=gifs/ar.gif><a href=\"", $this_program_name, "\?$par.1", "\"><b><i>$TMP[1]", "</b></i></a><img src=gifs/al.gif>  ");
	$uk_navn=$TMP[1];
    } else {
	$U_LINJE[$count++] = join("", "<a href=\"", $this_program_name, "\?$par.1",  "\">$TMP[1]", "</a>  ");
    }
}




# Lag referanse til alle underunderkategoriene
$count=0;
foreach $_ (@UNDERUNDERKAT) {
    chop;
    @TMP = split(/\#/);
    $par=$TMP[0];
    $TMP[1]=~ tr/a-z/A-Z/;
    $TMP[1]=~ tr/זרו/ֶ״ֵ/;

    # Vi mו fremheve den kategorien vi er i spesielt.
    if ($par eq $uukat) {
	$UU_LINJE[$count++] = join("", "<img src=gifs/ar.gif><a href=\"", $this_program_name, "\?$par", "\"><b><i>$TMP[1]", "</b></i></a><img src=gifs/al.gif>  ");
	$uuk_navn=$TMP[1];
    } else {
	$UU_LINJE[$count++] = join("", "<a href=\"", $this_program_name, "\?$par",  "\">$TMP[1]", "</a>  ");
    }
}


# Lag title-tag...
$title = join("",$k_navn," - ",$uk_navn," - ",$uuk_navn);

# Lag body-tag...
$body_tag = "<body bgcolor=\"#ffffbb\" link=\"#ff2000\" vlink=\"#ff2000\" >";

&header;
&table;
&footer;


##
## Genererer header utifra kategoriparameter...
##


sub header {

    print "Content-type: text/html\n\n";
    print "
<html>
<head>
<title>
$title
</title>
</head>

$body_tag

<hr size=\"1\" noshade>
<table border=\"0\" width=\"100%\" align=\"right\">
<tr>
<td valign=\"top\" align=\"left\">
<a href=\"index.html\"><img src=\"gifs/rsi.gif\" border=\"0\"></a>
</td>

<td valign=\"top\" align=\"right\">\n";

# Skriv ut alle toppikonene...

    print @HOVED_IKONER,"\n<br>\n";

# Skriv ut underkategoriene...
    print "<font size=\"+0\">\n";
    print @U_LINJE;
    print "</font><p>\n";

# Skriv ut underunderkategoriene...
    print "<font size=\"-1\">\n";
    print @UU_LINJE;
    print "</font>";

# ... og slutten pו headeren
    print "
<br>
<a href=\"info.html\"><img src=\"gifs/inf.gif\" border=\"0\"></a><a href=\"oversikt.html\"><img src=\"gifs/oversikt.gif\" border=\"0\"></a><a href=\"soek.html\"><img src=\"gifs/soek.gif\" border=\"0\"></a><a href=\"nyheter.html\"><img src=\"gifs/nyheter.gif\" border=\"0\"></a>
</td>
</tr>
</table>

<hr size=2 noshade>


";


    return;
}


#
# Genererer selve innholdet pו produktsiden, gitt kategoriparameter
#
sub table {

    # Start tabell...
    print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"2\"> ";
    print "
<tr><td><strong>Varenr.<\/strong><\/td>
<td><strong>Navn<\/strong><\/td>
<td><strong>Pris<\/strong><\/td>
<td><strong>Handlekurv:<\/strong><\/td><\/tr>";

    # Skriv ut alle feltene...

    while(<PROD_FILE>) {
	if (/^$kat\.*/) {
	    ($varenr,$navn,$pris,$bilde,$beskriv)=split(/\#/);
	    print "\n<tr><td>\n";
	    print "$varenr <\/td><td> <a href=\"prodside.cgi?$varenr\">$navn<\/a><\/td><td> $pris <\/td><td><a href=\"\/kurv\/hent.cgi/intershop/$varenr\">Legg i kurven<\/a>";
	    print "\n<\/td><\/tr>\n";
	    
	}
    }

    # Avslutt tabell...
    print "
<\/td>
<\/tr>
<\/table>";

    return;
}


#
# Genererer footeren til produktsiden, gitt kategoriparameter
#
sub footer {

    print "
<br><br>
<p>
<table border=\"0\" width=\"100%\">
<tr>
<td align=\"left\">
<a href=\"\"><img src=\"gifs/big_button.gif\" border=\"0\"></a>
</td>
</tr>
</table><p>
<address>
<font size=\"-1\">
Oslonett AS</address>

</body>
</html>

";
    return;
}




#print @UNDERKAT,"\n\n";
#print @UNDERUNDERKAT,"\n\n";
#print @HOVED_IKONER,"\n\n";
#print @U_LINJE,"\n";
#print @UU_LINJE, "\n";
#print "$hkat, $ukat, $uukat \n\n";
exit(0);



