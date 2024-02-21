use warnings 'all';
use strict;
use feature qw(say);
use Getopt::Long;

my $file;
my $verbose;
my $result = GetOptions (
                    "file=s"   => \$file,      # string
                    "verbose"  => \$verbose) or die "Usage: $0 --file NAME\n";;  # flag
if (not defined $file) {
    say STDERR "Argument 'file' is mandatory";
    usage();
}

open(IN, '<' . $file ) or die $!;
while(<IN>)
{
    $_ =~ s/^\"?([\d]+)\"?,\"?((.+)\.)?([(\w\-]+)\.([\w\-]+)\"?(,\".+\")?/0,$4.$5/g;
    print $_
}
close(IN);

sub usage {
    say STDERR "Usage: $0 --file <filename>";   # full usage message
    exit;
}