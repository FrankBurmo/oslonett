#!/local/bin/perl5

# Loggfiler som holder oversikt over oppdateringer i produktdatabasen og avd.basen
$CONTLOG = "prodbase.log";
$AVDLOG  = "avdbase.log";

# Her er databasefilene
$INDEX_ROOT="/local/www/sh/is/";
$PROD_FILE = $index_root . "katalog/produktbase.txt";
$AVD_FILE  = $index_root . "katalog/avdelingsbase.txt";
$AVD_BAK   = $AVD_FILE . ".bak";

# Åpner loggfil for avdeling
open(LOG, "<$AVDLOG") || error("Får ikke åpnet logg-fil! <\/a href=\"fjernavd.cgi\"(tilbake)<\/a>");

# Formater input
&ReadParse;

# Sjekk om bruker har registrert seg
error("Bruker må registreres før endring utføres! <\/a href=\"fjernavd.cgi\"(tilbake)<\/a>") if $in{'bruker'} eq "";

# Sjekk om vi har fått inn noe data
error("Ingen avdelinger definert. <\/a href=\"fjernavd.cgi\"(tilbake)<\/a>") if $in{'avdelinger'} eq "";

# Analyser data
@FJERNE = split(/\,/, $in{'avdelinger'};

# Lag backup av avdelingsbasen
system ("cp $AVD_FILE $AVD_BAK") || error("Kunne ikke lage sikkerhetskopi av avdelingsbase. <\/a href=\"fjernavd.cgi\"(tilbake)<\/a>");

# Fjern de avdelingene som er "lovlige"
open(AVD, "<$AVD_FILE") || error("Får ikke åpnet avdelings-fil! <\/a href=\"fjernavd.cgi\"(tilbake)<\/a>");

# Les inn alle avdelingene i avdelingsbasen som en lang streng
undef($/);
$avdbase = <AVD>;

foreach $f (@FJERNE) {
   # Let efter $f ... $$, fjern hvis vi finner det
   if (s#\s$f(.*)$$\s#\s#g) {

}

# Skriv til log
print LOG "$in{'bruker'} > Fjernet avdelingen $in{'avdelinger'};


&write_header;


&write_footer;



#--------------------------------------------------
# formater input
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
    print "Content-type: text/html\n\n";
    print qq!
<html>
<head>
<title>
InterShop - Fjerning av avdeling
</title>
</head>
<body bgcolor=#ffffff>
<h2>Fjerning av avdeling</h2>
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