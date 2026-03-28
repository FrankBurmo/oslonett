#!/usr/bin/perl

@indeks = ( 0,0,0,0, 1,1,1,1,1,1, 2,2,2,2,2, 3,3,3,3, 0,0,0,0,0 );
@tekst = ( 'natt', 'morgen', 'dag', 'aften' );

@i = localtime;

print "Location: $ENV{SERVER_URL}/img/home_$tekst[$indeks[$i[2]]].gif\n\n";
exit 0;
