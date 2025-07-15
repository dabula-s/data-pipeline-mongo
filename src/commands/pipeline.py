import logging

import click

logger = logging.getLogger(__name__)


@click.group()
def pipeline():
    pass


@pipeline.command()
def run_pipeline():
    from src.infrastructure.pipeline import fetching_step, normalization_step, deduplication_step
    fetching_step()
    normalization_step()
    deduplication_step()
