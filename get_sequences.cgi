#!/usr/bin/perl

# This script extracts sequences from a blast formated binary sequence
# database. It requires that the sequence IDs have been parsed. An
# example to create a  database
# $ makeblastdb -in my.fasta -parse_seqids
# 
# or using the legacy blast,
# $ formatdb -i my.fasta -o

# Specify the way in which sequences should be extracted from the database.
# By default, use the BLAST+ program blastdbcmd.
# Change this constant to 'fastacmd' to use the legacy BLAST version instead.
#my $BLAST_DB_EXTRACT_METHOD = 'fastacmd';
my $BLAST_DB_EXTRACT_METHOD = 'blastdbcmd';


print "Content-type: text/html\n\n";

use CGI;
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

  # specify the command to extract data from the databases
  my $cmd = undef;
  if ($BLAST_DB_EXTRACT_METHOD eq 'blastdbcmd'){
    $cmd = "blastdbcmd -db '$db' -entry '$first_id' >/dev/fd/".fileno($temp_out_fh)." 2>/dev/fd/".fileno($temp_err_fh);
  } 
  elsif ($BLAST_DB_EXTRACT_METHOD eq 'fastacmd'){
    $cmd = "fastacmd -d '$db' -s '$first_id' >/dev/fd/".fileno($temp_out_fh)." 2>/dev/fd/".fileno($temp_err_fh);
  }
  #print $cmd."\n";

  # Was this script setup properly?
  if (defined($cmd)){
    # setup all good. Run the extraction command.
    my $exit_code = system $cmd;

    my @warnings = <$temp_err_fh>;
    # Did running the command work?
    if ($#warnings != -1){
      print '<b>Errors were recorded during extraction of the sequences! Please contact the administrator of this BLAST quoting the errors below and the URL of the current page.</b>'."\n";
      print '<p>'.join '<br />', @warnings,'</p>';
      print "<p>Database used was `$db', and the entry to extract was `$first_id'</p>";
      print "The command line used to extract the sequences was <pre>`$cmd'</pre>";
    } else {
      # No problems running the command. Was the expected number of sequences retrieved?
      my $count_retrieved = 0;
      my @fasta_lines = ();
      foreach (<$temp_out_fh>){
        push @fasta_lines, $_; #cache the line for output later
        $count_retrieved += 1 if m/^>/;#increment for each line starting with '>'
      }
      unless ($count_retrieved == $#identifiers+1){
        print '<b>WARNING: Expected to retreive '.($#identifiers+1).' sequences, but '.$count_retrieved.' were retrieved</b>';
      }
      # Print the sequences, even if the count wasn't right for best effort.
      print "<p>\n";
      foreach $i (0..$#fasta_lines){print $fasta_lines[$i];}
      print '</p>';
    }
  } else {
    # setup fail.
    print "<b>Error while attempting to choose how to extract the sequences. Is the variable BLAST_DB_EXTRACT_METHOD in the blast_link file get_sequences.cgi set properly? It should either be `blastdbcmd' or `fastacmd'. It was `$BLAST_DB_EXTRACT_METHOD'.</b>";
  }
}
print "</pre>\n";
print "</body>";
print "</html>";

