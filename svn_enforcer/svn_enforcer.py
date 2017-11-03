# This routine is used to create SVN report of different paths in svn.cfg file.
# Author: Rupinder Singh
# Last Reviewed: August 4, 2017

import imp
import os
import time
#IMPORTANT: svn.cfg should be in same path as this script (svn_enforcer.py)
cfg_pth = os.path.dirname(os.path.abspath(__file__)) 
#IMPORTANT: pLib directory should exist in same path as svn_enforcer direcotry 
pth_lib = os.path.dirname(cfg_pth)+'/pLib/' 
rsvn = imp.load_source('rs_svn',pth_lib+'rs_svn.py')
rss = imp.load_source('rs_scraper',pth_lib+'rs_scraper.py')
rsql = imp.load_source('rs_mysql',pth_lib+'rs_mysql.py')

if __name__ == '__main__':

    #Make sure svn.cfg exists (see README for details)
    cfg_fn = "/svn.cfg" 
    cfg = rsql.load_config_file(cfg_pth+cfg_fn)
    pth_key = 'path' #key used in cfg for path
    email_key = 'email' #key use in cfg for emails
    
    #EMAIL Details
    HOSTNAME = rss.get_hostname()
    eFrom = "svn_enforcer@"+HOSTNAME

    try:
        for key in cfg:
            #
            svn_pth = cfg[key][pth_key]
            eTo = cfg[key][email_key]
            
            #CREATE HTML FOR EMAIL:
            eHTML = "<!DOCTYPE html>" 
            eHTML += "<html>"

            eSubject = "SVN ENFORCER: "+key+'@'+HOSTNAME

            eHTML += "<h3> 1) SVN INFO ("+time.strftime("%c")+") </h3>"
            out,err = rsvn.svn_info(svn_pth)
            eHTML += out.replace('\n', '<br />')+'<br />'+err

            eHTML += "<h3> 2) SVN CLEANUP ("+time.strftime("%c")+") </h3>"
            out,err = rsvn.svn_cleanup(svn_pth)
            eHTML += out.replace('\n', '<br />')+'<br />'+err

            eHTML += "<h3> 3) SVN UPDATE ("+time.strftime("%c")+") </h3>"
            out,err = rsvn.svn_update(svn_pth)
            eHTML += out.replace('\n', '<br />')+'<br />'+err

            eHTML += "<h3> 4) SVN RESOLVE ("+time.strftime("%c")+") </h3>"
            out,err = rsvn.svn_resolve(svn_pth) #adding as fail-safe if update doesn't accept conflict via thiers-full option
            eHTML += out.replace('\n', '<br />')+'<br />'+err

            eHTML += "<h3> 5) SVN STATUS ("+time.strftime("%c")+") </h3>"
            out,err = rsvn.svn_status(svn_pth)
            eHTML += out.replace('\n', '<br />')+'<br />'+err

            eHTML += "<h3> 6) SVN DIFF ("+time.strftime("%c")+") </h3>"
            out,err = rsvn.svn_diff(svn_pth)
            eHTML += "Please see attachment (svn_diff.log)"
            eFiles = [svn_pth.replace('\ ',' ').replace(" ","\ ")+'/svn_diff.log']
            with open(eFiles[0], 'wb') as f:
                f.write(out)

            eHTML += "<h3> 7) SVN RECENT COMMIT PER FILE ("+time.strftime("%c")+") </h3>"
            df = rsvn.svn_commit_per_file(svn_pth)
            eHTML += df.to_html(justify='left')

            eHTML += "<h3> 8) SVN LOG STATS ("+time.strftime("%c")+") </h3>"
            df = rsvn.svn_log_stats(svn_pth)
            eHTML += df.to_html(justify='left')

            eHTML += "<h3> Finished! ("+time.strftime("%c")+") </h3>"
            eHTML += "</html>" 
                
            #SEND EMAIL
            rss.send_email(eFrom, eTo, eSubject, eHTML, FILES = eFiles)
    except:
        if 'eHTML' not in locals():
            #CREATE HTML FOR EMAIL:
            eHTML = "<!DOCTYPE html>" 
            eHTML += "<html>"
        eTo = 'rupinder@cozeva.com' #default email for errors
        eSubject = "SVN ENFORCER: "+HOSTNAME+" (FAILED!)"
        eHTML += "<h4> Process Failed! ("+time.strftime("%c")+") </h4>"
        eHTML += "</html>" 
        
        #SEND EMAIL
        rss.send_email(eFrom,eTo,eSubject,eHTML)
