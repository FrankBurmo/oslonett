#!/local/bin/perl5

require "intern/lib.pl";
$NOCHECKGIF     = "/kurv/gifs/nocheck.gif";
$CHECKGIF       = "/kurv/gifs/check.gif";
$KURV_INNHOLD   = "/local/www/kurv/innhold.pl";

# Trenger å kunne dekode handlekurv-id for å kunne vise i kurv/ikke i kurv
$id = $1 if $ENV{HTTP_COOKIE} =~ /kurvid=(\d+)/;

$| = 1;

print "Content-type: text/html\n\n";
&printheader("Produktinformasjon", 'kurv');

%input = &getinput;


&error("Katalognummer ikke angitt") unless length $input{no};

dbmopen(%index, $ITEMINDEX, 0664);
$pos = $index{$input{no}};
dbmclose %index;

&linsearch unless length $pos;

open(C, $CATFILE) || &error("Kunne ikke åpne katalogfilen $CATFILE");
seek(C, $pos, 0);
@f{@FIELDS} = split(/;/, scalar(<C>));

@f{@FIELDS} = &linsearch unless $f{no} == $input{no};

&error("Produktnummeret $input{no} finnes ikke i katalogen")
    unless length $f{no};

if ($f{category} eq "DIV. KLASSISK") {
    $tmp = $f{title};
    $f{title} = $f{recording};
    $f{recording} = $f{artist};
    $f{artist} = $tmp;
}

print qq!<dl>\n<table border="4" cellpadding="6">!;
$f{price} = "[ukjent]" if $f{price} == 0;

foreach $i ($[ .. $#NORSKEFELTER) {
    next if $NORSKEFELTER[$i] =~ /bilde$/i;
    next unless $f{$FIELDS[$i]} =~ /\S/;
    $f{$FIELDS[$i]} =~ s/,(\d\d)\d+/.$1/ if $FIELDS[$i] eq "price";
    if ($f{product} eq 'SPILL') {
	print " <tr>\n <dt> <td><b>$NORSKEFELTER_SPILL[$i]</b></td>\n";
    } else {
	print " <tr>\n <dt> <td><b>$NORSKEFELTER[$i]</b></td>\n";
    }
    print " <dd> <td>$f{$FIELDS[$i]}</td>\n";
}
print qq! <tr>\n<dt> <td colspan="2" align="center">!;
$innhold = `$KURV_INNHOLD $id`;
if ($innhold =~ m,akersmic/$f{no},) {
    print qq! <b>Varen er i handlekurven</b><img alt=""!;
    print qq! src="$CHECKGIF" border="0" align="absmiddle"></td>\n!;
} else {
    print qq! <a href="http://www.sn.no/kurv/hent.cgi/akersmic/$f{no}?ref=$ENV{SCRIPT_NAME}%3Fno%3D$f{no}">!;
    print qq! <b>Legg denne i handlekurven</b><img alt=""!;
    print qq! src="$NOCHECKGIF" border="0" align="absmiddle"></a></td>!;
}

print "<tr>\n</table></dl>\n";

print qq!Tilbake til <a href="form-new-cd.html">søkeskjemaet</a>. Vil !;
print "du tilbake til treff-listen, bruk web-browserens 'back'-funksjon.<p>\n";

&printfooter;

open(L, ">>$ITEMLOG") || exit 0;
@f = localtime(time);
$dato = sprintf("%02d%02d%02d %02d:%02d:%02d",
		$f[5], $f[4]+1, $f[3], @f[2,1,0]);
$maskin = $ENV{REMOTE_HOST} || $ENV{REMOTE_ADDR};
print L "$input{no};$f{artist};$f{title};$f{recording};$dato;$maskin\n";
close L;

exit 0;


sub linsearch {
    print "Hurtigoppslag ga ikke resultat, søker sekvensielt i stedet...<p>\n";
    seek(C, 0, 0);
    while (<C>) {
	@f{@FIELDS} = split(/;/, scalar(<C>));
	if ($f{no} == $input{no}) {
	    @found = @f;
	    last;
	}
    }
    return @found;
}
