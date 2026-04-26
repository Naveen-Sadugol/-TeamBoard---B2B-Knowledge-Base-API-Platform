from django.core.management.base import BaseCommand

from api.models import KBEntry


KB_ENTRIES = [
    {
        "question": "What is select_related in Django ORM?",
        "answer": "select_related performs a SQL join and fetches related foreign key objects in the same query.",
        "category": KBEntry.Category.DATABASE,
    },
    {
        "question": "When should I use prefetch_related instead of select_related?",
        "answer": "Use prefetch_related for many-to-many or reverse foreign key relationships when a join would duplicate rows.",
        "category": KBEntry.Category.DATABASE,
    },
    {
        "question": "How does transaction.atomic() work in Django?",
        "answer": "transaction.atomic wraps a block in a database transaction and rolls back everything if an exception is raised.",
        "category": KBEntry.Category.DATABASE,
    },
    {
        "question": "What is a JWT token?",
        "answer": "A JWT token is a signed JSON payload often used for stateless API authentication between clients and servers.",
        "category": KBEntry.Category.API,
    },
    {
        "question": "When should I use Q objects?",
        "answer": "Q objects help build complex OR, AND, and NOT conditions in Django ORM queries.",
        "category": KBEntry.Category.FRAMEWORK,
    },
    {
        "question": "What are Django signals used for?",
        "answer": "Signals let you react to model lifecycle events like post_save without placing that logic directly in a view.",
        "category": KBEntry.Category.FRAMEWORK,
    },
    {
        "question": "How do API keys differ from usernames?",
        "answer": "API keys are server-issued secrets for authenticating requests, while usernames are public identifiers.",
        "category": KBEntry.Category.API,
    },
    {
        "question": "What is horizontal scaling in cloud infrastructure?",
        "answer": "Horizontal scaling adds more machines or containers to handle more traffic instead of increasing a single server size.",
        "category": KBEntry.Category.CLOUD,
    },
    {
        "question": "Why use connection pooling with PostgreSQL?",
        "answer": "Connection pooling reduces overhead by reusing database connections across requests.",
        "category": KBEntry.Category.DATABASE,
    },
    {
        "question": "How should onboarding tools consume a knowledge base API?",
        "answer": "They should authenticate each request, send the search term, and display the returned question and answer matches.",
        "category": KBEntry.Category.GENERAL,
    },
    {
        "question": "How can query logging help an API platform?",
        "answer": "Query logging tracks total usage, popular search terms, and billing-related activity even when no answers are returned.",
        "category": KBEntry.Category.GENERAL,
    },
]


class Command(BaseCommand):
    help = "Seed the knowledge base with initial TeamBoard entries."

    def handle(self, *args, **options):
        created_count = 0
        for entry in KB_ENTRIES:
            _, created = KBEntry.objects.get_or_create(
                question=entry["question"],
                defaults={
                    "answer": entry["answer"],
                    "category": entry["category"],
                },
            )
            if created:
                created_count += 1
        self.stdout.write(self.style.SUCCESS(f"Seed complete. Added {created_count} entries."))
