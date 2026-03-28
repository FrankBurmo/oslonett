#!/local/bin/perl5




# Loggfiler som holder oversikt over oppdateringer i produktdatabasen og avd.basen
$CONTLOG = "prodbase.log";
$AVDLOG  = "avdbase.log";

# Her er databasefilene
$INDEX_ROOT="/local/www/sh/is/";
$PROD_FILE = $index_root . "katalog/produktbase.txt";
$AVD_FILE  = $index_root . "katalog/avdelingsbase.txt";



#--------------------------------------------------
# write_header - skriver header for HTML-dokument
#--------------------------------------------------
sub write_header {
    print "Content-type: text/html\n\n";
    print qq!
<html>
<head>
<title>
InterShop - 
</title>
</head>
<body bgcolor=#ffffff>
<h2>Vedlikeholdssider for InterShop</h2>
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
