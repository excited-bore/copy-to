#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK

import importlib.metadata
__version__ = importlib.metadata.version("copy-to")

import os
import platform
import shutil
import re
import json
import sys
import pathlib
import errno
import argparse
import argcomplete
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.completion import PathCompleter
from prompt_toolkit.application.current import get_app
from pathlib import Path
import subprocess
import filecmp
if shutil.which("git"):
   import git
   from git import Repo


if platform.system() == 'Linux' or platform.system() == 'Darwin':
    os.popen("eval $(register-python-argcomplete copy-to)").read()
#elif platform.system() == 'Windows' and os.popen("powershell.exe Get-ExecutionPolicy").read() != "Restricted\n":
    #if os.popen("powershell.exe Get-Module -ListAvailable -Name copy-to").read() == '':
    #    import tempfile
    #    import subprocess
    #    res = os.popen("where.exe register-python-argcomplete").read()
    #    res = res.partition('\n')[0]
    #    res = os.popen("python " + res + " --shell powershell copy-to.exe").read()
    #    temp = tempfile.NamedTemporaryFile(prefix='copy-to', suffix='.psm1', delete=False)
    #    temp.write(bytes(res, 'utf-8'))
    #    temp.close()
    #    subprocess.run(["powershell.exe", "-Command", "Import-Module " + temp.name], check=True)
        #os.popen("powershell.exe -C Import-Module " + temp.name)
        #os.popen("python ((where.exe register-python-argcomplete).Split([Environment]::NewLine) | Select -First 1) --shell powershell copy-to.exe | Out-String | Invoke-Expression").read()
        #subprocess.Popen(["powershell.exe", "-c", "python ((where.exe register-python-argcomplete).Split([Environment]::NewLine) | Select -First 1) --shell powershell copy-to.exe | Out-String | Invoke-Expression"], stdout=subprocess.PIPE, stderr=None)

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
    if not shutil.which("git"):
        return False
    try:
        repo = git.Repo(path, search_parent_directories=True).git_dir
        return True
    except git.exc.InvalidGitRepositoryError:
        return False


if is_git_repo("./"):
    try:
        repo = git.Repo("./", search_parent_directories=True)
        res = os.path.realpath(repo.config_reader().get_value("copy-to", "file"))
        if res:
            conf.file = os.path.abspath(res)
            conf.folder = os.path.dirname(res)
            conf.readfile()
    except:
        pass

def is_valid_dir(arg):
    if not pathlib.Path(arg).is_dir():
        raise NotADirectoryError(arg)
    return pathlib.Path.absolute(arg)

def is_src(parser, name1, value1, arg):
    last = len(value1['src'])
    if re.search(r'\d-\d', arg):
        nums = re.findall(r'\d+', arg)
        nums[0] = int(nums[0])
        nums[1] = int(nums[1])
        if nums[0] < 1 or nums[0] > last:
            print("'SourceNumStart', the first sourcenumber needs to more then 1 and lower then " + last + ". See with copy-to list")
            raise SystemExit 
        elif nums[1] < 1 or nums[1] > last:
            print("'SourceNumEnd', the first sourcenumber needs to more then 1 and lower then " + last + ". See with copy-to list")
            raise SystemExit
        elif nums[0] > nums[1]:
            print("'SourceNumStart', the first sourcenumber needs to be lower then the second sourcenumber 'SourcNumEnd'. See with copy-to list")
            raise SystemExit
        else:
            if nums[0] > last or nums[0] < 1:
                print("'SourceNumStart', the first sourcenumber needs to be inbetween 1 and " + str(last) + ". See with copy-to list")
                raise SystemExit
            elif (nums[1] < nums[0] or nums[1] < 1):
                print("'SourceNumEnd', the second sourcenumber needs to be higher then the first sourcenumber and inbetween 1 and " + str(last) + ". See with copy-to list")
                raise SystemExit
            else:
                return str(arg)
    elif re.search(r'\d', arg):
        nums = re.findall(r'\d+', arg)
        nums[0] = int(nums[0])
        if nums[0] > last or nums[0] < 1:
            print("Sourcenumber for " + name1 + " needs to be inbetween 1 and " + str(last) + ". See with copy-to list")
            raise SystemExit
        else:
            return str(arg)
    else:
        print("Source must be of format 'SourceNum' or 'SourceNumStart-SourcNumEnd'. See with copy-to list")
        raise SystemExit

def get_sourcepath_subparsers(subparser):
    set_source_path = subparser.add_parser('set-path-source')
    name_parser = set_source_path.add_subparsers(dest='name')
    numbers = {}
    for name, value in conf.envs.items():
        if not name == 'group':
            source_parser = name_parser.add_parser(name)
            last = len(value['src'])
            numbers[name] = []
            for idx, src in enumerate(value['src']):
                numbers[name].append(str(idx+1))
            i=1
            j=1
            for e in value['src']:
                for r in value['src']:
                    if i < j:
                        numbers[name].append(str(i) + '-' + str(j))
                    j+=1
                i+=1
                j=1
            source_parser.add_argument("path", type=pathlib.Path, default=os.path.curdir, help="Source path", metavar="Source path")
            source_parser.add_argument("src" , type=int, nargs='+', help="Source number/Source Number Range", metavar="Source number/Source Number Range", choices=numbers[name])
    return set_source_path

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
        repo = git.Repo(name, search_parent_directories=True).git_dir
        with repo.config_writer() as confw: 
            confw.set(key, value)
        print('Added ' + str(key) + ' = ' + str(value) + ' to git settings')

#def is_valid_file_or_dir(parser, arg):
#    arg=os.path.abspath(arg)
#    if os.path.isdir(arg):
#        return arg
#    elif os.path.isfile(arg):
#        return arg              
#    elif os.path.exists(os.path.join(os.getcwd(), arg)):
#        return os.path.join(os.getcwd(), arg)
#    else:
#        raise FileNotFoundError("The file/directory %s does not exist!" % arg)

def copy_to_dest(dest, src):
    for element in src:
        if not os.path.exists(dest):
            res = prompt("The destination " + dest + " does not exist. Do you want to create it? [yes/no]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
            if res == "y":
                os.makedirs(dest)
            else:
                raise SystemExit
        exist_dest=os.path.join(dest, os.path.basename(os.path.normpath(element)))

        if os.path.exists(exist_dest):
            if is_git_repo("./"):
                repo = git.Repo("./", search_parent_directories=True)
                try:
                    reslt = repo.config_reader().get_value("copy-to", "overwrite")
                except:
                    if os.path.isfile(exist_dest) and shutil.which("git"):
                        reslt = prompt("There's already a file in the destination: " + exist_dest + ". What to do with it? [diff/overwrite/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["diff", "overwrite", "exit"]))
                    else:
                        reslt = prompt("There's already a file/folder in the destination: " + exist_dest + ". What to do with it? [overwrite/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["overwrite", "exit"]))
                if reslt == 'diff':
                    subprocess.run(["git", "diff", element, exist_dest]) 
                    reslt = prompt("What to do with " + exist_dest + "? [overwrite/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["overwrite", "exit"]))

                if reslt == "exit":
                    raise SystemExit
                elif reslt == 'overwrite':
                    if os.path.isfile(exist_dest):
                        pathlib.Path.unlink(exist_dest)
                    elif os.path.isdir(exist_dest) and os.listdir(exist_dest) == 0:
                        pathlib.Path.rmdir(exist_dest)
                    elif os.path.isdir(exist_dest):
                        print(exist_dest + ": ")
                        for i in os.listdir(exist_dest):
                            print(" -" + str(pathlib.Path(i).absolute()))
                        reslt = prompt(exist_dest + " is not empty. Are you sure you want to remove the entire directory? [yes/no(exit)]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["yes", "no"]))
                        if reslt == 'yes':
                            shutil.rmtree(exist_dest)
                        else:
                            raise SystemExit
                    print(exist_dest + " removed")
        print('blh')           
        if os.path.isfile(element): 
            shutil.copy2(element, exist_dest)
            print("Copied to " + str(exist_dest))
        elif os.path.isdir(element):
            shutil.copytree(element, exist_dest, dirs_exist_ok=True)
            print("Copied to " + str(exist_dest) + " and all it's inner content")

def copy_from_dest(dest, src, overwrite=False):
    for element in src:
        exist_dest=os.path.join(dest, os.path.basename(os.path.normpath(element)))
        if not os.path.exists(exist_dest):
            reslt = prompt(exist_dest + " doesn't exist. Skip? [yes/no(exit)]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["yes", "no"]))
            if reslt == 'yes':
                continue
            else:
                raise SystemExit
        
        exist_dest=os.path.join(dest, os.path.basename(os.path.normpath(element)))
        if os.path.exists(exist_dest):
            if is_git_repo("./"):
                repo = git.Repo("./", search_parent_directories=True)
                try:
                    reslt = repo.config_reader().get_value("copy-to", "overwrite")
                except:
                    if os.path.isfile(element) and shutil.which("git"):
                        reslt = prompt("There already exists a sourcefile: " + element + ". What to do with it? [diff/overwrite/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["diff", "overwrite", "exit"]))
                    else:
                        reslt = prompt("There's already a source-file/folder: " + element + ". What to do with it? [overwrite/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["overwrite", "exit"]))
                if reslt == 'diff':
                    subprocess.run(["git", "diff", element, exist_dest]) 
                    reslt = prompt("What to do with " + element + "? [overwrite/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["overwrite", "exit"]))

                if reslt == "exit":
                    raise SystemExit
                elif reslt == 'overwrite':
                    if os.path.isfile(element):
                        pathlib.Path.unlink(element)
                    elif os.path.isdir(element) and os.listdir(element) == 0:
                        pathlib.Path.rmdir(element)
                    elif os.path.isdir(element):
                        print(element + ": ")
                        for i in os.listdir(element):
                            print(" -" + str(pathlib.Path(i).absolute()))
                        reslt = prompt(element + " is not empty. Are you sure you want to remove the entire directory? [yes/no(exit)]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["yes", "no"]))
                        if reslt == 'yes':
                            shutil.rmtree(element)
                        else:
                            raise SystemExit
                    print(element + " removed")        
        if os.path.isfile(element):
            shutil.copy2(exist_dest, element)
            print("Copied to " + str(element))
        elif os.path.isdir(element):
            shutil.copytree(exist_dest, element, dirs_exist_ok=True)
            print("Copied to " + str(element) + " and all it's inner content")

def link_to_dest(dest, src):
    for element in src:
        if not os.path.exists(dest):
            res = prompt("The destination " + dest + " does not exist. Do you want to create it? [yes/no]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
            if res == "y":
                os.makedirs(dest)
            else:
                raise SystemExit
        exist_dest=os.path.join(dest, os.path.basename(os.path.normpath(element)))
        if os.path.exists(exist_dest):
            if is_git_repo("./"):
                repo = git.Repo("./", search_parent_directories=True)
                try:
                    reslt = repo.config_reader().get_value("copy-to", "overwrite")
                except:
                    if os.path.islink(element):
                        print(element + " is already symlinked. Skipping.")
                        continue
                    elif os.path.isfile(exist_dest) and not filecmp.cmp(exist_dest, element) and shutil.which("git"):
                        reslt = prompt("There's already a file in the destination: " + exist_dest + ". What to do with it? [diff/remove/copy-to-source-and-remove/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["diff", "remove", "copy-and-remove", "exit"]))
                    else:
                        reslt = prompt("There's already a file/folder in the destination: " + exist_dest + ". What to do with it? [remove/copy-to-source-and-remove/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["remove", "copy-and-remove", "exit"]))
                if reslt == 'diff':
                    subprocess.run(["git", "diff", element, exist_dest]) 
                    reslt = prompt("What to do with " + exist_dest + "? [remove/copy-to-source-and-remove/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["remove", "copy-and-remove", "exit"]))

                if reslt == 'copy-and-remove':
                    copy_from_dest(dest, src)
                    reslt='remove'

                if reslt == "exit":
                    raise SystemExit 
                elif reslt == 'remove':
                    if os.path.isfile(exist_dest):
                        pathlib.Path.unlink(exist_dest)
                    elif os.path.isdir(exist_dest) and os.listdir(exist_dest) == 0:
                        pathlib.Path.rmdir(exist_dest)
                    elif os.path.isdir(exist_dest):
                        print(exist_dest + ": ")
                        for i in os.listdir(exist_dest):
                            print(" -" + str(pathlib.Path(i).absolute()))
                        reslt = prompt(exist_dest + " is not empty. Are you sure you want to remove the entire directory? [yes/no(exit)]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["yes", "no"]))
                        if reslt == 'yes':
                            shutil.rmtree(exist_dest)
                        else:
                            raise SystemExit        
                    print(exist_dest + " removed")
        if not os.path.islink(element):                                 
            if os.path.isfile(element):
                os.symlink(element, exist_dest)
                print("Symlinked " + str(element) + " to " + str(exist_dest))
            elif os.path.isdir(element):
                os.symlink(element, exist_dest, True)
                print("Symlinked " + str(element) + " to " + str(exist_dest))

def link_from_dest(dest, src):
    for element in src:
        if not os.path.exists(dest):
            res = prompt("The destination " + dest + " does not exist. Do you want to create it? [yes/no(exit)]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
            if res == "y":
                os.makedirs(dest)
            else:
                raise SystemExit
        exist_dest=os.path.join(dest, os.path.basename(os.path.normpath(element)))
        if os.path.exists(element):
            if is_git_repo("./"):
                repo = git.Repo("./", search_parent_directories=True)
                try:
                    reslt = repo.config_reader().get_value("copy-to", "overwrite")
                except:
                    if os.path.islink(exist_dest):
                        print(exist_dest + " is already symlinked. Skipping.")
                        continue
                    elif os.path.isfile(element) and not filecmp.cmp(exist_dest, element) and shutil.which("git"):
                        reslt = prompt("There's already a file in the source: " + element + ". What to do with it? [diff/remove/copy-to-destination-and-remove/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["diff", "remove", "copy-and-remove", "exit"]))
                    else:
                        reslt = prompt("There's already a file/folder in the source: " + element + ". What to do with it? [remove/copy-to-destination-and-remove/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["remove", "copy-and-remove", "exit"]))
                
                    if reslt == 'diff':
                        subprocess.run(["git", "diff", element, exist_dest]) 
                        reslt = prompt("What to do with " + element + "? [remove/copy-to-destination-and-remove/exit]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["remove", "copy-and-remove", "exit"]))

                    if reslt == 'copy-and-remove':
                        copy_to_dest(dest, src)
                        reslt='remove'

                    if reslt == "exit":
                        raise SystemExit 
                    elif reslt == 'remove':
                        if os.path.isfile(element):
                            pathlib.Path.unlink(element)
                        elif os.path.isdir(element) and os.listdir(element) == 0:
                            pathlib.Path.rmdir(element)
                        elif os.path.isdir(element):
                            print(element + ": ")
                            for i in os.listdir(element):
                                print(" -" + str(pathlib.Path(i).absolute()))
                            reslt = prompt(element + " is not empty. Are you sure you want to remove the entire directory? [yes/no(exit)]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["yes", "no"]))
                            if reslt == 'yes':
                                shutil.rmtree(element)
                            else:
                                raise SystemExit
                        print(element + " removed")
                    else:
                        raise SystemExit
                        
        if not os.path.islink(exist_dest):                       
            if os.path.isfile(exist_dest):        
                os.symlink(exist_dest, element)
                print("Symlinked " + str(exist_dest) + " to " + str(element))
            elif os.path.isdir(exist_dest):
                os.symlink(exist_dest, element, True)
                print("Symlinked " + str(exist_dest) + " to " + str(element))


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

def get_source_num(group):
    names=[]
    for e in conf.envs['group'][group]:
        names.append(e)
    return names

def get_group_subparsers(subparser):
    add_to_group = subparser.add_parser('add-to-group')
    remove_from_group = subparser.add_parser('remove-from-group')
    add_group_parser = add_to_group.add_subparsers(dest='group')
    remove_group_parser = remove_from_group.add_subparsers(dest='group')
    names_add = {}
    names_del = {}
    for name, value in conf.envs.items():
        if name == 'group':
            for i in value:
                add_parser = add_group_parser.add_parser(i)
                remove_parser = remove_group_parser.add_parser(i)
                names_add[i]=[]
                names_del[i]=[]
                for e in get_reg_names():
                    if not e in conf.envs['group'][i]:
                        names_add[i].append(e)
                    elif e in conf.envs['group'][i]:
                        names_del[i].append(e)
                add_parser.add_argument("name" , nargs='+', help="Group name holding multiple configuration names", metavar="Group name", choices=names_add[i])
                remove_parser.add_argument("name" , nargs='+', help="Configuration name", metavar="Configuration name(s)", choices=names_del[i])
    return add_to_group,remove_from_group


def cpt_to_dest(name):
    if name == ['none']:
        raise SystemExit
    if name == ['all']:
        for i in conf.envs:
            if not i == 'group':
                print('\n' + i + ':')
                dest = conf.envs[i]['dest']
                src = conf.envs[i]['src']
                copy_to_dest(dest, src)
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
                print("Look again. " + key + " is not known. ")
                listAllNames()
                raise SystemExit
        for i in var1:
            i=str(i)
            print('\n' + i + ':')
            dest = conf.envs[i]['dest']
            src = conf.envs[i]['src']
            copy_to_dest(dest, src)

def symlink_to_dest(name):
    if name == ['none']:
        raise SystemExit
    if name == ['all']:
        for i in conf.envs:
            if not i == 'group':
                print('\n' + i + ':')
                dest = conf.envs[i]['dest']
                src = conf.envs[i]['src']
                link_to_dest(dest, src)
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
                print("Look again. " + key + " is not known. ")
                listAllNames()
                raise SystemExit
        for i in var1:
            i=str(i)
            print('\n' + i + ':')
            dest = conf.envs[i]['dest']
            src = conf.envs[i]['src']
            link_to_dest(dest, src)


def cpt_from_dest(name):
    if name == ['none']:
        raise SystemExit
    elif name == ['all']:
        for i in conf.envs:
            if not i == 'group':
                print('\n' + i + ':')
                dest = conf.envs[i]['dest']
                src = conf.envs[i]['src']
                copy_from_dest(dest, src)
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
            copy_from_dest(dest, src)

def symlink_from_dest(name):
    if name == ['none']:
        raise SystemExit
    if name == ['all']:
        for i in conf.envs:
            if not i == 'group':
                print('\n' + i + ':')
                dest = conf.envs[i]['dest']
                src = conf.envs[i]['src']
                link_from_dest(dest, src)
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
                print("Look again. " + key + " is not known. ")
                listAllNames()
                raise SystemExit
        for i in var1:
            i=str(i)
            print('\n' + i + ':')
            dest = conf.envs[i]['dest']
            src = conf.envs[i]['src']
            link_from_dest(dest, src)


def prompt_autocomplete():
    app = get_app()
    b = app.current_buffer
    if b.complete_state:
        b.complete_next()
    else:
        b.start_completion(select_first=False)

def ask_git(prmpt="Setup git configuration to copy objects between? [yes/no]: "):
    res = "all"
    repo = git.Repo("./" , search_parent_directories=True)
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
        res = prompt("File: ('.json' file - can be nonexistant - Empty: " + str(conf.file) + "): ", pre_run=prompt_autocomplete, completer=PathCompleter())
        if not res:
            res = conf.file
        res = os.path.realpath(os.path.expanduser(res))
        if not os.path.exists(res):
            print("The file %s does not exist!" % res)
            res1 = prompt("Do you want to create " + res + "? [yes/no]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
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
        git_path = pathlib.Path(os.path.dirname(repo.git_dir))
        res_path = pathlib.Path(res)
        if git_path in res_path.parents:
            res = str(res_path.relative_to(os.path.dirname(git.Repo("./", search_parent_directories=True).git_dir)))
            res = os.path.realpath(res)
        with repo.config_writer() as confw:
            confw.set_value("copy-to", "file", res)
        print("Added file = " + str(res) + " to local git configuration")
        res = prompt("Name(s): (Spaces for multiple - Empty: all): ", pre_run=prompt_autocomplete, completer=WordCompleter(names))
        with repo.config_writer() as confw:
            confw.set_value("copy-to", "name", res)
        print("Added copy-to = " + str(res) + " to local git configuration")
        res = prompt("Overwrite existing files?: (prevents prompt - yes / no): ", pre_run=prompt_autocomplete, completer=WordCompleter(["yes", "no"]))
        with repo.config_writer() as confw:
            confw.set_value("copy-to", "overwrite", res)
        print("Added overwrite = " + str(res) + " to local git configuration")
        return res
    else:
        res1 = prompt("You selected no. Prevent this popup from coming up again? [yes/no]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
        if res1 == 'y':
           with repo.config_writer() as confw:
                confw.set_value("copy-to", "name", "none")
           print("Added name = none to local git configuration")
        return False

def main():
    choices = argcomplete.completers.ChoicesCompleter
    parser = argparse.ArgumentParser(description="Setup configuration to copy files and directories to",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
     
    subparser = parser.add_subparsers(dest='command')
    list1 = subparser.add_parser('list')
    copy_to = subparser.add_parser('copy-to')
    copy_from = subparser.add_parser('copy-from')
    symlink_from = subparser.add_parser('symlink-from')
    symlink_to = subparser.add_parser('symlink-to')
    add = subparser.add_parser('add')
    remove = subparser.add_parser('remove')
    add_source = subparser.add_parser('add-source')
    set_source_path = get_sourcepath_subparsers(subparser)
    add_to_group, remove_from_group = get_group_subparsers(subparser)
    if shutil.which("git"):
        set_git = subparser.add_parser('set-git')
    add_group = subparser.add_parser('add-group')
    remove_group = subparser.add_parser('remove-group')
    reset_destination = subparser.add_parser('reset-destination')
    remove_source = subparser.add_parser('remove-source')
    reset_source = subparser.add_parser('reset-source')
    help1 = subparser.add_parser('help')
    list1.add_argument("name" , nargs='?', type=lambda x: is_names_or_group(parser, x), help="Configuration names or groups", metavar="Configuration names or groups", choices=get_list_names(True))
    
    copy_to.add_argument("name" , nargs='?', type=str ,help="Configuration name", metavar="Configuration name", choices=get_names(True))
    copy_from.add_argument("name" , nargs='?', type=str ,help="Configuration name", metavar="Configuration name", choices=get_names(True))
    symlink_to.add_argument("name" , nargs='?', type=str ,help="Configuration name", metavar="Configuration name", choices=get_names(True))
    symlink_from.add_argument("name" , nargs='?', type=str ,help="Configuration name", metavar="Configuration name", choices=get_names(True))

    add.add_argument("name" , type=lambda x: exist_name(parser, x) ,help="Configuration name", metavar="Configuration name")
    add.add_argument("dest" , type=pathlib.Path, default=os.path.curdir, metavar="Destination directory")
    add.add_argument("src" , nargs='*', type=argparse.FileType('r'), metavar="Source files and directories", help="Source files and directories")
    
    remove.add_argument("name" , nargs='+', type=lambda x: is_valid_name(parser, x) ,help="Configuration name", metavar="Configuration name", choices=get_reg_names())
   
    add_group.add_argument("groupname" , type=lambda x: exist_name(parser, x) ,help="Group name holding multiple configuration names", metavar="Group name")
    add_group.add_argument("name" , nargs='+', type=lambda x: is_valid_name(parser, x) ,help="Configuration name", metavar="Configuration name", choices=get_reg_names())

    remove_group.add_argument("groupname" , type=lambda x: is_valid_group(parser, x) ,help="Group name holding multiple configuration names", metavar="Group name", choices=get_group_names())
    
    if shutil.which("git"):
        git_command = set_git.add_subparsers(dest='gitcommand')
        git_run = git_command.add_parser('copy-to')
        git_run.add_argument("value" , nargs='?' ,type=str , help="Configuration name", metavar="Configuration name", choices=get_names(True))
        git_file = git_command.add_parser('file')
        git_file.add_argument("value" , nargs='?' ,type=lambda x: is_valid_conf(parser, x) , help="Configuration file", metavar="Configuration file")
        git_overwrite = git_command.add_parser('overwrite')
        git_overwrite.add_argument("value" , nargs='?' ,type=str , help="Overwrite files?", metavar="Configuration file", choices=['yes','no'])
        
    
    add_source.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration name",  choices=get_reg_names())
    add_source.add_argument("src" , nargs='+', type=argparse.FileType('r'), metavar="Source files and directories", help="Source files and directories")

    reset_destination.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration name",  choices=get_reg_names())
    reset_destination.add_argument("dest" , type=pathlib.Path, default=os.path.curdir, metavar="Destination directory", help="Destination directory")

    name_parser = remove_source.add_subparsers(dest='name')
    reset_name_parser = reset_source.add_subparsers(dest='name')
    numbers = {}
    for name, value in conf.envs.items():
        if not name == 'group':
            del_source_parser = name_parser.add_parser(name)
            reset_source_parser = reset_name_parser.add_parser(name)
            last = len(value['src'])
            numbers[name] = []
            for idx, src in enumerate(value['src']):
                numbers[name].append(str(idx+1))
            i=1
            j=1
            for e in value['src']:
                for r in value['src']:
                    if i < j:
                        numbers[name].append(str(i) + '-' + str(j))
                    j+=1
                i+=1
                j=1
            del_source_parser.add_argument("src_num" , nargs='+', help="Source number/Source Number Range", metavar="Source number/Source Number Range", choices=numbers[name]) 
            reset_source_parser.add_argument("src_num" , nargs='+', help="Source number/Source Number Range", metavar="Source number/Source Number Range", choices=numbers[name])

    reset_source.add_argument("src" , nargs='*', type=argparse.FileType('r'), metavar="Source files and directories", help="Source files and directories")
    output_stream = None
    if "_ARGCOMPLETE_POWERSHELL" in os.environ:
        output_stream = codecs.getwriter("utf-8")(sys.stdout.buffer)

    parser.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
    parser.add_argument("-f","--file", type=lambda x: is_valid_conf(parser, x), required=False, help="Configuration file", metavar="Configuration file", default=conf.file)
    parser.add_argument('--version', action='version', version='%(prog)s {version}'.format(version=__version__)) 


    argcomplete.autocomplete(parser, output_stream=output_stream)
    """
    if platform.system() == 'Linux' or platform.system() == 'Darwin':
        os.popen("eval $(register-python-argcomplete copy-to)").read()
    elif platform.system() == 'Windows':
        os.popen("python ((where.exe register-python-argcomplete).Split([Environment]::NewLine) | Select -First 1) --shell powershell copy-to.exe | Out-String | Invoke-Expression").read()


    from os.path import dirname, abspath
    d = dirname(abspath(__file__))

    sys.path.append(d)"""
    
    args = parser.parse_args()

    name= args.name if "name" in args else ""
    dest= args.dest if "dest" in args else []
    src=args.src if "src" in args else []
    if type(name) is list:
        name = filterListDoubles(name)
    src = filterListDoubles(src)
     

    if args.command == 'help':
        print("Copy or symlink (or both) from a config using userdefined names")
        parser.print_help()
        raise SystemExit

    elif args.command == 'copy-to':
        if not args.name:
            if is_git_repo("./"):
                repo = git.Repo("./", search_parent_directories=True)
                try:
                    res = repo.config_reader().get_value("copy-to", "name")
                except:
                    res = ask_git("No name given but in a git repository. Setup git configuration to copy objects between? [yes/no]: ")
                if res:
                    cpt_to_dest(res.split())
                    if args.list:
                        listName(res)
            else:
                print("No name given and not in a git repository. Give up an configuration to copy objects between")
                raise SystemExit   
        elif conf.envs == {} or conf.envs == {"group": []}:
            print("Add an configuration with 'copy-to add dest src' first to copy all it's files to destination")
            raise SystemExit
        else:
            cpt_to_dest(name.split())
            if args.list:
                listName(name)
    elif args.command == 'copy-from':
        if not args.name:
            if is_git_repo("./"):
                 res = 'all'
                 try:
                    res = repo.config_reader().get_value("copy-to", "name")
                 except:
                    res = ask_git("No name given but in a git repository. Setup git configuration to copy objects between? [yes/no]: ")
                 if res:
                    cpt_from_dest(res.split())
                    if args.list:
                        listName(res)
            else:
                print("No name given and not in a git repository. Give up an configuration to copy objects between")
                raise SystemExit
        elif conf.envs == {} or conf.envs == {"group": []}:
            print("Add an configuration with 'copy-to add dest src' first to copy all it's files to destination")
            raise SystemExit   
        else:
            cpt_from_dest(name.split())
            if args.list:
                listName(name)
    elif args.command == 'symlink-to':
        if not args.name:
            if is_git_repo("./"):
                repo = git.Repo("./", search_parent_directories=True)
                try:
                    res = repo.config_reader().get_value("copy-to", "name")
                except:
                    res = ask_git("No name given but in a git repository. Setup git configuration to copy objects between? [yes/no]: ")
                if res:
                    symlink_to_dest(res.split())
                    if args.list:
                        listName(res)
            else:
                print("No name given and not in a git repository with config. Give up an configuration to copy objects between")
                raise SystemExit   
        elif conf.envs == {} or conf.envs == {"group": []}:
            print("Add an configuration with 'copy-to add dest src' first to copy all it's files to destination")
            raise SystemExit
        else:
            symlink_to_dest(name.split())
            if args.list:
                listName(name)
    elif args.command == 'symlink-from':
        if not args.name:
            if is_git_repo("./"):
                repo = git.Repo("./", search_parent_directories=True)
                try:
                    res = repo.config_reader().get_value("copy-to", "name")
                except:
                    res = ask_git("No name given but in a git repository. Setup git configuration to copy objects between? [yes/no]: ")
                if res:
                    symlink_from_dest(res.split())
                    if args.list:
                        listName(res)
            else:
                print("No name given and not in a git repository with config. Give up an configuration to copy objects between")
                raise SystemExit   
        elif conf.envs == {} or conf.envs == {"group": []}:
            print("Add an configuration with 'copy-to add dest src' first to copy all it's files to destination")
            raise SystemExit
        else:
            symlink_from_dest(name.split())
            if args.list:
                listName(name)            
    elif args.command == 'set-git':
        if not args.gitcommand:
            args.gitcommand = prompt("Give up a git value to set (name/file/overwrite): ", pre_run=prompt_autocomplete, completer=WordCompleter(["name", "file", 'overwrite']))

        if args.gitcommand == 'name':
           repo = git.Repo("./", search_parent_directories=True)
           res = "all"
           names = []
           if not hasattr(args, 'value') or not args.value:
               for name, value in conf.envs.items():
                    if not name == 'group':
                        names.append(str(name))
               res = prompt("Name(s): (Spaces for multiple - Empty: all): ", pre_run=prompt_autocomplete, completer=WordCompleter(names))
               if res == '':
                   res = "all"
           else:
               res = args.value
           with repo.config_writer() as confw:
               confw.set_value("copy-to", "name", res)
           if args.list:
                listName(res)
           print("Added " + str(res) + " to local git configuration")
        elif args.gitcommand == 'file':
           repo = git.Repo("./", search_parent_directories=True)
           res = conf.file
           if hasattr(args, 'value') and args.value:
               res = args.value
           else: 
               res = prompt("File: ('.json' file - can be nonexistant - Empty: " + str(conf.file) + "): " , pre_run=prompt_autocomplete, completer=PathCompleter())
           if not res:
               res = conf.file
           res = os.path.realpath(os.path.expanduser(res))
           if not os.path.exists(res):
                print("The file %s does not exist!" % res)
                res1 = prompt("Do you want to create it " + res + "? [yes/no]: ", pre_run=prompt_autocomplete, completer=WordCompleter(["y", "n"]))
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
           git_path = pathlib.Path(os.path.dirname(git.Repo("./", search_parent_directories=True).git_dir))
           res_path = pathlib.Path(res)
           if git_path in res_path.parents:
               res = str(res_path.relative_to(os.path.dirname(git.Repo("./", search_parent_directories=True).git_dir)))
               res = os.path.realpath(res)
           with repo.config_writer() as confw:
               confw.set_value("copy-to", "file", res)
           print("Added " + str(res) + " to local git configuration")
        elif args.gitcommand == 'overwrite':
           repo = git.Repo("./", search_parent_directories=True)
           with repo.config_writer() as confw:
               confw.set_value("copy-to", "overwrite", args.value)

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
        elif not pathlib.Path(args.dest).absolute().exists():
            raise FileNotFoundError("The directory %s does not exist!" % dest)
        elif not pathlib.Path(args.dest).is_dir():
            raise NotADirectoryError(dest)
        elif type(args.src[0]) == 'TextIOWrapper' and not all(os.path.exists(str(i.name)) for i in args.src):

            raise FileNotFoundError("The file/directory %s does not exist!" % all(os.path.exists(str(i.name)) for i in args.src))
        else:
            if str(type(args.src[0])) == "<class '_io.TextIOWrapper'>":
                src=[]
                for i in args.src:
                    src.append(str(os.path.abspath(i.name)))
            with open(conf.file, 'w') as outfile: 
                conf.envs[str(name)] = { 'dest' : str(dest), 'src' : [*src] }
                json.dump(conf.envs, outfile)
            args.name = name
            if args.list:
                listName(name)
            print(str(args.name) + ' added to configuration file')
    elif args.command == 'set-path-source':
        names = get_reg_names()
        nameFound=False
        for name in names:
            if args.name == name:
                nameFound = True
                for i in args.src:
                    if args.path[-1] != '/':
                        args.path = args.path + '/'
                    if re.search(r'\d-\d', i):
                        nums = re.findall(r'\d+', i)
                        for j in range(int(nums[0]),int(nums[1])+1):
                            item = os.path.basename(conf.envs[str(args.name)]['src'][int(j)-1])
                            conf.envs[str(args.name)]['src'][int(j)-1] = args.path + item  
                    else: 
                        item = os.path.basename(conf.envs[str(args.name)]['src'][int(i)-1])
                        conf.envs[str(args.name)]['src'][int(i)-1] = args.path + item
                    with open(conf.file, 'w') as outfile: 
                        json.dump(conf.envs, outfile)
                listName(args.name)
                    
        if not nameFound:
            set_source_path.print_help()
            print("'set-path-source' needs a new path, a configuration name and a source range/number")
            raise SystemExit

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
        if not 'group' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not args.group in conf.envs['group']:
            print(str(args.group) + ". Doesn't exist. Look again.")
            listGroupNames()
            raise SystemExit
        else:
            groupnames = []
            groupnames = conf.envs['group'][args.group]
            for known in groupnames:
                for n in args.group:
                    if known == n:
                        print("Look again. " + known + " is already in " + args.group)
                        listAllGroups()
                        raise SystemExit
            with open(conf.file, 'w') as outfile: 
                for key in name:
                    conf.envs['group'][args.group].append(key)
                json.dump(conf.envs, outfile)
            if args.list:
                listName(args.group)
            print(str(args.name) + ' added to ' + str(args.group))

    elif args.command == 'remove':
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
    
    elif args.command == 'remove-group':
        if not 'groupname' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif args.groupname == 'group':
            print("Name 'group' is reserved to keep track of groupnames")
            raise SystemExit
        elif not args.groupname in conf.envs['group']:
            print("Look again. " + str(args.groupname) + " is not in known groups")
            listGroups()
            raise SystemExit
        else:
            conf.envs['group'].pop(args.groupname)
            if args.list:
                listGroups()
            print(str(args.groupname) + ' removed from existing settings')
            with open(conf.file, 'w') as outfile:
                json.dump(conf.envs, outfile)
    
    elif args.command == 'remove-from-group':
        if not 'group' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not args.group in conf.envs['group']:
            print(str(args.group) + ". Doesn't exist. Look again.")
            listGroupNames()
            raise SystemExit
        else:
            group = []
            groupnames = conf.envs['group'][args.group]
            for known in conf.envs['group'][args.group]:
                for n in args.name:
                    if known == n:
                        with open(conf.file, 'w') as outfile: 
                            conf.envs['group'][args.group].remove(known)
                            json.dump(conf.envs, outfile)
                        args.name.remove(n)
                        if args.list:
                            listName(args.group) 
                        print(str(n) + ' removed from ' + str(args.group))
            if not args.name == []:
                print("Look again. " + str(args.name) + " isn't/aren't in " + str(args.group))
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
    
    elif args.command == 'remove-source':
        if not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not 'src_num' in args:
            print("Give up the indices of the directories and files to be removed from configuration")
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
                if re.search(r'\d-\d', i):
                    nums = re.findall(r'\d+', i)
                    if nums[0] > nums[1]:
                        print("The first given number should be lower then the second")
                        raise SystemExit
                    elif int(nums[0]) > len(conf.envs[name]['src']) or int(nums[1]) > len(conf.envs[name]['src']):
                        print("One of the given numbers exceeds the amount of sources for " + str(args.name))
                        raise SystemExit
                    src = conf.envs[name]['src']
                    for j in reversed(range(int(nums[0]),int(nums[1])+1)):
                        name_src = src[int(j)-1]
                        src.pop(int(j) - 1)
                        print('Releted source from'+ str(name) + " " + str(j) + ' - ' + str(name_src))
                else:
                    i = int(i)
                    if i > len(conf.envs[name]['src']):
                        print("One of the given numbers exceeds the amount of sources for "  + str(args.name))
                        raise SystemExit
                    src = conf.envs[name]['src']
                    name_src = src[int(i)-1]
                    src.pop(int(i) - 1)
                    print('Removed source from'+ str(name) + " " + str(i) + ' - ' + str(name_src))
            with open(conf.file, 'w') as outfile:
                conf.envs[name].update({ "src" : [*src] })
                json.dump(conf.envs, outfile)
            if args.list:
                listName(name)

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

    elif (args.command == 'list' and not args.name) or (args.command == None and args.list):
        listAll()
    elif not args.command and not args.list:
        parser.print_help()


if __name__ == "__main__":
#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
    main()
