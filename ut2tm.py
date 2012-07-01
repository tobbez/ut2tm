#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright (c) 2012, Torbjörn Lönnemark <tobbez@ryara.net>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
#

from __future__ import print_function, division
import os
import struct
import ntpath
from pyrobase.bencode import bencode, bdecode
from shutil import copy2

def migrate_to_transmission(srcdir, dstdir, name, utresume):
    dl_name = ntpath.basename(utresume['path'])
    paused = 0
    if dl_name != name[:-8]:
        print('Warning: Transmission does not support changing target name, pausing {}'.format(name))
        paused = 1
    tmresume = {
            'activity-date': utresume['last_active'],
            'added-date': utresume['added_on'],
            'bandwidth-priority': 0,
            'corrupt': utresume['waste'],
            'destination': ntpath.dirname(utresume['path']),
            'dnd': len(utresume['prio']) * [0], # TODO: figure out what the values in the prio string means
            'done-date': utresume['completed_on'],
            'downloaded': utresume['downloaded'],
            'downloading-time-seconds': 0,
            'idle-limit': {'idle-limit': 30, 'idle-mode': 0},
            'max-peers': 75,
            'paused': paused or not utresume['started'],
            'peers2': 0,
            'peers2-6': 0,
            'priority': len(utresume['prio']) * [0], # see notes for the dnd key
            'progress': {'blocks': 'all', 'have': 'all', 'time-checked': len(utresume['prio']) * [0]},
            'ratio-limit': {'ratio-limit': utresume['wanted_ratio']//10, 'ratio-mode': 0},
            'seeding-time-seconds': utresume['seedtime'],
            'speed-limit-down': {'speed-Bps': 0, 'use-global-speed-limit': 1, 'use-speed-limit': 0},
            'speed-limit-up': {'speed-Bps': 0, 'use-global-speed-limit': 1, 'use-speed-limit': 0},
            'uploaded': utresume['uploaded']
            }
    info_hash_str = ''.join(map(lambda x: hex(x)[2:], struct.unpack('BBBBBBBBBBBBBBBBBBBB', utresume['info'])))

    output_base = '{}.{}'.format(name.replace('/', '_')[:-8], info_hash_str[:16])

    with open(os.path.join(dstdir, 'resume', '{}.resume'.format(output_base)), 'w') as resume:
        resume.write(bencode(tmresume))

    copy2(os.path.join(srcdir, name), os.path.join(dstdir, 'torrents', '{}.torrent'.format(output_base)))

def main(args):
    if len(args) != 3 or '-h' in args or '--help' in args:
        print('Usage: {} <uTorrent-directory> <transmission-directory>'.format(args[0]))
        return

    input_dir = args[1]
    input_file_name = os.path.join(input_dir, 'resume.dat')
    output_dir = args[2]

    dec = None

    try:
        with open(input_file_name) as ut:
            dec = bdecode(ut.read())
    except Exception, e:
        print('Error: {}'.format(e))
        return

    try:
        os.makedirs(os.path.join(output_dir, 'resume'))
    except:
        pass

    try:
        os.makedirs(os.path.join(output_dir, 'torrents'))
    except:
        pass

    for tk, tv in dec.iteritems():
        if tk == '.fileguard' or tk == 'rec':
            continue
        migrate_to_transmission(input_dir, output_dir, tk, tv)
        #print('Migrated {}'.format(tk))

if __name__ == '__main__':
    from sys import argv
    main(argv)
