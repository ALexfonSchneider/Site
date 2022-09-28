from Site.settings import ALLOWED_HOSTS
from django.shortcuts import render
from django.http.response import StreamingHttpResponse, HttpResponse, FileResponse, HttpResponseNotFound
from django.http import Http404
from wsgiref.util import FileWrapper
from .models import *
import os
import io
import mimetypes
import pathlib
import re

video_extentions = (
    '.mp4', 'mkv',
)

text_extentions = (
    '.txt', '.doc', '.pdf', '.docx', 'dll', 'xml', '.html', '.css', '.py'
)

def renderdock(request, path):
    if path.endswith('.pdf'):
        return FileResponse(open(f'{path}', 'rb'), content_type=('application/pdf'))
    else:
        return HttpResponse(open(f'{path}', 'rb'), content_type='text/plain')

def RenderWebExplorerMainPage(request):
    paths = Path.objects.all()

    directoryes = {}

    for path in paths:
        directoryes[path.uri] = f'{path}/'

    data = {'DirictoryName': 'Home', 'lst': directoryes.items()}

    return render(request, 'WebExplorer/DirectoryPage.html', context=data)

def isvideo(path: str):
    if path.endswith(video_extentions):
        return True
    else:
        return False

def isdocument(path: str):
    if path.endswith(text_extentions):
        return True
    else:
        return False

def isfolder(path: str):
    if os.path.isdir(path):
        return True
    else:
        return False

def ReadFolder(path):
    folders = {}
    video_files = {}
    doc_files = {}

    for name in os.listdir(path):
        if isfolder(f'{path}/{name}'):
            folders[name] = f'{name}'
        if isvideo(name):
            video_files[name] = f'{name}'
        if isdocument(name):
            doc_files[name] = f'{name}'

    lst = {}
    lst.update(folders)
    lst.update(video_files)
    lst.update(doc_files)

    print(lst)

    return lst

def RenderWebExplorerPage(request, uri, system_path=''):
    dirictory = Path.objects.filter(uri=uri).first()

    if not dirictory:
        return HttpResponseNotFound('Directory does not exist')

    abs_path = f'{dirictory.system_path}' + ('' if system_path == '' else f'/{system_path}')

    try:
        if isfolder(abs_path):
            data = {'DirictoryName': uri, 'lst': ReadFolder(abs_path).items()}
            return render(request, 'WebExplorer/DirectoryPage.html', context=data)
        elif isvideo(abs_path):
            print(123)
            return stream_video(request, abs_path)
        elif isdocument(abs_path):
            return renderdock(request, abs_path)
    except PermissionError:
        return HttpResponse('does not have permission')

    return HttpResponse('<h1>404. Page not found</h1>')

class RangeFileWrapper(object):
    def __init__(self, filelike, blksize=8192, offset=0, length=None):
        self.filelike = filelike
        self.filelike.seek(offset, os.SEEK_SET)
        self.remaining = length
        self.blksize = blksize

    def close(self):
        if hasattr(self.filelike, 'close'):
            self.filelike.close()

    def __iter__(self):
        return self

    def __next__(self):
        if self.remaining is None:
            # If remaining is None, we're reading the entire file.
            data = self.filelike.read(self.blksize)
            if data:
                return data
            raise StopIteration()
        else:
            if self.remaining <= 0:
                raise StopIteration()
            data = self.filelike.read(min(self.remaining, self.blksize))
            if not data:
                raise StopIteration()
            self.remaining -= len(data)
            return data

range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)

def stream_video(request, path):
    range_header = request.META.get('HTTP_RANGE', '').strip()
    print(range_header)
    range_match = range_re.match(range_header)
    print(range_match)

    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = int(last_byte) if last_byte else size - 1
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(RangeFileWrapper(open(path, 'rb'), offset=first_byte, length=length), status=206,
                                     content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp