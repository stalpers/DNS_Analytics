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
    if (/\d{4}\-\d{2}\-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}\s\[\w+\]\s\-\sFailed to Query Domain (.+) for type (.+)\s\((\d+),\s'(.+)'\)/g)
	{
		print "$1,$4\n"
	}
}
close(IN);

sub usage {
    say STDERR "Usage: $0 --file <filename>";   # full usage message
    exit;
}
