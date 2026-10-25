"""Module 09 - news ingestion and daily edition pipeline.

    sources -> fetch -> normalize -> deduplicate/cluster -> metadata ->
    classify -> rank -> summarize -> validate sources -> edition

Each stage is a small module with plain functions so it can be tested (and
replaced) alone. `runner.run_pipeline` wires them together; `__main__` is the
scheduler-facing CLI.
"""

PIPELINE_VERSION = "1.0.0"
