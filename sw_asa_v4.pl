#!/usr/bin/perl

use strict;
use warnings;

my $input_acl = <<'END_ACL';
permit ip host 192.168.1.10 host 10.0.0.1
permit ip host 192.168.1.10 10.0.0.0 255.255.255.0
deny ip 192.168.1.0 255.255.255.0 10.0.0.0 255.255.255.0
permit ip 192.168.1.0 255.255.255.0 host 10.0.0.1
END_ACL

my @lines = split /\n/, $input_acl;

my %objects;

foreach my $line (@lines) {
    if ($line =~ /(permit|deny) ip (host|(\d+\.\d+\.\d+\.\d+)) (\d+\.\d+\.\d+\.\d+)(\/\d+)? (\d+\.\d+\.\d+\.\d+)(\/\d+)?/) {
        my $action = $1;
        my $source_type = $2;
        my $source_ip = $3;
        my $source_mask = $5 // '';
        my $destination_ip = $6;
        my $destination_mask = $8 // '';

        my $source_object;
        my $destination_object;

        if ($source_type eq 'host') {
            $source_object = create_host_object($source_ip);
        } else {
            $source_object = create_network_object($source_ip, $source_mask);
        }

        $destination_object = create_network_object($destination_ip, $destination_mask);

        print "$action ip object-group $source_object object-group $destination_object\n";
    }
}

sub create_host_object {
    my ($ip) = @_;
    my $object_name = "HST_$ip";
    $objects{$object_name} = $ip;
    return $object_name;
}

sub create_network_object {
    my ($ip, $mask) = @_;
    my $object_name = "NET_$ip" . ($mask eq '' ? '' : "_$mask");
    $objects{$object_name} = "$ip$mask";
    return $object_name;
}

foreach my $object_name (keys %objects) {
    my $ip = $objects{$object_name};
    if ($object_name =~ /^HST_/) {
        print "object network $object_name\n";
        print " host $ip\n";
    } elsif ($object_name =~ /^NET_/) {
        my ($network, $mask) = split /\//, $ip;
        print "object network $object_name\n";
        print " subnet $network $mask\n";
    }
}
