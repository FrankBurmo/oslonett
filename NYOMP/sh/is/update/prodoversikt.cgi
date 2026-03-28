#!/local/bin/perl5


#----------------------------------------------------------------------
# prodoversikt.cgi - viser alle produktene i databasen. 
#
# (c) 1995 Kent Roger Vilhelmsen, Schibsted Nett AS
#----------------------------------------------------------------------

# Loggfiler som holder oversikt over oppdateringer i produktdatabasen 
$CONTLOG = "prodbase.log";

# Her er databasefilene
$INDEX_ROOT="/local/www/sh/is/";
$PROD_FILE = $INDEX_ROOT . "katalog/pb.txt";
$AVD_FILE  = $INDEX_ROOT . "katalog/ab.txt";
# Åpne produktbasen 



&write_header;

print qq! 
<blockquote>
Hvis du ønsker å fjerne/endre et produkt, klikk på varenummeret. 
</blockquote>
!;


# Les inn oversikt over avdelingene
open(FIL,"<$AVD_FILE") || die "Not able to open $AVD_FILE\n";
open(PROD_FILE,"<$PROD_FILE") || die "Not able to open $PROD_FILE\n";
 
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

open(PROD, "<$PROD_FILE") || error("Fikk ikke åpnet produktdatabasen");
@TMP_PROD = <FIL>;

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

# OK, list opp alle varene, bruk kategoriene også for å skape litt mer oversikt
$this_level = 0;
$prev_level = 0;
foreach $k (@KATALOG) {
  ($kat, @FOO) = split(/\#/,$k);
  $this_level = length(s/\d//g);
  if ($this_level > prev_level) {
	print "<blockquote>";
  }
  # Lag innrykk osv. for å få litt struktur i oversikten. 
  while ($this_level < $prev_level) {
     $prev_level --;
     print "</blockquote>";
  }
  $prev_level = $this_level;

  $k =~ s/\#/  /;
  print "<font size=+1><b>$k</b></font>\n";
  foreach $p (@PROD_LIST) {
	# Skriv ut alle produkter som hører hjemme under denne kategorien. 
        ($prod, @FOO) = split(/\#/,$p);
        $rest=join("",@FOO);

        if (/^$kat/) {
 	print qq!
<a href="select.cgi?$prod">$prod</a> $rest <br>
        !;
        }
  }
}

print "<blockquote>";

&write_footer;
exit(0);



#--------------------------------------------------
# write_header - skriver header for HTML-dokument
#--------------------------------------------------
sub write_header {
    print "Content-type: text/html\n\n";
    print qq!
<html>
<head>
<title>
InterShop - Produktoversikt
</title>
</head>
<body bgcolor=#ffffff>
<h2></h2>
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

    print "Content-type: text/html\n\n";
    print qq!
<html>
<head>
<title>

</title>
</head>
<body bgcolor="#ffffff">
<center><font size=+2> $_ </font></center>
</body>
</html>

!;

	exit(0);
}