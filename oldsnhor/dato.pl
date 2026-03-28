#!/local/bin/perl5

$INDEX = '/home/frogner/www/index.html';
$NYINDEX = '/home/frogner/www/index.tmp';
$/="";
$* = 1;


@DAG = ('Søndag','Mandag','Tirsdag','Onsdag','Torsdag','Fredag','Lørdag');
@MND = ('januar','februar','mars','april','mai','juni',
            'juli','august','september','oktober','november','desember');

($sec, $min, $hour, $mday, $mon, $year, $wday, $yday)
    = localtime;
$year += 1900;

$idag = "<em>$mday. $MND[$mon] $year</em>";

open (IND,$INDEX);
open (NY, ">$NYINDEX");

while (<IND>)
{
    s/(^\<\!-- DATO.*\n).*/$1 $idag/; 
    print NY;
};

close(IND);
close(NY);
