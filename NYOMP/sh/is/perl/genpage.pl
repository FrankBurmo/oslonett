#!/local/bin/perl


#
# Finn path, hvor html-treet starter, katalogfil og kategorinr. 
#
$path=$ENV{'PWD'};
$index_root="/local/www/sh/is/";
$this_program_name="genpage.cgi";
$kat_file=join("",$index_root,"katalog/avdelingsbase.txt");
$header_dir="header/";
$footer_dir="footer/";


$kat = $ARGV[0];

# 1. underkategori
$_=$kat;
/^(\d+.\d+)/;
$ukat = $1;

# Hvor dypt er treet?
@KAT = split(/\./,$kat);
$depth=scalar(@KAT);

if ($depth = 4) {
    $uukat=$kat;
} else {
    $_=$kat;
    /^(\d+.\d+.\d+)/;
    $uukat = $1;
}



# Hvilken hovedkategori skal vi ha? (utheves grafisk med inntrykket knapp)
$this_main_kat=$KAT[0];

# Les inn katalogfil
open(FIL,"<$kat_file") || die "Not able to open $kat_file\n";
@KATALOG=<FIL>;

# Les inn alle aktuelle kategorier 

$count1=$count2=$count3=0;

foreach $_ (@KATALOG) {
    # Hovedkategoriene:
    if (/^(\d)\#/) {
	$HOVEDKAT[$count1++]=$_;
    }
    if (/^($this_main_kat).(\d+)\#/) {
	$UNDERKAT[$count2++]=$_;
    }
    if (/^($ukat).(\d+)\#/) {
	$UNDERUNDERKAT[$count3++]=$_;
    }
}


# Lag referanse til alle hovedikonene
$count=0;
foreach $_ (@HOVEDKAT) {
    chop;
    @TMP = split(/\#/);
    $HOVED_IKONER[$count] = join("", "<a href=\"", $this_program_name, "\&", $count+1, ".1.1","\"><img src\=\"gifs\/$TMP[3]", "\" border=0></a> \n");
    $count++;
}



# Lag referanse til alle underkategoriene
$count=0;
foreach $_ (@UNDERKAT) {
    chop;
    @TMP = split(/\#/);
    $par=$TMP[0];
    $TMP[1]=~ tr/a-z/A-Z/;

    # Vi må fremheve den kategorien vi er i spesielt. 

    if ($par eq $ukat) {
	$U_LINJE[$count++] = join("", "<a href=\"", $this_program_name, "\&$par", "\"><b><i>$TMP[1]", "</b></i></a>  ");
    } else {
	$U_LINJE[$count++] = join("", "<a href=\"", $this_program_name, "\&$par",  "\">$TMP[1]", "</a>  ");
    }
}


# Lag referanse til alle underunderkategoriene
$count=0;
foreach $_ (@UNDERUNDERKAT) {
    chop;
    @TMP = split(/\#/);
    $par=$TMP[0];
    $TMP[1]=~ tr/a-z/A-Z/;

    # Vi må fremheve den kategorien vi er i spesielt
    if ($par eq $uukat) {
	$UU_LINJE[$count++] = join("", "<a href=\"", $this_program_name, "\&$par", "\"><b><i>$TMP[1]", "</b></i></a>  ");
    } else {
	$UU_LINJE[$count++] = join("", "<a href=\"", $this_program_name, "\&$par",  "\">$TMP[1]", "</a>  ");
    }
}


#
# Genererer siden...
#

&header;
&table;
&footer;


#
# Genererer header utifra kategoriparameter...
#
sub header {
    print << ".";
<html>
<head>
<title>
$
</title>
</head>

<!-- SPORTHEAD_BEGIN -->




<!-- SPORTHEAD_END -->
.

    return;
}


#
# Genererer selve innholdet på produktsiden, gitt kategoriparameter
#
sub table {





    return;
}


#
# Genererer footeren til produktsiden, gitt kategoriparameter
#
sub footer {





    return;
}






print @HOVEDKAT,"\n\n";
print @UNDERKAT,"\n\n";
print @UNDERUNDERKAT,"\n\n";
print @HOVED_IKONER,"\n\n";
print @U_LINJE,"\n";
print @UU_LINJE, "\n";
print "$this_main_kat, $ukat, $uukat \n\n";
exit(0);



