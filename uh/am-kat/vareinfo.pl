#!/local/bin/perl5

$TOP         = "/home/frogner/www/uh/am-kat";
$CATFILE     = "$TOP/intern/katalog.txt";
$ITEMINDEX   = "$TOP/intern/item-index"; # dbm file mapping item.no -> filepos
$CATINDEX    = "$TOP/intern/cat-index"; # dbm file mapping cat.name -> filepos
@FIELDS         = qw(product category no artist title
                     recording year price cover1 cover2);

$id = shift(@ARGV);

dbmopen(%index, $ITEMINDEX, 0664);
$pos = $index{$id};
dbmclose %index;

&linsearch unless length $pos;

open(C, $CATFILE) || &error("Kunne ikke åpne katalogfilen $CATFILE");
seek(C, $pos, 0);
@f{@FIELDS} = split(/;/, scalar(<C>));

@f{@FIELDS} = &linsearch unless $f{no} == $id;

&error("Produktnummeret $id finnes ikke i katalogen")
    unless ( length $f{no} );

if ($f{category} eq "DIV. KLASSISK") {
    $tmp = $f{title};
    $f{title} = $f{recording};
    $f{recording} = $f{artist};
    $f{artist} = $tmp;
}

print "Navn : $f{product}: $f{title}\n";
print "Pris : $f{price}\n";
print "URL : /uh/am-kat/showitem-new.cgi?no=$id\n";

exit 0;


sub linsearch {
    seek(C, 0, 0);
    while (<C>) {
	@f{@FIELDS} = split(/;/, scalar(<C>));
	if ($f{no} == $id) {
	    @found = @f;
	    last;
	}
    }
    return @found;
}


sub error {
    local($txt) = $_[0];

    print $txt,"\n";
    exit 0;
}
