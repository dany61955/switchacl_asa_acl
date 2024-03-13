#!/usr/bin/perl
#perl script_name.pl your_acl_file.txt > modified_acl_file.txt

use strict;
use warnings;

# Assuming the input file is provided as the first argument
my $acl_file = $ARGV[0];
open my $fh, '<', $acl_file or die "Cannot open file: $!";

# Hash to hold object name conversions
my %object_conversions;

# Read the ACL file line by line
while (my $line = <$fh>) {
    chomp $line;
    # Check if the line defines an object
    if ($line =~ /^object\s+(network|host)\s+(\S+)/) {
        my $type = $1;
        my $name = $2;
        # Determine if it's a network or a host and set new name accordingly
        if ($type eq 'network') {
            if ($line =~ /subnet (\S+) (\S+)/) {
                my $network = $1;
                my $mask = $2;
                $object_conversions{$name} = "NET_${network}_$mask";
            }
        } elsif ($type eq 'host') {
            if ($line =~ /host (\S+)/) {
                my $host = $1;
                $object_conversions{$name} = "HST_$host";
            }
        }
    }
}

# Reset file handle to read the file again for replacement
seek $fh, 0, 0;

# Now, replace object names in the ACL
while (my $line = <$fh>) {
    foreach my $original_name (keys %object_conversions) {
        my $new_name = $object_conversions{$original_name};
        # Replace the original object name with the new one in the line
        $line =~ s/\b$original_name\b/$new_name/g;
    }
    print $line;
}

close $fh;
