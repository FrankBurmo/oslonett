#!/local/bin/perl5

# Loggfiler som holder oversikt over oppdateringer i produktdatabasen og avd.basen
$CONTLOG = "prodbase.log";
$AVDLOG  = "avdbase.log";

# Her er databasefilene
$INDEX_ROOT="/local/www/sh/is/";
$PROD_FILE = $index_root . "katalog/produktbase.txt";
$AVD_FILE  = $index_root . "katalog/avdelingsbase.txt";


&write_header;

print qq! 
<blockquote>
<form method="POST" action="rm_avdeling.cgi">
<font size=+1>Tast inn avdelingsnummer(e), separert med komma:</font><br>
<input size=40 name="avdelinger"> Bruker-id: <input size=5 name="bruker">
<input type="SUBMIT" value="Utfør">
<br><b>Eksempler:</b> 1.2, 1.1.2, 3.4.5.1<p>
</form>
<p>
<a href="avdoversikt.cgi"><font size=+1>Oversikt over alle avdelingene</a></font>
</blockquote>
!;

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
InterShop - Fjerning av avdeling
</title>
</head>

<body bgcolor=#ffffff>
<hr size=1 noshade>
<center>
<h2>Fjerning av avdeling</h2>
</center>
<hr size=1 noshade>
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
