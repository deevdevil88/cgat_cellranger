"""===========================
Pipeline template
===========================

.. Replace the documentation below with your own description of the
   pipeline's purpose

Overview
========

This pipeline computes the word frequencies in the configuration
files :file:``pipeline.yml` and :file:`conf.py`.

Usage
=====

See :ref:`PipelineSettingUp` and :ref:`PipelineRunning` on general
information how to use cgat pipelines.

Configuration
-------------

The pipeline requires a configured :file:`pipeline.yml` file.
cgatReport report requires a :file:`conf.py` and optionally a
:file:`cgatreport.yml` file (see :ref:`PipelineReporting`).

Default configuration files can be generated by executing:

   python <srcdir>/pipeline_@template@.py config

Input files
-----------

None required except the pipeline configuration files.

Requirements
------------

The pipeline requires the results from
:doc:`pipeline_annotations`. Set the configuration variable
:py:data:`annotations_database` and :py:data:`annotations_dir`.

Pipeline output
===============

.. Describe output files of the pipeline here

Glossary
========

.. glossary::


Code
====

"""

from ruffus import *
from cgatcore import pipeline as P

import sys
import os
import re
import pandas as pd


PARAMS = P.get_parameters(
    ["%s/pipeline.yml" % os.path.splitext(__file__)[0],
     "../pipeline.yml",
     "pipeline.yml"])

# prints date and time, e.g. '2020-07-14T10:03:08'
DATETIME = "date +'%Y-%m-%dT%H:%M:%S'"

SAMPLES = pd.read_csv("samples.csv")
SAMPLES.set_index('name', inplace=True)


@follows(mkdir("count"))
@transform("data/*/.sample",
           regex(r"data/([A-Za-z0-9_]*)/.sample"),
           r"count/\1.done")
def cellranger_count(infile, outfile):
    '''Docstring'''

    sample = re.search('data/([A-Za-z0-9_]*)/.sample', infile).group(1)

    fastqs = SAMPLES['fastqs'][sample]
    cells = SAMPLES['cells'][sample]
    chemistry = SAMPLES['chemistry'][sample]

    transcriptome = PARAMS["transcriptome"]

    datetime = DATETIME

    job_threads = PARAMS["cellranger"]["count"]["threads"]
    job_memory = PARAMS["cellranger"]["count"]["memory"]

    local_memory = int(job_memory.replace("G", "")) * job_threads

    statement = """
    %(datetime)s > count/%(sample)s.time &&
    cellranger count
        --id %(sample)s
        --transcriptome %(transcriptome)s
        --fastqs %(fastqs)s
        --expect-cells %(cells)s
        --chemistry %(chemistry)s
        --localcores %(job_threads)s
        --localmem %(local_memory)s &&
        mv %(sample)s count/ &&
        touch %(outfile)s &&
    %(datetime)s >> count/%(sample)s.time
    """

    P.run(statement)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    P.main(argv)


if __name__ == "__main__":
    sys.exit(P.main(sys.argv))
