#!/usr/bin/env python
# PYTHON_ARGCOMPLETE_OK
import os
import shutil
import json
import sys
import errno
import argparse
import argcomplete
from pathlib import Path 
import IPython

#file=os.path.expanduser("~/.copy_to_confs.json")
file=os.path.expanduser("~/.copy_to_confs.json")
if not os.path.exists(file):
    with open(file, "w") as outfile:
        json.dump({}, outfile)

def is_valid_dir(parser, arg):
    if os.path.isdir(arg):
        return os.path.abspath(arg)
    elif os.path.isfile(arg):
        print('%s is a file. A folder is required' % arg)
        raise SystemExit              
    else:
        print("The directory %s does not exist!" % arg)
        raise SystemExit

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
        exist_dest=os.path.join(dest, os.path.basename(os.path.normpath(element)))
        if os.path.isfile(element):
            shutil.copy2(element, exist_dest)
            print("Copied to " + str(exist_dest))

        elif os.path.isdir(element):
            shutil.copytree(element, exist_dest, dirs_exist_ok=True)
            print("Copied to " + str(exist_dest) + " and all it's inner content")

def listAll():
    for name, value in envs.items():
        if not name == 'group':
            print(name + ":")
            print("     dest:     '" + str(value['dest']) + "'")
            print("     src:")
            for src in value['src']:
                print("          '" + str(src) + "'")


def filterListDoubles(a):
    # https://stackoverflow.com/questions/9835762/how-do-i-find-the-duplicates-in-a-list-and-create-another-list-with-them
    seen = set()
    ret = [x for x in a if x not in seen and not seen.add(x)]
    return ret

def EnvironCompleter(**kwargs):
    return os.environ
 
   
with open(file, 'r') as outfile:
    envs = json.load(outfile)

def exist_name(parser, x):
    not_exists=True
    if x in envs or x == 'group' or x in envs['group']:
        print("The name %s already exists as conf name!" % x)
        listAll()
        raise SystemExit 
    return x

def get_names():
    names=[]
    for key, name in envs.items():
        if not key == "group":
            names.append(key)
        else:
            for e in envs['group']:
                names.append(e)
    return names

def get_reg_names():
    names=[]
    for key, name in envs.items():
        if not key == "group":
            names.append(key)
    return names

def get_group_names():
    names=[]
    for e in envs['group']:
        names.append(e)
    return names

def get_main_parser():
    choices = argcomplete.completers.ChoicesCompleter

    parser = argparse.ArgumentParser(description="Setup configuration to copy files and directories to",formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    subparser = parser.add_subparsers(dest='command')
    list1 = subparser.add_parser('list')
    run = subparser.add_parser('run')
    add = subparser.add_parser('add')
    delete = subparser.add_parser('delete')
    add_source = subparser.add_parser('add_source')
    add_group = subparser.add_parser('add_group')
    delete_group = subparser.add_parser('delete_group')
    reset_destination = subparser.add_parser('reset_destination')
    reset_source = subparser.add_parser('reset_source')
    help1 = subparser.add_parser('help')
    list1.add_argument("name" , nargs='?', type=str ,help="Configuration name", metavar="Configuration Name", choices=get_names())
    run.add_argument("name" , nargs='+', type=str ,help="Configuration name", metavar="Configuration Name", choices=get_names())
    delete.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
    delete.add_argument("name" , nargs='+', type=str ,help="Configuration name", metavar="Configuration Name", choices=get_reg_names()).completer=choices(get_reg_names())
    add.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
    add.add_argument("name" , type=lambda x: exist_name(parser, x) ,help="Configuration name", metavar="Configuration Name")
    add.add_argument("dest" , type=lambda x: is_valid_dir(parser, x), help="Destination folder")
    add.add_argument("src" , nargs='*', type=lambda x: is_valid_file_or_dir(parser, x), help="Source files and directories")
    add_group.add_argument("groupname" , type=lambda x: exist_name(parser, x) ,help="Group name holding multiple configuration names", metavar="Group Name")
    add_group.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
    add_group.add_argument("name" , nargs='+', type=str ,help="Configuration name", metavar="Configuration Name", choices=get_reg_names())
    delete_group.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
    delete_group.add_argument("groupname" , type=str ,help="Group name holding multiple configuration names", metavar="Group Name", choices=get_group_names())
    add_source.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration Name",  choices=get_reg_names())
    add_source.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
    add_source.add_argument("src" , nargs='+', type=lambda x: is_valid_file_or_dir(parser, x), help="Source files and directories")
    reset_destination.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
    reset_destination.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration Name",  choices=get_reg_names())
    reset_destination.add_argument("dest" , type=lambda x: is_valid_dir(parser, x), help="Destination folder")
    reset_source.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
    reset_source.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration Name",  choices=get_reg_names())
    reset_source.add_argument("src" , nargs='*', type=lambda x: is_valid_file_or_dir(parser, x), help="Source files and directories")
    argcomplete.autocomplete(parser)
    return parser

if __name__ == "__main__":
    parser = get_main_parser()
    args = parser.parse_args()

    name= args.name if "name" in args else ""
    dest= args.dest if "dest" in args else []
    src=args.src if "src" in args else []
    if type(name) is list:
        name = filterListDoubles(name)
    src = filterListDoubles(src)
                    
    if not 'group' in envs:
        with open(file, 'w') as outfile: 
            envs['group'] = []
            json.dump(envs, outfile)
    
    if args.command == 'help':
        print("Positional argument 'run' to run config by name")
        parser.print_help()
        raise SystemExit
    
    if args.command == 'run':
        if envs == {}:
            print("Add an configuration with 'copy_to add dest src' first to copy all it's files to destination")
            raise SystemExit
        elif not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        else:
            var = []
            grps = []
            for key in name:
                if key in envs['group']:
                    var.append(envs['group'][key])
                    grps.append(key)
            var1=[]
            for i in var:
                for e in i:
                    var1.append(e)
            for key in name:
                if not key in grps:
                    var1.append(key)
            var1 = filterListDoubles(var1)
            print(var1)
            for key in var1:
                if not key in envs:
                    print("Look again. " + key + " isn't in there.")
                    listAll()
                    raise SystemExit
            for i in var1:
                i=str(i)
                dest = envs[i]['dest']
                src = envs[i]['src']
                copy_to(dest, src)
    elif args.command == 'add':
        if not 'name' in args:
            print("Give up a configuration name to copy objects between")
            raise SystemExit
        elif args.name == 'group':
            print("Name 'group' is reserved to keep track of groupnames")
            raise SystemExit
        elif name in envs:
            print("Look again. " + str(name) + " is/are already used as name.")
            listAll()
            raise SystemExit
        elif name in envs['group']:
            print("Look again. " + str(name) + " is/are already used as groupname.")
            listAll()
            raise SystemExit
        elif str(dest) in src:
            print("Destination and source can't be one and the same")
            raise SystemExit
        else:
            with open(file, 'w') as outfile: 
                envs[str(name)] = { 'dest' : str(dest), 'src' : [*src] }
                json.dump(envs, outfile)
    
    elif args.command == 'add_group':
        if not 'groupname' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif args.groupname == 'group':
            print("Name 'group' is reserved to keep track of groupnames")
            raise SystemExit
        elif args.groupname in envs:
            print("Can't have both the same groupname and regular name. Change " + str(args.groupname))
            raise SystemExit
        elif args.groupname in envs['group']:
            print("Change " + str(args.groupname) + ". It's already taken")
            raise SystemExit
        else:
            for key in name:
                if not key in envs:
                    print("Look again. " + key + " isn't in there.")
                    listAll()
                    raise SystemExit
            with open(file, 'w') as outfile: 
                envs['group'] = { args.groupname : name }
                print(str(args.groupname) + ' added to confs')
                json.dump(envs, outfile)
    
    elif args.command == 'delete':
        if not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif envs == {} or os.stat(file).st_size == 0:
            print("Add an configuration with -a, --add first to copy all it's files to destination")
            raise SystemExit
        else:
            for key in name:
                if not key in envs:
                    print("Look again. '" + key + "' isn't in there.")
                    listAll()
                    raise SystemExit
            for key in name:
                if name == 'group':
                    print("Don't try to break the script silly")
                    raise SystemExit
                envs.pop(key)
                if 'list' in args:
                    print(str(key) + ' removed from confs')
            with open(file, 'w') as outfile:
                json.dump(envs, outfile)
    
    elif args.command == 'delete_group':
        if not 'groupname' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif args.groupname == 'group':
            print("Name 'group' is reserved to keep track of groupnames")
            raise SystemExit
        elif not args.groupname in envs['group']:
            print("Look again." + str(args.groupname) + " is not in there")
            listAll()
            raise SystemExit
        else:
            envs['group'].pop(args.groupname)
            print(str(args.groupname) + ' removed from confs')
            with open(file, 'w') as outfile: 
                json.dump(envs, outfile)
                
    elif args.command == 'add_source':
        if not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not 'src' in args:
            print("Give up a new set of source files and folders to copy objects between")
            raise SystemExit
        elif envs == {} or os.stat(file).st_size == 0:
            print("Add an configuration with -a, --add first to copy all it's files to destination")
            raise SystemExit
        elif not name in envs:
            print("Look again. " + str(name) + " isn't in there.")
            listAll()
            raise SystemExit
        elif envs[name]['dest'] in src:
            print('Destination and source can"t be one and the same')
            raise SystemExit
        else:
            src = [*src]
            with open(file, 'w') as outfile:
                for i in src:
                    if i in envs[name]['src']:
                        print(str(i) + " already in source of " + str(name))
                    else:
                        envs[name]["src"].append(i)
                        print('Added' + str(i) + ' to source of ' + str(name))
                json.dump(envs, outfile)
    
    elif args.command == 'reset_destination':
        if not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not 'dest' in args:
            print("Give up a new destination folder to copy objects between")
            raise SystemExit
        elif envs == {} or os.stat(file).st_size == 0:
            print("Add an configuration with -a, --add first to copy all it's files to destination")
            raise SystemExit
        elif not name in envs:
            print("Look again. " + str(name) + " isn't in there.")
            raise SystemExit
        elif dest in envs[name]['src']:
            print('Destination and source can"t be one and the same')
            raise SystemExit
        else:
            with open(file, 'w') as outfile:
                envs[name]['dest'] = str(dest)
                json.dump(envs, outfile)
            print('Reset destination of '+ str(name) +' to', dest)
    
    elif args.command == 'reset_source':
        if not 'name' in args:
            print("Give up an configuration to copy objects between")
            raise SystemExit
        elif not 'src' in args:
            print("Give up a new set of source files and folders to copy objects between")
            raise SystemExit
        elif envs == {} or os.stat(file).st_size == 0:
            print("Add an configuration with -a, --add first to copy all it's files to destination")
            raise SystemExit
        elif not name in envs:
            print("Look again. " + str(name) + " isn't in there.")
            raise SystemExit
        elif envs[name]['dest'] in src:
            print('Destination and source can"t be one and the same')
            raise SystemExit
        else:
            with open(file, 'w') as outfile:
                envs[name].update({ "src" : [*src] })
                json.dump(envs, outfile)
            print('Reset source of '+ str(name) + ' to', src)
    
    if args.command == None :
        parser.print_help()
    else: 
        if args.command == 'list' and "name" in args and args.name:
            for key, value in envs.items():
                if name == key:
                    print(key + ":")
                    print("     dest:     '" + str(value['dest']) + "'")
                    print("     src:")
                    for src in value['src']:
                        print("        '" + str(src) + "'")
        elif not args.command == None and args.command == 'list' or list in args:
            listAll()
        else:
            pass
