#!/local/bin/perl5


#----------------------------------------------------------------------
#
# index.cgi
#
# Viser hovedsiden for vedlikeholdssystemet for Intershop
#
# (c) Kent Vilhelmsen, Schibsted Nett, Desember 1995
#----------------------------------------------------------------------


# Loggfiler som holder oversikt over oppdateringer i databasene
$CONTLOG = "contentsbase.log";

# Her er databasefilene
$INDEX_ROOT="/local/www/sh/is/";
$PROD_FILE = $index_root . "katalog/produktbase.txt";
$AVD_FILE  = $index_root . "katalog/avdelingsbase.txt";




# Konfigurasjonsfil som viser hvordan systemet er satt opp
$CONFFILE = "web.cfg";

# Finn div. systeminformasjon

$HOME_UPDATED = "unknown";	# Finn når index.html ble endret sist vha. ls -l
$CONT_UPDATED = "unknown";      # Finn når BASER/kategoridb.txt sist ble endret
$CFG_UPDATED  = "unknown";      # Finn når konfigurasjonsfilen web.cfg sist ble endret

# open(STDERR, "/dev/null");

# Les informasjon fra konfigurasjonsfilen inn i en assosiativ array
open(CFGFIL, "<$CONFFILE") || die "Kan ikke åpne konfigurasjonsfilen!";
while (<CFGFIL>) {
    @TMP=split(/\#/);
    @CONF{$TMP[0]} = $TMP[1];
}


&write_header;
&write_menu;
&write_footer;




#--------------------------------------------------
# write_header - skriver header for HTML-dokument
#--------------------------------------------------
sub write_header {
    print "Content-type: text/html\n\n";
    print qq!
<html>
<head>
<title>
Vedlikeholdssider for Schibsted Nett Horisont
</title>
</head>
<body bgcolor=#ffffff>
<h2>Dynamisk Web - kontrollprogram</h2>
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
<font size="+1"><a href="forside.cgi">FORSIDE</a></font>
<blockquote>
    Siste oppdatering: <b>$HOME_UPDATED</b> <br>
	Siste registrerte oppdatering: <b> $CONF{"HOME_UPDATED"}</b>, $CONF{"HOME_UPDATED_BY"}
</blockquote><p>
	!;

    # Innholdsdatabasen
    print qq!
<font size="+1"><a href="innhold.cgi">INNHOLDSDATABASE</a></font>
<blockquote>		
    Siste oppdatering: <b>$CONT_UPDATED</b> <br>
	Siste registrerte oppdatering: <b> $CONF{"CONT_UPDATED"}</b>, $CONF{"CONT_UPDATED_BY"}
</blockquote><p>
    !;

    # Malfiler
    print qq!
<font size="+1"><a href="malfiler.cgi">MALFILER</a></font>
<blockquote>

</blockquote><p>
	!;

    # Generering
    print qq!
<font size="+1">GENERERING AV SIDER</font>
<blockquote>
<a href="gpg.cgi">Generer sider for både Netscape og Mosaic</a><br>
<a href="gpg.cgi?n">Generer sider for Netscape</a><br>
<a href="gpg.cgi?m">Generer sider for Mosaic</a><br>
<form method="POST" action="gpg.cgi?t">
<b>Generer <b>testside</b> for kategorinr.: <br></b>
<pre><input size=8 name="kategori"> <select name=type><option>Netscape</option><option>Mosaic</option></select> <input type="SUBMIT" value="Generer testside"></pre>

</blockquote>
	!;

    # Konfigurasjonsfiler
    print qq!
<hr size=2 noshade>
<font size="+1"><a href="konfigfiler.cgi">KONFIGURASJONSFILER</a></font>
<blockquote>
Siste oppdatering: <b>$CFG_UPDATED</b><br>
    Siste registrerte oppdatering: <b>$CONF{"CFG_UPDATED"}</b>, $CONF{"CFG_UPDATED_BY"}
</blockquote>
<hr size=2 noshade>
<p>
    !;

    return;
}


#--------------------------------------------------
# write_footer - skriver footer for HTML-dokument
#--------------------------------------------------
sub write_footer {

    print qq!
(C) 1995 Schibsted Nett
</body>
</html>
    !;	     

    return;
}


