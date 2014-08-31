# -*- coding: utf-8 -*- 
from django.http import HttpResponse
from django.http import Http404

import zipfile
import StringIO

class InMemoryZip(object):
    def __init__(self):
        # Create the in-memory file-like object
        self.in_memory_zip = StringIO.StringIO()

    def append(self, filename_in_zip, file_contents, folder=""):
        '''Appends a file with name filename_in_zip and contents of 
        file_contents to the in-memory zip.'''
        # Get a handle to the in-memory zip in append mode
        zf = zipfile.ZipFile(self.in_memory_zip, "a", zipfile.ZIP_DEFLATED, False)

        if not folder:
            folder=""
        if len(folder)>0:
            if folder[-1]!='/':
                folder += '/';
#            zf.wirte(filename_in_zip, folder+filename_in_zip, 
#        print folder
        # Write the file to the in-memory zip
        zf.writestr(str(folder)+filename_in_zip, file_contents)

        # Mark the files as having been created on Windows so that
        # Unix permissions are not inferred as 0000
        for zfile in zf.filelist:
            zfile.create_system = 0        
        zf.close()

        return self

    def read(self):
        '''Returns a string with the contents of the in-memory zip.'''
        self.in_memory_zip.seek(0)
        return self.in_memory_zip.read()

    def writetofile(self, filename):
        '''Writes the in-memory zip to a file.'''
        f = file(filename, "w")
        f.write(self.read())
        f.close()

    def close(self):
        self.in_memory_zip.close()


def zip(src, dst):
    zf = zipfile.ZipFile("%s" % (dst), "w")
    abs_src = os.path.abspath(src)
    for dirname, subdirs, files in os.walk(src):
        for filename in files:
            absname = os.path.abspath(os.path.join(dirname, filename))
            arcname = absname[len(abs_src) + 1:]
            print 'zipping %s as %s' % (os.path.join(dirname, filename),
                                        arcname)
            zf.write(absname, arcname)
    zf.close()

import os
def home(request):
#    print request
    response = HttpResponse()
#    print os.path.exists('arch')
#    print os.path.exists('DjangoTest/haha')
    # Run a memzip test
    if 'zip' in request.GET:
        folder = 'arch/'
        filename = 'abc'
        zipname = 'abc.zip'

        filepath = folder+filename
        zippath = folder+zipname
        if not os.path.exists(filepath):
            raise Http404

        print 'zipping'
        zip(filepath, zippath)

        print 'ready to open'
        if not os.path.exists(zippath):
            raise Http404

        print 'opening'
        f = open(zippath, "r")
        response['Content-Type'] = 'application/octet-stream'
        response['Content-disposition'] = 'attachment; filename=%s' % zipname
        response.write(f.read())
        f.close()

    # Run a memzip test
    elif 'memzip' in request.GET:
        filename = 'test.zip'
        imz = InMemoryZip()
        imz.append("測試.txt", "一二三Another test", "abc/") \
           .append("test2.txt", "Still another")
#        imz.writetofile(filename)

        response['Content-Type'] = 'application/octet-stream'
        response['Content-disposition'] = 'attachment; filename=%s' % filename
        response.write(imz.read())
        imz.close()

    elif 'readline' in request.GET:
        path = 'arch/abc/hahahah.txt'
        print 'check path %s' % path
        if not os.path.exists(path):
            print '%s not exists' % path
            raise Http404

        print 'opening'
        f = open(path)
        print f
        content = f.read().rstrip('\n').split('||')
        f.close()

        print content
        status = content[0]
        total = int(content[1])
        now = int(content[2])
        content[2] = now+20
        content = map(str, content)
        print content

        f = open(path, 'w')
        content = f.write( '||'.join(content) )
        f.close()

    else:
        response.write("Hello, world. You're at the Home!!")

    return response



