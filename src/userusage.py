#!/usr/bin/env python

##############################################################
#     _     __   ____  ___   _     __    __    __    ____    # 
#    | | | ( (` | |_  | |_) | | | ( (`  / /\  / /`_ | |_     # 
#    \_\_/ _)_) |_|__ |_| \ \_\_/ _)_) /_/--\ \_\_/ |_|__    #
#               Userusage Python by Will Drach               #
##############################################################
# Userusage comes with no guarantee, warranty, or suggestion #
# that it even remotely does what it's supposed to.          #
##############################################################

VERSION = "1.19.04"

##############################################################################
# run version check                                                          #
##############################################################################

def check_version(greater_than = 2, greater_sub = 6,
                  less_than = 3, less_sub = 0):
    '''Checks the python version to make sure
       it is correct
    '''

    try:
        import sys
        from sys import stderr
    except:
        print('ERROR: sys library not imported.')
        exit(1)
    try:
        ver = sys.version_info
    except:
        stderr.write('ERROR: Error getting version.')
        exit(1)
    if ver >= (less_than, less_sub) or ver < (greater_than, greater_sub):
        stderr.write("""
ERROR: userusage is built for Python 2.6+
Your version is %d.%d.
""" %(ver[0],ver[1]))
        exit(1)

check_version()

##############################################################################
# import our libraries and throw an error if something goes wrong            #
##############################################################################

try:
    from sys import stderr
    import os
    import argparse
    import psutil
    import socket
    import pwd
    import string
    import subprocess
    import email
    import smtplib
    import ConfigParser
    from ConfigParser import SafeConfigParser
    from subprocess import call, Popen, PIPE
    from psutil import disk_usage, disk_partitions
    from os import stat, listdir
    from os.path import isfile, join, ismount, getsize, isdir
    from pwd import getpwuid
    from sys import stderr
except ImportError as import_error:
    stderr.write('ERROR: Import Error, ' + str(import_error) + '\n')
    exit(1)

#############################################################################
# helper functions                                                          #
#############################################################################

def remove_duplicates(original_list):
    '''remove duplicates from a list'''

    new_list = []
    for x in original_list:
        if x not in new_list:
            new_list.append(x)
    return new_list

def threshold_check(config):
    '''check if used space is greater than threshold'''

    part = config.partition
    try:
        #turn threshold into a percent
        thresh = float(config.space_threshold)
        partd = disk_usage(part)
        #check disk usage
        if partd.percent < thresh:
            #if its lower than the threshold
            #return false
            return False
        else:
            #else return true
            return True
    except Exception as err:
        stderr.write(config.disk_error)
        exit(1)

def sort(intuple, mode):
    '''sort a list/tuple
       mode = 1:
         sort by intuple[0]
       mode = 2:
         sort by intuple[1]
         reverse it
    '''

    if mode == 1:
        out = sorted(intuple, key = lambda intu: intu[0])
    else: 
        out = sorted(intuple, key = lambda intu: intu[1], reverse=True)
    return out

##############################################################################
# formatting functions                                                       #
##############################################################################

def space_format(in_string, x):
    '''expand a string to x length by adding spaces
       to the end
    '''
    in_string = in_string + ' '*(x - len(in_string))
    return in_string

def space_format_front(in_string, x):
    '''expand a string to x length by adding spaces
       to the beginning
    '''

    in_string = ' '*(x - len(in_string)) + in_string
    return in_string

def unformat(in_string, unform_error):
    '''Function for turning formatted numbers
       a la '8M' into kilobytes, supports
       b (bytes), K (Kilobytes), M (Megabytes),
       G (Gigabytes), T (Terabytes)
    '''

    try:
        #this should be fairly self explanitory
        #get a string with some sort of units
        #put out just that flat value in an int

        in_string = str(in_string)
        ends = in_string.endswith
        rep = in_string.replace
        if ends('b'):
            in_string = float(rep('b',''))
            out = in_string/1024
        elif ends('K'):
            out = float(rep('K',''))
        elif ends('M'):
            in_string = float(rep('M',''))
            out = in_string * 1024
        elif ends('G'):
            in_string = float(rep('G',''))
            out = 1024 * 1024 * in_string
        elif ends('T'):
            in_string = float(rep('T',''))
            out = 1024 * 1024 * 1024 * in_string
        else:
            out = float(in_string)
    except:
        parser.print_usage()
        stderr.write(unform_error)
        exit(1)

    return int(out)

def reformat(in_string):
    '''Format KB into human readable numbers'''
    try:
        in_string = int(in_string)
        if in_string >= 1073741824:
            in_string = float(in_string)/1073741824
            in_string = "%.2f" % round(in_string,2)
            out = str(in_string) + 'T'
        elif in_string >= 1048576:
            in_string = float(in_string)/1048576
            in_string = "%.2f" % round(in_string,2)
            out = str(in_string) + 'G'
        elif in_string >= 1024:
            in_string = float(in_string)/1024
            in_string = "%.2f" % round(in_string,2)
            out = str(in_string) + 'M'    
        else:
            out = str(in_string) + 'K'    
        return out
    except:
        stderr.write('\nERROR: Error with reformat')
        return out

##############################################################################
# Start general use functions                                                #
##############################################################################

def is_home(config):
    '''check if the current directory home or on its way to home
       return 0 if we're not in home/there is no home
       return 1 if we're in the full home directory
       return 2 if we're almost in the home directory

       the --home-dir option should be used instead more often than not
    '''

    if config.loud_noises:
        print('\nChecking if %s is home dir'%(config.dir))
    try:
        pwlist = pwd.getpwall()
        home_list = []
        user_list = []
        for item in pwlist:
            if item.pw_uid > 1000 and item.pw_name not in config.no_users:
                pwdir = item.pw_dir
                rdir = pwdir.rfind('/')
                home_list.append(pwdir[:rdir])
                user_list.append(item.pw_name)
        #go through passwd and find everyone's home
        #then make a list with all of the home prefixes
        #i.e. /home/pitserver, /home/client, etc.

        hlen = len(home_list)
        if not hlen:
        #if hlen is 0 (no user home dirs) return 0
            return 0, 0, user_list

        home_list = remove_duplicates(home_list)
        hlen = len(home_list)
        hm = home_list[0]
        hr = hm.rfind('/')
        bhm = hm[:hr]

        if config.dir == hm and hlen == 1:
        #if there's only 1 base home dir
        #and this is it, return 1
            return 1, home_list, user_list
        elif config.dir == bhm:
            a = 1
            for r in home_list:
                rr = r.rfind('/')
                br = r[:rr]
                if not br == config.dir:
                    a = a * 0
            if a == 1:
                return 2, home_list, user_list
            else:
                return 0, 0, user_list
            #if the len is > 1 we want to return 3
            #but have to double check that all of 
            #the home directories start with 
            #config.dir.
        else:
            return 0, 0, user_list
            #we're not in home
    except:
        stderr.write(config.disk_error)
        exit(1)

def directory_size(directory_location, config):
    '''find the size of a directory with du'''

    try:
        if config.loud_noises == 2:
            print('\nFinding size of %s'%(directory_location))
        cmd = 'du -sx ' + directory_location
        process = Popen(cmd.split(' '),stdout=PIPE)
        output = process.communicate()
        exit_code = process.wait()
        if exit_code != 0 and config.loud_noises == 2:
            print('\nWARNING: du command exited with exit code %d'%(exit_code))

        output = output[0].split('\t')
        output = output[0]
        if config.loud_noises == 2:
            print('Done')

        return output
    except:
        stderr.write('\nERROR, issue finding the size of %s'%(directory_location))
        exit(1)

##############################################################################
# Mail functions                                                             #
##############################################################################

def mail_user(user, usage, percent_usage, total_space, hostname, config):
    '''mail a user with a generic message'''
    if config.loud_noises:
        print('Mailing: %s, Usage: %s'%(user,usage))
        if usage == '0K':
            print('\nWARNING: You are mailing a user who is using no space!')

    #we want the email to be informative, so we get some data for it
    user = user.title()
    sender = config.sender
    email = user + config.extension

    #the main message
    message = """Subject: Disk usage on %s


Hello %s,

%s is currently at %d percent capacity. 
You are using %s out of the %s of disk space. 
Please consider removing unnecessary files.

Thank you.
    """%(hostname, user, hostname, percent_usage, usage, total_space)
    server = smtplib.SMTP('localhost')
    server.sendmail(sender, email, message)    
    server.quit()
    if config.loud_noises:
        print('Done')
    return

def mail_root(intuple, user_list, config):
    '''mails the root of the server with a full
       list of users and usages
    '''

    if config.loud_noises:
        print('\nMailing Root')
    user_high = len(max(user_list, key=len))
    hostname = socket.gethostname()
    message = """Subject: Userusage on %s

This is the Userusage list for %s directory %s

    """%(hostname,hostname,config.dir)
    user_formatted = []
    for item in intuple:
        user_formatted.append(space_format(item[0], user_high))

    n = 0
    while n < len(intuple):
        sortedi = intuple[n]
        if int(sortedi[1]) != 0:
            usage_formatted = space_format_front(reformat(sortedi[1]),7)
            message = message + '\nUser: %s Usage: %s'%(user_formatted[n],usage_formatted)
        n += 1
    sender = config.sender
    email = config.root_mail

    server = smtplib.SMTP('localhost')
    server.sendmail(sender, email, message)    
    server.quit()

    if config.loud_noises:
        print('Done')

##############################################################################
# Usage check functions                                                      #
##############################################################################

def normal_usage_check(user_list, usage, prefix, config):
    '''check for disk usage without recursing and
       return the list of users and the list of used storage
    '''

    try:
        paths = listdir(prefix)
        for path in paths:
            npath = prefix + '/' + path
            owner = getpwuid(stat(npath).st_uid).pw_name
            if owner not in config.no_users:
                user_list.append(owner)
                if isdir(npath):
                    spaceusage = directory_size(npath, config)
                else:
                    spaceusage = getsize(path)
                usage.append(spaceusage)

    except:
        stderr.write('\nERROR: Something went wrong with the usage check.')
        stderr.write('check your syntax and try again.')
        exit(2)
    return user_list, usage

def recursive_usage_check(user_list, config):
    '''check for disk usage and recurse
    '''

    #fix this as it can cause problems with find
    if not config.dir.endswith('/'):
        dir_loc = config.dir + '/'

    if config.loud_noises:
        print('\nStating files in %s'%(config.dir))

    #find the dir and return the stat username and size from it
    cmd = ['find',dir_loc,'-type','f','-exec','stat','-c','%U %s','{}','+']
    process = Popen(cmd,stdout=PIPE)
    find_out = process.communicate()
    exit_code = process.wait()    

    #split each line up
    find_out = find_out[0].split('\n')

    out_tuple = []
    #split each line into user and size
    for item in find_out:
        out_tuple.append(item.split(' ',1))

    #this next part just zips up a dict type
    #which makes calculating size easier 
    #(and is fast as hell)
    n = 0
    nout_tuple = []
    for item in out_tuple:
        if not len(item) < 2:
            nout_tuple.append(item)
    usage = []

    out_dict = {}
    for key, val in nout_tuple:
        out_dict.setdefault(key, []).append(val)

    if config.loud_noises:
        print('Done')

    for usr in user_list:
        usage.append(0)
        #if the user has no sizes/files make their dir
        #blank so the for doesn't throw an error
        out_dict.setdefault(usr, [])

    #add up our sizes for each user
    for usr in user_list:
        if config.loud_noises == 2:
            print('\nFinding %s\'s usage in %s'%(usr,config.dir))
        user_sizes = out_dict[usr]
        size = 0
        for usize in user_sizes:
            size = size + int(usize)/1024


            
        userindex = user_list.index(usr)
        usage[userindex] = size
        if config.loud_noises == 2:
            print('Done')

    return user_list, usage

##############################################################################
# userusage function                                                         #
##############################################################################

def userusage(config):
    '''This is the main function that runs the usage check'''

    #see if we are looking at a home dir
    userhome, home_list, userlist = is_home(config)
    if config.loud_noises:

        print('Done')
    #run either recursive or non recursive mode
    if config.recursive:
        if userhome != 0 and config.loud_noises:
            print('\nWARNING: The path given is a home directory.')
            print('Running non-recursive will be much faster and')
            print('will likely return the same results.')
        user_list, spclt = recursive_usage_check(userlist, config)
    else:
        if userhome == 1:
            user_list, spclt = normal_usage_check([],[],config.dir,config)
        elif userhome == 2:
            user_list, spclt = [],[]
            for i in home_list:
                user_list, spclt = normal_usage_check(user_list,spclt,i,config)
        else:
            if config.loud_noises:
                print('\nWARNING: The path given is not a home directory. \n We suggest running recursive mode for non-home directories')

            user_list, spclt = normal_usage_check([],[],config.dir,config)

    if config.loud_noises:

        print('\nSorting lists')
    try:
        #zip up our values into one tuple for sorting
        spclt = [ int(x) for x in spclt ]
        big_daddy = zip(user_list,spclt)
        sortedlist = sort(big_daddy, config.sort_list)
        #sort by size by default and alphabetically if specified
        if config.sort_list == 0:
            sortedmail = sortedlist
        else:
            sortedmail = sort(big_daddy, 0)
    except:
        #this shouldn't happen, but we have that safety net if 
        #it does
        stderr.write('\nERROR: Unexpected error in sorting.')
        exit(2)
    if config.loud_noises:

        print('Done\n')

    #this is where we list our users, by the specifications
    #given by command line arguments.
    if config.list_top:
        user_high = len(max([c[0] for c in sortedlist], key=len))
        user_formatted = []

        for item in sortedlist:
            user_item = item[0]
            user_formatted.append(space_format(user_item, user_high))

        if config.list_top != 0:
            n = 0
            nlist_top = config.list_top
            if config.list_top == -1:
                nlist_top = len(user_list)

            while n < nlist_top:
                sortedi = sortedlist[n]
                usage_formatted = space_format_front(reformat(sortedi[1]),7)
                print('User: %s Usage: %s'%(user_formatted[n],usage_formatted))
                n += 1
        else:
            for i in sortedlist:
                if i[1] > config.list_threshold:
                    usage_formatted = space_format_front(reformat(i[1]),7)
                    print('User: %s Usage: %s'%(user_formatted[n],
                        usage_formatted))

    #this is where we mail our users depending on the specification. 
    #if verbose is on we'll tell you which users we mailed
    if config.mail_top:
        #some stuff to include in the email
        psutil_usage = disk_usage(config.partition)
        percent_usage = psutil_usage.percent
        total_space = reformat(psutil_usage.total/1024)
        hostname = socket.gethostname()

        if config.mail_top != 0:
            n = 0
            nmail_top = config.mail_top
            if config.mail_top == -1:
                nmail_top = len(user_list)

            while n < nmail_top:
                sortedi = sortedmail[n]
                mail_user(sortedi[0],reformat(sortedi[1]),percent_usage,
                       total_space,hostname,config)
                n += 1
        else:
            for i in sortedmail:
                if i[1] > config.list_threshold:
                    mail_user(i[0],reformat(i[1]),percent_usage,total_space,
                        hostname,config)

    if config.mail_root:
        mail_root(sortedmail, user_list, config)

    if config.loud_noises:
        print('\nUserusage finished successfully, exiting')

    exit(0)

##############################################################################
# config object                                                              #
##############################################################################

class conf(object):
    '''An object containing all of the configurable options
       with functions for parsing configs and command line args
    '''

    def __init__(self):
        '''init function for config'''

        # frequently used errors
        self.disk_error = """\nERROR: something went wrong with a disk check
Make sure you gave it the right partition/directory.
"""
        self.unform_error = """\nERROR, something went wrong parsing one or more of
your size arguments. Check your syntax or use -h for help
"""
        # set hostname and email settings
        hostname = socket.gethostname()
        self.sender = 'root@' + hostname
        self.extension = hostname
        self.root_mail = self.sender
        self.mail_root = False

        # options
        self.loud_noises = 0
        self.recursive = False
        self.partition = '/'
        self.dir = '/'
        self.home_dir = False
        self.space_threshold = 0
        self.mail_users = True
        self.list_users = False
        self.mail_threshold = 0
        self.list_threshold = 0
        self.mail_top = 10
        self.list_top = 0
        self.sort_list = 0
        self.DEBUG = False
        self.no_users = ['root','nobody', 'nobody4', 'noaccess', 'operator',
                         'nagios', 'mysql','nfsnobody','snort']
        self.inconf = ''
    
    def parse_arguments(self):
        '''parse all of our arguments'''
        #start parser
        parser = argparse.ArgumentParser()

        #add groups
        parsea = parser.add_mutually_exclusive_group()
        parseb = parser.add_mutually_exclusive_group()
        parsec = parser.add_mutually_exclusive_group()

        #shortcuts
        parsee = parser.add_argument
        parsea = parsea.add_argument
        parseb = parseb.add_argument
        parsec = parsec.add_argument

        #add options
        parsee("-u", "--usage", 
            help="Show usage help and exit", 
            action="store_true")
        parsee("-r", "--recursive", 
            help="Recursively scan directory's users", 
            action="store_true")
        parsee("--home-dir",
            help="Scan all of the user's home directories non-recursively",
            action="store_true")
        parsee("-p","--partition",
            help="Get partition to monitor",
            action="store")
        parsee("-t","--threshold",
            help="Set threshold for percent usage on given partition",
            action="store")
        parsee("-d","--directory",
            help="Set directory to scan",
            action="store")
        parsea("--list-size",
            help="List users who are using over a given size (units in T, G, M, K, b)",
            action="store")
        parsea("--list-top",
            help="List top X space using users. If X is -1, will list all users",
            action="store")
        parsee("--sort", 
            help="Sort list alphabetically", 
            action="store_true")
        parseb("--mail-size",
            help="Mail users who are using over a given size (units in T, G, M, K, b)",
            action="store")
        parseb("--mail-top",
            help="Mail top X space using users. If X is -1 will mail all users",
            action="store")
        parsee("--mail-root",
            help="Mail root a full report",
            action="store_true")
        parsec("-v","--verbose",
            help="Run in verbose mode",
            action="store_true")
        parsec("-vv","--very-verbose",
            help="Run in very verbose mode",
            action="store_true")
        parsee("--config", 
            help="Specify a config file to read from", 
            action="store")
        parsec("-db","--debug",
            help="Run in debug mode (verbose with no mailing and list all)",
            action="store_true")
        parsee('--version', 
            action='version', 
            version='Userusage Python v%s'%(VERSION))

        #parse args
        args = parser.parse_args()

        #parse options into something useful
        if args.usage:
            parser.print_usage()
            exit()

        #sort list
        self.sort_list = args.sort

        #parse verbose args
        if args.verbose:
            self.loud_noises = 1
        elif args.very_verbose:
            self.loud_noises = 2
        elif args.debug:
            self.DEBUG = True
            self.loud_noises = 2
            self.mail_users = False
            self.list_users = True
            self.list_top = -1
        if self.loud_noises == 2:
            print('Getting command line arguments.')

        #parse the easy args
        self.recursive = args.recursive
        try:
            if args.partition:
                self.partition = args.partition
            if args.directory:
                self.dir = args.directory
        except:
            parser.print_usage()
            stderr.write(self.unform_error)
            exit(1)
        try:
            if args.threshold:
                self.space_threshold = int(args.threshold)
        except:
            parser.print_usage()
            stderr.write('\nERROR: Error parsing threshold. Check your syntax.')
        try:
            if args.list_top:
                self.list_top = int(args.list_top)
                self.mail_top = 0
            if args.mail_top:
                self.mail_top = int(args.mail_top)
        except:
            parser.print_usage()
            stderr.write('\nERROR: one or more of your top arguments failed to parse.')
            stderr.write('Make sure they are formatted correctly.')
            exit()

        if args.config:
            self.inconf = args.config

        if args.list_size:
            self.list_threshold = unformat(args.list_size, self.unform_error)
        if args.mail_size:
            self.mail_threshold = unformat(args.mail_size, self.unform_error)
        if args.mail_root:
            self.mail_root = True

        if args.list_size or args.list_top:
            self.list_users = True

        if self.partition.endswith('/') and len(self.partition) > 1:
            self.partition = self.partition[:-1]
        if self.dir.endswith('/') and len(self.dir) > 1:
            self.dir = self.dir[:-1]

        if args.home_dir:
            self.home_dir = True

        if self.sort_list and self.list_top > 0:
            stderr.write('\nERROR: You can\'t list top and sort alphabetically.')
            exit()

        if self.loud_noises == 2:
            print('Done')

    def find_config(self):
        '''Find where the config file is hiding'''

        home = os.environ.get('HOME')
        if self.inconf == '':
            locations = [ # check local locations first
                         home + '/userusage.ini',
                         home + '/userusage.conf',
                         home + '/.userusage.ini',
                         home + '/.userusage.conf',
                         home + '/.config/userusage.ini',
                         home + '/.config/userusage.conf',
                         home + '/.config/userusage',
                         home + '/uuconf.ini',
                         home + '/uuconf',
                         home + '/uuconf.conf',
                         home + '/.uuconf.ini',
                         home + '/.uuconf',
                         home + '/.config/uuconf.ini',
                         home + '/.config/uuconf',
                         home + '/.config/uuconf.conf',
                         home + '/.config/.uuconf.ini',
                         home + '/.config/.uuconf',
                         home + '/.config/.uuconf.conf',

                         # if there's no REALLY local scan
                         # /usr/local/etc
                         '/usr/local/etc/userusage/userusage.ini',
                         '/usr/local/etc/userusage/userusage.conf',
                         '/usr/local/etc/userusage/uuconf.ini',
                         '/usr/local/etc/userusage/uuconf.conf',
                         '/usr/local/etc/userusage/uuconf',

                         # lastly check /etc/
                         '/etc/userusage/userusage.ini',
                         '/etc/userusage/userusage.conf',
                         '/etc/userusage/uuconf.ini',
                         '/etc/userusage/uuconf.conf',
                         '/etc/userusage/uuconf',

                         # if it's being run from the repo
                         # we can use the example conf
                         '../config/userusage.ini']
        else:
            locations = [self.inconf]

        for locale in locations:
            try:
                fi = open(locale, 'r')
                fi.close
                return(locale)
            except:
                pass
        return('')

    def tf(self, ins):
        '''Is ins true or false?'''
        if ins == "False" or ins == "false":
            return False
        else:
            return True

    def read_config(self, config_location):
        '''Read our config file'''

        # warn if they are using the sample config
        if config_location == '../config/userusage.ini':
            stderr.write('\nWARNING: You are using a ' +
                         'sample configuration file!\n')

        hostname = socket.gethostname()


        conf_parser = SafeConfigParser()
        conf_parser.read(config_location)
        conf_dict = dict(conf_parser.items('Config'))

        for key,item in conf_dict.items():
            if key == 'sender':
                self.sender = item.replace('hostname', hostname)
            elif key == 'extension':
                self.extension = item.replace('hostname', hostname)
            elif key == 'recursive':
                self.recursive = self.tf(item)
            elif key == 'threshold':
                try:
                    self.space_threshold = int(item)
                except:
                    pass
            elif key == 'list_users':
                self.list_users = self.tf(item)
            elif key == 'mail_users':
                self.mail_users = self.tf(item)
            elif key == 'list_threshold':
                self.list_threshold = unformat(item, self.unform_error)
            elif key == 'mail_threshold':
                self.mail_threshold = unformat(item, self.unform_error)
            elif key == 'mail_top':
                try:
                    self.mail_top = int(item)
                except:
                    pass
            elif key == 'list_top':
                try:
                    self.list_top = int(item)
                except:
                    pass
            elif key == 'sort_list':
                self.sort_list = self.tf(item)
            elif key == 'verbose':
                try:
                    self.loud_noises = int(item)
                    if self.loud_noises > 2:
                        self.loud_noises = 2
                    elif self.loud_noises < 0:
                        self.loud_noises = 0
                except:
                    self.loud_noises = 0
            elif key == 'partition':
                self.partition = item
            elif key == 'directory':
                self.dir = item
            elif key == 'home_dir':
                self.home_dir = self.tf(item)
            elif key == 'root_mail':
                self.root_mail = item.replace('hostname', hostname)
            elif key == 'mail_root':
                self.mail_root = self.tf(item)
            elif key == 'exclude':
                self.no_users = ['root']
                exclude_list = [c.replace(' ','') for c in item.split(',')]
                for thing in exclude_list:
                    if thing not in self.no_users:
                        self.no_users.append(thing)

    def fix_partition(self):
        '''psutil has to have partitions in the mounted designation
           not the /dev designation, so we change it to that
        '''
        if self.partition[:4] == '/dev':
            try:
                disklist = psutil.disk_partitions()
                for disk in disklist:
                    if disk.device == self.partition:
                        self.partition = disk.mountpoint
            except:
                stderr.write(self.disk_error)
                exit(1)
        if self.partition != self.dir[:len(self.partition)]:
            if self.loud_noises:
                print('\nWARNING: %s does not include %s!'%(self.partition,self.dir))


##############################################################################
# main                                                                       #
##############################################################################

def main():
    #and here, we, go.
    config = conf()

    conf_locale = config.find_config()
    if conf_locale != '':
        config.read_config(conf_locale)

    if __name__ == '__main__':
        try:
            config.parse_arguments()
        except:
            exit(1)

    new_conf_locale = config.find_config()
    if new_conf_locale != conf_locale and new_conf_locale != '':
        config.read_config(new_conf_locale)

    config.fix_partition()

    try:
        if config.loud_noises == 2:
            print("""
     _     __   ____  ___   _     __    __    __    ____
    | | | ( (` | |_  | |_) | | | ( (`  / /\  / /`_ | |_ 
    \_\_/ _)_) |_|__ |_| \ \_\_/ _)_) /_/--\ \_\_/ |_|__
            Userusage Python v%s by Will Drach
    """%(VERSION))
        if config.loud_noises:
            print("Checking if %s is over %d percent full"%(config.partition,
                config.space_threshold))
        if threshold_check(config):
            if config.loud_noises:
                print('Done')
                print('\n%s is over %d percent full. Running Userusage.'
                    %(config.partition,config.space_threshold))

            userusage(config)
            exit(0)
        else:
            if config.loud_noises:
                print('Done')
                print('\n%s is under %d percent full. Stopping Userusage.'
                    %(config.partition,config.space_threshold))
            exit(0)

    except Exception as err:
        print(err)
        exit(1)

##############################################################################
# run!                                                                       #
##############################################################################

main()

##############################################################################
# if for some reason we get kicked out of main, exit.                        #
##############################################################################

exit(3)
