from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apps', '0014_alter_clientnotification_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='WebsiteTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Template Name')),
                ('category', models.CharField(
                    max_length=50,
                    choices=[
                        ('restaurant', '🍽️ Restaurant'),
                        ('salon', '💅 Salon & Beauty'),
                        ('hotel', '🏨 Hotel & Lodging'),
                        ('shop', '🛒 Shop / Duka'),
                        ('clinic', '🏥 Clinic & Healthcare'),
                        ('church', '⛪ Church & Religion'),
                        ('school', '🎓 School & Education'),
                        ('portfolio', '🎨 Portfolio & Personal'),
                        ('other', '🌐 Other'),
                    ],
                    verbose_name='Category'
                )),
                ('description', models.TextField(verbose_name='Description')),
                ('badge', models.CharField(
                    max_length=10,
                    blank=True,
                    choices=[('HOT', '🔥 HOT'), ('NEW', '✨ NEW'), ('PRO', '⭐ PRO')],
                    verbose_name='Badge'
                )),
                ('rating', models.DecimalField(
                    max_digits=2, decimal_places=1, default=4.9,
                    verbose_name='Rating (e.g. 4.9)'
                )),
                # Prices
                ('price_hosted_monthly', models.IntegerField(
                    default=30000, verbose_name='Hosted Plan Monthly Price (TSh)'
                )),
                ('price_source_code', models.IntegerField(
                    default=150000, verbose_name='Source Code Price (TSh)'
                )),
                # The actual HTML preview code
                ('preview_html', models.TextField(
                    verbose_name='Preview HTML Code',
                    help_text='Weka HTML code yote ya template hapa. Itaonekana automatically kwenye preview page.'
                )),
                # Gradient colors for the card
                ('gradient_start', models.CharField(
                    max_length=20, default='#6c63ff',
                    verbose_name='Gradient Start Color (e.g. #ff6584)'
                )),
                ('gradient_end', models.CharField(
                    max_length=20, default='#ff6584',
                    verbose_name='Gradient End Color (e.g. #ff9a56)'
                )),
                ('is_active', models.BooleanField(default=True, verbose_name='Show on website')),
                ('order', models.IntegerField(default=0, verbose_name='Display Order (0 = first)')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Website Template',
                'verbose_name_plural': 'Website Templates',
                'ordering': ['order', '-created_at'],
            },
        ),
    ]
