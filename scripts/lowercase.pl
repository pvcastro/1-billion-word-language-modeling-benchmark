#!/usr/bin/perl -w
# Modified version of the same script downloaded from
# http://statmt.org/wmt11/translation-task.html
binmode(STDIN, ":utf8");
binmode(STDOUT, ":utf8");

use strict;
use warnings FATAL => 'all';
use utf8;
# NFC normalize the input text, see http://perldoc.perl.org/Unicode/Normalize.html.
# This may still lead to different results depending on the Perl version you are running.
# I (ciprianchelba@google.com) ran this on perl 5.14.2, see
# README.corpus_generation_checkpoints for exact configuration
# and checkpoints in the corpus generation pipeline. If you run on an earlier/different
# version of Perl, use the md4 ckeck sums to make sure your data matches my run.
require 5.14.2;

my $QUIET = 0;
my $HELP = 0;

while (@ARGV) {
    $_ = shift;
    /^-q$/ && ($QUIET = 1, next);
    /^-h$/ && ($HELP = 1, next);
}

if ($HELP) {
    print "Usage ./lowercase.pl (-l) \
         < textfile > file with lowercased sentences\n";
    exit;
}
if (!$QUIET) {
    print STDERR "Lowercase sentences v1\n";
}

while (<STDIN>) {
    $_ = lc $_;

    print $_;
}
