#!/local/bin/perl5


# search.pl - søker gjennom kategori- og avdelingsdatabase for et firma. 
# Opprinnelig laget for InterShop (Ronny Sørensen)
#
# 1995 Kent Vilhelmsen
#


# Finn path, hvor html-treet starter, katalogfil og kategorinr. 

$path=$ENV{'PWD'};
$INDEX_ROOT="/local/www/sh/is/";

$KAT_FILE  = join("",$index_root,"katalog/avdelingsbase.txt");
$PROD_FILE = join("",$index_root,"katalog/produktbase.txt");
@TMP = @_;

open(STDERR, "/dev/null");

print "Content-type: text/html\n\n"; 
# $|=1;

# Hent søkeordet/ene med parametre & Co. 
print @TMP;
return;

&do_search;
&write_header;
&write_contents;
&write_footer;
exit 0;




sub do_search {
    return;
    local($_, $sokeord, @KAT, @PRO);

    # OK, da raser vi gjennom databasen...
    return 0 if !open(KFIL,"<$KAT_FILE");
    return 0 if !open(PFIL,"<$PROD_FILE");

    @KAT = <KFIL>;
    @PRO = <PFIL>;

    close(KFIL);
    close(PFIL);

    $kcount = $pcount = 0;
    foreach (@KAT) {
	$PFOUND[$c++] = $_ if /^\.*$sokeord\.*/;
    }
    foreach (@PFIL) {
	$KFOUND[$c++] = $_ if /^\.*$sokeord\.*/;
    }
    return 1;
}


sub write_header {
    print qq!
<html>
<head>
<title>
InterShop Sokeresultat
</title>
</head>
<body>
    !;
    return;
}


sub write_contents {
    local($_);

    print "<p><h1> Produkter: </h1><p>";
    foreach (@PFOUND) {
	print $_,"<p>\n";
    }
    print "<p><h1> Kategorier: </h1><p>";
    foreach (@KFOUND) {
	print $_,"<p>\n";
    }

    return;
}


sub write_footer {
    print qq!
</body>
</html>
    !;
    return;
}














































