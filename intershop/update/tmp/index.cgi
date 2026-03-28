#!/local/bin/perl5

#----------------------------------------------------------------------
#
# index.cgi
#
# Viser hovedsiden for vedlikeholdssystemet for Intershop
#
# (c) Kent Vilhelmsen, Schibsted Nett, Desember 1995
#----------------------------------------------------------------------


# Loggfiler som holder oversikt over oppdateringer i produktdatabasen og avd.basen
$CONTLOG = "prodbase.log";
$AVDLOG  = "avdbase.log";

# Her er databasefilene
$INDEX_ROOT="/local/www/sh/is/";
$PROD_FILE = $index_root . "katalog/produktbase.txt";
$AVD_FILE  = $index_root . "katalog/avdelingsbase.txt";

$CONT_UPDATED = "unknown";      

# Konfigurasjonsfil som viser hvordan systemet er satt opp
$CONFFILE = "is.cfg";

# Les informasjon fra konfigurasjonsfilen inn i en assosiativ array
open(CFGFIL, "<$CONFFILE") || die "Kan ikke åpne konfigurasjonsfilen!";
while (<CFGFIL>) {
    @TMP=split(/\#/);
    @CONF{$TMP[0]} = $TMP[1];
}

open(STDERR, "/dev/null");

&write_header;
&write_menu;
&write_footer;

exit(0); # just for fun!


#--------------------------------------------------
# write_header - skriver header for HTML-dokument
#--------------------------------------------------
sub write_header {
    print "Content-type: text/html\n\n";
    print qq!
<html>
<head>
<title>
Vedlikeholdssider for InterShop
</title>
</head>
<body bgcolor=#ffffff>
<hr noshade size=1>
<center>
<h2>Vedlikeholdssider for InterShop</h2>
</center>
<hr noshade size=1>
<p>
    !;				

    return;
}



#--------------------------------------------------
# write_menu - skriver "innholdet" for vedlike-
#              holdssidene
#--------------------------------------------------
sub write_menu {

    # Meny for forsiden
    print qq!
<font size="+1"><b>OPPDATERE/ENDRE FASTE SIDER</b></font>
<blockquote>
<a href="tools.cgi?fastside&forsidelogo">Endre logo på forsiden</a><br>
<a href="tools.cgi?fastside&endrenyhet">Endre nyhetssiden</a><br>
<a href="tools.cgi?fastside&endresiste">Endre siste-nytt siden</a><p>
    Siste oppdatering: <b>$HOME_UPDATED</b> <br>
    Siste registrerte oppdatering: <b> $CONF{"HOME_UPDATED"}</b>, $CONF{"HOME_UPDATED_BY"}
</blockquote><p>
	!;


    # Avdelingsdatabasen
    print qq!
<font size="+1"><b>AVDELINGSDATABASE</b></font>
<blockquote>	
<b>NB:</b><font size=2> Avdelingsoppdateringene er ikke ferdigtestet ennaa, og endringer vil ikke ha noen innvirkning. Maalet er aa faa tid til a gjoere det ferdig i loepet av/over helgen. -Kent<p>	</font>
<a href="tools.cgi?avdeling&oversikt">Oversikt over alle avdelingene</a><br>
<a href="tools.cgi?avdeling&ny">Legg til avdeling</a><br>
<a href="tools.cgi?avdeling&fjern">Fjern avdeling</a><br>
<a href="tools.cgi?avdeling&endre">Endre avdeling</a><p>
    Siste oppdatering: <b>$AVD_UPDATED</b> <br>
	Siste registrerte oppdatering: <b> $CONF{"AVD_UPDATED"}</b>, $CONF{"AVD_UPDATED_BY"}
</blockquote><p>
    !;


    # Produktdatabasen
    print qq!
<font size="+1"><b>PRODUKTDATABASE</b></font>
<blockquote>
<a href="tools.cgi?produkt&oversikt">Oversikt over alle produktene</a><br>
<a href="tools.cgi?produkt&ny">Nytt produkt</a><br>
<a href="tools.cgi?produkt&fjern">Fjern produkt</a><br>
<a href="tools.cgi?produkt&endre">Endre produkt</a><p>
Siste oppdatering: <b>$PROD_UPDATED</b><br>
Siste registrerte oppdatering: <b> $CONF{"PROD_UPDATED"}</b>, $CONF{"PROD_UPDATED_BY"}
</blockquote><p>
	!;

    return;
}


#--------------------------------------------------
# write_footer - skriver footer for HTML-dokument
#--------------------------------------------------
sub write_footer {

    print qq!
<hr size=1 noshade>
(C) 1995 Schibsted Nett
</body>
</html>

    !;	     

    return;
}


