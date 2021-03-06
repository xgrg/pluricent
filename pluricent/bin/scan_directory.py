#!/usr/bin/env python
# -*- coding: utf-8 -*-
''' Contains code supposed to parse directories and identify files
that will populate the clean database. Mostly ad-hoc scripts
performing quick and dirty operations

*** scandir_BVdatabase : to run on BVddatabase directories
(make use of pluricent.checkbase)
'''

def size_to_human(full_size):
  size = full_size
  if size >= 1024:
    unit = 'KiB'
    size /= 1024.0
    if size >= 1024:
      unit = 'MiB'
      size /= 1024.0
      if size >= 1024:
        unit = 'GiB'
        size /= 1024.0
        if size >= 1024:
          unit = 'TiB'
          size /= 1024.0
    s = '%.2f' % (size,)
    if s.endswith( '.00' ): s = s[:-3]
    elif s[-1] == '0': s = s[:-1]
    return s + ' ' + unit + ' (' + str(full_size) + ')'
  else:
    return str(size)

stat_attributes = ('st_atime', 'st_ctime', 'st_gid', 'st_mode', 'st_mtime',
               'st_nlink', 'st_size', 'st_uid', 'st_blksize', 'st_blocks',
               'st_dev','st_rdev', 'st_ino')


def scandir_BVdatabase(studydir):
    '''Objectif: trouver sujets, centres et images T1 nifti'''
    ''' Strategie : BVdatabase '''
    import os.path as osp
    import os

    actions = []
    studydir = osp.abspath(studydir)
    assert(osp.isdir(studydir))
    studydir = studydir.rstrip('/')
    assert(osp.split(studydir)[-1] == 'BVdatabase')

    from pluricent import checkbase as cb
    m = cb.MorphologistCheckbase(studydir)

    subjects = m.get_flat_subjects()

    for subject in subjects:
      files = m.get_subject_hierarchy_files(subject)

      for k,v in files.items():
        for each in v:
           fp = cb.getfilepath(k, each)
           if osp.isfile(fp):
              if k not in ['acpc', 'spm_tiv_logfile'] :
                 if k == 'nobias' and each['analysis'] == 'spm8_new_segment':
                    k = 'spm_nobias'
                 print fp, 'identified as', k

                 actions.append(('add_image', subject, k, fp, each))

    return actions

def identification_ratio(a, studydir):
    import os.path as osp
    import os
    allfiles = []
    actions_files = [e[3] for e in a]

    for root, dirs, files in os.walk(studydir):
        allfiles.extend([osp.join(studydir,root, e) for e in files])

    leftfiles = list(set(allfiles).difference(set(actions_files)))
    left = {}
    left['minf'] = [e for e in leftfiles if e.endswith('.minf')]
    leftfiles = list(set(leftfiles).difference(set(left['minf'])))
    left['snapshots'] = [e for e in leftfiles if 'snapshots' in e]
    leftfiles = list(set(leftfiles).difference(set(left['snapshots'])))
    left['folds'] = [e for e in leftfiles if 'folds' in e]
    leftfiles = list(set(leftfiles).difference(set(left['folds'])))
    left['trm'] = [e for e in leftfiles if 'trm' in e]
    leftfiles = list(set(leftfiles).difference(set(left['trm'])))
    left['mat'] = [e for e in leftfiles if 'mat' in e]
    leftfiles = list(set(leftfiles).difference(set(left['mat'])))
    left['Lgw'] = [e for e in leftfiles if 'Lgw' in e or 'Rgw' in e]
    leftfiles = list(set(leftfiles).difference(set(left['Lgw'])))
    left['history'] = [e for e in leftfiles if 'history' in e]
    leftfiles = list(set(leftfiles).difference(set(left['history'])))
    left['skullscalp'] = [e for e in leftfiles if 'skull' in e or 'scalp' in e]
    leftfiles = list(set(leftfiles).difference(set(left['skullscalp'])))
    left['scalp'] = [e for e in leftfiles if 'scalp' in e]
    leftfiles = list(set(leftfiles).difference(set(left['scalp'])))
    left['mni'] = [e for e in leftfiles if 'Mni' in e]
    leftfiles = list(set(leftfiles).difference(set(left['mni'])))
    left['hfiltered']= [e for e in leftfiles if 'hfiltered' in e]
    leftfiles = list(set(leftfiles).difference(set(left['hfiltered'])))
    left['normalized'] = [e for e in leftfiles if 'normalized' in e]
    leftfiles = list(set(leftfiles).difference(set(left['normalized'])))
    left['histogram'] = [e for e in leftfiles if '.his' in e or '.han' in e]
    leftfiles = list(set(leftfiles).difference(set(left['histogram'])))
    left['edges'] = [e for e in leftfiles if 'edges' in e or 'variance' in e or 'roots' in e or 'skeleton' in e or 'head' in e or 'whiteridge' in e or 'Lcortex' in e or 'Rcortex' in e]
    leftfiles = list(set(leftfiles).difference(set(left['edges'])))
    left['referential'] = [e for e in leftfiles if '.referential' in e]
    leftfiles = list(set(leftfiles).difference(set(left['referential'])))
    left['apc'] = [e for e in leftfiles if '.APC' in e]
    leftfiles = list(set(leftfiles).difference(set(left['apc'])))
    left['matlab'] = [e for e in leftfiles if e.endswith('.m')]
    leftfiles = list(set(leftfiles).difference(set(left['matlab'])))
    left['sanlm'] = [e for e in leftfiles if 'sanlm' in e]
    leftfiles = list(set(leftfiles).difference(set(left['sanlm'])))
    return actions_files, allfiles, left, leftfiles


    # estimating directory size
    cumulative_size = 0
    for root, dirs, files in os.walk(studydir):
        for f in files:
            cumulative_size += os.stat(osp.join(root,f)).st_size

    print size_to_human(cumulative_size)


def move_mapt_to_cloud_hierarchy(actions, destdir):
    import os.path as osp
    import os, shutil
    from pluricent import checkbase as cb
    csv = ['']
    cl = cb.CloudyCheckbase(destdir)
    destdir = osp.abspath(destdir)

    for a in actions:
        k, v = a[0], a[1:]
        if k=='add_image' and v[1] == 'raw':
            print v
            subject, datatype, fp, att = v
            #d = osp.join(destdir, subject, 'anatomy')
            att.update({'database': destdir, 'session': '*'})
            #fp_joker = cb.getfilepath(datatype, att, patterns=cl.patterns)
            #from glob import glob
            number = 1 #len(glob(fp_joker)) + 1
            att.update({'database': destdir, 'session': '%03d'%number})
            d2 = cb.getfilepath(datatype, att, patterns=cl.patterns)

        elif k=='add_image' and v[1] != 'raw':
            print v
            subject, datatype, fp, att = v
            if datatype == 'nobias' and att['analysis'] == 'spm8_new_segment':
               datatype = 'spm_nobias'
            #d = osp.join(destdir, subject, 'analysis')
            att.update({'database': destdir, 'session': '*'})
            #fp_joker = cb.getfilepath(datatype, att, patterns=cl.patterns)
            #from glob import glob
            number = 1 #len(glob(fp_joker)) + 1
            att.update({'database': destdir, 'session': '%03d'%number})
            d2 = cb.getfilepath(datatype, att, patterns=cl.patterns)

        if not osp.exists(osp.dirname(d2)): os.makedirs(osp.dirname(d2))
        print 'cp %s %s'%(fp, d2)
        assert(not osp.isfile(d2))
        os.system('cp %s %s'%(fp, d2))



def check_pushzone(pzdir, destdir):
    ''' Checks that every file/folder in pzdir is identified by the hierarchy
    and that they are not already existing in destdir.
    No control on the database entries in this function.
    Returns two lists of items marked as unknown and already existing'''

    from pluricent import checkbase as cb
    cl = cb.CloudyCheckbase(pzdir)
    import os
    import os.path as osp
    unknown = []
    already_existing = []

    for root, dirs, files in os.walk(pzdir):
        for f in files:
            fp = osp.join(root, f)
            print fp
            res = cb.parsefilepath(fp, cl.patterns)
            if res is None:
               unknown.append(fp)
            else:
               datatype, att = res
               att['database'] = destdir
               fp = cb.getfilepath(datatype, att, cl.patterns)
               if osp.exists(fp):
                  already_existing.append(fp)

    return unknown, already_existing


def push_to_repo(pzdir, destdir):
    ''' This functions is only to push images (provided studies and subjects
    have been already previously created'''
    unknown, already_existing = check_pushzone(pzdir, destdir)
    from pluricent import checkbase as cb
    import os
    import os.path as osp
    import pluricent as pl
    from pluricent.web import settings

    cl = cb.CloudyCheckbase(pzdir)
    if len(unknown) == 0 and len(already_existing) == 0:
       print 'pushzone ok'
       for root, dirs, files in os.walk(pzdir):
          for f in files:
             fp = osp.join(root, f)
             res = cb.parsefilepath(fp, cl.patterns)
             datatype, att = res
             study_dir = osp.split(att['database'])[-1]
             att['database'] = osp.join(destdir, study_dir)
             fp2 = cb.getfilepath(datatype, att, cl.patterns)
             print 'cp %s %s'%(fp, fp2)
             s = pl.create_session(settings.DATABASE)
             print '...checking directory %s already referring to a study'%study_dir
             study = [e for e in pl.studies(s) if study_dir == pl.study_dir(s, e)][0]
             studies_dir = [pl.study_dir(s, e) for e in pl.studies(s)]
             assert(study_dir in studies_dir)
             print '=> yes (%s)'%study

             print '...checking %s already exists in %s'%(att['subject'], study)
             subjects = pl.subjects(s, study)
             assert(att['subject'] in subjects)
             print '=> yes'

             print '...checking that the image %s is not already existing'%fp[len(pzdir)+1:]
             t1images = pl.t1images(s, study)

             print '...creating action'
             #pl.add_action(

             print '...copying file'
             print '...adding entry in database'

    else:
       print 'pushzone errors'
       print 'unknown', unknown
       print 'already_existing', already_existing

def collect_dwi():
    dd = '/neurospin/cati/MEMENTO/DiffusionMRI/'
    from glob import glob
    import os.path as osp
    import os
    header = ['subject','side','value','maximum', 'minimum', 'mean', 'standard_deviation','filepath']

    files = []
    res = [header]

    files.extend(glob(osp.join(dd, '*', '7_stats', '*', 'Fornix_*')))
    #files.extend(glob(osp.join(dd, '*', '7_stats', '*', 'Fornix_*', 'fa.csv')))

    import json
    json.dump(files, open('/tmp/files.json','w'))
    #files = json.load(open('/tmp/files.json'))

    for f in files[:]:
        if not osp.isdir(f):
            print f, 'skipped'
            continue
        s = f.split('/')
        center = s[-4]
        subject = '%s%s'%(center,s[-2].split('_')[-1])
        side = s[-1].split('_')[-1].lower()
        print f
        for i in ['adc', 'fa']:
            res.append([subject, side, i])
            stats = {}
            fp = osp.join(f, '%s.csv'%i)
            execfile(fp, stats)
            for each in ['maximum', 'minimum', 'mean', 'standard-deviation']:
                if len(stats['statistics']) > 0:
                    res[-1].append(stats['statistics'][stats['statistics'].keys()[0]][each])
                else:
                    res[-1].append('')
            res[-1].append(fp)


    #save csv
    import csv
    with open('fornix.csv', 'wb') as testfile:
        csv_writer = csv.writer(testfile)
        for each in res:
            csv_writer.writerow(each)
    return res
