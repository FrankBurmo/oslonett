#!/local/bin/perl5

#
# generate - genererer dynamisk www struktur fo Schibsted NETTs nye web. 
#
# Versjon 1.001
#
# OPSJONER:
# v - verbose. 
# b - lag backupfiler.
# t - lag "testside" for side gitt ved indeks: -t1.1 vil lage for "side" 1.1
# n - lag kun sider for Netscape
# m - lag kun sider for Mosaic
#
#
#  Kent Vilhelmsen, Schibsted NETT 1995
#

# $PATH	    = $ENV{'PWD'};
$BASE       = "/local/www/";     # Webens root
$LOCATION   = "/local/www/XXgen";  # Her legges de genererte sidene for Netscape
$M_LOCATION = "/local/www/XXgenm"; # Her legges de generete sidene for Mosaic
$URL_BASE   = "/XXgen";  # URL-base for Netscape 
$M_URL_BASE = "/XXgenm"; # URL-base for Mosaic

$HTML_SRC   = $BASE."/"."HTML";
$BASER      = $BASE."/"."BASER";
$WWW_MAIN   = $BASER."/"."kategoridb.txt";
$MENU_PATH  = "/img/margmeny";
$TMP_FILE   = "gen.tmp";

$M_EXT      = "_m";   # Extension for mosaic-filer.
                      # Legges på STD_L1 og på malfilene.

# Substitusjoner for norske bokstaver
%norsk = ('æ','ae', 'ø', 'oe', 'å', 'aa', 'Æ', 'AE', 'Ø', 'OE', 'Å', 'AA');

# Definerer standardsstrukturer i de tilfeller hvor spes. strukt. ikke er gitt
# (disse benyttes meget lite - kun i krisetilfeller)
$STD_STRUCT[1] = $HTML_SRC."/"."STD_L1";
$STD_STRUCT[2] = $HTML_SRC."/"."STD_L2";
$STD_STRUCT[3] = $HTML_SRC."/"."STD_L3";
$STD_STRUCT[4] = $HTML_SRC."/"."STD_L4";


# Les inn parameterne
$backup=$verbose=$report=$page_no=0;
$mosaic=$netscape=1;		# Default er både netscape og mosaic
while ($ARGV[0] =~ /^-/) {
    $_ = shift;
    $backup   = 1  if  /b(.*)/; # Lag backupfiler
    $verbose  = 1  if  /v(.*)/; # Skriv ut info underveis
    $report   = 1  if  /r(.*)/; # Generer rapport (report.html)
    $mosaic   = 0  if  /n(.*)/;	# Vi skal bare generere mosaic
    $netscape = 0  if  /m(.*)/; # Vi skal bare generere netscape
    if (/n(.*)/ && /m(.*)/) {	# OK, vi genererer begge
	$mosaic=$netscape=1;
    }

    $page_no  = $1 if $_ =~ /t(.+)$/;
}

# Les inn web-strukturen i en  array, og generer alle sidene
open(FIL,"<$WWW_MAIN") || die "Not able to open $WWW_MAIN\n";
$|=1;			       

@CONT=<FIL>;
$count=0;

# Traverser web-strukturfilen
foreach (@CONT) {
    next if /^\s*$/;
    # Alle linjer skal slutte med $$. Hvis ikke, slå sammen denne og (de) neste
    # linje(r), til vi får avsluttet med $$.
    if (!/.*\$\$$/) {		
	$in=$in.$_;
	next;
    }	
    s/\$\$//;
    $in=$in.$_;
    $LINES[$count++] = $in;
    $in = "";			   
}


# Genererer titler
@name_stack=();
$prev_depth=0;
foreach (@LINES) {	  
    # Lag en assosiativ array med kategori og tittel til bruk i title-feltene
    ($kat, @PARAM) = split(/#/, $_);  
    @TMP   = split (/\./,$kat); 
    $title = "";
    
    $this_title = $PARAM[0];
    $this_depth = scalar(@TMP);
    $this_title =~ s/\n$//;

    while ($this_depth <= $prev_depth) {
	pop(@name_stack);
	$prev_depth--;
    }
    push(@name_stack, $this_title);

    foreach (@name_stack) {
        $title = $title." - ".$_; 
    }
    $title=~ s/^\s-\s//;

    # Oppussning av tittelen - hvert ord skal starte med stor bokstav
    $title = lc $title;
    $title =~ s/\b(.)/\U$1\E/g;

    # Fixer på norske tegn
    $title =~ s/([æøåÆØÅ])/$tr{$1}/g;

    $prev_depth = $this_depth;
    $TITLES{$kat} = $title;
}


# Her begynner selve genereringen - kallene på generate_page
foreach (@LINES) {
    ($kat, @PARAM) = split(/#/, $_);  
    # Sjekk om det "kan" lages side for dette nivået
    # Kravet er at det må være fra 0 til nest siste nivå.
    $g=0;
    foreach (@LINES) {
        $g=1 if (/^$kat\.(\d+)/);
    }

    &generate_page($kat, "netscape", @PARAM) if ($g && $netscape);
    &generate_page($kat, "mosaic"  , @PARAM) if ($g && $mosaic); 
}
close(FIL);
exit(0);


#
# generate_page - genererer en html-side gitt kategori-index.
# HVIS IKKE ANNET ER ANGITT, VIL FILSTRUKTUREN VÆRE FLAT, og legges under
# $LOCATION
#
sub generate_page  {
    local($kat, $type, @PARAM) = @_;
    local($_, @TMP);

    # Returnerer dersom vi kun skal ha generert en side "on the fly"
    # (funksjon mest for uttesting o.l.)
    return if ($page_no != 0 && !($page_no eq $kat));

    # Hvor dypt skal vi?
    @TMP   = split (/\./,$kat);
    $depth = scalar(@TMP);
    $hkat  = $TMP[0];
    $ukat  = $TMP[1];

    # Produser et filnavn
    $x = substr($PARAM[0],0,8);
    $x =~ s/\s//g;
    $this_file = $x."_".$kat;
    $this_file =~ s/\./\_/g;

    # Fjerner norsk tegnsetting
    $this_file =~ s/([æøåÆØÅ])/$norsk{$1}/g;

    $this_file = $this_file.".html";

    if ($type eq "netscape") {
	$this_file = $LOCATION."/".$this_file;
    } else {
	$this_file = $M_LOCATION."/".$this_file;
    }

    open(OUT, ">$TMP_FILE") || die "can't open tmp file $TMP_FILE\n";

    # Les inn en mal for siden, enten for Netscape eller for Mosaic
    if ($PARAM[4] eq "") {
	    print "\nSTANDARD\n";

	@TMP = split (/\./,$kat);
        # Les inn en standardfil utifra dypden på nivået og hvilken type vi skal ha
	# Hvis det ikke finnes egen mal for mosaic, benytt netscape-malen. 
	if ($type eq "netscape") {
	    open(MFILE, "<$STD_STRUCT[$depth]") || \
		    die "can't open STANDARD description file $STD_STRUCT[$depth]";
	} else {
	   # SJekk først om det *finnes* en egen mosaic-mal
		if (!open(MFILE, "<$STD_STRUCT[$depth]$M_EXT")) {
		   open(MFILE, "$STD_STRUCT[$depth]") || \
		   die "can't open standard description file $STD_STRUCT[$depth]";
	   }
	}
    } else {

	# Klargjør navnet på malen
	$PARAM[4] =~ s/\s//g;

	if ($type eq "netscape") {

	    open(MFILE, "<$HTML_SRC\/$PARAM[4]") || \
		    die "can't open description file $PARAM[4]\n";
	} else {
            # Sjekk først om det *finnes* en egen mosaic-mal
            if (!open(MFILE, "<$HTML_SRC\/$PARAM[4]$M_EXT")) { 
		    open(MFILE, "<$HTML_SRC\/$PARAM[4]") || \
			    die "can't open description file $PARAM[4]\n";
	    } 
	}				
    }					

    # Legg på toppfelt med tittel...
    GenerateTitle($kat);

    while (<MFILE>) {
	# Traverser strukturfilen.
	if (/\#INSERT\s(.*)$/) {
	    &InsertFile($HTML_SRC."/".$1);
	    next;
	} 

	if ($type eq "netscape") { # GENERER FOR NETSCAPE
	    if (/^\#GTN(.*)/) {
		&GenerateThisLevel($kat,$hkat,$ukat,$depth,$1);
	    } elsif (/^\#GLN(.*)/) {
		&GenerateLowLevel($kat,$hkat,$ukat,$depth,$1);
	    } else { print OUT $_,"\n"; }
	} elsif ($type eq "mosaic") { # GENERER FOR MOSAIC 
	    if (/^\#GTM(.*)/) {

		&GenerateThisLevel($kat,$hkat,$ukat,$depth,$1);
	    } elsif (/^\#GLM(.*)/) {

		&GenerateLowLevel($kat,$hkat,$ukat,$depth,$1);
	    } else { print OUT $_,"\n"; }
	}
    }

    close(MFILE);
    close(OUT);

    if ($page_no eq $kat) {
	    # Test-output, avslutt programmet efter cat av aktuell fil
	    system "cat $this_file";
	    close(FIL);
	    exit(0);
	    }
        
    # Lag evt. backupkopi
    system "cp $this_file $this_file\.bak" if (-f $this_file && $backup);  

    # Kopier gen.tmp til this_file
    system "mv gen.tmp $this_file" || die "Could not create $this_file";
  
    # Rydd opp i eierforhold og denslags
    system "chmod 775 $this_file";

    # Verbose
    print "Laget backup $this_file.bak\n" if ($verbose && $backup);
    print "Opprettet $this_file\n" if $verbose;

    return
}


# GenerateTitle - generer toppheader med tittelfelt
sub GenerateTitle {
    local($kat) = @_;

    print OUT qq!
<html>
<head>
<title>
    !;
    print OUT $TITLES{$kat};
    print OUT qq!
</title>
</head>
    !;

    return;
}


# InsertFile - les fil fra disk og skriv ut til OUT
sub InsertFile {
    local($infile) = @_;
    local($_);
		# 
    open(IF, "<$infile") || die "can't open file $infile\n";
    

    while (<IF>) {
	print OUT $_;
    }
    close(IF);
    return
}


# GenerateThisLevel - genererer html for nivået gitt ved $kat og $depth
sub GenerateThisLevel {
    local($kat,$hkat,$ukat,$depth,$params) = @_;
    local($p_tmp,@TMP, @HOVEDKAT, $x, $_);
    $count1 = 0;

    # Les inn alle i denne kategorien i en array
    foreach (@LINES) {
	$HOVEDKAT[$count1++]=$_ if (/^(\d+)\#/ && $depth==1);
	$HOVEDKAT[$count1++]=$_ if (/^($hkat).(\d+)\#/ && $depth==2);
	$HOVEDKAT[$count1++]=$_ if (/^($hkat).($ukat).(\d+)\#/ && $depth==3);
    }

    # Generer linker og skriv ut - husk å utheve $kat, som vi er i nå
    # Trenger litt feilsjekking for "svak" base; f.eks. hvis vi har hovedgrupper
    # med få eller ingen subgrupper (f.eks. marked, hvor man går "direkte" ut i verden)

    $p_tmp = $params;			
    foreach (@HOVEDKAT) {
	$url = "";
	@TMP = split(/#/, $_);
        $k = $TMP[0];
	$x = substr($TMP[1],0,8);
	$x =~ s/\s//g;

	# Generer url
        $url = $x."_".$k;
        $url =~ s/\./\_/g;

        # Fjerner norsk tegnsetting
	$url =~ s/([æøåÆØÅ])/$norsk{$1}/g;

	# Ekstensjon er .html (kan fint endres til .htm)
        $url = $url.".html";

	# Hvor skal vi legge de genererte sidene? (gen - genm)
	if ($type eq "netscape") { 
	    $url = $URL_BASE."/".$url;
	} else {
	    $url = $M_URL_BASE."/".$url;
	}

	# Hvilket margikon skal vi bruke - på eller av?
	if ($k eq $kat) {
		$ACTIVE="_pa";
		# Uthev denne kategorien hvis vi benytter mosaic e.l.
		$TMP[1] =~ s/(.*)/<strong>\U$1\E<\/strong>/;
	} else {
		$ACTIVE="_av";
	}	     

	# Analyser og bygg opp uttrykk utifra $params-variabelen
        # - fire forskjellige primitiver, #URL, #MAIN, #BODY og #GIF
	$params =~ s/\#URL/$url/;
	$params =~ s/\#MAIN/$TMP[1]/;
	$params =~ s/\#BODY/$TMP[2]/;
	$params =~ s/\#GIF/$MENU_PATH\/$TMP[4]$ACTIVE.gif/;

	# Skriv til utfil
	print OUT $params;
	$params = $p_tmp;
    }
    return
}

# GenerateLowLevel - genererer html for undernivået til $kat.
sub GenerateLowLevel {
    local($kat,$hkat,$ukat,$depth,$params) = @_;
    local($p_tmp,@TMP,@UNDERKAT,$x,$_);
    $count2 = 0;
    $depth++;

    # Les inn alle i underkategoriene i en array
    foreach (@LINES) {
	$UNDERKAT[$count2++]=$_ if /^($kat).(\d+)\#/;
    }

    # Generer linker og skriv ut
    $p_tmp = $params;
    foreach (@UNDERKAT) {
	$url = "";
	@TMP = split(/#/, $_);
	$k=$TMP[0];

	# Finn URL'en; bruk den som er oppgitt, hvis ikke generer
	if ($TMP[3] ne "") {
	    $url = $TMP[3];
	    $url =~ s/\n$//;
	} else {
	    $x = substr($TMP[1],0,8);
	    $x =~ s/(\s)//g;
	    
	    $url = $x."_".$k;
	    $url =~ s/\./\_/g;
	    
	    # Fjerner norsk tegnsetting
	    $url =~ s/([æøåÆØÅ])/$norsk{$1}/g;
	    
	    $url = $url.".html";
	
	    if ($type eq "netscape" ) {
		$url = $URL_BASE."/".$url;
	    } else {
		$url = $M_URL_BASE."/".$url;
	    }
	}

	# Analyser og bygg opp uttrykk utifra $params-variabelen
        # - fire forskjellige primitiver, #URL, #MAIN, #BODY og #GIF
	$params =~ s/\#URL/$url/;
	$params =~ s/\#MAIN/$TMP[1]/;
	$params =~ s/\#BODY/$TMP[2]/;
	$params =~ s/\#GIF/$TMP[4]/;


	# Skriv til utfil
	print OUT $params,"\n";
		     $params = $p_tmp;
    }
    return
}







