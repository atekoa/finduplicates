# -*- coding: utf-8 -*-
# !/usr/bin/python
"""
MIGUEL LINARES DE LA PUERTA
"""
import matplotlib as mpl
from joblib import Parallel, delayed

mpl.use('Agg')
import os
import glob
import json
import numpy as np
import shutil


def _process_single_image_thread(args):
    _base = args[0]
    _image = args[1]
    _inpath = args[2]
    _outpath = args[3]

    try:
        if (".gif" in str(_image).lower() or ".jpg" in str(_image).lower() or ".jpeg" in str(_image).lower()) and "exported" not in str(_base).lower():
            newpath = _base.replace(_inpath, _outpath)
            if not os.path.exists(newpath):
                os.makedirs(newpath)
            if not os.path.exists(newpath + "/" + _image):
                shutil.copy(_base + "/" + _image, newpath)
                return newpath + "/" + _image
            else:
                return "ya existia: " + _image
        else:
            return "no imagen: " + _image
    except Exception as ex:
        # print ex.message
        return str(ex.message)


def copy_images(input_path, output_path):
    num_jobs = -1

    if not os.path.exists(output_path):
        os.makedirs(output_path)
    for base, dirs, files in os.walk(input_path):
        for f in files:
            '''
            try:
                if ".jpg" in str(f).lower() and "exported" not in str(base).lower():
                    print "base:" + base + " file:" + f
                    newpath = base.replace(input_path, output_path)
                    if not os.path.exists(newpath):
                        os.makedirs(newpath)
                    shutil.copy(base + "/" + f, newpath)
            except Exception as ex:
                print ex.message
                continue
            '''
            arg_list = []
            arg_list.append([base, f, input_path, output_path])
            results = Parallel(n_jobs=num_jobs, backend="threading")(
                map(delayed(_process_single_image_thread), arg_list))
            print results


if __name__ == "__main__":
    num_jobs = -1

    copy_images("Z:/2018/", "d:/fotos/backup/2018/")
    copy_images("Z:/2017/", "d:/fotos/backup/2017/")
    copy_images("Z:/2016/", "d:/fotos/backup/2016/")
    copy_images("Z:/Movil/", "d:/fotos/backup/Movil/")

    print "Done!"
