import os
import shutil
import json
import sys
import errno
import argcomplete
import argparse
from pathlib import Path
file=Path("/home/burp/.copy_to_confs.json")

#try:
#    os.rename('/etc/foo', '/etc/bar')
#except IOError as e:
#    print(e)
#    if (e == errno.EPERM):
#       sys.exit("You need root permissions to do this, laterz!")

if not os.path.exists(file):
    with open(file, "w") as outfile:
        json.dump({}, outfile)

def is_valid_dir(parser, arg):
    if os.path.isdir(arg):
        print('1' + arg)
        return arg
    elif os.path.isdir(os.path.join(os.getcwd(), arg)):
        print('2' + os.path.join(os.getcwd(), arg))
        return os.path.join(os.getcwd(), arg)
    elif os.path.isfile(arg):
        print('%s is a file. A folder is required' % arg)
        raise SystemExit              
    else:
        print("The directory %s does not exist!" % arg)
        raise SystemExit

def is_valid_file_or_dir(parser, arg):
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

with open(file, 'r') as outfile:
    envs = json.load(outfile)

parser = argparse.ArgumentParser(description="Setup configuration to copy files and directories to",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
subparser = parser.add_subparsers(dest='command')
list = subparser.add_parser('list')
run = subparser.add_parser('run')
#subparser.add_parser('run').completer = argcomplete.
add = subparser.add_parser('add')
delete = subparser.add_parser('delete')
add_source = subparser.add_parser('add_source')
reset_destination = subparser.add_parser('reset_destination')
reset_source = subparser.add_parser('reset_source')
#subparser.add_parser('modify').completer = EnvironCompleter

help = subparser.add_parser('help')
list.add_argument("name" , nargs='?', type=str ,help="Configuration name", metavar="Configuration Name")
run.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
run.add_argument("name" , nargs='+', type=str ,help="Configuration name", metavar="Configuration Name")
delete.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
delete.add_argument("name" , nargs='+', type=str ,help="Configuration name", metavar="Configuration Name")
add.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
add.add_argument("name" , type=str ,help="Configuration name", metavar="Configuration Name")
add.add_argument("dest" , type=lambda x: is_valid_dir(parser, x), help="Destination folder")
add.add_argument("src" , nargs='*', type=lambda x: is_valid_file_or_dir(parser, x), help="Source files and directories")
add_source.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration Name")
add_source.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
add_source.add_argument("src" , nargs='+', type=lambda x: is_valid_file_or_dir(parser, x), help="Source files and directories")
reset_destination.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
reset_destination.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration Name")
reset_destination.add_argument("dest" , type=lambda x: is_valid_dir(parser, x), help="Destination folder")
reset_source.add_argument("-l", "--list", action='store_true', required=False, help="List configuration")
reset_source.add_argument("name" , type=str ,help="Configuration name for modifications", metavar="Configuration Name")
reset_source.add_argument("src" , nargs='*', type=lambda x: is_valid_file_or_dir(parser, x), help="Source files and directories")
argcomplete.autocomplete(parser)
args=parser.parse_args()
name= args.name if "name" in args else ""
dest= args.dest if "dest" in args else []
src=args.src if "src" in args else []
envs={}
                
with open(file, 'r') as outfile:
    envs = json.load(outfile)

def listAll():
    for name, value in envs.items():
        print(name + ":")
        print("     dest:     '" + str(value['dest']) + "'")
        print("     src:")
        for src in value['src']:
            print("          '" + str(src) + "'")

if args.command == 'help':
    print("Positional argument 'modify' to configure")
    print("Positional argument 'run' to run config by name")
    parser.print_help()
    raise SystemExit

if args.command == 'run':
    if envs == {}:
        print("Add an configuration with modify -a first to copy all it's files to destination")
        raise SystemExit
    elif not 'name' in args:
        print("Give up an configuration to copy objects between")
        raise SystemExit
    else:
        for key in name:
            if not key in envs:
                print("Look again. " + key + " isn't in there.")
                listAll()
                raise SystemExit
        for i in name:
            i=str(i)
            dest = envs[i]['dest']
            src = envs[i]['src']
            copy_to(dest, src)
elif args.command == 'add':
    print(dest)
    print(src)
    if not 'name' in args:
        print("Give up an configuration to copy objects between")
        raise SystemExit
    elif name in envs:
        print("Look again. " + name + " is/are already used as names.")
        listAll()
        raise SystemExit
    elif dest == []:
        print("Give up an destination folder to copy objects between")
        raise SystemExit    
    elif src == []:
        print("Give up a list of source files and/or folder to copy objects between")
        raise SystemExit
    elif str(dest) in src:
        print('Destination and source can"t be one and the same')
        raise SystemExit
    else:
        with open(file, 'w') as outfile: 
            envs[str(name)] = { 'dest' : str(dest), 'src' : [*src] }
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
                print("Look again. " + key + " isn't in there.")
                listAll()
                raise SystemExit
        for key in name:
            envs.pop(key)
            if 'list' in args:
                print(str(key) + ' removed from confs')
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
        print("Look again. " + name + " isn't in there.")
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
        print("Look again. " + name + " isn't in there.")
        raise SystemExit
    else:
        with open(file, 'w') as outfile:
            envs[name]['dest'] = str(dest)
            print(envs)
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
        print("Look again. " + name + " isn't in there.")
        raise SystemExit
    else:
        with open(file, 'w') as outfile:
            envs[name].update({ "src" : [*src] })
            json.dump(envs, outfile)
        print('Reset source of '+ str(name) + ' to', src)

if not args.command == "list" and not 'list' in args:
    parser.print_help()
else: 
    if not "name" in args or args.name == None:
        listAll()
    else:
        for key, value in envs.items():
            if name == key:
                print(key + ":")
                print("     dest:     '" + str(value['dest']) + "'")
                print("         src:\n")
                for src in value['src']:
                    print("        '" + str(src) + "'")
