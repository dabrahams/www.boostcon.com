from django.db import models
from django.utils.translation import gettext_lazy as _
import django.contrib.auth.models as auth
from django.conf import settings
from django.dispatch import dispatcher
from django.db.models import signals

import os, os.path
import Image

# Handle settings here
try:
    STOCKPHOTO_BASE = settings.STOCKPHOTO_BASE.strip('/')
except AttributeError:
    STOCKPHOTO_BASE='stockphoto'
    
try:
    STOCKPHOTO_URL = settings.STOCKPHOTO_URL
except AttributeError:
    STOCKPHOTO_URL='/stockphoto'
if STOCKPHOTO_URL[-1] == '/':
    STOCKPHOTO_URL=STOCKPHOTO_URL[:-1]

try:
    ADMIN_URL = settings.ADMIN_URL
except AttributeError:
    ADMIN_URL='/admin'
if ADMIN_URL[-1] == '/':
    ADMIN_URL=ADMIN_URL[:-1]

# Create your models here.
class Gallery(models.Model):
    title = models.CharField(_("title"), maxlength=80)
    slug = models.SlugField(prepopulate_from=("title",))
    date = models.DateField(_("publication date"), auto_now_add=True)
    created = models.ForeignKey(auth.User,
                              verbose_name=_("gallery created by")
                              )
    display_width = models.IntegerField(
        _("width to display full images"),
        default=640)
    display_height = models.IntegerField(
        _("height to display full images"),
        default=480)
    thumbnail_width = models.IntegerField(
        _("width to display thumbnails"),
        default=150)
    thumbnail_height = models.IntegerField(
        _("height to display thumbnails"),
        default=100)

    class Meta:
        get_latest_by = 'date'

    class Admin:
        ordering = ['date']

    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return "%s/%d/" % (STOCKPHOTO_URL, self.id)
    def get_admin_url(self):
        return "%s/stockphoto/gallery/%d/" % (ADMIN_URL, self.id)
    def was_published_today(self):
        return self.date.date() == datetime.date.today()

    def first(self):
        try:
            return self.photo_set.all()[0]
        except IndexError:
            return None
    def update_thumbs(self):
        for photo in self.photo_set.all():
            photo.create_disp()
            photo.create_thumb()

class Photo(models.Model):
    # import os, os.path, Image
    image = models.ImageField(_("Photograph"),
                            upload_to= STOCKPHOTO_BASE + "/%Y/%m/%d/")
    title = models.CharField(_("title"), maxlength=80)
    desc = models.TextField(_("description"), blank=True)
    gallery = models.ForeignKey(Gallery)
    photographer = models.CharField(_("photographer"), maxlength=80,
                                  blank=True)
    date = models.DateField(_("date photographed"), blank=True, null=True)
    extra = models.TextField(_("any extra information about the photo"),
                           blank=True)
    class META:
        get_latest_by = 'date'

    class Admin:
        ordering = ['date']

    def __str__(self):
        return self.title

    def delete_thumbnails(self):
        """Remove thumbnail and display-sized images when deleting.

        This may fail if, for example, they don't exist, so it should
        fail silently.  It may not be a good idea to delete the
        original, as the user may not understand that deleting it from
        the gallery deletes it from the filesystem, so currently we
        don't do that.
        
        """
        try:
            os.unlink(self.thumbpath())
        except (IOError, OSError):
            pass
        try:
            os.unlink(self.disppath())
        except (IOError, OSError):
            pass
        # Deleting the original might be a bad thing.
        #os.unlink(self.fullpath())

    def get_absolute_url(self):
        return "%s/detail/%d/" % (STOCKPHOTO_URL, self.id)

    def get_admin_url(self):
        return "%s/stockphoto/photos/%d/" % (ADMIN_URL, self.id)

    def thumbpath(self):
        """Path to the thumbnail
        """
        photobase = self.image[len(STOCKPHOTO_BASE)+1:]
        return os.path.join( settings.MEDIA_ROOT, STOCKPHOTO_BASE,
                     "cache", "thumbs", photobase)

    def thumburl(self):
        """URL to the thumbnail
        """
        photobase = self.image[len(STOCKPHOTO_BASE)+1:]
        if settings.MEDIA_URL.endswith('/'):
            return settings.MEDIA_URL + STOCKPHOTO_BASE + \
                "/cache/thumbs/" + photobase
        return settings.MEDIA_URL + '/' + STOCKPHOTO_BASE + \
            "/cache/thumbs/" + photobase
            

    def disppath(self):
        photobase = self.image[len(STOCKPHOTO_BASE)+1:]
        return os.path.join( settings.MEDIA_ROOT, STOCKPHOTO_BASE,
                         "cache", photobase)

    def dispurl(self):
        photobase = self.image[len(STOCKPHOTO_BASE)+1:]
        if settings.MEDIA_URL.endswith('/'):
            return settings.MEDIA_URL + STOCKPHOTO_BASE + "/cache/" \
                + photobase
        return settings.MEDIA_URL + '/' + STOCKPHOTO_BASE + \
            "/cache/" + photobase            

    def fullpath(self):
        if self.image.startswith(os.path.sep):
            return self.image
        return os.path.join(settings.MEDIA_ROOT, self.image)

    def fullurl(self):
        if self.image.startswith(os.path.sep):
            # Shouldn't happen anymore
            return (settings.MEDIA_URL +
                    self.image[len(settings.MEDIA_ROOT):])
        else:
            if settings.MEDIA_URL.endswith('/'):
                return settings.MEDIA_URL + self.image
            return settings.MEDIA_URL + '/' + self.image
        

    def next(self):
        '''Return id of 'next' photo in the same gallery or None if at
        the end.'''
        # we could probably be more clever here by using the new nifty 
        # db access filters and queries, but for now, this is good enough
        photo_list = [x for x in self.gallery.photo_set.all()]
        ind = photo_list.index(self)
        if (ind +1) == len(photo_list):
            return None
        else:
            return photo_list[ind + 1]

    def prev(self):
        """Return id of 'previous' photo in the same gallery or None
        if at the beginning
        """
        photo_list = [x for x in self.gallery.photo_set.all()]
        ind = photo_list.index(self)
        if ind == 0:
            return False
        else:
            return photo_list[ind - 1]

    def full_exists(self):
        return os.path.exists( self.fullpath() )

    def disp_exists(self):
        return os.path.exists( self.disppath() )

    def thumb_exists(self):
        return os.path.exists( self.thumbpath() )

    def create_disp(self):
        im = Image.open( self.fullpath() )
        format = im.format
        # create the path for the display image
        disp_path = self.disppath()
        disp_dir = os.path.dirname(disp_path)
        if not os.path.exists(disp_dir):
            os.makedirs(disp_dir, 0775)

        # Make a copy of the image, scaled, if needed.
        maxwidth = self.gallery.display_width
        maxheight = self.gallery.display_height
        width, height = im.size
        if (width > maxwidth) and width > height:
            scale = float(maxwidth)/width
            width = int(width * scale)
            height = int(height * scale)
            newim = im.resize( (width, height), Image.ANTIALIAS )
        elif (height > maxheight) and height >= width:
            scale = float(maxheight)/height
            width = int(width * scale)
            height = int(height * scale)
            newim = im.resize( (width, height), Image.ANTIALIAS )
        else:
            newim = im
        newim.save(disp_path, format)

    def create_thumb(self):
        im = Image.open( self.fullpath() )
        format = im.format
        # create the path for the thumbnail image
        thumb_path = self.thumbpath()
        thumb_dir = os.path.dirname(thumb_path)
        if not os.path.exists(thumb_dir):
            os.makedirs(thumb_dir, 0775)

        # Make a copy of the image, scaled, if needed.
        maxwidth = self.gallery.thumbnail_width
        maxheight = self.gallery.thumbnail_height
        width, height = im.size
        if (width > maxwidth) and (width > height):
            scale = float(maxwidth)/width
            width = int(width * scale)
            height = int(height * scale)
            newim = im.resize( (width, height), Image.ANTIALIAS )
        elif (height > maxheight):
            scale = float(maxheight)/height
            width = int(width * scale)
            height = int(height * scale)
            newim = im.resize( (width, height), Image.ANTIALIAS )
        else:
            newim = im
        newim.save(thumb_path, format)

    def build_display_images(self):
        """Make thumbnail and display-sized images after saving.
        
        For some reason, this may fail on a first pass (self.image may
        be empty when this is called), but if we just let it fail
        silently, it will apparently get called again and succeed.
        """
        if self.image:
            if not self.thumb_exists():
                self.create_thumb()
            if not self.disp_exists():
                self.create_disp()

def build_display_images(sender, instance, signal, *args, **kwargs):
    """Simple hook for save-after trigger
    """
    instance.build_display_images()
def delete_thumbnails(sender, instance, signal, *args, **kwargs):
    """Simple hook for pre-delete trigger.
    """
    instance.delete_thumbnails()

dispatcher.connect(build_display_images, signal=signals.post_save,
                   sender=Photo) 
dispatcher.connect(delete_thumbnails, signal=signals.pre_delete,
                   sender=Photo)
