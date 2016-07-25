# -*- coding: utf-8 -*-
import subprocess
import os
from multiprocessing import Pool
import time
import multiprocessing
import argparse
from functools import partial


def convert(src, dst, vb="3M", verbose=False):
    # cmd = 'mencoder -o test.avi -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=5000 -oac lavc test.MP4'
    # cmd = "mencoder -o %s -ovc lavc -lavcopts vcodec=mpeg4:vbitrate=5000 -oac lavc %s" % (src,dst)
    # cmd = "ffmpeg -i '%s' -b:v 64k -s 1024x768 -r 50 '%s'" % (src,dst)
    cmd = "ffmpeg -i '{}' -vb {} -r 50 '{}'".format(src, vb, dst)
    x = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = x.communicate()
    if output:
        if verbose: print "success ", output
        return True
    else:
        if verbose: print "error ", err
        return False


def all_files(path='/'):
    for path, _, filenames in os.walk(path):
        for f in filenames:
            yield os.path.join(path, f)



def worker(vb, verbose, del_source, file_path):
    try:
        f = file_path
        print "worker pid {} process : {}".format(os.getpid(), file_path)
        dst = "".join(f.split('.')[0:-1]) + '.avi'
        try:
            os.remove(dst)
        except OSError:
            pass
        convert(f, dst, vb, verbose)
        dst_size = os.path.getsize(dst)
        src_size = os.path.getsize(f)
        if del_source and dst_size > 0: os.remove(f)  # if result done
        return (src_size, dst_size,)
    except OSError, e:
        print 'os error', e
        return (0, 0,)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', help='path to directory with video files')
    parser.add_argument('--vb', help='bitrate default 3M (higher - more quality more disk space)', default="3M")
    parser.add_argument('--verbose', help='show ffmpeg output', default=False)
    parser.add_argument('--del_source', help='delete source files', default=False)
    args = parser.parse_args()

    if not args.path:
        print parser.print_help()
        exit()

    print "processing path {} \nconvert to bitrate {}".format(args.path, args.vb)
    cpus = multiprocessing.cpu_count()
    print "total cpus found: ", cpus
    pool = Pool(cpus)
    print "Process pool created with workers : {}".format(cpus)
    # '/media/se7en/bighdd/NEW-CAM-ARCHIVE2/185YBPHH'
    start_time = time.time()
    files_to_convert = (i for i in all_files(args.path) if i.lower().endswith(('.mp4', '.mov')))
    pworker = partial(worker, args.vb, args.verbose, args.del_source)
    compress_results = (i for i in pool.imap(pworker, files_to_convert))


    def f(r, r1):
        s, d = r
        s1, d1 = r1
        return (s + s1, d + d1,)


    total = reduce(f, compress_results)
    s0 = total[0] / (1024 * 1024)
    s1 = total[1] / (1024 * 1024)
    elapsed_time = time.time() - start_time
    print "videos compressed info: {} mb -> {} mb : saved {} mb ".format(s0, s1, s0 - s1)
    print "time taken: ", elapsed_time

# http://stackoverflow.com/questions/26959283/python-call-ffmpeg-command-line-with-subprocess
# http://stackoverflow.com/questions/6906922/threading-subprocesses-in-python
