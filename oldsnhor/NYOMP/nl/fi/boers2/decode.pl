#!/local/bin/perl
#
# decode log fra BaSe ?
#
# Ketil Kirkerud, ketilk@a.sn.no
#



%idx = (
 '1','Bank',
 '2','Forsikring',
 '3','Industri',
 '4','Skip',
 '5','Total',
 '6','OBX',
 '7','BRIX', );

@day = ('søndag', 'mandag', 'tirsdag',
        'onsdag', 'torsdag', 'fredag', 'lørdag');

@month = ('januar', 'februar', 'mars', 'april', 'mai',
          'juni', 'juli', 'august', 'september',
          'oktober', 'november', 'desember');

binmode STDIN;


dbmopen(%AKSJER,"aksje",0664);
dbmopen(%INDEXER,"indeks",664);

read(STDIN,$head,5);

($ver,$d1,$d2,$d3,$d4) = unpack("C C C C C",$head);

$d = $d1 + (256 * ( $d2 + (256 * ($d3 + (256 * $d4)))));
$d = $d - 2440588; # $d er dager siden 1/1 1970.
$ds = $d * 24 * 3600; #regn om til sekunder.
($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdist) = localtime($ds);
#dette brukes til "timestamp", se slutten av programmet

while (read(STDIN,$record,22))
   {
   ($s,$h,$m,$v00,$v01,$v02,$v03,$v10,$v11,$v12,$v13,
    $v20,$v21,$v22,$v23,$v30,$v31,$v32,$v33) = 
      unpack("a4 C C C C C C C C C C C C C C C C C C",$record);
   ($b1,$b2,$b3,$b4) = unpack("C C C C",$s);

# hm. signed/unsigned. hva med pack/unpack, igjen ?
# endring er signed.

   $v0 = $v00 + (256 * ( $v01 + (256 * ($v02 + (256 * $v03))))); 
   $v1 = $v10 + (256 * ( $v11 + (256 * ($v12 + (256 * $v13))))); 
   $v2 = $v20 + (256 * ( $v21 + (256 * ($v22 + (256 * $v23))))); 
   $v3 = $v30 + (256 * ( $v31 + (256 * ($v32 + (256 * $v33))))); 

   if($b1 < 8)
      {
      #index
 
      #korriger change (er signed)
      $chg=unpack("l",pack("C4",$v13,$v12,$v11,$v10)) / 100;
      $val = $v0/100;
      $trade= $v2;
      $INDEXER{$idx{$b1}} = "$h:$m, Value: $val, change : $chg, trade: $trade\n";
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

      $AKSJER{"$s"} = "$h:$m, bid:$bid, ask:$ask, price:$price, vol:$vol\n";
      }
   }


dbmclose(%AKSJER);
dbmclose(%INDEXER);

$MIN = sprintf ("%02d",$m);

open (DATE,">.timestamp");
print DATE "$day[$wday] $mday. $month[$mon], kl. $h:$MIN\n";
close DATE;
