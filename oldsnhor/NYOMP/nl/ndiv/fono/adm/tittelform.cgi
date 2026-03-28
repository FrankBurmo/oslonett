#!/local/bin/perl5

# Setter opp et form for å legge inn nye titler.
# Leser genredata, artistdata og labeldata fra eksisterende filer

require "../lib/tittellib.pl";
use POSIX;
setlocale(LC_CTYPE, "iso_8859_1");

@g = &readbase ($genredata);
@a = &readbase ($artistdata);


# Medlemslista må leses annerledes

  open(B, $mdldata)
      || return("<font size=\"+1\">Kunne ikke åpne databasen</font>");

 while (<B>) {
        $mdl = (split(/"/))[3];
	push(@m, $mdl);

    }
    close B;

    @b = @m;

    @m = @m[sort bytitle $[..$#m]; 
 


&printheader("Innlegging av nye titler i FONOs database");

print<<EOT;

Fyll inn informasjon om en ny oppføring her. Navnene på plateprodusentene
er hentet fra FONOs medlemsregister. Finner du ikke riktig label, 
betyr det at dette FONO medlemmet ikke er lagt inn. Du kan 
registrere nye medlemmer <a href="nyttmdl.htm">her</a>.
<p>
Navnet på genrene er hentet fra eksisterende genrer i basen. Har du
bruk for å legge inn en ny genre, lar du være å velge genre fra menyen,
men bruker i stedet tekstfeltet under for å skrive inn en ny.
<p>
Det samme gjelder for artistnavnene. Se først om du finner aktuell
artist i menyen, hvis ikke bruk tekstfeltet under.
<p>
Hvis du benytter de ekstra tekstfeltene for ny artist eller ny genre,
spiller det ingen rolle hva som er valgt i de respektive menyfeltene.

<form method="POST" action="http://www.sn.no/fono/adm/nytittel.cgi">
<input type=hidden name=mailto value="steinar\@sn.no">
<input type=hidden name=subject value="Nytt FONO tittel lagt inn">
<input type=hidden name="reply-to" value="www\@sn.no">

<blockquote>
<pre>
Label   : <select name="Label">
EOT
    for (@m) {
	print "<option>$_\n";}
print "</select>\n\nArtist  : <select name=\"Artist\">\n";
    for (@a) {
	print "<option>$_";}    
print "</select>\n";

print<<EOT;
Nyartist: <input name="Nyartist" size="50">
Tittel  : <input name="Tittel" size="50">

Genre   : <select name="Genre">
EOT
    for (@g) {
	print "<option>$_";}
print<<EOT;
</select>
Nygenre : <input name="Nygenre" size="50">

Kat.nr  : <input name="Kat.nr" size="14"> Utgivelsesår <input name="År" size="4"> Pris <input name="Pris" size=4> (CD2,CD3,CD4 osv). 

</pre>
</blockquote>

<input type="submit" value="Send inn">
</form>
EOT


&printfooter;



sub readbase {
    local ($fil) = shift;
    local (@b);

    open(B, $fil)
      || return("<font size=\"+1\">Kunne ikke åpne databasen</font>");

    while (<B>) {
	push(@b, $_);

    }
    close B;
    @b = @b[sort bytitle $[..$#b]; 
 
    return @b;
}

sub bytitle { $b[$a] cmp $b[$b]; }






