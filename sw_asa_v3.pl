#!/usr/bin/perl

use strict;
use warnings;

# Function to create object groups
sub create_object_group {
    my ($type, $name, $value) = @_;
    open(my $fh, '>>', 'object-groups.txt') or die "Could not open file 'object-groups.txt' $!";
    print $fh "object-group $type $name\n";
    print $fh " $type $value\n";
    print $fh "exit\n";
    close $fh;
}

# Function to convert ACL lines
sub convert_acl_line {
    my ($line) = @_;

    my ($action, $protocol, $source, $destination) = ($line =~ /^(permit|deny) ip (host|any|\d+\.\d+\.\d+\.\d+) (host|any|\d+\.\d+\.\d+\.\d+)(?: (\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+))?$/);

    unless ($protocol && $source && $destination) {
        print "Invalid ACL line: $line\n";
        return;
    }

    my $source_type = $source eq 'any' ? 'any' : ($source =~ /\d+\.\d+\.\d+\.\d+/ ? 'host' : 'network');
    my $destination_type = $destination eq 'any' ? 'any' : ($destination =~ /\d+\.\d+\.\d+\.\d+/ ? 'host' : 'network');

    my $source_name;
    my $destination_name;

    if ($source_type eq 'host') {
        $source_name = "HST_$source";
        create_object_group('network', $source_name, $source);
    } else {
        my ($subnet, $mask) = ($source =~ /^(\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)$/);
        my $subnet_name = "NET_$subnet" . "_$mask";
        create_object_group('network', $subnet_name, "$subnet $mask");
        $source_name = $subnet_name;
    }

    if ($destination_type eq 'host') {
        $destination_name = "HST_$destination";
        create_object_group('network', $destination_name, $destination);
    } else {
        my ($subnet, $mask) = ($destination =~ /^(\d+\.\d+\.\d+\.\d+) (\d+\.\d+\.\d+\.\d+)$/);
        my $subnet_name = "NET_$subnet" . "_$mask";
        create_object_group('network', $subnet_name, "$subnet $mask");
        $destination_name = $subnet_name;
    }

    return "access-list acl_name extended $action $protocol object $source_name object $destination_name\n";
}

# Main program

my $input_file = 'acl_input.txt';
my $output_file = 'asa_acl_output.txt';

open(my $in_fh, '<', $input_file) or die "Could not open file '$input_file' $!";
open(my $out_fh, '>', $output_file) or die "Could not open file '$output_file' $!";

while (my $line = <$in_fh>) {
    chomp $line;
    my $converted_line = convert_acl_line($line);
    print $out_fh "$converted_line\n" if $converted_line;
}

close $in_fh;
close $out_fh;

print "Conversion complete. ASA ACL written to '$output_file' and object groups written to 'object-groups.txt'.\n";
