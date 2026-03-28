#!/local/bin/perl5

require "intern/lib.pl";

$| = 1;

print "Content-type: text/html\n\n";
&printheader("Product information");

%input = &getinput;


&error("No catalogue number specified") unless length $input{no};

dbmopen(%index, $ITEMINDEX, 0664);
$pos = $index{$input{no}};
dbmclose %index;

&linsearch unless length $pos;

open(C, $CATFILE) || &error("Failed to open file: $CATFILE");
seek(C, $pos, 0);
@f{@FIELDS} = split(/;/, scalar(<C>));

@f{@FIELDS} = &linsearch unless $f{no} == $input{no};

&error("Unknown product number: $input{no}")
    unless length $f{no};

if ($f{category} eq "DIV. KLASSISK") {
    $tmp = $f{title};
    $f{title} = $f{recording};
    $f{recording} = $f{artist};
    $f{artist} = $tmp;
}

print qq!<dl>\n<table border="4" cellpadding="6">!;

foreach $i ($[ .. $#ENGELSKEFELTER) {
    next if $NORSKEFELTER[$i] =~ /bilde$/i;
    next unless length $f{$FIELDS[$i]};
    $f{$FIELDS[$i]} =~ s/,(\d\d)\d+/.$1/ if $FIELDS[$i] eq "price";
    print " <tr>\n <dt> <td><b>$ENGELSKEFELTER[$i]</b></td>\n";
    print " <dd> <td>$f{$FIELDS[$i]}</td>\n";
}
print "<tr>\n</table></dl>\n";

&printfooter_eng;

open(L, ">>$ITEMLOG") || exit 0;
@f = localtime(time);
$dato = sprintf("%02d%02d%02d %02d:%02d:%02d",
		$f[5], $f[4]+1, $f[3], @f[2,1,0]);
$maskin = $ENV{REMOTE_HOST} || $ENV{REMOTE_ADDR};
print L "$input{no};$f{artist};$f{title};$f{recording};$dato;$maskin\n";
close L;

exit 0;


sub linsearch {
    print "Fast lookup unsuccessful, trying linear search...<p>\n";
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
