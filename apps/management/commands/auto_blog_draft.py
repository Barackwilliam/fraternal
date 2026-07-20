"""
Auto-draft blog: AI inaandika RASIMU ya makala kama hakuna post mpya kwa siku 3.

Endesha kwa cron/scheduler (mfano kila siku saa 6 usiku):
    python manage.py auto_blog_draft

Options:
    --force        Andika draft hata kama siku 3 hazijapita
    --days N       Badilisha kizingiti (default 3)

AI inaandika DRAFT tu (status='draft'). Mmiliki anakagua admin, anabonyeza Publish.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from apps.models import BlogPost, BlogCategory


class Command(BaseCommand):
    help = 'AI inaandika rasimu ya blog kama hakuna post mpya kwa siku 3'

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true',
                            help='Andika hata kama siku 3 hazijapita')
        parser.add_argument('--days', type=int, default=3,
                            help='Idadi ya siku bila post kabla AI kuandika (default 3)')

    def handle(self, *args, **opts):
        days = opts['days']
        force = opts['force']

        # Angalia post ya mwisho (published AU draft — tusiandike draft juu ya draft)
        last = BlogPost.objects.order_by('-created_at').first()
        if last and not force:
            age = timezone.now() - last.created_at
            if age < timedelta(days=days):
                remaining = timedelta(days=days) - age
                hrs = int(remaining.total_seconds() // 3600)
                self.stdout.write(
                    f'Post ya mwisho ni ya hivi karibuni ({age.days}d). '
                    f'Bado ~{hrs}h kabla ya kuandika mpya. Tumia --force kulazimisha.')
                return

        # Kama tayari kuna draft inayosubiri kukaguliwa, usiongeze nyingine
        pending = BlogPost.objects.filter(status='draft').count()
        if pending >= 2 and not force:
            self.stdout.write(
                f'Kuna rasimu {pending} zinazosubiri kukaguliwa. '
                f'Kagua/publish hizo kwanza. Tumia --force kupuuza.')
            return

        # Kusanya titles zilizopo ili AI isirudie mada
        existing = list(BlogPost.objects.values_list('title', flat=True))

        self.stdout.write('AI inaandika rasimu ya makala…')
        try:
            from apps import blog_ai
            ok, result = blog_ai.generate_draft(existing_titles=existing)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'AI imeshindwa: {type(e).__name__}: {e}'))
            return

        if not ok:
            self.stderr.write(self.style.ERROR(f'Imeshindwa: {result}'))
            return

        # Hakikisha slug ni ya kipekee
        base_slug = result['slug']
        slug = base_slug
        n = 2
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{n}'
            n += 1

        # Category kwa lugha
        cat_name = 'Web Development'
        cat, _ = BlogCategory.objects.get_or_create(
            slug='web-development', defaults={'name': cat_name})

        post = BlogPost.objects.create(
            title=result['title'],
            slug=slug,
            category=cat,
            excerpt=result['excerpt'],
            body=result['body'],
            meta_description=result['meta_description'],
            focus_keyword=result['focus_keyword'],
            author_name='JamiiTek',
            status='draft',   # ← DRAFT, si published
            is_featured=False,
        )
        self.stdout.write(self.style.SUCCESS(
            f'✓ Rasimu imeundwa: "{post.title}" ({result["language"].upper()})\n'
            f'  Kagua kwenye admin → Blog Posts → weka Published ukiridhika.\n'
            f'  Slug: /blog/{post.slug}/'))
