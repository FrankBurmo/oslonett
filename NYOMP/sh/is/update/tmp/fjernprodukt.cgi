#!/local/bin/perl5

# Loggfiler som holder oversikt over oppdateringer i produktdatabasen 
$CONTLOG = "prodbase.log";

# Her er databasefilene
$INDEX_ROOT="/local/www/sh/is/";
$PROD_FILE = $index_root . "katalog/pb.txt";

&write_header;

print qq! 
<blockquote>
<form method="POST" action="rm_avdeling.cgi">
<font size=+1>Tast inn kategorinummer og varenummer(e), separert med .-tegn. Vil du fjerne flere varer, skriv komma i mellom.</font><br>
<input size=40 name="produkter"> Bruker-id: <input size=5 name="bruker">
<input type="SUBMIT" value="Utfør">
<br><b>Eksempler:</b> 1.1.2.30005NO <p>
</form>
<p>
<a href="prodoversikt.cgi"><font size=+1>Oversikt over alle produktene</a></font>
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
InterShop - Fjerning av produkt
</title>
</head>
<body bgcolor=#ffffff>
<h2>Fjerning av produkt</h2>
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
