
package mySSI;

use Carp;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(expand_inc);

my $docroot       = '/home/oslonett';
my $inc_directive = '<!--#include virtual="(.*?)" -->';
my $max_recursion = 5;

sub expand_inc
{
    my $str = shift;
    my $file; my $n = 0;
    while ($str =~ /($inc_directive)/) {
        last 
	    if $n++ == $max_recursion;
	$file = $docroot . $2;        
        { local($/) = undef;
          open F, $file;
          $f = <F>;
          close F;
          $str =~ s/$1/$f/;
        }
    }
    return $str;

}


1;

__END__

=head1 NAME

mySSI.pm - very simple package implementing one commonly used SSI directive

=head1 SYNOPSIS

 use mySSI;
 my $html_template;
 { local ($/) = undef;
  open T, "name of HTML template file" || die "Cannot open ..";
  $html_template = <T>;
  close T;
 }

 $html_template = mySSI::expand_inc($html_template);

 # Expand other stuff in template
 ...

 print "Content-type: text/html\n\n$html_template";



=head1 DESCRIPTION

The package implements the Apache SSI directive "#include virtual", using
exactly the same syntax. The name of the exported method is expand_inc().
Since this directive uses an URI namespace, but
the package needs to retrieve the files from the file system, the package
needs to know where the documentroot of the webserver is. This is configured
at the top of the .pm file, in the variable $docroot.

When the package retrieves an included file, it will try to expand directives
in this file in the same way. The number of maximum allowed recursions
is configurable, and defaults to 5. If the maximum number of recursive
inclusions are reached, the method returns with no further warnings.

=head1 BUGS AND DEFICIENCIES

Probably many. For instance - the package knows nothing about the webserver 
setup, and will for instance fail to include files referred to by URLs defined 
by aliases in the webserver.

=head1 AUTHOR

Steinar Kjærnsrød E<lt>steinar@manamind.com>
