#!/local/bin/perl5

$skjema = "brevskjema.html";
$quotemark = "> ";
$replymark = "Re:";

require "intern/lib.pl";
print "Content-type: text/html\n\n";

&getinput;

open(REF, $input{ref})
    || &error("Kunne ikke åpne referansebrevet $input{ref}");
while (<REF>) {
    $ref{lc $1} = $2 if /([^:]+)\s*:\s*(.+)/;
}
close REF;

if ($input{sitat}) {
    $ref{leserbrev} =~ s/<p>\s*/\n$quotemark\n$quotemark/g;
    $ref{leserbrev} =~ s/<br>\s*/\n$quotemark/g;
    $body = qq!"$ref{navn}" skriver ($ref{regdato}):\n\n$quotemark$ref{leserbrev}\n!;

    if (defined $ref{svar}) {
	$ref{svar} =~ s/<p>\s*/\n$redquotemark\n$redquotemark/g;
	$ref{svar} =~ s/<br>\s*/\n$redquotemark/g;
	$body .= qq!\n"$ref{signatur}" svarer ($ref{revdato}):\n\n$redquotemark$ref{svar}\n!;
    }


}
($header = $ref{overskrift}) =~ s/^($replymark\s*)*/$replymark /;
open(FILE, $skjema) || &error("Kunne ikke åpne leserbrev-mal");

$refurl = "$utscript?file=$input{ref}";

while (<FILE>) {
    s/(name\s*=\s*"?Overskrift?")/$1 value="$header"/i;
	s%<\s*input[^>]*type\s*=\s*"?reset[^>]*>%<input type="reset" value="Gjenvinn original">\n<input type="hidden" name="ref" value="$input{ref}"><p>\nDette er en oppfølger til "<a href="$refurl">$ref{overskrift}</a>"\n%i;
    if ($input{sitat} !~ /^ja/i) {
	print;
    } else {
	s%(</textarea>)%$ref$body$1%i;
	print;
    }
}
exit 0;

