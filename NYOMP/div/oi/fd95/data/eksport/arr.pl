#!/local/bin/perl5

while (<ARGV>) {

    $tittel = &format($1) if ( /arrangement.+value="(.+)"/i );
    $beskr = &format($1) if ( /Beskrivelse.+ with ``(.+)`/i );
    $sted = &format($1) if ( /sted.+value="(.+)"/i );
    $inst = &format($1) if ( /instnummer.+value="(.+)"/i );
    $dt = $1 if ( /`.+name.+Dato.+value.+=\D+(\d+\.\d+).+` / );
    $dato .= (length $dato)?", $dt" : $dt;
    $tid = &format($1) if ( /klokkeslett.+value="(.+)"/i );
    $kont = &format($1) if ( /kontakt.+value="(.+)"/i );
    $gr = &format($1) if ( /maalgruppe.+value="(.+)"/i );
    $pris = $1 if ( /pris.+value="(.+)"/i );

}


    print "Tittel: $tittel\n\n";
    print "$beskr\n\n";
    print "Sted:   $sted\n";
    print "Tid:    $tid\n";
    print "Dato:   $dato\n\n";
    print "Målgruppe:     $gr\n" if length $gr;
    print "Påmelding til: $kont\n" if length $kont;
    print "Pris:          $pris\n" if length $pris;
    print "\n";


exit 0;



sub format {
    local($text) = $_[0];

    $text =~ s/(.{50,70})\s+/$1\n/g;

    return $text;
}
