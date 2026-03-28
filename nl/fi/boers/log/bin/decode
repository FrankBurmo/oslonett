#!/local/bin/perl
#
# decode log fra BaSe ?
#
# Ketil Kirkerud, ketilk@a.sn.no
#

$filnavn1 = "aksjelogg.dta";
$filnavn2 = "indexlogg.dta";


%idx = (
 '1','Bank',
 '2','Forsikring',
 '3','Industri',
 '4','Skip',
 '5','Total',
 '6','OBX',
 '7','BRIX', );

binmode STDIN;

open(STDERR, "/dev/null");

open(OUT,">$filnavn1") || die "Not able to open $filnavn1\n";
open(INDEX,">$filnavn2") || die "Not able to open $filnavn2\n";

read(STDIN,$head,5);

while (read(STDIN,$record,22))
   {
   ($s,$h,$m,$v00,$v01,$v02,$v03,$v10,$v11,$v12,$v13,
    $v20,$v21,$v22,$v23,$v30,$v31,$v32,$v33) = 
      unpack("a4 C C C C C C C C C C C C C C C C C C",$record);
   ($b1,$b2,$b3,$b4) = unpack("C C C C",$s);

# hm. signed/unsigned. hva med pack/unpack, igjen ?


   $v0 = $v00 + (256 * ( $v01 + (256 * ($v02 + (256 * $v03))))); 
   $v1 = $v10 + (256 * ( $v11 + (256 * ($v12 + (256 * $v13))))); 
   $v2 = $v20 + (256 * ( $v21 + (256 * ($v22 + (256 * $v23))))); 
   $v3 = $v30 + (256 * ( $v31 + (256 * ($v32 + (256 * $v33))))); 

   if($b1 < 8)
      {
      # index
      $val = $v0/100;
      $chg = $v1/100;
      $trade= $v2;
      print OUT "index: $idx{$b1}, $h:$m, Value: $val change : $chg trade: $trade\n";
      }
   else
      {
      # aksje
      $bid = $v0 / 100;
      $ask = $v1 / 100;
      $price = $v2 / 100;
      if($v3 & 0x80000000)
        {
        $vol = ($v3 & 0x7fffffff) * 1000;
        }
      else
        {
        $vol = $v3;
        }
      print OUT "aksje: s= $s, $h:$m bid:$bid ask:$ask price:$price vol:$vol\n";
      }
   }

close OUT,INDEX;
