#!/local/bin/perl 
# General access counter script for WWW pages.
# KGN, 2.6.95

$ENV{'PATH'} = '/local/bin:/local/X11R6/bin/pbm';
$fontdir = '/home/frogner/www2/cgi-src/counter/pbmtext';
$0 =~ s#.+/##;

open(STDERR,">/dev/null");	# pbm progs are always verbose :-(

&getquery;			# build %arg array

$digits = $arg{'digits'} || 6;
$font = $arg{'font'} || 'large';

# Read and update counter file...
open(COUNT,"+</local/www/tmp/$0.txt") || die;
$count = <COUNT>;
seek(COUNT,0,0);
$count++;
print COUNT $count;
close(COUNT);

$font = "$fontdir/$font.pbm" unless -r $font;
if ($font && -r $font) {
    $font = "-font $font";
} else {
    undef $font;
}

$| = 1;  # Remember to flush output before system() function is called
print "Content-type: image/gif\n\n";

$colorize = "-g \\#000000=\\$arg{'color'}" if $arg{color};
$text = sprintf("\"%s%0${digits}d%s\"", $arg{'pre'}, $count, $arg{'post'});
$cmd = "pbmtext $font $text | pnmcrop | ppmtogif | giftrans -t \\#ffffff $colorize";
$cmd =~ s/(,&$"';!#)/\\$1/;	# be safe - escape shell special characters
system($cmd);

exit 0;


sub getquery {
# parses QUERY_STRING and builds associative array %arg
# with keys = field names and values = field values.
    foreach $i ( split("&",$ENV{QUERY_STRING}) ) {
        ($name, $val) = split("=",$i);
        $val =~ s/%([a-fA-F0-9][a-fA-F0-9])/pack("C", hex($1))/eg;
        $arg{$name} = $val if ($val);
    }
}
