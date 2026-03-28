#!/local/bin/perl5

$dbfil  = "./m2base.txt"; 

&write_header("Soekeresultat");

open(BASE,"<$dbfil") || error("Fikk ikke &Aring;pnet databasefilen $dbfil");

# Diverse lokale variable
%priser = (
	   "Alle", 10000000,		
	   "< 400 000", 400000,
	   "< 500 000", 500000,
	   "< 600 000", 600000,
	   "< 700 000", 700000,
	   "< 800 000", 800000,
	   "< 1 000 000", 10000000,
	   "> 1 000 000", 100000000
	   );

%mina = (
	 "< 50 kvm", 0,
	 "50 - 100 kvm", 50,
	 "100 - 150 kvm", 100,
	 "> 150 kvm", 150,
	 "Alle", 0
	 );

%maxa = (
	 "< 50 kvm", 50,
	 "50 - 100 kvm", 100,
	 "100 - 150 kvm", 150,
	 "> 150 kvm", 10000,
	 "Alle", 10000
	 );			

%omraade = (
	    "Alle", 0,
	    "Nord", 10,
	    "Vest", 20,
	    "Øst", 30
	    );

%dkode = (
	  "0", "Uspes.",
	  "10", "Vest",
	  "20", "Nord",
	  "30", "Øst"
	  );

# Les inn fra forms
&ReadParse;

# Lag søkeuttrykk
$SOEKESTRENG = "/^$in{oppdrag}.*$in{saksbehandler}\#.*$in{adr}.*\#.*$\/";

# Sett grenseverdier for søket
$OENSKETPRIS = $priser{$in{prisopt}};
$MINAREAL    = $mina{$in{areal}};
$MAXAREAL    = $maxa{$in{areal}};
$OMRAADE     = $omraade{$in{omraade}};

if ($in{prisfra} ne "") {
    $MINPRIS = $in{prisfra};
} else {
    $MINPRIS = 0;
}

if ($in{pristil} ne "") {
    $MAXPRIS = $in{pristil};
} else {
    $MAXPRIS = 10000000;
}


# Lag en tabellpresentasjon av s;keresultatet
print qq!
<table border=1>
<tr>
<td valign=top><b>Kode</b></td>
<td valign=top><b>Adresse</b></td>
<td valign=top><b>Komm</b></td>
<td valign=top><b>Distrikt</b></td>
<td valign=top><b>Areal</b></td>
<td valign=top><b>Verditakst</b></td>
</tr>
!;

$count=0;
$upcount=0;
# Søk gjennom databasen
foreach $_ (<BASE>) {
    # Fjern dobbelt dollar på slutten av hver streng
    s/(.*)\$\$$/$1/;
    $OK = 1;
    
    # Sjekk uttrykket...
    if (eval $SOEKESTRENG) {
	$in = $_;
	@TMP = split(/\#/,$in);
	$pris = $TMP[5];        
	$areal = $TMP[4];  
	$omr = $TMP[3];
	
	# Sjekk at areal og pris er OK
	$OK = 0 if ($MINAREAL > $areal);
	$OK = 0 if ($MAXAREAL < $areal);
 	$OK = 0 if ($pris > $OENSKETPRIS);
	$OK = 0 if ($pris < $MINPRIS);
	$OK = 0 if ($pris > $MAXPRIS);

	# Sjekk at omraadekode er OK
	$OK = 0 if ($OMRAADE > 0 && $OMRAADE !=$omr);

	if ($OK == 1) {
	    # Samle opp alle de hvor vi ikke har angitt pris...
	    if ($pris == 0) {       
		$UKJENTEPRISER[$upcount++] = $in;
	    } else {	
		print "<tr>";
		print "<td>$TMP[0]</td><td>$TMP[1]</td><td>$TMP[2]</td>";
		print "<td>$dkode{$TMP[3]}</td>";
		print "<td>$TMP[4]</td><td>$TMP[5]</td>";
		print "</tr>";
		$count++;
	    }		
	}	 
    }				 
}				

if ($count == 0) {
    print "<td colspan=6 align=center><b>Ingen treff med angitt pris</b></td></tr>";
}

if ($upcount ==0) {
    print "<td colspan=6 align=center><b>Ingen treff p&aring; uspes. pris</b></td></tr>";
} else {
    print "<td colspan=6 align=center><b>F&oslash;lgende treff med uspes. pris:</b></td></tr>";
    foreach $in (@UKJENTEPRISER) {
	print "<tr>";
	@TMP = split(/\#/,$in);
	print "<tr>";
	print "<td>$TMP[0]</td><td>$TMP[1]</td><td>$TMP[2]</td>";
	print "<td>$dkode{$TMP[3]}</td>";
	print "<td>$TMP[4]</td><td>$TMP[5]</td>";
	print "</tr>";
    }
}

print "</table>";

&write_footer;

exit(0);




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
