#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import os
import platform
import shutil
import json
import sys
import errno
import argparse
import argcomplete
import git
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.application.current import get_app
from git import Repo
from pathlib import Path 
import subprocess

if platform.system() == 'Linux' or platform.system() == 'Darwin':
    os.popen("eval $(register-python-argcomplete copy-to)").read()
elif platform.system() == 'Windows':
    pass
    #os.popen("register-python-argcomplete --shell powershell copy-to | Out-String | Invoke-Expression").read()

class Conf:
    def __init__(self):
        if os.getenv('COPY_TO'):
            self.file=os.path.expanduser(os.path.realpath(os.getenv('COPY_TO')))
            self.folder=os.path.dirname(self.file)
        else:
            self.file=os.path.expanduser("~/.config/copy-to/confs.json")
            self.folder=os.path.dirname(self.file)
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.readfile()

    def readfile(self):
        if not os.path.exists(self.file):
            with open(self.file, "w") as outfile:
                self.envs = {}
                self.envs['group'] = [] 
                json.dump(self.envs, outfile)
        with open(self.file, 'r') as infile: 
            self.envs = json.load(infile)


conf = Conf()

def is_git_repo(path):
    try:
        repo = git.Repo(path).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False

if is_git_repo("./"):
    try:
        repo = git.Repo("./")
        res = repo.config_reader().get_value("copy-to", "file")
        if res:
            conf.file = os.path.abspath(res)
            conf.folder = os.path.dirname(res)
            conf.readfile()
    except:
        pass

def is_valid_dir(parser, arg):
    if os.path.isdir(arg):
        return os.path.abspath(arg)
    elif os.path.isfile(arg):
        print('%s is a file. A folder is required' % arg)
        raise SystemExit              
    else:
        print("The directory %s does not exist!" % arg)
        res = prompt("Do you want to create the directory " + arg + "? [y/n]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
        if res == "y":
            try:
                os.makedirs(arg)
                return os.path.abspath(arg)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise SystemExit

def is_names_or_group(parser, arg):
    if arg == 'all':
        listAll()
        return arg
    elif arg in get_names(False):
        listName(arg)
        return arg
    elif arg == 'names':
        listNames()
        return arg
    elif arg == 'all-no-group':
        listNoGroup()
        return arg
    elif arg == 'file':
        listFile()
        return arg
    elif arg == 'groups':
        listGroups()                
        return arg
    elif arg == 'all-groups':
        listAllGroups()                
        return arg
    elif arg == 'groupnames':
        listGroupNames()                
        return arg
    elif arg == 'all-names':
        listAllNames()                
        return arg
    else:
        print("Give up 'file'/'all'/'all-no-group'/'groups'/'all-groups'/'names'/'groupnames'/'all-names' or a configuration name/groupname as an argument")
        raise SystemExit

def is_valid_name(parser, arg):
    if arg in get_reg_names():
        return arg
    else:
        print("Give up a name. Look at this list for reference: ")
        listNoGroup()
        raise SystemExit 

def is_valid_group(parser, arg):
    if arg in get_group_names():
        return arg
    else:
        print("Give up a groupname. Look at this list for reference: ")
        listGroups()
        raise SystemExit

def is_valid_conf(parser, arg):
    file = os.path.realpath(os.path.expanduser(arg)) 
    if arg.endswith('.json') and os.path.exists(os.path.expanduser(arg)):
        try:
            with open(file) as fp:
                conf.envs = json.load(fp)
                if not 'group' in conf.envs:
                    print("The file %s is not a valid configuration file!" % arg)
                    raise SystemExit
            conf.file = file
            conf.folder = os.path.dirname(file)
            conf.readfile()
            return file
        except:
            print("Couldn't open the file. Was the file a readable '.json'?")
            raise SystemExit
    elif arg.endswith('.json') and not os.path.exists(os.path.expanduser(arg)):
        try:
            with open(file, "w") as outfile:
                conf.envs = {}
                conf.envs['group'] = [] 
                json.dump(conf.envs, outfile)
            conf.file = file
            conf.folder = os.path.dirname(file)
            conf.readfile()
            return file
        except:
            print("Couldn't create a new configurationfile. Did the path exist and was the filetype '.json'?")
            raise SystemExit
    else:
        print("The file %s does not exist/is not in .json format!" % arg)
        raise SystemExit

def get_git_repo_name():
    try: 
        if is_git_repo("./"):
            return os.path.basename(os.getcwd())  
    except git.exc.InvalidGitRepositoryError:
        print("This is not a git repository")
        raise SystemExit

def git_write_conf(key, value):
    if is_git_repo("./"):
        name = get_git_repo_name()
        repo = git.Repo(path).git_dir
        with repo.config_writer() as confw: 
            confw.set(key, value)
        print('Added ' + str(key) + ' = ' + str(value) + ' to git settings')

def is_valid_file_or_dir(parser, arg):
    arg=os.path.abspath(arg)
    if os.path.isdir(arg):
        return arg
    elif os.path.isfile(arg):
        return arg              
    elif os.path.exists(os.path.join(os.getcwd(), arg)):
        return os.path.join(os.getcwd(), arg)
    else:
        print("The file/directory %s does not exist!" % arg)
        raise SystemExit

def copy_to(dest, src):
    for element in src:
        if not os.path.exists(dest):
            prompt("The destination " + dest + " does not exist. Do you want to create it? [y/n]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
            if res == "y":
                os.makedirs(dest)
            else:
                raise SystemExit
        exist_dest=os.path.join(dest, os.path.basename(os.path.normpath(element)))
        if os.path.isfile(element):
            shutil.copy2(element, exist_dest)
            print("Copied to " + str(exist_dest))

        elif os.path.isdir(element):
            shutil.copytree(element, exist_dest, dirs_exist_ok=True)
            print("Copied to " + str(exist_dest) + " and all it's inner content")

def copy_from(dest, src):
    for element in src:
        if not os.path.exists(dest):
            prompt("The destination " + dest + " does not exist. Do you want to create it? [y/n]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
            if res == "y":
                os.makedirs(dest)
            else:
                raise SystemExit
        exist_dest=os.path.join(dest, os.path.basename(os.path.normpath(element)))
        if os.path.isfile(exist_dest):
            shutil.copy2(exist_dest, element)
            print("Copied to " + str(element))

        elif os.path.isdir(exist_dest):
            shutil.copytree(exist_dest, element, dirs_exist_ok=True)
            print("Copied to " + str(element) + " and all it's inner content")


def listAll():
    for name, value in conf.envs.items():
        if name == 'group':
            for group in conf.envs['group']:
                print(group + " (group):")
                for key in conf.envs['group'][group]:
                    print("     " + key)
        elif not name == 'group':
            print(name + ":")
            print("     Destination: '" + str(value['dest']) + "'")
            print("     Source :")
            for idx, src in enumerate(value['src']):
                print("          " + str(idx+1) + ") '" + str(src) + "'")

def listName(arg):      
    for key, value in conf.envs.items():
        if arg == key:
            print(key + ":")
            print("     Destination: '" + str(value['dest']) + "'")
            print("     Source: ")
            for idx, src in enumerate(value['src']):
                print("          " + str(idx+1) + ") '" + str(src) + "'")        
        elif 'group' == key and arg in value:
            print(arg + ":")
            for key1 in conf.envs[key][arg]:
                for name, value in conf.envs.items():
                    if key1 == name:
                        print("     " + name + ":")
                        print("         Destination: '" + str(value['dest']) + "'")
                        print("         Source: ")
                        for idx, src in enumerate(value['src']):
                            print("             " + str(idx+1) + ") '" + str(src) + "'")

def listNoGroup():
    for name, value in conf.envs.items():
        if not name == 'group':
            print(name + ":")
            print("     Destination: '" + str(value['dest']) + "'")
            print("     Source: ")
            for idx, src in enumerate(value['src']):
                print("          " + str(idx+1) + ") '" + str(src) + "'")


def listAllGroups():
    for name, value in conf.envs.items():
        if name == 'group':
            for group in conf.envs['group']:
                print(group + ":")
                for key in conf.envs['group'][group]:
                     for name1, value in conf.envs.items():
                        if key == name1:
                            print("     " + name1 + ":")
                            print("         Destination: '" + str(value['dest']) + "'")
                            print("         Source: ")
                            for idx, src in enumerate(value['src']):
                                print("             " + str(idx+1) + ") '" + str(src) + "'")

def listGroups():
    for name, value in conf.envs.items():
        if name == 'group':
            for group in conf.envs['group']:
                print(group + " (group):")
                for key in conf.envs['group'][group]:
                    print("     " + key)

def listGroupNames():
    for name, value in conf.envs.items():
        if name == 'group':
            for group in conf.envs['group']:
                print(group)

def listNames():
    for name, value in conf.envs.items():
        if not name == 'group':
            print(name) 

def listAllNames():
    for name, value in conf.envs.items():
        if name == 'group':
            for group in conf.envs['group']:
                print(group + "(group)")
    listNames()

def listFile():
    print(conf.file)

def filterListDoubles(a):
    # https://stackoverflow.com/questions/9835762/how-do-i-find-the-duplicates-in-a-list-and-create-another-list-with-them
    seen = set()
    ret = [x for x in a if x not in seen and not seen.add(x)]
    return ret

#def PathCompleter(**kwargs):
#    return os.path

def PathOnlyDirsCompleter(**kwargs):
    return [ name for name in os.listdir(str(os.getcwd())) if os.path.isdir(os.path.join(os.getcwd()), name) ]

def SourceComplete():    
    return range(1,4)

def exist_name(parser, x):
    not_exists=True
    with open(conf.file, 'r') as outfile:
        conf.envs = json.load(outfile)
        if x in conf.envs or x == 'group' or x in conf.envs['group']:
            print("The name %s already exists as conf name!" % x)
            listAll()
            raise SystemExit 
        return x

def exist_groupname(parser, x):
    not_exists=True
    if x in conf.envs or x == 'group' or x in conf.envs['group']:
        print("The name %s already exists as conf name!" % x)
        listAll()
        raise SystemExit 
    return x 

def get_list_names(special=False):
    names=[]
    for key, name in conf.envs.items():
        if not key == "group":
            names.append(key)
        else:
            for e in conf.envs['group']:
                names.append(e)
    if special:
        names.append("all")
        names.append("all-no-group")
        names.append("file")
        names.append("groups")
        names.append("all-groups")
        names.append("names")
        names.append("groupnames")
        names.append("all-names")
    return names

def get_names(special=False):
    names=[]
    for key, name in conf.envs.items():
        if not key == "group":
            names.append(key)
        else:
            for e in conf.envs['group']:
                names.append(e)
    if special:
        names.append("all")
    return names

def get_reg_names():
    names=[]
    for key, name in conf.envs.items():
        if not key == "group":
            names.append(key)
    return names

def get_group_names():
    names=[]
    for e in conf.envs['group']:
        names.append(e)
    return names

def get_names_group(group):
    names=[]
    for e in conf.envs['group'][group]:
        names.append(e)
    return names


def cpt_run(name):
    if name == ['none']:
        raise SystemExit
    if name == ['all']:
        for i in conf.envs:
            if not i == 'group':
                print('\n' + i + ':')
                dest = conf.envs[i]['dest']
                src = conf.envs[i]['src']
                copy_to(dest, src)
    else:
        var = []
        grps = []
        for key in name:
            if key in conf.envs['group']:
                var.append(conf.envs['group'][key])
                grps.append(key)
        var1=[]
        for i in var:
            for e in i:
                var1.append(e)
        for key in name:
            if not key in grps:
                var1.append(key)
        var1 = filterListDoubles(var1)
        for key in var1:
            if not key in conf.envs:
                print("Look again." + key + " is not known. ")
                listAllNames()
                raise SystemExit
        for i in var1:
            i=str(i)
            print('\n' + i + ':')
            dest = conf.envs[i]['dest']
            src = conf.envs[i]['src']
            copy_to(dest, src)

def cpt_run_reverse(name):
    if name == ['none']:
        raise SystemExit
    elif name == ['all']:
        for i in conf.envs:
            if not i == 'group':
                print('\n' + i + ':')
                dest = conf.envs[i]['dest']
                src = conf.envs[i]['src']
                copy_from(dest, src)
    else:
        var = []
        grps = []
        for key in name:
            if key in conf.envs['group']:
                var.append(conf.envs['group'][key])
                grps.append(key)
        var1=[]
        for i in var:
            for e in i:
                var1.append(e)
        for key in name:
            if not key in grps:
                var1.append(key)
        var1 = filterListDoubles(var1)
        for key in var1:
            if not key in conf.envs:
                print("Look again. " + key + " isn't a known name.")
                listAllNames()
                raise SystemExit
        for i in var1:
            i=str(i)
            print('\n' + i + ':')
            dest = conf.envs[i]['dest']
            src = conf.envs[i]['src']
            copy_from(dest, src)

def prompt_autocomplete():
    app = get_app()
    b = app.current_buffer
    if b.complete_state:
        b.complete_next()
    else:
        b.start_completion(select_first=False)

def ask_git(prmpt="Setup git configuration to copy objects between? [y/n]: "):
    res = "all"
    repo = git.Repo("./")
    names = []
    for name, value in conf.envs.items():
        if not name == 'group':
            names.append(str(name))
        else:
            for e in conf.envs['group']:
                names.append(e)
        names.append("all")
    res1 = prompt(prmpt, pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
    if res1 == "y":
        res = prompt("Names: (Spaces for multiple - Empty: all): ", pre_run=prompt_autocomplete, completer=WordCompleter(names))
    else:
        with repo.config_writer() as confw:
            confw.set_value("copy-to", "run", 'none')
    res = prompt("File: ('.json' file - can be nonexistant - Empty: " + str(conf.file) + "): ", pre_run=prompt_autocomplete, completer=PathCompleter())
    res = os.path.realpath(os.path.expanduser(res))
    if not res:
        res = conf.file
    elif not os.path.exists(res):
        print("The file %s does not exist!" % res)
        res1 = prompt("Do you want to create " + res + "? [y/n]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
        if res1 == "y":
            try:
                if not os.path.exists(os.path.dirname(res)):
                    os.makedirs(os.path.dirname(res))
                with open(res, "w") as outfile:
                    conf.envs = {}
                    conf.envs['group'] = [] 
                    json.dump(conf.envs, outfile)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise SystemExit
    elif not res.endswith('.json'):
        print("The file " + str(res) + " is not a .json file")
        raise SystemExit
    with repo.config_writer() as confw:
        confw.set_value("copy-to", "file", res)
    print("Added " + str(res) + " to local git configuration")
    return res

def get_main_parser():
    choices = argcomplete.completers.ChoicesCompleter
    parser = argparse.ArgumentParser(description="Setup configuration to copy files and directories to",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
    parser.add_argument("-f","--file", type=lambda x: is_valid_conf(parser, x), required=False, help="Configuration file", metavar="Configuration file")
    subparser = parser.add_subparsers(dest='command')
    list1 = subparser.add_parser('list')
    run = subparser.add_parser('run')
    run_reverse = subparser.add_parser('run-reverse')
    add = subparser.add_parser('add')
    delete = subparser.add_parser('delete')
    add_source = subparser.add_parser('add-source')
    set_git = subparser.add_parser('set-git')
    add_group = subparser.add_parser('add-group')
    delete_group = subparser.add_parser('delete-group')
    add_to_group = subparser.add_parser('add-to-group')
    delete_from_group = subparser.add_parser('delete-from-group')
    reset_destination = subparser.add_parser('reset-destination')
    delete_source = subparser.add_parser('delete-source')
    reset_source = subparser.add_parser('reset-source')
    help1 = subparser.add_parser('help')
    list1.add_argument("name" , nargs='?', type=lambda x: is_names_or_group(parser, x), help="Configuration names or groups", metavar="Configuration names or groups", choices=get_list_names(True))
    
    run.add_argument("name" , nargs='?', type=str ,help="Configuration name", metavar="Configuration name", choices=get_names(True))
    run_reverse.add_argument("name" , nargs='?', type=str ,help="Configuration name", metavar="Configuration name", choices=get_names(True))
    
    add.add_argument("name" , type=lambda x: exist_name(parser, x) ,help="Configuration name", metavar="Configuration name")
    add.add_argument("dest" , type=lambda x: is_valid_dir(parser, x), metavar="Destination directory")
    add.add_argument("src" , nargs='*', type=lambda x: is_valid_file_or_dir(parser, x), metavar="Source files and directories", help="Source files and directories")
    
    delete.add_argument("name" , nargs='+', type=lambda x: is_valid_name(parser, x) ,help="Configuration name", metavar="Configuration name", choices=get_reg_names())
    
    add_group.add_argument("groupname" , type=lambda x: exist_name(parser, x) ,help="Group name holding multiple configuration names", metavar="Group name")
    add_group.add_argument("name" , nargs='+', type=lambda x: is_valid_name(parser, x) ,help="Configuration name", metavar="Configuration name", choices=get_reg_names())

    delete_group.add_argument("groupname" , type=lambda x: is_valid_group(parser, x) ,help="Group name holding multiple configuration names", metavar="Group name", choices=get_group_names())
    
    add_to_group.add_argument("groupname", type=lambda x: is_valid_group(parser, x), help="Group name holding multiple configuration names", metavar="Group name", choices=get_group_names())
    add_to_group.add_argument("name" , nargs='+', type=lambda x: is_valid_name(parser, x), help="Configuration name", metavar="Configuration name", choices=get_reg_names())

    delete_from_group.add_argument("groupname" , type=lambda x: is_valid_group(parser, x), help="Group name holding multiple configuration names", metavar="Group name", choices=get_group_names())
    delete_from_group.add_argument("name" , nargs='+', type=lambda x: is_valid_name(parser, x), help="Configuration name", metavar="Configuration name", choices=get_reg_names())
    
    git_command = set_git.add_subparsers(dest='gitcommand')
    git_run = git_command.add_parser('run')
    git_run.add_argument("value" , nargs='?' ,type=str , help="Configuration name", metavar="Configuration name", choices=get_names(True))
    git_file = git_command.add_parser('file')
    git_file.add_argument("value" , nargs='?' ,type=lambda x: is_valid_conf(parser, x) , help="Configuration file", metavar="Configuration file")
    
    add_source.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration name",  choices=get_reg_names())
    add_source.add_argument("src" , nargs='+', type=lambda x: is_valid_file_or_dir(parser, x), metavar="Source files and directories", help="Source files and directories")

    reset_destination.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration name",  choices=get_reg_names())
    reset_destination.add_argument("dest" , type=lambda x: is_valid_dir(parser, x), metavar="Destination directory", help="Destination directory")

    delete_source.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration name",  choices=get_reg_names())
    delete_source.add_argument("src_num" , nargs='*', type=int, metavar="Source files and directories or Index numbers", help="Source files and directories or Index numbers")

    reset_source.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration name",  choices=get_reg_names())
    reset_source.add_argument("src" , nargs='*', type=lambda x: is_valid_file_or_dir(parser, x), metavar="Source files and directories", help="Source files and directories")
    output_stream = None
    if "_ARGCOMPLETE_POWERSHELL" in os.environ:
        output_stream = codecs.getwriter("utf-8")(sys.stdout.buffer)

    argcomplete.autocomplete(parser, output_stream=output_stream)
    return parser

def main():
    """
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        os.popen("eval $(register-python-argcomplete copy-to)").read()
    elif platform.system() == 'Windows':
        pass
        #os.popen("register-python-argcomplete --shell powershell copy-to | Out-String | Invoke-Expression").read()

    from os.path import dirname, abspath
    d = dirname(abspath(__file__))

    sys.path.append(d)"""
    
    parser = get_main_parser()
    args = parser.parse_args()

    name= args.name if "name" in args else ""
    dest= args.dest if "dest" in args else []
    src=args.src if "src" in args else []
    if type(name) is list:
        name = filterListDoubles(name)
    src = filterListDoubles(src)
     

    if args.command == 'help':
        print("Positional argument 'run' to run config by name")
        parser.print_help()
        raise SystemExit

    elif args.command == 'run':
        if not args.name:
            if is_git_repo("./"):
                repo = git.Repo("./")
                try:
                    res = repo.config_reader().get_value("copy-to", "run")
                except:
                    res = ask_git("No name given but in a git repository. Setup git configuration to copy objects between? [y/n]: ")
                cpt_run(res.split())
                if args.list:
                    listName(res)
            else:
                print("No name given and not in a git repository. Give up an configuration to copy objects between")
                raise SystemExit   
        elif conf.envs == {} or conf.envs == {"group": []}:
            print("Add an configuration with 'copy-to add dest src' first to copy all it's files to destination")
            raise SystemExit
        else:
            cpt_run(name.split())
            if args.list:
                listName(name)
    elif args.command == 'run-reverse':
        if not args.name:
            if is_git_repo("./"):
                 res = 'all'
                 try:
                    res = repo.config_reader().get_value("copy-to", "run")
                 except:
                    res = ask_git("No name given but in a git repository. Setup git configuration to copy objects between? [y/n]: ")
                 cpt_run_reverse(res.split())
                 if args.list:
                    listName(res) 
            else:
                print("No name given and not in a git repository. Give up an configuration to copy objects between")
                raise SystemExit
        elif conf.envs == {} or conf.envs == {"group": []}:
            print("Add an configuration with 'copy-to add dest src' first to copy all it's files to destination")
            raise SystemExit   
        else:
            cpt_run_reverse(name.split())
            if args.list:
                listName(name)
    elif args.command == 'set-git':
        if not args.gitcommand:
            args.gitcommand = prompt("Give up a git value to set (run/file): ", pre_run=prompt_autocomplete, completer=WordCompleter(["run", "file"]))
            
        if args.gitcommand == 'run':
           repo = git.Repo("./")
           res = "all"
           names = []
           if not hasattr(args, 'value') or not args.value:
               for name, value in conf.envs.items():
                    if not name == 'group':
                        names.append(str(name))
               res = prompt("Names: (Spaces for multiple - Empty: all): ", pre_run=prompt_autocomplete, completer=WordCompleter(names))
               if res == '':
                   res = "all"
           else:
               res = args.value
           with repo.config_writer() as confw:
               confw.set_value("copy-to", "run", res)
           if args.list:
                listName(res)
           print("Added " + str(res) + " to local git configuration")
        elif args.gitcommand == 'file':
           repo = git.Repo("./")
           res = conf.file
           if hasattr(args, 'value') and args.value:
               res = args.value
           else: 
               res = prompt("File: ('.json' file - can be nonexistant - Empty: " + str(conf.file) + "): " , pre_run=prompt_autocomplete, completer=PathCompleter())
           res = os.path.realpath(os.path.expanduser(res))
           if not res:
               res = conf.file
           elif not os.path.exists(res):
                print("The file %s does not exist!" % res)
                res1 = prompt("Do you want to create it " + res + "? [y/n]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
                if res1 == "y":
                    try:
                        if not os.path.exists(os.path.dirname(res)):
                            os.makedirs(os.path.dirname(res))
                        with open(res, "w") as outfile:
                            conf.envs = {}
                            conf.envs['group'] = [] 
                            json.dump(conf.envs, outfile)
                    except OSError as e:
                        if e.errno != errno.EEXIST:
                            raise SystemExit
           elif not res.endswith('.json'):
               print("The file " + str(res) + " must be a '.json' file")
               raise SystemExit
           with repo.config_writer() as confw:
               confw.set_value("copy-to", "file", res)
           print("Added " + str(res) + " to local git configuration")
        

    elif args.command == 'add':
        if not 'name' in args:
            print("Give up a configuration name to copy objects between")
            raise SystemExit
        elif args.name == 'none' or args.name == 'group' or args.name == 'all':
            print("Name 'none', 'group' and 'all' are reserved in namespace")
            raise SystemExit
        elif name in conf.envs:
            print("Look again. " + str(name) + " is/are already used as name.")
            listNames()
            raise SystemExit
        elif name in conf.envs['group']:
            print("Look again. " + str(name) + " is/are already used as groupname.")
            listGroupNames()
            raise SystemExit
        elif str(dest) in src:
            print("Destination and source can't be one and the same")
            raise SystemExit
        else:
            with open(conf.file, 'w') as outfile: 
                conf.envs[str(name)] = { 'dest' : str(dest), 'src' : [*src] }
                json.dump(conf.envs, outfile)
            args.name = name
            if args.list:
                listName(name)
            print(str(args.name) + ' added to configuration file')

    elif args.command == 'add-group':
        if not 'groupname' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif args.groupname == 'none' or args.groupname == 'group' or args.groupname == 'all' :
            print("Name 'none', 'group' and 'all' are reserved in namespace")
            raise SystemExit
        elif args.groupname in conf.envs:
            print("Can't have both the same groupname and regular name. Change " + str(args.groupname))
            raise SystemExit
        elif args.groupname in get_names(False):
            print("Can't have both the same groupname and regular name. Change " + str(args.groupname))
            raise SystemExit
        elif args.groupname in conf.envs['group']:
            print("Change " + str(args.groupname) + ". It's already taken")
            raise SystemExit
        else:
            groups = []
            for key in name:
                if not key in conf.envs:
                    print("Look again. " + key + " isn't in there.")
                    listGroupNames()
                    raise SystemExit
            with open(conf.file, 'w') as outfile: 
                for key in name:
                    groups.append(key)
                conf.envs['group'][args.groupname] = groups
                if args.list:
                    listName(args.groupname)
                print(str(args.groupname) + ' added to group settings')
                json.dump(conf.envs, outfile)

    elif args.command == 'add-to-group':
        if not 'groupname' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not args.groupname in conf.envs['group']:
            print(str(args.groupname) + ". Doesn't exist. Look again.")
            listGroupNames()
            raise SystemExit
        else:
            groupnames = []
            with open(conf.file, 'w') as outfile: 
                groupnames = conf.envs['group'][args.groupname]
                for known in groupnames:
                    for n in args.name:
                        if known == n:
                            print("Look again. " + known + " is already in " + args.groupname)
                            listAllGroups()
                            raise SystemExit
                for key in name:
                    conf.envs['group'][args.groupname].append(key)
                json.dump(conf.envs, outfile)
            if args.list:
                    listName(args.groupname)
            print(str(args.name) + ' added to ' + str(args.groupname))

    elif args.command == 'delete':
        if not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif conf.envs == {} or os.stat(conf.file).st_size == 0:
            print("Add an configuration with add first to copy all it's files to destination")
            raise SystemExit
        else:
            for key in name:
                if not key in conf.envs:
                    print("Look again. '" + key + "' isn't a known name")
                    listAllNames()
                    raise SystemExit
            for key in name:
                if name == 'group':
                    print("Name 'group' is reserved for addressing groups of dest/src at once")
                    raise SystemExit
                conf.envs.pop(key)
                if args.list:
                    listNoGroup()
                print(str(key) + ' removed from existing settings')
            with open(conf.file, 'w') as outfile:
                json.dump(conf.envs, outfile)
    
    elif args.command == 'delete-group':
        if not 'groupname' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif args.groupname == 'group':
            print("Name 'group' is reserved to keep track of groupnames")
            raise SystemExit
        elif not args.groupname in conf.envs['group']:
            print("Look again." + str(args.groupname) + " is not in known groups")
            listGroups()
            raise SystemExit
        else:
            conf.envs['group'].pop(args.groupname)
            if args.list:
                listGroups()
            print(str(args.groupname) + ' removed from existing settings')
            with open(conf.file, 'w') as outfile:
                json.dump(conf.envs, outfile)
    
    elif args.command == 'delete-from-group':
        if not 'groupname' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not args.groupname in conf.envs['group']:
            print(str(args.groupname) + ". Doesn't exist. Look again.")
            listGroupNames()
            raise SystemExit
        else:
            groupnames = []
            with open(conf.file, 'w') as outfile: 
                groupnames = conf.envs['group'][args.groupname]
                for known in groupnames:
                    for n in args.name:
                        if known == n:
                            conf.envs['group'][args.groupname].remove(known)
                            args.name.remove(n)
                            if args.list:
                                listName(args.groupname) 
                            print(str(n) + ' removed from ' + str(args.groupname))
                json.dump(conf.envs, outfile)
                if not args.name == []:
                    print("Look again. " + str(args.name) + " isn't/aren't in " + str(args.groupname))
                    raise SystemExit
                

    elif args.command == 'add-source':
        if not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not 'src' in args:
            print("Give up a new set of source files and folders to copy objects between")
            raise SystemExit
        elif conf.envs == {} or os.stat(conf.file).st_size == 0:
            print("Add an configuration with 'copy-to add' first to copy all it's files to destination")
            raise SystemExit
        elif not name in conf.envs:
            print("Look again. " + str(name) + " isn't a known name.")
            listNames()
            raise SystemExit
        elif conf.envs[name]['dest'] in src:
            print('Destination and source can"t be one and the same')
            raise SystemExit
        else:
            src = [*src]
            with open(conf.file, 'w') as outfile:
                for i in src:
                    if i in conf.envs[name]['src']:
                        print(str(i) + " already in source of " + str(name))
                    else:
                        conf.envs[name]["src"].append(i)
                        if args.list:
                            listName(name)
                        print('Added ' + str(i) + ' to source of ' + str(name))
                json.dump(conf.envs, outfile)
    
    elif args.command == 'reset-destination':
        if not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not 'dest' in args:
            print("Give up a new destination folder to copy objects between")
            raise SystemExit
        elif conf.envs == {} or os.stat(conf.file).st_size == 0:
            print("Add an configuration with add first to copy all it's files to destination")
            raise SystemExit
        elif not name in conf.envs:
            print("Look again. " + str(name) + " isn't a known name.")
            listNames()
            raise SystemExit
        elif dest in conf.envs[name]['src']:
            print('Destination and source can"t be one and the same')
            raise SystemExit
        else:
            with open(conf.file, 'w') as outfile:
                conf.envs[name]['dest'] = str(dest)
                json.dump(conf.envs, outfile)
            if args.list:
                listName(name)
            print('Reset destination of '+ str(name) +' to', dest)
    
    elif args.command == 'delete-source':
        if not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not 'src_num' in args:
            print("Give up the indices of the directories and files to be deleted from configuration")
            raise SystemExit
        elif conf.envs == {} or os.stat(conf.file).st_size == 0:
            print("Add an configuration with add first to copy all it's files to destination")
            raise SystemExit
        elif not name in conf.envs:
            print("Look again. " + str(name) + " isn't in there.")
            raise SystemExit
        elif conf.envs[name]['dest'] in src:
            print("Destination and source can't be one and the same")
            raise SystemExit
        else:
            for i in args.src_num:
                if i > len(conf.envs[name]['src']):
                    print("One of the given indices exceeds the amount of sources")
                    raise SystemExit
            src = conf.envs[name]['src']
            for i in args.src_num:
                src.pop(i - 1)
            with open(conf.file, 'w') as outfile:
                conf.envs[name].update({ "src" : [*src] })
                json.dump(conf.envs, outfile)
            if args.list:
                listName(name)
            print('Deleted source of '+ str(name))

    elif args.command == 'reset-source':
        if not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not 'src' in args:
            print("Give up a new set of source files and folders to copy objects between")
            raise SystemExit
        elif conf.envs == {} or os.stat(conf.file).st_size == 0:
            print("Add an configuration with -a, --add first to copy all it's files to destination")
            raise SystemExit
        elif not name in conf.envs:
            print("Look again. " + str(name) + " isn't in there.")
            listNames()
            raise SystemExit
        elif conf.envs[name]['dest'] in src:
            print('Destination and source can"t be one and the same')
            raise SystemExit
        else:
            with open(conf.file, 'w') as outfile:
                conf.envs[name].update({ "src" : [*src] })
                json.dump(conf.envs, outfile)
            if args.list:
                listName(name)
            print('Reset source of '+ str(name) + ' to', str(src))

    elif args.command == None and args.list:
        listAll()
    elif not args.command and not args.list:
        parser.print_help()


if __name__ == "__main__":
#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
    main()
