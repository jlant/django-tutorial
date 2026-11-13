from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection
from polls.models import Choice, Question


class Command(BaseCommand):
    help = (
        "Deletes all polls data, resets SQLite sequences, and reloads polls_seed.json"
    )

    def handle(self, *args, **options):
        self.stdout.write("Clearing existing polls data...")
        Choice.objects.all().delete()
        Question.objects.all().delete()

        self.stdout.write("Resetting SQLite auto-increment sequences...")
        with connection.cursor() as cursor:
            cursor.execute(
                "DELETE FROM sqlite_sequence WHERE name IN ('polls_question', 'polls_choice');"
            )

        self.stdout.write("Loading fixture: polls_seed.json...")
        call_command("loaddata", "polls_seed.json")

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully reset polls data and preserved admin users."
            )
        )
