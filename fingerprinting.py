# import the necessary packages
import os
import shutil

from PIL import Image
import imagehash
import argparse
import shelve
import glob

# construct the argument parse and parse the arguments

ap = argparse.ArgumentParser()
ap.add_argument("-d", "--dataset", required=True, help="path to input dataset of images")
ap.add_argument("-s", "--shelve", required=True, help="output shelve database")
args = vars(ap.parse_args())


def get_new_name(file_complete_path, counter):
    _base, _name = os.path.split(file_complete_path)
    _file, _ext = _name.split(".")
    _f = _file + "_" + str(counter) + "." + _ext
    return os.path.join(_base, _f)


def move2dest(old, new, copy=True):
    if old == new:
        return new
    try:
        parent = os.path.dirname(new)
        if not os.path.exists(parent):
            os.makedirs(parent)

        if not os.path.isfile(new):
            if copy:
                shutil.copy2(old, new)
            else:
                shutil.move(old, new)
        else:
            print "FILE %s ALREADY EXISTS" % new

    except OSError as ose:
        print ose.filename + " ====> " + ose.strerror

    return new


if __name__ == '__main__':
    # open the shelve database
    db = shelve.open(args["shelve"], writeback=True)

    # loop over the image dataset
    # for imagePath in glob.glob(args["dataset"] + "/*.jpg"):
    for root, dirs, files in os.walk(args["dataset"]):
        if os.path.basename(root).startswith('.'):
            continue
        for f in files:
            # Skip hidden files
            if f.startswith('.'):
                continue
            ext = f.split(".")[-1]
            if str(ext).lower() in ['jpg', 'jpeg', 'gif']:
                imagePath = os.path.join(root, f)

                best_size = 0
                best_file = ""
                statinfo = os.stat(imagePath)
                best_size = statinfo.st_size
                best_file = f

                # load the image and compute the difference hash
                image = Image.open(imagePath)
                base, name = os.path.split(imagePath)
                ext = name.split(".")[-1]
                nameaspath = str(name)[0:len(name)-4]
                try:
                    h = str(imagehash.dhash(image))
                except IOError as ex:
                    print ex.message
                    continue

                # loop over the images
                has_duplicity = False
                try:
                    db_filenames = db[h]

                    # HAY DUPLICADAS
                    has_duplicity = True
                    print "Found %d similar images" % (len(db_filenames))
                    if len(db_filenames) > 0:
                        # copiar el fichero que estamos tratando
                        move2dest(imagePath, "d:/fotos/procesadas/duplicadas/" + str(h) + "/" + f, copy=False)
                        imagePath = "d:/fotos/procesadas/duplicadas/" + str(h) + "/" + f

                    for filename in db_filenames:
                        # image = Image.open(filename)
                        # image.show()
                        the_db_file_best = "d:/fotos/procesadas/" + filename
                        the_db_file_others = "d:/fotos/procesadas/duplicadas/" + str(h) + "/" + filename
                        if os.path.isfile(the_db_file_best):
                            statinfo = os.stat(the_db_file_best)
                            if statinfo.st_size > best_size:
                                imagePath = the_db_file_best
                                best_file = filename
                                best_size = statinfo.st_size
                            move2dest(the_db_file_best, "d:/fotos/procesadas/duplicadas/" + str(h) + "/" + filename, copy=False)

                        elif os.path.isfile(the_db_file_others):
                            statinfo = os.stat(the_db_file_others)
                            if statinfo.st_size > best_size:
                                imagePath = the_db_file_others
                                best_file = filename
                                best_size = statinfo.st_size


                except KeyError as ke:
                    print "Key: %s" % ke.message

                # extract the filename from the path and update the database
                # using the hash as the key and the filename append to the
                # list of values
                # filename = imagePath[imagePath.rfind("/") + 1:]
                db[h] = db.get(h, []) + [f]
                if has_duplicity:
                    move2dest(imagePath, "d:/fotos/procesadas/" + best_file, copy=True)
                else:
                    move2dest(imagePath, "d:/fotos/procesadas/" + best_file, copy=False)
    # close the shelf database
    db.close()
