# Oslonett A/S, Februar 1995 / Anders Ellefsrud

# Ymse sm}rutiner

package Util;
require Exporter;
@ISA = qw(Exporter);
@EXPORT = qw(makedir);


sub makedir {
    local ($dir, $parentdir) = @_;
    unless (-d $dir) {
	($parentdir = $dir) =~ s%/[^/]+$%%;
	&makedir ($parentdir);
	mkdir ($dir, 0777);
    }
}

# Local Variables:
# mode:perl
# End: 

1
