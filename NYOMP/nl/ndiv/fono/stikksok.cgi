#!/local/bin/perl

# Setter opp et form for å legge inn nye titler.
# Leser genredata, artistdata og labeldata fra eksisterende filer

require "lib/tittellib.pl";

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
 


&printheader("Søk på stikkord FONOs stikkordregister");

print<<EOT;

<form method="POST" action="finnstikk.cgi">


Dette skjemaet brukes til å søke i <a href="/fono/sok.htm">stikkordregisteret</a>
<p>

Dersom ingen av feltene nedenfor fylles ut, returneres en <a
href="finnstikk.cgi?format=html">liste
over alle kutt</a>. Hvis flere felter fylles ut brukes logisk
<b>og</b>-operasjon i utvelgelsen av kuttene. I feltet for
stikkord kan man fylle ut et regulært uttrykk (perl regexp).

<p>

<pre>
<hr noshade size=2>

<input type="submit" value="Start søk">

Stikkord     :  <input name="Stikkord" type="text" size=50>

Kutt         :  <input name="Tittel" type="text" size=50>

Artist       :  <input name="Artist" type="text" size=50>

Genre        :  <select name="Genre">
 <option selected value=".*">[vilkårlig]
EOT
    for (@g) {
	print "<option>$_";}
print<<EOT;
</select>

Label        :  <input name="Label" type="text" size=50>
</pre>

<hr noshade size=2>


<h2>Ønsket format</h2>

Oppgi ønsket format for dokumentet som returneres:

<blockquote>
<input type="radio" name="format" value="html" checked>
Kompakt HTML-dokument, med hyperlinker til kuttene<br>
<input type="radio" name="format" value="htmlfull">
HTML-dokument med all informasjon, velegnet for printing<br>

<!-- <input type="radio" name="format" value="psskjerm">PostScript-dokument for visning på skjerm<br> -->

<!-- <input type="radio" name="format" value="psfil">PostScript-dokument for lagring til fil<br> -->

</blockquote>

<h2>Ønskede felter i liste</h2>

Nedenfor velges hvilke felter som skal med i listen i tillegg til
tittelnavn. (Pass selv på å ikke velge for mange linjer
slik at det ikke blir plass på arket/skjermen.)

<blockquote>
<input type="checkbox" name="felt.artist" > Artist <br>
<input type="checkbox" name="felt.label" > Label <br>
<input type="checkbox" name="felt.genre" > Genre <br>
<input type="checkbox" name="felt.katnr" > Katalognr <br>
<input type="checkbox" name="felt.tid" > Tid <br>

</blockquote>
<h2>Sorteringsalgoritme</h2>
Dersom søket gir to eller flere treff i registeret skal listen sorteres...

<blockquote>
<input type="radio" name="sortering" value="alfabetisk" checked>
alfabetisk<br>
<input type="radio" name="sortering" value="dato">
etter registreringsdato, siste registrering først
</blockquote>

<input type="submit" value="Start søk">
<input type="reset" value="Resett skjema">


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






