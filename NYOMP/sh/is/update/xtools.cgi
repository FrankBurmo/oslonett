#!/local/bin/perl5

#--------------------------------------------------------------------------------
#
# TOOLS.CGI - program som implementerer en ferdig løsning for oppdatering og 
#             vedlikehold av InterShop's produktdatabase. 
#
#             Programmet tar et antall parametre, som kontrollerer hva som skal
#             skje av oppdateringer, listinger, fjerning av produkter osv. osv. 
#
#             Disse er spesifisert nedenfor:
#
#             Ved kall fra et html-dokument, benytter man tools.cgi?<parametere>
#             Slik antyder man hva man ønsker som neste skjermbilde.
#
#             Inputs via forms er også støttet. Denne input parses og legges i
#             en assosiativ array, slik den er lett å hente frem fra de ulike
#             delene i programmet.
#
# PARAMETRE:
#             produkt - vi ønsker å gjøre noe med et produkt i produktbasen
#                       Eksempel: tools.cgi?produkt&fjern&prod_id
#                                 tools.cgi?produkt&ny
#                                 tools.cgi?produkt&endre
#                                 tools.cgi?produkt&oversikt
#
#             avdeling - vi ønsker å gjøre noe med en avdeling i avdelingsbasen
#                        virker på tilsvarende måte som for produkt, med de samme
#                        tilleggsparameterne. 
#
#             fastside - endring(er) på "faste" sider, som nyheter, forside o.l.
#
#             
# (c) 1995 Kent Vilhelmsen, Shibsted Nett, All Rights Reserved
#--------------------------------------------------------------------------------


# Loggfiler som holder oversikt over oppdateringer i produktdatabasen og avd.basen
$CONTLOG = "prodbase.log";
$AVDLOG  = "avdbase.log";
$INDEX_ROOT="/local/www/sh/is/";
$PROD_FILE = $INDEX_ROOT . "katalog/pb.txt";
$AVD_FILE  = $INDEX_ROOT . "katalog/ab.txt";

$CONT_UPDATED = "unknown";      

open(STDERR, "/dev/null");

# Analyser input/parametre

@PARAMS = split(/\&/,$ENV{'QUERY_STRING'});

# INITIALVERDIER
$first=$second=$third=$fourth=0;

# Her ser vi hvilken type side/data vi skal jobbe mot
$first = 1 if $PARAMS[0] eq "produkt";
$first = 2 if $PARAMS[0] eq "avdeling";
$first = 3 if $PARAMS[0] eq "fastside";

# Hva skal vi gjøre/type av operasjon
$second   = 1 if $PARAMS[1] eq "endre";
$second   = 2 if $PARAMS[1] eq "fjern";
$second   = 3 if $PARAMS[1] eq "ny";
$second   = 4 if $PARAMS[1] eq "oversikt";
$second   = 5 if $PARAMS[1] eq "produktinnhold";

# Skal vi oppdatere, søke, utføre osv. i forbindelse med operasjonen?
$third = 1 if $PARAMS[2] eq "update";
$third = 2 if $PARAMS[2] eq "undo";
$third = 3 if $PARAMS[2] eq "soek";
$fourth= 1 if $PARAMS[3] eq "go";

$param = $PARAMS[$#PARAMS];

# LAG EN ASSOSIATIV ARRAY SOM SIER HVOR VI SKAL 
# Rekkefølge på elementene:
# 1. produkt/avdeling/fastside (1-3)
# 2. endre/fjern/ny/oversikt   (1-4)
# 3. update/undo/soek          (1-3)
# 4. go                        (1)

%jumptable = (
	'2430', '&avdelingssoek',
	'2400', '&AvdelingsOversikt',
	'2100', '&AvdelingEndre',
	'2210', '&fjernavdeling_update',
	'2220', '&undo_avddbendring',
	'2200', '&FjernAvdeling',
	'2300', '&NyAvdeling',
	'2500', '&VisAvdeling',
	'1310', '&prod_update',
	'1300', '&NyttProdukt',
	'1100', '&EndreProdukt',
	'1111', '&prod_update',
	'1110', '&endreprodukt_update',
	'1200', '&FjernProdukt',
	'1210', '&fjernprodukt_update',
	'1220', '&undo_perdbendring',
	'1400', '&ProduktOversikt',
	'1430', '&produktsoek'
);

# SJEKK OM VI HAR FÅTT MED NOE DATA FRA FORMS
&ReadParse;

# LES INN DATABASENE FOR PRODUKTER OG AVDELINGER
&ReadAvdProd;

eval ($jumptable{"$first$second$third$fourth"});

&write_footer;

exit(0);


#--------------------------------------------------
# AvdelingsOversikt
#--------------------------------------------------
sub AvdelingsOversikt {
    &write_header("Avdelingsoversikt");

    print qq! 
<p>
<font size=+1>
<a href="tools.cgi?avdeling&ny">[Legg til Avdeling]</a>
<a href="tools.cgi?avdeling&endre">[Endre Avdeling] </a>
<a href="tools.cgi?avdeling&fjerne">[Fjerne Avdeling] </a>
<a href="index.cgi">[Hovedside]</a>
</font>

<p>
<blockquote>
<form method="POST" action="tools.cgi?avdeling&oversikt&soek">
<font size="+1">Tast inn søkebegrep:</font><br>
<input size="40" name="soekebegrep">
<input type="SUBMIT" value="Utfør"><input type="RESET" value="Reset">
<br><b>Eksempler:</b> IBM, Apple, 1.1 (kategori) etc. Hvis du vil se alle, la feltet stå åpent.<p>
</form>
</blockquote>
<pre>

</pre>
<b><a href="tools.cgi?avdeling&oversikt&soek">Oversikt over alle avdelingene</a></b>
    !;				

    return;
}


#--------------------------------------------------
# avdelingssoek
#--------------------------------------------------
sub avdelingssoek {
    local(@TMP, $_);
    &write_header("Avdelingsoversikt - resultat av søk");

    print qq! 
<p>
<font size=+1>
<a href="tools.cgi?avdeling&oversikt"><b>[Søk]</b></a>
<a href="tools.cgi?avdeling&ny">[Ny Avdeling]</a>
<a href="tools.cgi?avdeling&endre">[Endre Avdeling] </a>
<a href="tools.cgi?avdeling&fjern">[Fjerne Avdeling]</a>
<a href="index.cgi">[Hovedside]</a>
<p>
<hr size=1 noshade width=200 align=left>
Antall poster i avdelingsbasen: $#AVD
<hr size=2 noshade width=200 align=left>
</font>
    !;			 

    print "<font size=+1>\n<table border=1 noshade>\n";
    print "<tr><td><strong><font size=+1>Avdelingsnummer -> Endre</font></strong></td><td><strong><font size=+1>Avdelingsnavn -> Produkter</font></strong></td></tr>";
    foreach $_ (@AVD) {
	if (/$in{'soekebegrep'}/) {
	    @TMP = split(/\#/, $_);
	    print "<tr><td><a href=\"tools.cgi?avdeling&endre&update&$TMP[0]\">$TMP[0]</a></td><td><a href=\"tools.cgi?avdeling&produktinnhold&$TMP[0]\">$TMP[1]</a></td></tr>\n";
	}
    }
    print "</table></font>\n";
    return;
}


#--------------------------------------------------
# VisAvdeling
#--------------------------------------------------
sub VisAvdeling {
	local(@TMP);

	&write_header("Oversikt over produkter i en kategori");

    print qq! 
<p>
<font size=+1>
<a href="tools.cgi?avdeling&oversikt"><b>[Søk]</b></a>
<a href="tools.cgi?avdeling&ny">[Ny Avdeling]</a>
<a href="tools.cgi?avdeling&endre">[Endre Avdeling] </a>
<a href="tools.cgi?avdeling&fjern">[Fjerne Avdeling]</a>
<a href="index.cgi">[Hovedside]</a>
<p>
<font size=+1><b>Avdeling/kategorinummer: $param</b>
<blockquote>
    !;		

# Skriv ut alle linjene med produkter som hører inn under denne kategorien

    print "<font size=+1>\n<table border=1 noshade>\n";
    print "<tr><td><strong><font size=+1>Produktnummer -> endre</font></strong></td><td><strong><font size=+1>Produkt -> produktside</font></strong></td></tr>";
    foreach $_ (@PROD_LIST) {
	if (/^$param/) {
	    @TMP = split(/\#/, $_);
	    print "<tr><td><a href=\"tools.cgi?produkt&endre&update&$TMP[0]\">$TMP[0]</a></td><td><a href=\"/sh/is/prodside.cgi?$TMP[0]\">$TMP[1]</a></td></tr>\n";
	}
    }
    print "</table></font></blockquote>\n";

	return;
}




#--------------------------------------------------
# ProduktOversikt
#--------------------------------------------------
sub ProduktOversikt {
    &write_header("Produktoversikt");

    print qq! 
<p>
<font size=+1>
<a href="tools.cgi?produkt&ny">[Nytt Produkt]</a>
<a href="tools.cgi?produkt&endre">[Endre Produkt] </a>
<a href="index.cgi">[Hovedside]</a>
</font>

<p>
<blockquote>
<form method="POST" action="tools.cgi?produkt&oversikt&soek">
<font size=+1>Tast inn søkebegrep:</font><br>
<input size=40 name="soekebegrep">
<input type="SUBMIT" value="Utfør"><input type="RESET" value="Reset">
<br><b>Eksempler:</b> IBM, Apple, 1.1.3 (kategori) etc. Hvis du vil se alle, la feltet stå åpent.<p>
</form>
</blockquote>
<pre>

</pre>
<b><a href="tools.cgi?produkt&oversikt&soek">Oversikt over alle produktene</a></b>
    !;				

    return;
}


#--------------------------------------------------
# produktsoek
#--------------------------------------------------
sub produktsoek {
    local(@TMP);
    &write_header("Produktoversikt - resultat av søk");

    print qq! 
<p>
<font size=+1>
<a href="tools.cgi?produkt&oversikt"><b>[Søk]</b></a>
<a href="tools.cgi?produkt&ny">[Nytt Produkt]</a>
<a href="tools.cgi?produkt&endre">[Endre Produkt] </a>
<a href="index.cgi">[Hovedside]</a>
<p>
<hr size=1 noshade width=200 align=left>
Antall poster i produktbasen: $#PROD_LIST
<hr size=1 noshade width=200 align=left>
</font>
    !;			 

    print "<font size=+1>\n<table border=1 noshade>\n";
    print "<tr><td><strong><font size=+1>Produktnummer -> endre</font></strong></td><td><strong><font size=+1>Produkt -> produktside</font></strong></td></tr>";
    foreach $_ (@PROD_LIST) {
	if (/$in{'soekebegrep'}/) {
	    @TMP = split(/\#/, $_);
	    print "<tr><td><a href=\"tools.cgi?produkt&endre&update&$TMP[0]\">$TMP[0]</a></td><td><a href=\"/sh/is/prodside.cgi?$TMP[0]\">$TMP[1]</a></td></tr>\n";
	}
    }
    print "</table></font>\n";
    return;
}


#--------------------------------------------------
# AvdelingEndre
#--------------------------------------------------
sub AvdelingEndre {
	&write_header("Endre avdeling");


    print qq! 
<p>
<font size=+1>
<a href="tools.cgi?avdeling&oversikt">[Søk]</a>
<a href="tools.cgi?avdeling&ny">[Legg til Avdeling]</a>
<a href="tools.cgi?avdeling&endre">[Endre Avdeling] </a>
<a href="tools.cgi?avdeling&fjern">[Fjerne Avdeling]</a>
<a href="index.cgi">[Hovedside]</a>
</font>
<p>
<blockquote>
<form method="POST" action="tools.cgi?avdeling&endre&update">
<font size=+1>Tast inn avdelingsnummer:</font><br>
<input size=40 name="avdeling">
<input type="SUBMIT" value="Utfør"><input type="RESET" value="Reset">
<br><b>Eksempler:</b> 1.1, 1.1.2, 2<p>
</form>
<p>
</blockquote>
!;

	return;
}


#--------------------------------------------------
# NyAvdeling
#--------------------------------------------------
sub NyAvdeling {
	&write_header("Ny Avdeling");


    print qq! 
<p>
<font size=+1>
<a href="tools.cgi?avdeling&oversikt">[Søk]</a>
<a href="tools.cgi?avdeling&ny">[Legg til Avdeling]</a>
<a href="tools.cgi?avdeling&endre">[Endre Avdeling] </a>
<a href="tools.cgi?avdeling&fjern">[Fjerne Avdeling]</a>
<a href="index.cgi">[Hovedside]</a>
</font>
<p>
<blockquote>

</blockquote>
!;

	return;

}

#--------------------------------------------------
# FjernAvdeling
#--------------------------------------------------
sub FjernAvdeling {
    &write_header("Fjern avdeling");

    print qq! 
<p>
<font size=+1>
<a href="tools.cgi?avdeling&ny">[Legg til Avdeling]</a>
<a href="tools.cgi?avdeling&endre">[Endre Avdeling] </a>
<a href="index.cgi">[Hovedside]</a>
</font>
<p>
<blockquote>
<form method="POST" action="tools.cgi?avdeling&fjern&update">
<font size=+1>Tast inn avdelingsnummer for den avdeling som skal fjernes. </font><br>
<input size=40 name="avdeling"><br>
<font size=+1>
<blockquote>
<INPUT TYPE="checkbox" NAME="fjernprod" value="true">Fjerne produkter i samme avdeling<br>
<INPUT TYPE="checkbox" NAME="oppdatere" value="true">Oppdatere efterfølgende avdelingsnummere og produktnummere<p>
</font>
</blockquote>
<input type="SUBMIT" value="Utfør"><input type="RESET" value="Reset">
</form>
<p>
<a href="tools.cgi?avdeling&oversikt&soek"><font size=+1>Oversikt over alle avdelingene</a></font>
</blockquote>
    !;

    return;
}


#--------------------------------------------------
# fjernavdeling_update
#--------------------------------------------------
sub fjernavdeling_update {

    &write_header("Fjerner en avdeling");

    print qq! 
<p>
<font size=+1>
<a href="tools.cgi?avdeling&ny">[Legg til Avdeling]</a>
<a href="tools.cgi?avdeling&endre">[Endre Avdeling] </a>
<a href="index.cgi">[Hovedside]</a><p>
</font>
    !;

# Går igjennom alle avdelingene
    for ($line=0; $line <= $#AVD; ++$line) {
	$_ = $AVD[$line];

	if (/^$in{'avdeling'}\#/) {
	    # Vi fant den. Oppdaterer.
	    print "<font size=+1><b>Følgende avdeling er fjernet:</b></font>\n";
	    &skriv_avd_linje($AVD[$line]);

	# Sjekk om vi også må oppdatere de andre avdelingene _OG_ alltid også produktnr.
	# Gi beskjed dersom vi fjernet noen av underavdelingene samtidig

	    # splice(@AVD, $line, 1);
	
	    # &save_avdbase;

	    print qq!
<p>
<font size=+1><b>Hvis du angrer slettingen, <a href="tools.cgi?produkt&fjern&undo"> trykk her.</a></FONT></B>
<pre>

</pre>
    !;

	    return;
	}
    }	
# Ingenting ble funnet, gi feilmelding
    error("Fant ikke data! $in{'produkter'}") if $#LINE < 2;

    return;
}



#--------------------------------------------------
# FjernProdukt
#--------------------------------------------------
sub FjernProdukt {
    &write_header("Fjern et produkt");

    print qq! 

<p>
<font size=+1>
<a href="tools.cgi?produkt&oversikt"><b>[Søk]</b></a>
<a href="tools.cgi?produkt&ny">[Nytt Produkt]</a>
<a href="tools.cgi?produkt&endre">[Endre Produkt] </a>
<a href="index.cgi">[Hovedside]</a>
</font>
<p>
<blockquote>
<form method="POST" action="tools.cgi?produkt&fjern&update">
<font size=+1>Tast inn kategorinummer og varenummer(e), separert med .-tegn.</font><br>
<input size=40 name="produkter">
<input type="SUBMIT" value="Utfør"><input type="RESET" value="Reset">
<br><b>Eksempler:</b> 1.1.2.30005NO <p>
</form>
<p>
<a href="tools.cgi?produkt&oversikt"><font size=+1>Oversikt over alle produktene</a></font>
</blockquote>
    !;


    return;
}

#--------------------------------------------------
# fjernprodukt_update
#--------------------------------------------------
sub fjernprodukt_update {
    &write_header("Fjerner et produkt");


    print qq!
<p>
<font size=+1>
<a href="tools.cgi?produkt&ny">[Nytt Produkt]</a>
<a href="tools.cgi?produkt&endre">[Endre Produkt] </a>
<a href="index.cgi">[Hovedside]</a>
</font>
<p>
    !;		


# Går igjennom alle produktene
    for ($line=0; $line <= $#PROD_LIST; ++$line) {
	$_ = $PROD_LIST[$line];

	if (/^$in{'produkter'}\#/) {
	    # Vi fant det. Oppdater.
	    print "<font size=+1><b>Følgende produkt er slettet:</b></font>\n";
	    &skriv_prod_linje($PROD_LIST[$line]);
	    splice(@PROD_LIST, $line, 1);

	    &save_prodbase;

	    print qq!
<p>
<font size=+1><b>Hvis du angrer slettingen, <a href="tools.cgi?produkt&fjern&undo"> trykk her.</a></FONT></B>
<pre>

</pre>
    !;

	    return;
	}
    }	
# Ingenting ble funnet, gi feilmelding
    error("Fant ikke data! $in{'produkter'}") if $#LINE < 2;

    return;
}



#--------------------------------------------------
# undo_perdbendring - kopierer tilbake backup-kopien
#--------------------------------------------------
sub undo_perdbendring {
    &write_header("Siste oppdatering av basen er fjernet");

    $PFB = $PROD_FILE . ".bak";
    system ("cp $PFB $PROD_FILE"); system("chmod 775 $PFB");

    print qq! 

<p>
<font size=+1>
<a href="tools.cgi?produkt&ny">[Nytt Produkt]</a>
<a href="tools.cgi?produkt&endre">[Endre Produkt] </a>
<a href="index.cgi">[Hovedside]</a>
</font>
<p>
    !;

    return;
}


#--------------------------------------------------
# NyttProdukt
#--------------------------------------------------
sub NyttProdukt {

    &write_header("Legg til nytt produkt");

	    print qq!
<p>
<font size=+1>
<a href="tools.cgi?produkt&oversikt">[Søke]</a>
<a href="tools.cgi?produkt&ny">[Nytt Produkt]</a>
<a href="tools.cgi?produkt&endre">[Endre Produkt] </a>
<a href="index.cgi">[Hovedside]</a>
</font>
<p>Her kan du legge inn nye produkter.Når du er fornøyd, trykker du på "Oppdater", og basen vil oppdateres. Evt. problemer vil rapporteres. For hver oppdatering lages en sikkerhetskopi av databasen. Den tidligere produktbasen kan dermed legges tilbake hvis man ikke oppdager feil før det er for sent. Angrefunksjonen er tilgjengelig fra forsiden.
<form method="POST" action="tools.cgi?produkt&ny&update">
<pre>
<font size="+1"><b>Kategorinummer:</b></font> <input size=10 name="kat"> <font size=+1><b>Produktnummer:</b></font> <input size="12" name="prodnr">
<font size="+1"><b>Produktnavn:</b>    <input size="40" name="navn">
<b>Pris:</b></font>            <input size="10" name="pris">  
<font size=+1><b>Evt. gif-bilde</b></font>  <input size="20" name="gif"><p>
<font size=+1><b>Evt. produktbeskrivelse</b> (gjerne med HTML-koder)</font>
<textarea rows=3 cols=70 name="beskr"></textarea>

</pre>
<input type="SUBMIT" value="Oppdater"> <input type="RESET" value="Reset">
</form>
!;
    return;
}


#--------------------------------------------------
# EndreProdukt - tast inn kategori og produktnummer
# derefter endres produktet via endreprodukt_i_forms
#--------------------------------------------------
sub EndreProdukt {
    &write_header("Endre Produkt");

	    print qq!
<p>
<font size=+1>
<a href="tools.cgi?produkt&oversikt">[Søke]</a>
<a href="tools.cgi?produkt&ny">[Nytt Produkt]</a>
<a href="tools.cgi?produkt&endre">[Endre Produkt] </a>
<a href="index.cgi">[Hovedside]</a>
</font>
<p>
<blockquote>
<form method="POST" action="tools.cgi?produkt&endre&update">
<font size=+1>Tast inn kategorinummer og varenummer, separert med . (punktum).</font><br>
<input size=40 name="produkter">
<input type="SUBMIT" value="Utfør"><input type="RESET" value="Reset">
<br><b>Eksempler:</b> 1.1.2.30005NO <p>
</form>
<p>
</blockquote>
    !;
    return;
}


#--------------------------------------------------
# endreprodukt_i_forms
#--------------------------------------------------
sub endreprodukt_update {
    local(@LINE);
    
    &write_header("Endre et produkt");

	    print qq!
<p>
<font size=+1>
<a href="tools.cgi?produkt&soek">[Søke]</a>
<a href="tools.cgi?produkt&ny">[Nytt Produkt]</a>
<a href="tools.cgi?produkt&endre">[Endre Produkt] </a>
<a href="index.cgi">[Hovedside]</a>
</font>
<p>
    !;		

    # Enten har vi fått koden for hvilket produkt vi skal endre via et forms,
    # eller så er det lagt med som parameter (ved direktevalg fra liste)

    $in{'produkter'} = $param if $in{'produkter'} eq "";

    foreach (@PROD_LIST) {
	if (/^$in{'produkter'}\#/) {
	    @LINE = split(/\#/,$_);
	    $in{'kat'} = $1 if $in{'produkter'} =~ /^(\d+(\.\d+)*)\./;
	    $in{'prodnr'} = $1 if $in{'produkter'} =~ /^[\d+|\.]*\.(.*)$/;
	    }		    
    }
    
    $LINE[3]=~ s#<br>#<br>\n#g;
    $LINE[3]=~ s#<p>#<p>\n#g;	
    $LINE[3]=~ s#>#\&gt\;#g;
    $LINE[3]=~ s#<#\&lt\;#g;

    $produkt_id = "$in{'kat'}.$in{'prodnr'}";

    print qq!
Her kan du endre et produkt. Når du er fornøyd, trykker du på "Oppdater", og basen vil oppdateres. Evt. problemer vil rapporteres. For hver oppdatering lages en sikkerhetskopi av databasen. Den tidligere produktbasen kan dermed legges tilbake hvis man ikke oppdager feil før det er for sent. Angrefunksjonen er tilgjengelig fra forsiden.<p>

<form method="POST" action="tools.cgi?produkt&endre&update&go">
<pre>
!;

    if ($#LINE < 2) {
	# Sannsynligvis har vi med et "kategoriprodukt" å gjøre
	print qq!
<font size="+1"><b>Kategorinummer:</b></font> <input size=10 name="kat" value="$in{'kat'}.$in{'prodnr'}>
<font size="+1"><b>Produktnavn:</b>    <input size="40" name="navn" value="$LINE[1]">
</pre>
<input type="SUBMIT" value="Oppdater"> <input type="RESET" value="Reset">
</form>
!;
    } else {
	print qq!
<font size="+1"><b>Kategorinummer:</b></font> <input size=10 name="kat" value=$in{'kat'}> <font size=+1><b>Produktnummer:</b></font> <input size="12" name="prodnr" value=$in{'prodnr'}>
<font size="+1"><b>Produktnavn:</b>    <input size="40" name="navn" value="$LINE[1]">
<b>Pris:</b></font>             <input size="10" name="pris" value="$LINE[2]">  
<font size=+1><b>Evt. gif-bilde</b></font>  <input size="20" name="gif" value="$LINE[4]"><p>
<font size=+1><b>Evt. produktbeskrivelse</b> (gjerne med HTML-koder)</font>
<textarea rows=8 cols=75 name="beskr">$LINE[3]</textarea>
</pre>
<input type="SUBMIT" value="Oppdater"> <input type="RESET" value="Reset">
</form>
<form method="POST" action="tools.cgi?produkt&fjern&update"><input type="hidden" name="produkter" value=$produkt_id><input type="SUBMIT" value="Fjern produkt"></form>
!;
    }

    return;
}


#--------------------------------------------------
# prod_update
#--------------------------------------------------
sub prod_update {

    &write_header("Endre produkt - Nytt produkt");

	    print qq!
<p>
<font size=+1>
<a href="tools.cgi?produkt&ny">[Nytt Produkt]</a>
<a href="tools.cgi?produkt&endre">[Endre Produkt] </a>
<a href="index.cgi">[Hovedside]</a>
</font>
<p>
    !;		

    # Vi skal legge til et produkt eller endre et produkt
    # 1. Sjekk at vi har nok info

    &error ("Vi må ha et kategorinummer!") if $in{'kat'} eq "";

    $tmp     = "\#" . $in{'gif'} . "\#" . $in{'beskr'};
    $tmp = "" if $tmp eq "\#\#";

    $nylinje =$in{'kat'} . "." . $in{'prodnr'} . "\#" . $in{'navn'} . "\#" . $in{'pris'} . $tmp;

    # 2. Sjekk om vi har oppdatering eller nytt produkt. 

    for ($line=0; $line <= $#PROD_LIST; ++$line) {
	$_ = $PROD_LIST[$line];

	if (/^$in{'kat'}\.$in{'prodnr'}\#/) {
	    # Vi fant det. Oppdater.
	    print "<font size=+1><b>Produktet ligger allerede i basen:</b></font>\n";
	    print "<p><pre><font size=+1>$PROD_LIST[$line]</font></pre>\n";
	    print "<p><font size=+1><b>Endret til:</b></font>\n";
	    print "<p><pre><font size=+1>$nylinje</font></pre>\n";

	    &skriv_prod_linje($nylinje);
	    $PROD_LIST[$line] = $nylinje;
	    
	    &save_prodbase;
	    &angre_knapp;

	    return;
	}
    }

    # Legg til en linje i basen. Finn først ut hvor vi vil ha den. 
    for ($line=0; $line <= $#PROD_LIST; ++$line) {
	$_ = $PROD_LIST[$line];
	if (/^$in{'kat'}/) {
	    #OK, legg inn linje.
	    print "<font size=+1><b>La til ny linje:<br></b></font>";
	    print "<pre>$nylinje</pre>";
	    splice(@PROD_LIST, $line, 0, $nylinje, $PROD_LIST[$line]);
	    &save_prodbase;
	    &angre_knapp;

	    return;
	}
    }

    &error("Ingen endringer gjort i basen!");
    return;
}


#--------------------------------------------------
# angre_knapp 
#--------------------------------------------------
sub angre_knapp {
    
    print qq!
<p>
<font size=+1><b>Hvis du angrer slettingen, <a href="tools.cgi?produkt&fjern&undo"> trykk her.</a></FONT></B>
    !;

    return;
}


#--------------------------------------------------
# Skriver ut en avdelingslinje.
#--------------------------------------------------
sub skriv_avd_linje {
  local($linje) = @_;
  local(@TMP);
  @TMP = split(/\#/, $linje);

  print qq!
<table border=1 cellspacing=5 cellpadding=0 width=80%>
<tr>
<td valign=top><b>Avdelingsnummer</b></td>
<td valing=top><b>Tittel</b></td>
</tr>
<tr>
<td valign=top>$TMP[0]</td>
<td valign=top>$TMP[1]</td>
</td>
</tr>
</table>
!;


return;	
}

#--------------------------------------------------
# Skriver ut en produktlinje. Benyttes av flere
# prosedyrer for interaktivitet mellom bruker. 
#--------------------------------------------------
sub skriv_prod_linje {
    local($linje) = @_;
    local(@TMP);
    @TMP = split(/\#/,$linje);

    print qq!
<table border=1 cellspacing=5 cellpadding=0 width=80%>
<tr>
<td valign=top><font size=+1><b>Kategori \& Prod.nr.</b></font></td>
<td valign=top><font size=+1><b>Navn</b></font></td>
<td valign=top><font size=+1><b>Pris</b></font></td>
<td valign=top><font size=+1><b>Gif</b></font></td>
</tr>
<tr>
<td valign=top>$TMP[0]</td>
<td valign=top>$TMP[1]</td>
<td valign=top>$TMP[2]</td>
<td valign=top>$TMP[4]</td>
</tr>
<tr>
<td valign=top align=left colspan=4>
<font size=+1><b>Beskrivelsestekst:</b></font><br>
<font size=2>$TMP[3]</font>
</td>
</tr>
</table>
	!;
    return;
}

#--------------------------------------------------
# save_prodbase - lagrer produktbasen, tar først
# backup av gammel base.
#--------------------------------------------------
sub save_prodbase {
    # Lag først en backupfi
    $PFB = $PROD_FILE . ".bak";
    system ("cp $PROD_FILE $PFB"); system("chmod 775 $PFB");

    # Skriv ut PROD_FILE
    open(PROD, ">$PROD_FILE") || error ("Kunne ikke skrive til produktfilen!");
    foreach $l (@PROD_LIST) {
	$l=~ s/^(.*)\s*$/$1\$\$/;
	print PROD "$l\n" if $l ne "####";
    }
    close(PROD);
    return;
}



#--------------------------------------------------
# save_avdbase - lagrer avdelingsdatabasen, tar først
# backup av gammel base
#--------------------------------------------------
sub save_avdbase {
    # Lag først en backupfi
    $AB = $AVD_FILE . ".bak";
    system ("cp $AVD_FILE $AB"); system("chmod 775 $AB");

    # Skriv ut AVD_FILE
    open(AFIL, ">$AVD_FILE") || error ("Kunne ikke skrive til produktfilen!");
    foreach $l (@AVD) {
	$l=~ s/^(.*)\s*$/$1\$\$/;
	print AFIL "$l\n";
    }
    close(AFIL);
    return;
}



#--------------------------------------------------
# Les inn avdelings- og katalogfilene
#--------------------------------------------------
sub ReadAvdProd {
    local($_);

    open(AFIL,"<$AVD_FILE") || error("Not able to open $AVD_FILE\n");
    @TMP_AVD = <AFIL>;
    @AVD = ();
    $count=0;
# Les gjennom kategori/avdelingsfilen for å sjekke om noen linjer må slås sammen
    foreach $_ (@TMP_AVD) {
	next if /^\s*$/;
	# Alle linjer skal slutte med $$. Hvis ikke, slå sammen denne og (de) neste
	# linje(r), til vi får avsluttet med $$.
	if (!/.*\$\$$/) {
	    $in=$in.$_;
	    next;
	}
	s/\$\$//;
	$in=$in.$_;
	$AVD[$count++] = $in;
	$in = "";                      
    }


    open(PROD, "<$PROD_FILE") || error("Fikk ikke åpnet produktdatabasen");
    @TMP_PROD = <PROD>;
    @PROD_LIST = ();
    $count=0;
    foreach $_ (@TMP_PROD) {
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

    close(AFIL);
    close(PROD);

}


#--------------------------------------------------
# formater input fra evt. forms
#--------------------------------------------------
sub ReadParse {
  if (@_) {
    local (*in) = @_;
  }

  local ($i, $loc, $key, $val);

  # Read in text
  if ($ENV{'REQUEST_METHOD'} eq "GET") {
    $in = $ENV{'QUERY_STRING'};
  } elsif ($ENV{'REQUEST_METHOD'} eq "POST") {
    for ($i = 0; $i < $ENV{'CONTENT_LENGTH'}; $i++) {
      $in .= getc;
    }
  } 

  @in = split(/&/,$in);

  foreach $i (0 .. $#in) {
    # Convert plus's to spaces
    $in[$i] =~ s/\+/ /g;

    # Convert %XX from hex numbers to alphanumeric
    $in[$i] =~ s/%(..)/pack("c",hex($1))/ge;

    # Split into key and value.
    $loc = index($in[$i],"=");
    $key = substr($in[$i],0,$loc);
    $val = substr($in[$i],$loc+1);
    $in{$key} .= '\0' if (defined($in{$key})); # \0 is the multiple separator
    $in{$key} .= $val;
  }

  return 1; # just for fun
}


#--------------------------------------------------
# update_avdelingsnummer
# - ved fjerning, innsetting o.l. av nye avdelinger,
#   benyttes denne rutinen for å endre de andre
#   avdelingsnummerne korrekt. 
#--------------------------------------------------
sub update_avdelingsnummer {
  ($start_kategori, $incr) = @_;
  local($_, $dybde, $this, , @T, @TMP);

  @TMP = split(/\./,$start_kategori);
  $dybde = $#TMP;
  $overkategori = $start_kategori;
  $overkategori = $1 if $start_kategori =~ /^(.*)\.\d+/;
  $siste_indeks = $TMP[$dybde];

  # Går igjennom avdelingsdatabasen
  foreach $this (@AVD) {
    if (/^$start_kategori/) {
      # Her må vi gjøre endringene
	@T = split(/\#/, $this);


    }
  }

  return;
}


#--------------------------------------------------
# update_produktnummer - tilsv. som for avd.nr.
#--------------------------------------------------
sub update_produktnummer {
  ($start_kategori, $incr) = @_;

  local($_, $dybde, $this, @T, @TMP);

  @TMP = split(/\./,$start_kategori);
  $dybde = $#TMP;
  $overkategori = $start_kategori;
  $overkategori = $1 if $start_kategori =~ /^(.*)\.\d+/;
  $siste_indeks = $TMP[$dybde];

  # Går igjennom produktdatabasen
  foreach $this (@PROD_LIST) {
    if (/^$start_kategori/) {
	

    }
  }

  return;
}


#--------------------------------------------------
# write_header - skriver header for HTML-dokument
#--------------------------------------------------
sub write_header {
    local($tittel) = @_;
    print "Content-type: text/html\n\n";
    print qq!
<html>
<head>
<title>
$tittel
</title>
</head>
<body bgcolor=#ffffff>
<hr noshade size=1>
<center>
<h2>$tittel</h2>
</center>
<hr noshade size=1>
<p>
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
<hr size=1 noshade>
</body>
</html>

    !;       

    return;
}


#---------------------------------------------------
# error - behandler feilmelding f.eks. ved filaksess
#---------------------------------------------------
sub error {

    local($_)=@_;

    print qq!

<center><font size=+2> $_ </font></center>
</body>
</html>

!;

        exit(0);
}
