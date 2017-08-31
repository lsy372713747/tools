# -*- coding: utf-8 -*-
import zipfile
import os

class ZFile(object):
    def __init__(self, filename, mode='r', basedir=''):
        self.filename = filename
        self.mode = mode
        if self.mode in ('w', 'a'):
            # zipfile.ZIP_DEFLATED 压缩 zipfile.ZIP_STORED 打包不压缩
            self.zfile = zipfile.ZipFile(filename, self.mode, compression=zipfile.ZIP_DEFLATED)
        else:
            self.zfile = zipfile.ZipFile(filename, self.mode)
        self.basedir = basedir
        if not self.basedir:
            self.basedir = os.path.dirname(filename)

    def addfile(self, path, arcname=None):
        path = path.replace('//', '/')
        if not arcname:
            if path.startswith(self.basedir):
                arcname = path[len(self.basedir):]
            else:
                arcname = ''
        self.zfile.write(path, arcname)

    def addfiles(self, paths):
        for path in paths:
            if isinstance(path, tuple):
                self.addfile(*path)
            else:
                self.addfile(path)

    def close(self):
        self.zfile.close()

    def extract_to(self, path):
        for p in self.zfile.namelist():
            self.extract(p, path)

    def extract(self, filename, path):
        if not filename.endswith('/'):
            f = os.path.join(path, filename)
            dir = os.path.dirname(f)
            if not os.path.exists(dir):
                os.makedirs(dir)
            file(f, 'wb').write(self.zfile.read(filename))

def create(zfile, files):
    z = ZFile(zfile, 'w')
    z.addfiles(files)
    z.close()

def extract(zfile, path):
    z = ZFile(zfile)
    z.extract_to(path)
    z.close()

import datetime
now = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
z = ZFile("./data/" + now+'.zip', 'w')
z.addfile('./data/crm_sysales_citypost_v_20170831160329.csv')
z.close()

