#!/local/bin/perl

# Genpage
#
# (c) 1995 Kent Vilhelmsen
# Modifikasjoner for tilpasning til handlekurv ved KGN
#
# Oppdatert 1996, februar

# Finn path, hvor html-treet starter, katalogfil og kategorinr. 

$path=$ENV{'PWD'};
$index_root="/local/www/sh/is/";

$KURV_HENT	= "/kurv/hent.cgi";
$KURV_DIR	= "/local/www/kurv/kunder";
$KURV_INNHOLD	= "/local/www/kurv/innhold.pl";

$NOCHECKGIF	= "/kurv/gifs/nocheck.gif";
$CHECKGIF	= "/kurv/gifs/check.gif";
$BUTIKK_ID	= "intershop";
$URL_PATH	= "/sh/is";

$this_program_name=$ENV{'SCRIPT_NAME'};
$kat_file=join("",$index_root,"katalog/avdelingsbase.txt");
$prod_file=join("",$index_root,"katalog/produktbase.txt");
$header_dir="header/";
$footer_dir="footer/";

# Neste linje virker kun for method="GET". Bør gi feilmelding hvis dette
# ikke er tilfelle eller bruke read(STDIN, $kat, $ENV{'CONTENT_LENGTH'}
# hvis method="POST".

$kat = $ENV{'QUERY_STRING'};

# Trenger å kunne dekode handlekurv-id hvis man skal vise i kurv/ikke i kurv
$id = $1 if $ENV{HTTP_COOKIE} =~ /kurvid=(\d+)/;


foreach ( split(/\n/, `$KURV_INNHOLD $id` ) ) {
    $ikurv{ $_ } = 1 if s!/intershop/!!;
}

# $DEBUG = 1;
if ($DEBUG) {
    print "Content-type: text/html\n\n";
    print "<pre>\nid=$id\nkat=$kat\nargv0=$ARGV[0]\n";

    print "cookie(s): $ENV{HTTP_COOKIE}\n";
    print "$KURV_INNHOLD:\n";
    print join("\n", %ikurv);
    exit 0;
}




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
 


# Les inn oversikt over avdelingene
open(FIL,"<$kat_file") || die "Not able to open $kat_file\n";
open(PROD_FIL,"<$prod_file") || die "Not able to open $prod_file\n";
 
@TMP_KAT = <FIL>;
@KATALOG = ();
$count=0;
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
    $KATALOG[$count++] = $in;
    $in = "";			   
}

# Les inn alle produktene i en array og sørg for å fjerne dobbel-dollar bak hver av dem
@TMP_PROD = <PROD_FIL>;
@PROD_LIST = ();
$count=0;
foreach (@TMP_PROD) {
    next if /^\s*$/;
    # Alle linjer skal slutte med $$. Hvis ikke, slå sammen denne og (de) neste
    # linje(r), til vi får avsluttet med $$.
    if (!/.*\$\$$/) {		
	$in=$in.$_;
	next;
    }	
    s/\$\$//;
    $in=$in.$_;
    $PROD_LIST[$count++] = $in;
    $in = "";			   
}


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
foreach (@HOVEDKAT) {
    chop;
    @TMP = split(/\#/);
    $par=$TMP[0];
    $TMP[1]=~ tr/a-z/A-Z/;
    $TMP[1]=~ tr/æøå/ÆØÅ/;
    
    if ($par eq $hkat) {
	# Uthev dette ikonet spesielt
	$HOVED_IKONER[$count] = join("", "<a href=\"", $this_program_name, "\?", $par, ".1.1","\"><img src=\"$URL_PATH/gifs\/$TMP[3]i.gif", "\" border=0></a>");
	$k_navn=$TMP[1];
    } else {			
	$HOVED_IKONER[$count] = join("", "<a href=\"", $this_program_name, "\?", $par, ".1.1","\"><img src\=\"$URL_PATH/gifs\/$TMP[3].gif", "\" border=0></a>");
    }
    $count++;
}


# Lag referanse til alle underkategoriene
$count=0;
foreach (@UNDERKAT) {
    chop;
    @TMP = split(/\#/);
    $par=$TMP[0];
    $TMP[1]=~ tr/a-z/A-Z/;
    $TMP[1]=~ tr/æøå/ÆØÅ/;

    # Vi må fremheve den kategorien vi er i spesielt. 
    # Sjekk om vi har noen underkategorier først
    $par =~ s/(\d\.\d)\.\d/$1/ if $#UNDERUNDERKAT;

    if ($par eq $ukat) {
	$U_LINJE[$count++] = join("", "<img src=$URL_PATH/gifs/ar.gif><a href=\"", $this_program_name, "\?$par.1", "\"><b><i>$TMP[1]", "</b></i></a><img src=$URL_PATH/gifs/al.gif>  ");
	$uk_navn=$TMP[1];
    } else {
	$U_LINJE[$count++] = join("", "<a href=\"", $this_program_name, "\?$par.1",  "\">$TMP[1]", "</a> || ");
    }
}




# Lag referanse til alle underunderkategoriene
$count=0;
foreach $_ (@UNDERUNDERKAT) {
    chop;
    @TMP = split(/\#/);
    $par=$TMP[0];
    $TMP[1]=~ tr/a-z/A-Z/;
    $TMP[1]=~ tr/æøå/ÆØÅ/;

    # Vi må fremheve den kategorien vi er i spesielt.
    if ($par eq $uukat) {
	$UU_LINJE[$count++] = join("", "<img src=$URL_PATH/gifs/ar.gif><a href=\"", $this_program_name, "\?$par", "\"><b><i>$TMP[1]", "</b></i></a><img src=$URL_PATH/gifs/al.gif>  ");
	$uuk_navn=$TMP[1];
    } else {
	$UU_LINJE[$count++] = join("", "<a href=\"", $this_program_name, "\?$par",  "\">$TMP[1]", "</a>  | ");
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
<table border=\"0\" width=\"100%\">
<tr>
<td valign=\"top\" align=\"left\">
<a href=\"is2.map\"><img src=\"gifs/rsi_new.gif\" border=\"0\" alt=\"InterShop\" ISMAP><br>[til forsiden]</a>
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

# ... og slutten på headeren
    print "
<br>

</td>
</tr>
</table>

<hr size=2 noshade>

Velg et produkt ved å klikke på \"I kurven\" under Handlekurv. Hvis du ønsker å sende en bestilling går du inn på <a href=\"/kurv/vis.cgi\">bestillingskjemaet</a><p>
";


    return;
}


#
# Genererer selve innholdet på produktsiden, gitt kategoriparameter
#
sub table {

    # Start tabell...
    print "<table border=\"1\" cellspacing=\"2\" cellpadding=\"2\"> ";
    print "
<tr>
<td><strong>Navn<\/strong><\/td>
<td><strong>Pris (inkl. mva)<\/strong><\/td>
<td><strong>Handlekurv:<\/strong><\/td><\/tr>";

    # Skriv ut alle feltene...

    foreach (@PROD_LIST) {
	if (/^$kat\.*/) {
	    ($varenr,$navn,$pris,$bilde,$beskriv)=split(/\#/);

	    $gifimg = $ikurv{$varenr} ? $CHECKGIF : $NOCHECKGIF;
	    print "<tr>";
	    # Test om vi skal ha med pris eller ikke...
	    if ($pris eq "") {
		print qq!
<td colspan=4><b><font size=+1>$navn</font></b></td>
</tr>
    !;


	    } else {
		print qq!

<td> <a href="$URL_PATH/prodside.cgi?$varenr">$navn</a></td>
<td align="right"> $pris,- </td>
<td align="center"><a href="$KURV_HENT/$BUTIKK_ID/$varenr?ref=$ENV{SCRIPT_NAME}%3F$kat">
I kurven: <img border="0" align="absbottom" alt="" src="$gifimg"></a></td>
</tr>
                !;				
	    }
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
<a href=\"$URL_PATH/menu.map\"><img src=\"$URL_PATH/gifs/big_button.gif\" border=\"0\" ismap></a>
</td>
</tr>
</table><p>
<address>
<hr>
<table border=0 width=100%>
<tr><td align=center>
<a href=\"/\">
 <img alt=\"[SN Horisont]\" src=\"/img/horisont.gif\" border=0></a></td>
<td align=center><a href=\"/sn/\"><img alt=\"[SchibstedNett AS]\" src=\"/img/snikon.gif\" border=0></a></td></tr>
</table>

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



