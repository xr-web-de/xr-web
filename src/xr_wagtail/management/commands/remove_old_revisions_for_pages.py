import logging

from django.core.management.base import BaseCommand

from xr_wagtail.services import get_old_revisions_for_all_pages


class Command(BaseCommand):
    help = "Deletes old revisions of all pages."

    def handle(self, *args, **options):
        logging.info("Starting the deletion of all old revisions of all pages.")
        revisions = get_old_revisions_for_all_pages()
        revisions.delete()
        logging.info("All old revisions of all pages have been deleted.")
