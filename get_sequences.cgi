#!/usr/bin/perl
print "Content-type: text/html\n\n";

use CGI;
use CGI::Upload;
require File::Temp;

$form = new CGI;

print "<html>";
print "<head>";
print "<h1>Selected sequences</h1>";
print "</head>";
print "<body>";

print $form->param("alignment_seq")."\n";

# Verarbeitung der HTML Eingabe
my $db = $form->param('database'); #path to the fasta file of the database
my $hit_count = int($form->param('hit_count'));
my @identifiers; #an array of sequence identifiers to extract

# Read in the identifiers to be given back to the user
for my $i (1..$hit_count){
  my $checkbox = $form->param("alignment_seq_$i");
  push @identifiers, $checkbox unless $checkbox eq '';
}

# check parameters are setup sensibly where they might otherwise indicate software bugs
if ($db eq ''){
  print "<b>Programming error!</b> No database parameter given";
}

if ($#identifiers==-1){
  print "No sequences were selected!";
  print "</body>";
  print "</html>";
  exit;
}

print "<pre>\n";
for my $id (@identifiers){
  my ($temp_out_fh, $temp_out) = File::Temp->new();
  my ($temp_err_fh, $temp_err) = File::Temp->new();
  # Unset close-on-exec bit as per instructions at
  # http://search.cpan.org/~tjenness/File-Temp-0.22/Temp.pm#WARNING
  use Fcntl qw/F_SETFD F_GETFD/; fcntl($temp_out_fh, F_SETFD, 0) or die "Can't clear close-on-exec flag on temp fh: $!\n";
  use Fcntl qw/F_SETFD F_GETFD/; fcntl($temp_err_fh, F_SETFD, 0) or die "Can't clear close-on-exec flag on temp fh: $!\n";


  my $first_id = (split / /, $id)[0];
  my $cmd = "blastdbcmd -db '$db' -entry '$first_id' 2>/dev/fd/".fileno($temp_err_fh);
  my $exit_code = system $cmd;

  my @warnings = <$temp_err_fh>;
  if ($#warnings != -1){
    print '<b>Errors were recorded during extraction of the sequences! Please contact the administrator of this BLAST quoting the errors below and the URL of the current page.</b>'."\n";
    print '<p>'.join '<br />', @warnings,'</p>';
    print "<p>Database used was '$db', and the entry to extract was '$first_id'</p>";
  } else {
    print "<p>\n";
    print <$temp_out_fh>;
    print '</p>';
  }
}
print "</pre>\n";
print "</body>";
print "</html>";

