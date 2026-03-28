#!/local/bin/perl5
# This script will handle server "Not Found" errors.
#
# The script will look up the original reference as 
#  1: a reference to a file, using the %refmapping hash
#  2: a reference to a file or directory, substituting leading
#     directoryname with the directories from the %dirmapping hash. 
# If a new reference is found and if this is a reference to a readable file,
# the script returns a HTML-document informing about the new URL, otherwise it 
# returns a standard error message.
#
# KGN, 24.7.95

# The file system root of the HTTP server
$wwwroot = "/local/www";

# Log file for redirection log messages
$logfile = "/home/frogner/www2/netsite/httpd-80/logs/redirect";

# Main rules: maps old directories to new ones
%dirmapping = qw(
                 /CW/                    /cw/
                 /EXPO94/                /itexpo/
                 /Elanders/              /el/
                 /IV/                    /iv/
                 /MB/                    /mb/
                 /NTIN/                  /ntin/
                 /OsloPRO/               /op/
                 /OsloPro/               /op/
                 /Skif/                  /sf/
                 /TASKON/                /taskon/
                 /wc94/                  /sp/fvm/
                 /Rondo/                 /rondo/
                 /am/                    /uh/am/
                 /akersm/                /uh/am/
                 /html/adv/AA/           /aa/
                 /html/adv/AC/           /nl/ja/ac/
                 /html/adv/BNbank/       /bnbank/
                 /html/adv/Candle/       /nl/dt/sw/candle/
                 /html/adv/Coltux/       /coltux/
                 /html/adv/DND/          /org/dnd/
                 /html/adv/FEKS/         /me/ts/feks/
                 /html/adv/HP/           /nl/dt/hw/hp/
                 /html/adv/IDG/          /idg/
                 /html/adv/INOVEX/       /inovex/
                 /html/adv/ITC/          /nl/dt/sw/itc/
                 /html/adv/ITEXPO/       /itexpo/
                 /html/adv/IV/           /iv/
                 /html/adv/KKTV          /home/gunnaraa/
                 /html/adv/KOPINOR/      /kopinor/
                 /html/adv/MSL/          /nl/rek/msl/
                 /html/adv/NE/           /me/ts/ne/
                 /html/adv/NFR/          /div/oi/nfr/
                 /html/adv/NLH/          /nlh/
                 /html/adv/ON/           /on/
                 /html/adv/PARX/         /parx/
                 /html/adv/PC_LAN_Prod/  /pclan_p/
                 /html/adv/PD/           /pd/
                 /html/adv/PIL/          /pil/
                 /html/adv/SG/           /sg/
                 /html/adv/TASKON/       /taskon/
                 /html/adv/TK/           /nl/ndiv/tk/
                 /html/adv/SystemSikk/   /systemsikk/
                 /html/adv/TONO/         /tono/
                 /html/adv/Telematikksys/        /telematikksys/
                 /html/adv/TELENOR-MOBIL/        /home/tm/
                 /html/adv/TM            /home/tm/
                 /html/adv/telenor/      /home/tm/
                 /html/adv/Upnet/        /nl/dt/dkom/upnet/
                 /html/adv/Uvdal/        /rl/uv/
		 /html/adv/VS/		 /nl/ndiv/vs/
                 /html/adv/atelier/      /home/atelier/
                 /html/adv/gf/           /gf/
                 /html/adv/INTERNET/     /org/int/
                 /html/jobb/             /nl/ja/
                 );

# Special cases: maps old files to new ones
%refmapping = qw(
                 /me/ts/cw/CW.html       /cw/
                 /BNbank.html            /bnbank/
                 /bnb/                   /bnbank/
                 /Timetech/              /home/timetech/
                 /DND_home.html          /dnd/
                 /ITC/ITC.html           /nl/dt/sw/itc/
                 /INTERNET.html          /org/int/
                 /Rondo/Rondo.html       /rondo/
                 /rondo.html             /rondo/
                 /html/adv/AA/AA.html                            /aa/
                 /html/adv/Candle/candle.html                    /nl/dt/sw/candle/
                 /html/adv/Coltux/Coltux.html                    /nl/dt/dkom/coltux/
                 /html/adv/DND/DND_home.html                     /org/dnd/
                 /html/adv/DND/DND.html		                 /org/dnd/
                 /html/adv/FEKS/FEKS.html                        /me/ts/feks/
                 /html/adv/gf/sommernatt.html                    /gf/
                 /html/adv/HP/HP.html                            /nl/dt/hw/hp/
                 /html/adv/IDG/IDG.html                          /idg/
                 /html/adv/INOVEX/INOVEX.html                    /nl/dt/sw/inovex/
                 /html/adv/IV/IV.html                            /iv/
                 /html/adv/ITC/ITC.html                          /nl/dt/sw/itc/
                 /html/adv/ITEXPO/ITEXPO.html                    /nl/mes/itexpo/
                 /html/adv/KOPINOR/KOPINOR.html                  /kopinor/
                 /html/adv/KKTV/KKTV.html                        /home/gunnaraa/
                 /html/adv/NFR/NFR.html                          /div/oi/nfr/
                 /html/adv/NLH/NLH.html                          /nlh/
                 /html/adv/NE/NE.html                            /me/ts/ne/
		 /html/adv/ON/ON.html				 /on/
		 /html/adv/ON-market.html			 /on/
                 /html/adv/PARX/PARX.html                        /parx/
                 /html/adv/PC_LAN_Prod/PC_LAN_Prod.html          /pclan_p/
                 /html/adv/PD/PD.html                            /pd/
                 /html/adv/PIL/PIL.html                          /pil/
                 /html/adv/SG/sgihome.html                       /sg/
                 /html/adv/Skif/Skif.html                        /sf/
                 /html/adv/SystemSikk/SystemSikk.html            /systemsikk/
                 /html/adv/TASKON/TASKON.html                    /taskon/
                 /html/adv/TK/TK.html                            /nl/ndiv/tk/
                 /html/adv/Telematikksys/Telematikksys.html      /telematikksys/
                 /html/adv/TONO/TONO.html                        /tono/
                 /html/adv/Upnet/Upnet.html                      /nl/dt/dkom/upnet/
		 /html/adv/VS/VS.html				 /nl/ndiv/vs/
                 /html/jobb/Jobbannonser.html                    /nl/ja/
                 /CW/CW.html             /me/ts/cw/
                 );

@mon = qw(Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec);

$path = $ENV{'PATH_INFO'};
$path =~ s#/+$##;
$newref = $refmapping{$path} || $dirmapping{"$path/"} || &dirmapping("$path");


if (length $newref) {
    &redirect($newref);
#    &moved($newref);
    $ENV{'HTTP_REFERER'} = '[unknown]' unless $ENV{'HTTP_REFERER'};
    if (open(LOG, ">>$logfile")) {
        printf LOG
            "%s redirection: host %s tried to access %s, referring doc: %s\n",
            &date, $ENV{'REMOTE_HOST'} || $ENV{'REMOTE_ADDR'},
            $ENV{'PATH_INFO'}, $ENV{'HTTP_REFERER'};
        close LOG;
    }
} else {
    &notfound;
}
exit 0;



sub date {
    local(@tm) = localtime(time);
    return sprintf("[%d/%s/19%02d:%02d:%02d:%02d]",
                   $tm[3], $mon[$tm[4]], @tm[5,2,1,0]);
}


sub dirmapping {
    local($newref) = $_[0];
    
    while ( ($olddir, $newdir) = each %dirmapping ) {
        return($newref) 
            if ( $newref =~ s/^$olddir/$newdir/ );
    }
    return undef;
}



sub notfound {
    print <<EOT;
Content-type: text/html

<html>
<head><title>Not Found</title></head>
<body>
<h1>Not Found</h1>

The requested object does not exist on this server. The link you
followed is either outdated, inaccurate, or the server has been
instructed not to let you have it.

</body>
</html>
EOT
    return 0;
}


sub redirect {
    local($newref) = $_[0];

    print "Location: $newref\n\n";
    return 0;
}



sub moved {
    local($newref) = $_[0];

    $newref = $ENV{'SERVER_URL'} . $newref;

    print <<EOT;
Content-type: text/html

<html>
<meta http-equiv="Refresh" content="10;URL=$newref">
<head><title>Document has moved</title></head>
<body>
<h1>Document has moved</h1>

The requested object ($ENV{'SERVER_URL'}$ENV{'PATH_INFO'}) has moved to:

<blockquote>
  <h2><a href="$newref">$newref</a></h2>
</blockquote>

Please use the new URL for future references.
EOT
    print <<EOT;
</body>
</html>
EOT
    return 0;
}
