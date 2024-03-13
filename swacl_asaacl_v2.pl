#!/usr/bin/perl
use strict;
use warnings;

# Open the input file containing the ACLs from a Cisco switch
my $input_filename = 'input_acl.txt'; # Replace with your actual input file
open(my $fh, '<', $input_filename) or die "Could not open file '$input_filename' $!";

# Process each line in the input file
while (my $line = <$fh>) {
    chomp $line;

    # Skip empty lines and comments
    next if $line =~ /^\s*$/ || $line =~ /^\s*!/;

    if ($line =~ /permit|deny/i) { # Matches lines containing 'permit' or 'deny'
        my ($action, $protocol, $src, $src_mask, $dst, $dst_mask, @rest) = split(/\s+/, $line);
        
        # Convert wildcard masks to subnet masks for object group definition
        $src_mask = wildcard_to_subnet($src_mask);
        $dst_mask = wildcard_to_subnet($dst_mask);

        my $src_group = ($src_mask eq "255.255.255.255") ? "HST_$src" : "NET_$src\_$src_mask";
        my $dst_group = ($dst_mask eq "255.255.255.255") ? "HST_$dst" : "NET_$dst\_$dst_mask";

        # Print object-group definitions
        print "object-group network $src_group\n";
        print " network-object host $src\n" if $src_mask eq "255.255.255.255";
        print " network-object $src $src_mask\n" unless $src_mask eq "255.255.255.255";

        print "object-group network $dst_group\n";
        print " network-object host $dst\n" if $dst_mask eq "255.255.255.255";
        print " network-object $dst $dst_mask\n" unless $dst_mask eq "255.255.255.255";

        # Print the ACL line for Cisco ASA
        my $rest_string = join(' ', @rest);
        print "access-list outside_access_in extended $action $protocol object-group $src_group object-group $dst_group $rest_string\n";
    }
}

close($fh);

# Function to convert wildcard masks to subnet masks
sub wildcard_to_subnet {
    my $wildcard_mask = shift;
    my @octets = split(/\./, $wildcard_mask);
    my @subnet_mask_octets;

    foreach my $octet (@octets) {
        push @subnet_mask_octets, 255 - $octet;
    }

    return join('.', @subnet_mask_octets);
}
