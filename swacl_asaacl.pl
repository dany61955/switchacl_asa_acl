#!/usr/bin/perl
use strict;
use warnings;

# Example input lines (could be read from a file or any other source)
my @input_lines = (
    'access-list 101 permit ip 192.168.1.0 0.0.0.255 any', # Network
    'access-list 102 permit ip host 10.1.1.1 any', # Host
    # Add more ACL lines as needed
);

foreach my $line (@input_lines) {
    if ($line =~ /access-list \d+ permit (\S+) (\S+) (\S+) (\S+)/) {
        my $protocol = $1;
        my $src = $2;
        my $src_mask = $3;
        my $dest = $4;
        my ($obj_group, $acl_line);

        if ($src eq 'host') {
            # It's a host
            $obj_group = "object network HST_$src_mask";
            $acl_line = "access-list outside_access_in extended permit $protocol object HST_$src_mask $dest";
        } else {
            # It's a network
            my $mask = convert_mask_to_wildcard($src_mask);
            $obj_group = "object network NET_$src_$mask";
            $acl_line = "access-list outside_access_in extended permit $protocol object NET_$src_$mask $dest";
        }

        print "$obj_group\n";
        print "$acl_line\n";
        print "\n"; # Print a newline for readability
    }
}

# Function to convert a subnet mask to a wildcard mask
sub convert_mask_to_wildcard {
    my $mask = shift;
    my @octets = split /\./, $mask;
    my @wildcard_octets = map { 255 - $_ } @octets;
    return join('.', @wildcard_octets);
}
