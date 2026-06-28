"""
Import real product photos.

USAGE
  1. Put your photos in the  product_photos/  folder at the project root.
  2. Name each file after the product, e.g.  air runner sneakers.jpg
     (spaces, underscores, capitals, and the extension are all ignored).
  3. Run:  python manage.py importimages

Any photo size works. Each image is centre-cropped to a consistent
4:5 portrait shape and resized, so the product grid stays tidy.

Options
  --dir FOLDER    read from a different folder
  --list          just show which products matched and which are missing
"""
import re
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from store.models import Product

try:
    from PIL import Image
except ImportError:
    Image = None

TARGET_W, TARGET_H = 900, 1100          # 4:5 portrait
VALID = {'.jpg', '.jpeg', '.png', '.webp', '.bmp'}


def key(text):
    """Normalise a name so 'Air Runner Sneakers' == 'air_runner-sneakers'."""
    return re.sub(r'[^a-z0-9]', '', text.lower())


class Command(BaseCommand):
    help = 'Import real product photos from a folder and attach them to products'

    def add_arguments(self, parser):
        parser.add_argument('--dir', default='product_photos')
        parser.add_argument('--list', action='store_true')

    def handle(self, *args, **opts):
        if Image is None:
            self.stderr.write('Pillow is not installed. Run: pip install Pillow')
            return

        src_dir = Path(settings.BASE_DIR) / opts['dir']
        if not src_dir.exists():
            src_dir.mkdir(parents=True, exist_ok=True)
            self.stdout.write(self.style.WARNING(
                f'Created {src_dir}. Put your photos in there and run this again.'))
            return

        photos = [p for p in src_dir.iterdir() if p.suffix.lower() in VALID]
        products = list(Product.objects.all())
        lookup = {key(p.name): p for p in products}

        if opts['list']:
            self.stdout.write(f'Looking in: {src_dir}')
            self.stdout.write('Photos found: %d' % len(photos))
            if not photos:
                self.stdout.write(self.style.WARNING(
                    'That folder is empty. Put your photos there, named after '
                    'the products, then run this again.'))
            for f in photos:
                match = lookup.get(key(f.stem))
                flag = 'MATCH   ' if match else 'NO MATCH'
                self.stdout.write(f'  {flag} {f.name}')

            have_photo = {key(f.stem) for f in photos}
            waiting = [p for p in products if key(p.name) not in have_photo]
            if waiting:
                self.stdout.write('')
                self.stdout.write('Products with no photo in the import folder '
                                  '(these keep their current image):')
                for p in waiting:
                    current = 'has generated artwork' if p.image else 'NO IMAGE AT ALL'
                    self.stdout.write(f'  {p.name}  ({current})')
            return

        media_dir = Path(settings.MEDIA_ROOT) / 'products'
        media_dir.mkdir(parents=True, exist_ok=True)

        done, skipped = 0, []
        for photo in photos:
            product = lookup.get(key(photo.stem))
            if not product:
                skipped.append(photo.name)
                continue

            img = Image.open(photo)
            if img.mode in ('RGBA', 'P', 'LA'):
                bg = Image.new('RGB', img.size, (18, 18, 26))
                img = img.convert('RGBA')
                bg.paste(img, mask=img.split()[-1])
                img = bg
            else:
                img = img.convert('RGB')

            # centre-crop to 4:5 then resize
            w, h = img.size
            want = TARGET_W / TARGET_H
            have = w / h
            if have > want:                       # too wide, trim sides
                new_w = int(h * want)
                left = (w - new_w) // 2
                img = img.crop((left, 0, left + new_w, h))
            else:                                 # too tall, trim top/bottom
                new_h = int(w / want)
                top = (h - new_h) // 2
                img = img.crop((0, top, w, top + new_h))
            img = img.resize((TARGET_W, TARGET_H), Image.LANCZOS)

            filename = key(product.name) + '.jpg'
            img.save(media_dir / filename, 'JPEG', quality=88)
            product.image = f'products/{filename}'
            product.save()
            done += 1
            self.stdout.write(f'  attached {photo.name} -> {product.name}')

        if skipped:
            self.stdout.write(self.style.WARNING(
                'No matching product for: ' + ', '.join(skipped)))
        self.stdout.write(self.style.SUCCESS(f'Imported {done} photo(s).'))
