"""
Seed the database with sample categories, products, images, and a demo user.

Run:  python manage.py seed

Product images are bundled with the project (store/static/store/products/)
and copied into MEDIA_ROOT, so the site works fully offline.
"""
import shutil
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Category, Product, UserProfile

# where the bundled images live
SRC_DIR = Path(settings.BASE_DIR) / 'store' / 'static' / 'store' / 'products'


class Command(BaseCommand):
    help = 'Seed sample data for the demo'

    def handle(self, *args, **kwargs):
        cats = {
            'shirts': 'Shirts', 'shoes': 'Shoes', 'jackets': 'Jackets',
            'accessories': 'Accessories', 'pants': 'Pants',
        }
        cat_objs = {}
        for slug, name in cats.items():
            c, _ = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            cat_objs[slug] = c

        products = [
            ('Classic Oxford Shirt', 'shirts', 'Zara', 49.99, 'Crisp cotton oxford, tailored fit.', 'S,M,L,XL'),
            ('Graphic Tee', 'shirts', 'H&M', 24.99, 'Soft cotton tee with modern print.', 'S,M,L,XL'),
            ('Air Runner Sneakers', 'shoes', 'Nike', 129.99, 'Lightweight everyday running shoe.', '7,8,9,10,11'),
            ('Ultraboost Trainers', 'shoes', 'Adidas', 149.99, 'Responsive cushioning for all day comfort.', '7,8,9,10,11'),
            ('Suede Chelsea Boots', 'shoes', 'Other', 99.99, 'Timeless suede boots.', '7,8,9,10,11'),
            ('Denim Trucker Jacket', 'jackets', 'Levis', 89.99, 'Iconic denim jacket, medium wash.', 'S,M,L,XL'),
            ('Puffer Jacket', 'jackets', 'Puma', 119.99, 'Warm insulated puffer for winter.', 'S,M,L,XL'),
            ('Leather Belt', 'accessories', 'Other', 34.99, 'Full grain leather belt.', 'Regular'),
            ('Wool Beanie', 'accessories', 'H&M', 19.99, 'Cozy ribbed wool beanie.', 'Regular'),
            ('Slim Fit Chinos', 'pants', 'Zara', 54.99, 'Versatile slim chinos.', 'S,M,L,XL'),
            ('Cargo Joggers', 'pants', 'Puma', 64.99, 'Relaxed cargo joggers with pockets.', 'S,M,L,XL'),
            ('Canvas Backpack', 'accessories', 'Other', 44.99, 'Durable canvas daypack.', 'Regular'),
        ]

        # make sure media/products/ exists
        media_dir = Path(settings.MEDIA_ROOT) / 'products'
        media_dir.mkdir(parents=True, exist_ok=True)

        attached = 0
        for name, cat, brand, price, desc, sizes in products:
            p, created = Product.objects.get_or_create(
                name=name, defaults={
                    'category': cat_objs[cat], 'brand': brand,
                    'price': price, 'description': desc, 'stock': 15,
                    'sizes': sizes,
                })
            # attach the bundled image if we have one and the product has none
            filename = name.lower().replace(' ', '_') + '.jpg'
            src = SRC_DIR / filename
            if src.exists():
                dest = media_dir / filename
                # always refresh so updated artwork propagates
                shutil.copyfile(src, dest)
                p.image = f'products/{filename}'
                p.save()
                attached += 1

        # demo user
        if not User.objects.filter(username='demo').exists():
            u = User.objects.create_user('demo', 'demo@threadline.local', 'demo12345')
            UserProfile.objects.create(user=u)
            self.stdout.write('Created demo user (demo / demo12345)')

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {Product.objects.count()} products across '
            f'{Category.objects.count()} categories. Images attached: {attached}.'))
