# Custom module with svn related functionalities
# Author: Rupinder Singh (Aug. 3, 2017)

import subprocess as sp
import pandas as pd
import sys
import os
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO

def svn_info(svn_pth): 
    """ Runs SVN INFO
    """
    cmd = "svn info "+svn_pth.replace('\ ',' ').replace(" ","\ ")+';'
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr= sp.PIPE, shell=True)
    stdout,stderr = p.communicate()
    return stdout.decode('utf8'), stderr.decode('utf8')

def svn_cleanup(svn_pth):
    """ Runs SVN CLEANUP
    """
    cmd = "svn cleanup "+svn_pth.replace('\ ',' ').replace(" ","\ ")+';' 
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr= sp.PIPE, shell=True)
    stdout,stderr = p.communicate()
    return stdout.decode('utf8'), stderr.decode('utf8')

def svn_update(svn_pth):
    """ Runs SVN UPDATE
    """
    cmd = "svn up --accept tf "+svn_pth.replace('\ ',' ').replace(" ","\ ")+';' #if there is a conflict, use verion in svn
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr= sp.PIPE, shell=True)
    stdout,stderr = p.communicate()
    return stdout.decode('utf8'), stderr.decode('utf8')

def svn_resolve(svn_pth):
    """ Runs SVN RESOLVE
    """
    cmd = "svn resolve -R --accept tf "+svn_pth.replace('\ ',' ').replace(" ","\ ")+';' #if there is a conflict, use verion of file in svn
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr= sp.PIPE, shell=True)
    stdout,stderr = p.communicate()
    return stdout.decode('utf8'), stderr.decode('utf8')

def svn_status(svn_pth):
    """ Runs SVN STATUS
    """
    cmd = "svn st "+svn_pth.replace('\ ',' ').replace(" ","\ ")+';' 
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr= sp.PIPE, shell=True)
    stdout,stderr = p.communicate()
    return stdout.decode('utf8'), stderr.decode('utf8')

def svn_diff(svn_pth):
    """ Runs SVN DIFF
    """
    cmd = "svn diff "+svn_pth.replace('\ ',' ').replace(" ","\ ")+';'
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr= sp.PIPE, shell=True)
    stdout,stderr = p.communicate()
    return stdout.decode('utf8'), stderr.decode('utf8')

def svn_recent_log(svn_fn):
    """Returns most recent log for file
    """
    cmd = "svn log -l 1 "+svn_fn.replace('\ ',' ').replace(" ","\ ")+' | '
    cmd += "grep -A1 -e'^[-].*$' | grep -e'[^-]'| cut -d'|' -f1,2,3" #next line after patern that begins with --- and ends with ---
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr= sp.PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout.decode('utf8'), stderr.decode('utf8')

def svn_commit_per_file(svn_pth):
    out = ''
    for path, subdirs, files in os.walk(svn_pth):
        for name in files:
            if '.svn' not in path:
                stdout, stderr = svn_recent_log(os.path.join(path, name))
                if stdout !='':
                    pth = os.path.join(os.path.basename(path), name)
                    out += pth + '|' + stdout
                
    df = pd.read_csv(StringIO(out),sep='|', 
        names = ['file','revision','user','timestamp'], 
        converters = {'revision':strip,'user':strip,'timestamp':strip})      
    df = df.sort_values(['revision'], ascending =[0]).reset_index()
    return df[['file','user','revision','timestamp']]

def svn_log(svn_pth):
    """ Runs SVN LOG
        svn log usually prints something like:
        >------------------------------------------------------------------------
        >r42841 | rsingh | 2017-04-15 15:55:03 -0700 (Sat, 15 Apr 2017) | 1 line
        >
        >comment

        This routine returns line after "---" pattern 
    """
    cmd = "svn log "+svn_pth.replace('\ ',' ').replace(" ","\ ")+' | ' 
    cmd += "grep -A1 -e'^[-].*$' | grep -e'[^-]'| cut -d'|' -f1,2,3" #next line after patern that begins with --- and ends with ---
    p = sp.Popen(cmd, stdout = sp.PIPE, stderr= sp.PIPE, shell=True)
    stdout, stderr = p.communicate()
    return stdout.decode('utf8'), stderr.decode('utf8')

def svn_log_stats(svn_pth):
    """ Returns dataframe of unique users with their commit count and most recent commit timestamp
    """
    stdout,stderr = svn_log(svn_pth)
    df = pd.read_csv(StringIO(stdout),sep='|', 
        names = ['revision','user','timestamp'], 
        converters = {'revision':strip,'user':strip,'timestamp':strip})

    f = {'revision':'count','timestamp':'first'}
    df = df[['user','revision','timestamp']].groupby(by='user').agg(f).sort_values(['revision'], ascending =[0]).reset_index()
    df = df.loc[df['user']!='']
    df.rename(columns={"revision": "# of revisions", "timestamp": "most recent commit"},inplace=True)

    return df[['user','# of revisions','most recent commit']]

def strip(text):
    try:
        return text.strip()
    except AttributeError:
        return text
