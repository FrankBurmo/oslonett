#!/local/bin/perl5

require "lib.pl";

&header("Administrasjon av Aftenpostens redigerte news-grupper");

print <<EOT;

<font size="+1">

Fra denne siden kan du gjøre følgende:

<ul>
  <li> <a href="$TOPP/diskusjon-adm/newgroup.cgi">Opprette ny diskusjonsgruppe</a><br>
       (Fra denne link'en får du dessuten oversikt over alle
       opprettede grupper.)
  <li> <a href="$TOPP/diskusjon-adm/cancel.cgi">Slette innlegg</a> i en av news-gruppene
       uten å måtte oppgi innsenders passord ("Master Cancel")
</ul>

Dersom en diskusjonsgruppe ønskes slettet, må man sende en forespørsel
til <a href="mailto:webmaster\@sn.no">webmaster\@sn.no</a>.
EOT
&footer;

exit 0;

