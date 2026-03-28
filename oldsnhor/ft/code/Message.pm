#!/opt/depot/perl_5001/bin/perl
# Oslonett A/S, Februar 1995 / Anders Ellefsrud

# Rutiner som masserer en enkeltmelding.
# Vi antar at den allerede ligger i den
# globale variabelen $N_message.

package Message;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(process_message);

# Gjør alt som gjøres skal med en melding. Etter at vi
# er ferdige er den klar for å skrives til disk.
sub process_message {
	$_ = '@STX@' . 	# Konverter meldingen til litt lettere leselig
	     $Article::N_message .
	     '@ETX@';
	&uncontrollify;
	&urlify;			# Kj|r til-URL filteret
	&kodestreng;
	&konverter_enkeltord;		# mere html for enkelt-elemnter som ikke m} skrus av igjen
	&konverter_iht_tabell;		# Lag litt html-kode, for avsnitt, etc
	&finn_innmat;			# Kast rusk foran og etter meldingen
	s/\@less\@/</;
	s/\@greater\@/>/;
	&final_hacks;			# Globale oppryddingsaksjoner
	$Article::N_message = $_;
}

# Konverterer alle mystiske enkelt-tegn til noe mer lettlest kode.
sub uncontrollify {
#	study $_;
	s/</\@less\@/g;
	s/>/\@greater\@/g;
	s/\000/\@NUL\@/g;
	s/\001/\@SOH\@/g;
	s/\002/\@STX\@/g;
	s/\003/<\@ETX\@/g;
	s/\004/\@EOT\@/g;
	s/\005/\@ENQ\@/g;
	s/\006/\@ACK\@/g;
	s/\007/\@BEL\@/g;
	s/\010/\@BS\@/g;
	s/\011/\@HT\@/g;
#    s/\012/\@LF\@/g;
	s/\013/\@VT\@/g;
	s/\014/\@FF\@/g;
	s/\015//g;
	s/\016/\@SO\@/g;
	s/\017/\@SI\@/g;
	s/\020/\@DLE\@/g;
	s/\021/\@DC1\@/g;
	s/\022/\@SSS\@/g;
	s/\023/\@DC3\@/g;
	s/\024/\@ESS\@/g;
	s/\025/\@NAK\@/g;
	s/\026/\@SYN\@/g;
	s/\027/\@ETB\@/g;
	s/\030/\@CAN\@/g;
	s/\031/\@EM\@/g;
	s/\032/\@SUB\@/g;
	s/\033/\@ESC\@/g;
	s/\034/\@DT\@/g;
	s/\035/\@PT\@/g;
	s/\036/\@IS2\@/g;
	s/\037/\@IS1\@/g;
	s/\200/\@QL\@/g;
	s/\201/\@QC\@/g;
	s/\202/\@QR\@/g;
	s/\203/\@QM\@/g;
	s/\204/\@TL\@/g;
	s/\205/\@TC\@/g;
	s/\206/\@TR\@/g;
	s/\207/\@SPLITT-1\@/g;
	s/\210/\@SPLITT-2\@/g;
	s/\211/\@EN-DASH\@/g;
	s/\212/\@UNUSED-212\@/g;
	s/\213/\@PLD\@/g;
	s/\214/\@PLU\@/g;
	s/\215/\@RLF\@/g;
	s/\216/\@SS2\@/g;
	s/\217/\@SS3/g;
	s/\220/<OV>/g;
	s/\221/\@UNUSED-221\@/g;
	s/\222/<ING>/g;
	s/\223/<FO>/g;
	s/\224/\@TE\@/g;
	s/\225/\@SLT\@/g;
	s/\226/<UT>/g;
	s/\227/\@UNUSED-227\@/;
	s/\230/<INF>/g;
	s/\231/<RED>/g;
	s/\232/\@STK\@/g;
	s/\233/\@CSI\@/g;
	s/\234/\@THIN-SPACE\@/g;
	s/\235/\@EN-SPACE\@/g;
	s/\236/\@EM-SPACE\@/g;
	s/\237/\@SLK\@/g;
	s/\266/\@PA\@/g;
	$_;
}

# Rutine som spiser opp alt rusk som m}tte ligge foran og
# bak meldingen.
sub finn_innmat {
    s/(.|\n)*\@STX\@//;
    s/\@ETX\@(.|\n)*$/\n/;
}

# Kj|r artikkelen gjennom v}rt substitusjonsfilter
sub urlify {
    open (TABLE, $urltable) || die "Failed to read $urltable: $!";
    while ($line = <TABLE>) {
	$line =~ s/#.*//;
	next if $line =~ /^\s*$/;
	unless ($line =~ /^([^:]+):\s*(\S.*)/) {
	    warn "Syntax error in file $urltable";
	    print STDERR $line;
	    next;
	}
        $key = $1;
	$val = $2;
        s/\b$key\b/$val/gi;
    }
    close (TABLE);    
}

# Hånterer kodestreng sekvenser
sub kodestreng {
	local ($inpre) = (0);
	s%\@STK\@(.*?)\@SLK\@%
		if ($1 eq 'PT' || $1 eq 'TE') {
			'<hr>'
		} else {
			# Ymse tabeller
			if ($inpre) {
				'</pre><pre>';
			} else {
				$inpre = 1;
				'<pre>';
			}
		}
	%eg;
}

# Les en tabell over hva slags HTML som skal genereres ut fra
# ymse NTB koder
sub konverter_iht_tabell {
    open (TABLE, $markuptable) || die "Failed to read $markuptable: $!";
    while ($line = <TABLE>) {
	$line =~ s/#.*//;
	next if $line =~ /^\s*$/;
	unless ($line =~ /^([^:]+):\s+"([^"]*)"\s+"([^"]*)"/) {
	    warn "Syntax error in file $markuptable";
	    print STDERR $line;
	    next;
	}
        $key = $1;
	$startval = $2;
        $endval = $3;
        while (s/<$key>([^<]*)</$startval$1$endval</g) {};
    }
    close (TABLE);
}

# Etter at vi har konvertert overskrifter og lignende ting 
# med b}de start og slutt tar vi oss av enkelt-elementene. 

sub konverter_enkeltord {
	open (TABLE, $enkeltordtabell) ||
		die "Failed to read $enkeltordtabell: $!"; 
	while ($line = <TABLE>) {
		$line =~ s/#.*//; 
		next if $line =~ /^\s*$/; 
		unless ($line =~ /^([^:]+):\s+"([^"]*)"/) { # "; {
			warn "Syntax error in file $enkeltordtabell"; 
			print STDERR $line; 
			next;
		}
		$key = $1;
		$val = $2;
		s/\@$key\@/$val/g;
		}
	close (TABLE); 
}

# En håndfull globale oppryddingsaksjoner. Denne koden inbiller
# seg at den vet endel ting som egentlig bare burde stått i
# tabellene våre. Det rydder opp i litt dobbelt-koding som NTB tidvis
# bruker, og som kan bli litt rotete i html.
sub final_hacks {
	# br eller p etter hr kastes.
	s/(<hr>)(\s*(<hr>|<br>|<p>))+/$1/mg;
	# avsnittsskillere eller linjeskift etter title fjernes.
	s%(</(title|blockquote|h2)>)(\s*(<br>|<p>|<hr>))+%$1%mg;
# Hvorvidt vi skal slå sammen to etterfølgende titler er et filosofisk
# spørsmål som overlates til html ekspertene.
#	s%</title>(\s*)<title>%$1%mg;
# br/p etterfulgt av hr/h2 fjernes
	s/((<br>|<p>)\s*)+(<hr>|<h2>)/$3/mg;
# br etterfulgt av p fjernes.
	s/(<br>\s*)+<p>/<p>/mg;
# Tomme tabeller gjør liten nytte, kastes
	s%<pre>\s*</pre>%%mg;
# Multiple br etterhverandre spises opp
	s/(<br>\s*)+/<br>/mg;
	# Bytt ut senere forekommende <title> med <h3>
	while (s%(<title>.*?</title>.*?)<title>(.*?)</title>%$1<h3>$2</h3>%xs) {
	}
	# To Slike subtitler kan trygt slås sammen tror jeg.
	s%</h3>(\s*)<h3>%$1%mg;
}

# Local Variables:
# mode:perl
# End: 

1
