#!/usr/bin/env python

"""
pydoop script to drive Illumina's bclToQseq program and
convert BCL files to Qseq.

Works in tandem with automator.bcl2qseq_mr.  This program *needs direct
access to sequencer's run directory*.  It will generate a file listing all the
tiles to be converted, with relative file paths.  In turn, this file will be
processed by the distributed component that runs on Hadoop.
"""


import argparse
import logging
import os
import subprocess
import sys
import tempfile
import urlparse

import automator.illumina_run_dir as ill
import automator.bcl2qseq_mr as bcl2qseq_mr
import pydoop.hdfs as hdfs

def serialize_cmd_data(cmd_dict):
    def serialize_item(k,v):
        # replace None values with empty strings
        k = k or ''
        v = v or ''
        # if there are "illegal" characters raise an exception
        if ':' in k or ';' in k or ';' in v or ';' in v:
            raise RuntimeError("datum '%s' with : or ;. Can't serialize!" % (k + ' ' + v))
        return "%s:%s;" % (k,v)
    return ''.join(serialize_item(k,v) for k,v in cmd_dict.iteritems())


class DistBcl2QseqDriver(object):
    def __init__(self, options):
        self.log = logging.getLogger('DistBcl2Qseq')
        self.log.setLevel(logging.DEBUG)
        self.options = {
                'module': options.module,
                'bclToQseq': options.bclToQseq_path,
                }
        u = urlparse.urlparse(options.run_dir)
        if u.scheme and u.scheme != 'file':
            raise RuntimeError("Sorry!  Current implementation requires that " +
              "the run directory be on a mounted file system (scheme %s not supported)" % u.scheme)
        self.run_dir = ill.RunDir(u.path)
        # collect necessary info
        self.run_params = self.run_dir.get_run_parameters()
        if hdfs.path.exists(options.output_dir):
            raise RuntimeError("output path %s already exists." % options.output_dir)
        self.output_path = options.output_dir

    def __write_mr_input(self, fd):
        """
        Write parameters for all the file conversions to be done in a format
        suitable for our map-reduce helper script.

        Returns the number of records written.
        """
        # commands are written one per line, in a form suitable for execution via sh.  If module loading
        # is required, it is inserted at the start of the command line, followed by && and finally the bclToQseq call.
        conversion_params = {
            'bclToQseq': self.options.get('bclToQseq') or 'bclToQseq', # default is to call bclToQseq assuming it's in the PATH
            'module': self.options.get('module', None),
            '--exclude-controls': '',
            '--repeat': '1',
            '--instrument': self.run_params.setup['ComputerName'],
            '--run-id': self.run_params.setup['ScanNumber'],
            '--input-directory': self.run_dir.get_base_calls_dir(),
            }

        count = 0
        for lane in self.run_params.get_lanes():
            conversion_params['--lane'] = str(lane)
            for read in self.run_params.get_reads():
                conversion_params['--read'] = str(read.num)
                conversion_params['--first-cycle'] = str(read.first_cycle)
                conversion_params['--number-of-cycles'] = str(read.last_cycle - read.first_cycle + 1)
                for tile in self.run_params.iget_simple_tile_codes():
                    conversion_params['--tile'] = str(tile)
                    # set filter, control, posotions files
                    conversion_params['--filter-file'] = self.run_dir.make_filter_path(lane, tile)
                    conversion_params['--control-file'] = self.run_dir.make_control_path(lane, tile)
                    conversion_params['--positions-file'] = self.run_dir.make_clocs_path(lane, tile)
                    #  we put the standard qseq name here.  The slave implementation may decide not to use it....
                    conversion_params['--qseq-file'] = os.path.join(self.output_path, self.run_dir.make_qseq_name(lane, tile, read.num))
                    fd.write(serialize_cmd_data(conversion_params))
                    fd.write("\n")
                    count += 1
        return count

    @staticmethod
    def find_exec(exec_name):
        """
        Find an executable in the current PATH.
        Returns the full path to the executable, if found.
        Returns None if not found.
        """
        for p in os.environ.get('PATH', '').split(os.pathsep):
            exec_path = os.path.join(p, exec_name)
            if os.access(exec_path, os.X_OK):
                return exec_path
        return None

    def run(self):
        pydoop_exec = self.find_exec('pydoop')
        if pydoop_exec is None:
            raise RuntimeError("Can't find pydoop executable in PATH")

        with tempfile.NamedTemporaryFile() as f:
            num_records = self.__write_mr_input(f)
            f.flush()
            self.log.debug("Wrote temp input file %s", f.name)
            input_filename = tempfile.mktemp(dir=os.path.dirname(self.output_path), prefix="dist_bcl2qseq_input")
            tmpfile_uri = "file://%s" % f.name
            try:
                self.log.debug("copying input from %s to %s", tmpfile_uri, input_filename)
                hdfs.cp(tmpfile_uri, input_filename)
                self.log.info("Run analyzed.  Launching distributed job")
                # launch mr task
                cmd = [ 'pydoop', 'script', '--num-reducers', '0', '--kv-separator', '',
                        '-Dmapred.map.tasks=%d' % num_records,
                        '-Dmapred.input.format.class=org.apache.hadoop.mapred.lib.NLineInputFormat',
                        '-Dmapred.line.input.format.linespermap=1',
                        bcl2qseq_mr.__file__,
                        input_filename,
                        self.output_path]
                self.log.debug(str(cmd))
                subprocess.check_call(cmd)
                self.log.info("Distributed job complete")
            finally:
                try:
                    hdfs.rmr(input_filename)
                except IOError as e:
                    self.log.debug("Problem cleaning up.  Error deleting temporary input file %s", input_filename)
                    self.log.debug(str(e))


if __name__ == "__main__":
    from automator import logformat

    parser = argparse.ArgumentParser(description="Distributed bcl2qseq.")
    parser.add_argument("-l", "--logfile", metavar="FILE", help="Write log output to a file")
    parser.add_argument("-m", "--module", metavar="MOD", help="Optional module to load before running bclToQseq")
    parser.add_argument("--bclToQseq-path", metavar="PATH", help="Full path to the bclToQseq binary. Needed only if it's not in the PATH")
    parser.add_argument('run_dir', help="Illumina run directory to process")
    parser.add_argument('output_dir', help="Path where the output qseq files should be created")

    options = parser.parse_args()

    if options.logfile:
        logging.basicConfig(format=logformat, filename=options.logfile)
    else:
        logging.basicConfig(format=logformat)

    try:
        driver = DistBcl2QseqDriver(options)
    except StandardError as e:
        logging.critical("Error initializing")
        if e.message:
            logging.exception(e)
        sys.exit(1)

    driver.run()

# vim: expandtab tabstop=4 shiftwidth=4 autoindent
