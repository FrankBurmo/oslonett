#!/local/bin/perl5

require "lib.pl";

$BESTILLINGSDIR	= '/home/sinsen/a/knesheim/orders';
@REQUIRED	= ( 'navn', 'adresse', 'postnr', 'poststed', 'e-post' );
$SENDER		= 'knesheim@sn.no';
$MAILPROG	= "/usr/lib/sendmail -t -f$SENDER";
@chr		= ( '0'..'9','A'..'Z','a'..'z','_' );

%input = &getinput;
$input{'e-post'} =~ tr/A-ZÆØÅ/a-zæøå/;

foreach (@REQUIRED) {
    push(@missing, $_) unless length $input{$_};
}
$missing = join(',', @missing);
$flertall = 'er' if $#missing;

&error("Følgende felt$flertall mangler og må fylles ut:<br>$missing")
    if length $missing;

$i=0;
while ( -f "$BESTILLINGSDIR/$input{'e-post'}-$i" ) {
    $i++;
}
$filename = "$BESTILLINGSDIR/$input{'e-post'}-$i";

srand(time || $$);
$auth = '';
foreach (1..10) {
    $auth .= $chr[int(rand($#chr))];
}

$salt = $chr[int(rand($#chr))] . $chr[int(rand($#chr))];
$input{auth} = crypt($auth, $salt);
push(@datanames, 'auth');

$auth = $i . '-' . $auth;

open(LOG, ">$filename") || &error("Kunne ikke skrive $filename");
open(MAIL, "| $MAILPROG") || &error("Kunne ikke åpne $MAILPROG");

&header("Takk for bestillingen");

print <<EOT;

Det er nettopp sendt ut elektronisk post til e-post-adressen din.
Denne må du svare på (f.eks. med den vanlige mail-leseren din) for å
bekrefte bestillingen. I mail\'en du sender tilbake må du passe på at
Subject-feltet returneres, enten ved at du velger "reply" i
mail-leseren din eller ved at du kopierer inn det opprinnelige
subject-feltet.<p>

Vi har mottatt følgende opplysninger fra deg:

<dl>
EOT


print MAIL <<EOT;
To: $input{'e-post'}
Reply-to: $SENDER
Subject: Bekreft bestilling hos SN, auth=<$auth>

Takk for bestillingen!

For å bekrefte bestillingen må du imidlertid svare på denne
elektroniske beskjeden. I svaret du sender tilbake må du passe på at
Subject-feltet returneres, enten ved at du velger "reply" i
mail-leseren din eller ved at du kopierer inn det opprinnelige
subject-feltet.<p>

Nedenfor følger en kopi av den mottatte bestillingen:

EOT

foreach (@datanames) {
    next unless length $input{$_};
    next if /^linje\d+/;
    next if /^id$/i;
    substr($fieldname = $_,0,1) =~ tr/a-zæøå/A-ZÆØÅ/;
    $input{$_} =~ s/[\n\r]+/ /g;
    printf LOG " %-20s: %s\n", $fieldname, $input{$_};
    printf MAIL " %-20s: %s\n", $fieldname, $input{$_};

    next if /^auth$/i;
    print "<dt> <b>$fieldname</b>\n<dd>$input{$_}\n";
}
print "</dl>\n<h2>Nedenfor følger selve bestillingen:</h2>\n<pre>\n";
print LOG "\n\n";
print MAIL "\n\n";

foreach (@datanames) {
    next unless /^linje\d+/;
    next unless length $input{$_};

    print LOG "$input{$_}\n";
    print "$input{$_}\n";
    $input{$_} =~ s/^\s*(\S+)\s+/$1\n/;
    print MAIL "$input{$_}\n\n";
}

close LOG;
close MAIL;


exit 0;
