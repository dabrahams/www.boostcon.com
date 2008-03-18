"""
views.py --- non-generic views used by stockphoto

This file is a part of stockphoto, a simple photogallery app for
    Django sites.

Copyright (C) 2006 Jason F. McBrayer <jmcbray-django@carcosa.net>
Copyright (C) 2006 William McVey <wamcvey@gmail.com>

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
02110-1301, USA.

"""

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

            # The path from the media root to the directory where we're
            # unzipping the photos.
            path_to_destdir= os.path.join(
                STOCKPHOTO_BASE, datetime.strftime(datetime.now(), "%Y/%m/%d/"))

            # Create that directory
            destdir = os.path.join(settings.MEDIA_ROOT, path_to_destdir)
            if not os.path.isdir(destdir):
                os.makedirs(destdir, 0775)
                
            for sourcepath in zip.namelist():
                data = zip.read(sourcepath)

                # Skip over anything that doesn't turn out to be an image
                file_data = StringIO(data)
                try:
                    Image.open(file_data)
                except:
                    continue

                # Extract the image
                filename = os.path.basename(sourcepath)
                photo = file(os.path.join(destdir, filename), "wb")
                photo.write(data)

                # Create the database object
                photo = Photo(image=os.path.join(path_to_destdir,filename),
                              date=date,
                              photographer=new_data['photographer'],
                              title = os.path.basename(sourcepath),
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
    

export = login_required(export)
