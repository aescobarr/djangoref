from django.db import models
from django.contrib.gis.db import models
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from django.dispatch import receiver
#from georef.models import Toponim, Recursgeoref, Toponimversio, pkgen
from georef.tasks import pkgen
import djangoref.settings as conf
import os
from django.utils.translation import gettext as _


# Create your models here.
class GeometriaToponimVersio(models.Model):
    idversio = models.ForeignKey('georef.Toponimversio', on_delete=models.CASCADE, db_column='idversio', blank=True, null=True, related_name='geometries')
    geometria = models.GeometryField(srid=4326)
    x_min = models.FloatField(blank=True, null=True)
    x_max = models.FloatField(blank=True, null=True)
    y_min = models.FloatField(blank=True, null=True)
    y_max = models.FloatField(blank=True, null=True)

    class Meta:
        verbose_name = _('Geometria de versió de topònim')

    def __str__(self):
        return 'Geometria %s %s' % (self.idversio.nom, self.geometria.geom_type)

    def clone(self):
        clone = GeometriaToponimVersio()
        clone.idversio = self.idversio
        clone.geometria = self.geometria.clone()
        return clone

    def save(self, *args, **kwargs):
        if self.geometria:
            extent = self.geometria.extent
            self.x_min = extent[0]
            self.y_min = extent[1]
            self.x_max = extent[2]
            self.y_max = extent[3]
        super(GeometriaToponimVersio, self).save(*args, **kwargs)

class GeometriaRecurs(models.Model):
    idrecurs = models.ForeignKey('georef.Recursgeoref', on_delete=models.CASCADE, db_column='idrecurs', blank=True, null=True, related_name='geometries')
    geometria = models.GeometryField(srid=4326)

    class Meta:
        verbose_name = _('Geometria de recurs de georeferenciació')


class Organization(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Organització')

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization = models.ForeignKey('georef_addenda.Organization', on_delete=models.CASCADE, blank=True, null=True)
    toponim_permission = models.CharField(max_length=200, null=True, blank=True)
    permission_recurs_edition = models.BooleanField(default=False)
    permission_toponim_edition = models.BooleanField(default=False)
    permission_tesaure_edition = models.BooleanField(default=False)
    permission_administrative = models.BooleanField(default=False)
    permission_filter_edition = models.BooleanField(default=False)

    class Meta:
        verbose_name = _("Perfil d'usuari")

    @property
    def is_admin(self):
        return self.permission_administrative

    @property
    def can_edit_recurs(self):
        return self.permission_recurs_edition

    @property
    def can_edit_toponim(self):
        return self.permission_toponim_edition

    @property
    def can_edit_tesaure(self):
        return self.permission_tesaure_edition

    @property
    def can_edit_filtre(self):
        return self.permission_filter_edition

    def __str__(self):
        return 'Permisos usuari %s' % (self.user.username)

class Autor(models.Model):
    id = models.CharField(primary_key=True, max_length=200, default=pkgen)
    nom = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = _('Autor')

    def __str__(self):
        return '%s' % (self.nom)


class HelpFile(models.Model):
    id = models.CharField(primary_key=True, max_length=200, default=pkgen)
    titol = models.TextField()
    h_file = models.FileField(upload_to=conf.LOCAL_DATAFILE_ROOT_DIRECTORY)
    created_on = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = _("Fitxer d'ajuda")


class MenuItem(models.Model):
    title = models.TextField(blank=True, null=True)
    language = models.CharField(max_length=5, blank=True, null=True)
    link = models.URLField(blank=True, null=True)
    open_in_outside_tab = models.BooleanField(default=True)
    is_separator = models.BooleanField(default=False)
    order = models.IntegerField(blank=True, null=True)

    class Meta:
        verbose_name = _("Item del menú")


@receiver(models.signals.post_delete, sender=HelpFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.h_file:
        if os.path.isfile(instance.h_file.path):
            os.remove(instance.h_file.path)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class LookupDescription(models.Model):
    model_fully_qualified_name = models.CharField(help_text="The name of the model, in form [package].[name]", max_length=300, null=True)
    model_label = models.CharField(help_text="The label of the lookup. This should be the same as the unstranslated string used for showing the name anywhere in the ui", max_length=200, null=True)
    locale = models.CharField(help_text="Language of the description", max_length=10, null=True)
    description = models.TextField(null=True)


class GeoreferenceProtocol(models.Model):
    name = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)

    @classmethod
    def get_default_pk(cls):
        prot, created = cls.objects.get_or_create(
            name=_('Protocol de georeferenciació del Museu de Zoologia de Barcelona')
        )
        return prot.pk

    class Meta:
        verbose_name = _('Protocol de georeferenciació')

    def __str__(self):
        return '%s' % (self.name)
