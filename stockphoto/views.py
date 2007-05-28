# Create your views here.

# django imports
from django.conf import settings
from django import forms, http, template
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse
from django.template.context import RequestContext

# other imports
import zipfile
import os
import stat
import shutil
from datetime import datetime
from tempfile import NamedTemporaryFile, mkdtemp
import Image
try:
	from cStringIO import StringIO
except ImportError:
	from StringIO import StringIO

# Handling settings here
try:
    STOCKPHOTO_BASE = settings.STOCKPHOTO_BASE.strip('/')
except AttributeError:
    STOCKPHOTO_BASE = 'stockphoto'
    
# models
from stockphoto.models import Gallery, Photo

# views

class ImportManipulator(forms.Manipulator):
    def __init__(self):
        self.fields = (
            forms.FileUploadField(field_name="zipfile",
                            is_required=True,
                            validator_list=[self.valid_zipfile,]),
            forms.TextField(field_name="photographer"),
            forms.DateField(field_name="date"),
        )
    def valid_zipfile(self, field_data, all_data):
    	zip_file = StringIO(field_data['content'])
	zip = zipfile.ZipFile(zip_file)
	return not zip.testzip()



@login_required
def import_photos(request, thegallery):
    """Import a batch of photographs uploaded by the user.

    Import a batch of photographs uploaded by the user, all with
    the same information for gallery, photographer and date.  The
    title will be set from the filename, and the description will be
    blank.  Self-respecting photographers will edit the fields for
    each photograph; this is just a way to get a bunch of photographs
    uploaded quickly.

    The photographs should be wrapped up in a zip archive.  The
    archive will be unpacked (and flattened) in a temporary directory,
    and all image files will be identified and imported into the
    gallery.  Other files in the archive will be silently ignored.

    After importing the images, the view will display a page which may
    contain the number of images imported, and a link to the gallery
    into which the images were imported.
    """
    # Check if the gallery is valid
    gallery = get_object_or_404(Gallery, pk=thegallery)
    # And that the user has permission to add photos
    if not request.user.has_perm('gallery.add_photo'):
        return http.HttpResponseForbidden("No permission to add photos")

    manipulator = ImportManipulator()
    if request.POST:
        new_data = request.POST.copy()
        new_data.update(request.FILES)
        errors = manipulator.get_validation_errors(new_data)
        if not errors:
            # So now everything is okay
	    f = StringIO(new_data['zipfile']['content']) # the zip"file"
	    zip = zipfile.ZipFile(f)
            manipulator.do_html2python(new_data)
            date = new_data['date']
            if not date:
                date = datetime.date(datetime.now())

	    destdir= os.path.join(settings.MEDIA_ROOT, STOCKPHOTO_BASE,
                                  datetime.strftime(datetime.now(), 
				  "%Y/%m/%d/"))
	    if not os.path.isdir(destdir):
	        os.makedirs(destdir, 0775)
            for filename in zip.namelist():
                photopath = os.path.join(destdir, os.path.basename(filename))
                data = zip.read(filename)
                file_data = StringIO(data)
                try:
                    Image.open(file_data)
                except:
                    # don't save and process non Image files
                    continue
                photo = file(photopath, "wb")
                photo.write(data)

                # Create the object
                if photopath.startswith(os.path.sep):
                    photopath = photopath[len(settings.MEDIA_ROOT):]
                photo = Photo(image=photopath, date=date,
                              photographer=new_data['photographer'],
                              title = os.path.basename(filename),
                              gallery_id = thegallery)
                # Save it -- the thumbnails etc. get created.
                photo.save()

            # And jump to the directory for this gallery
            response = http.HttpResponseRedirect(gallery.get_absolute_url())
            response['Pragma'] = 'no cache'
            response['Cache-Control'] = 'no-cache'
            return response
    else:
        errors = new_data = {}
    form = forms.FormWrapper(manipulator, new_data, errors)
    return render_to_response('stockphoto/import_form.html',
			      dict(form=form, gallery=gallery),
                              context_instance = RequestContext(request))
	# request, 

@login_required
def export(request, thegallery):
    """Export a gallery to a zip file and send it to the user.
    """
    # Check if the gallery is valid
    gallery = get_object_or_404(Gallery, pk=thegallery)
    
    # gather up the photos into a new directory
    tmpdir = mkdtemp()
    for photo in gallery.photo_set.all():
        shutil.copy(photo.get_image_filename(),
                        tmpdir)
    files = [ os.path.join(tmpdir, ff) for ff in os.listdir(tmpdir) ]
    outfile = NamedTemporaryFile()
    zf = zipfile.ZipFile(outfile, "w",
                         compression=zipfile.ZIP_DEFLATED)
    for filename in files:
        zf.write(filename, arcname=os.path.basename(filename))
    zf.close()
    outfile.flush()
    outfile.seek(0)
    shutil.rmtree(tmpdir)
    response = HttpResponse(outfile)
    response['Content-Type'] = "application/zip"
    response['Content-Length'] = str(os.stat(outfile.name)[stat.ST_SIZE])
    response['Content-Disposition'] = "attachment; filename=photos.zip"
    return response
    
