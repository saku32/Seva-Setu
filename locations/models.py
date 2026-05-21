from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class District(models.Model):
    name_en = models.CharField(max_length=100, verbose_name=_('Name (English)'))
    name_mr = models.CharField(max_length=100, verbose_name=_('Name (Marathi)'))
    name_hi = models.CharField(max_length=100, verbose_name=_('Name (Hindi)'))
    code = models.CharField(max_length=10, unique=True, verbose_name=_('Code'))
    slug = models.SlugField(unique=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        verbose_name = _('District')
        verbose_name_plural = _('Districts')
        ordering = ['name_en']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name_en

    def get_name(self, lang='en'):
        return getattr(self, f'name_{lang}', self.name_en)


class City(models.Model):
    district = models.ForeignKey(
        District,
        on_delete=models.CASCADE,
        related_name='cities',
        verbose_name=_('District')
    )
    name_en = models.CharField(max_length=100, verbose_name=_('Name (English)'))
    name_mr = models.CharField(max_length=100, verbose_name=_('Name (Marathi)'))
    name_hi = models.CharField(max_length=100, verbose_name=_('Name (Hindi)'))
    slug = models.SlugField(blank=True)
    pin_codes = models.CharField(max_length=500, blank=True, verbose_name=_('PIN Codes'),
                                  help_text=_('Comma-separated PIN codes'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = ['name_en']
        unique_together = ['district', 'slug']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name_en}, {self.district.name_en}'

    def get_name(self, lang='en'):
        return getattr(self, f'name_{lang}', self.name_en)


class Area(models.Model):
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name='areas',
        verbose_name=_('City')
    )
    name_en = models.CharField(max_length=100, verbose_name=_('Name (English)'))
    name_mr = models.CharField(max_length=100, verbose_name=_('Name (Marathi)'))
    name_hi = models.CharField(max_length=100, verbose_name=_('Name (Hindi)'))
    slug = models.SlugField(blank=True)
    pin_code = models.CharField(max_length=6, blank=True, verbose_name=_('PIN Code'))
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        verbose_name = _('Area')
        verbose_name_plural = _('Areas')
        ordering = ['name_en']
        unique_together = ['city', 'slug']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.name_en}, {self.city.name_en}'

    def get_name(self, lang='en'):
        return getattr(self, f'name_{lang}', self.name_en)
