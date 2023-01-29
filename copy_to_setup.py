import os
import json
import shutil
import argparse
from pathlib import Path
file=Path("/home/burp/Applications/copy_to_setup.json")

def is_valid_file_or_dir(parser, arg):
    if os.path.isdir(arg):
        return arg
    elif os.path.isfile(arg):
        return arg             #open(arg, 'r')  # return an open file handle 
    elif os.path.exists(os.path.join(os.getcwd(), arg)):
        return os.path.join(os.getcwd(), arg)
    else:
        print("The file/directory %s does not exist!" % arg)
        raise SystemExit

def copy_to(dest, src):

    exist_dest = ""
    for element in src:

        if os.path.isfile(element):
            exist_dest=os.path.join(dest, os.path.basename(element))
            if os.path.isfile(exist_dest):
                shutil.copy2(element, exist_dest)
            else:
                shutil.copy2(element, dest)
            print("Copied " + str(exist_dest))

        elif os.path.isdir(element):
            exist_dest=os.path.join(dest, os.path.basename(element))
            shutil.copytree(element, exist_dest, dirs_exist_ok=True)
            print("Copied " + str(exist_dest) + " and all it's content")

def get_src(src):
    return list(str(e) for e in src)

parser = argparse.ArgumentParser(description="Setup environments to copy files and directories to",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
subparser = parser.add_subparsers(dest='command')
run = subparser.add_parser('run')
modify = subparser.add_parser('modify')
group = modify.add_mutually_exclusive_group()
parser.add_argument("-l", "--list", action='store_true', required=False, help="Don't list environments")

run.add_argument("name" , nargs='+', type=str ,help="Environment name", metavar="Environment Name")

modify.add_argument("name" , type=str ,help="Environment name for modifications", metavar="Environment Name")
modify.add_argument("dest" , nargs="?", type=lambda x: is_valid_file_or_dir(parser, x), help="Destination folder")
modify.add_argument("src" , nargs='*', type=lambda x: is_valid_file_or_dir(parser, x), help="Source files and directories")
modify.add_argument("-l", "--list", action='store_true', required=False, help="List environments")
group.add_argument("-a", "--add", action='store_true', required=False, help="Add environment")
group.add_argument("-d", "--delete", action='store_true', required=False, help="Delete environment")
group.add_argument("-r_d", "--remap_destination", action='store_true', required=False, help="Remap environment destination")
group.add_argument("-a_s", "--append_source", action='store_true', required=False, help="Append to environment source")
group.add_argument("-r_s", "--remap_source", action='store_true', required=False, help="Remap environment source")
args=parser.parse_args()

envs={}
if not os.path.exists(file):
    with open(file, "w") as outfile:
        json.dump({}, outfile)
                
with open(file, 'r') as outfile:
    envs = json.load(outfile)

if args.list:
    print(envs)

if args.command == None:
    parser.print_help()
    print("Positional argument 'modify' to configure")
    print("Positional argument 'run' to run config by name")
    raise SystemExit

name=args.name
dest= args.dest if args.command == 'modify' else []
src=args.src if args.command == 'modify' else []


if args.command == 'run':
    if envs == {}:
        print("Add an environment with modify -a first to copy all it's files to destination")
        raise SystemExit
    else:
        for i in name:
            i=str(i)
            dest = envs[i]['dest']
            src = envs[i]['src']
            copy_to(dest, src)

elif args.command == 'modify':

    if args.add:

        if not name:
            print("Give up an environment to copy objects between")
            raise SystemExit
        
        elif not dest:
            print("Give up an destination folder to copy objects between")
            raise SystemExit
        
        elif not src:
            print("Give up a list of source files and/or folder to copy objects between")
            raise SystemExit

        elif name in envs:
            print("Try a different name. " + name + " is already taken.")
            raise SystemExit
        else:
            with open(file, 'w') as outfile: 
                envs[str(name)] = { 'dest' : str(dest), 'src' : get_src(src) }
                json.dump(envs, outfile)

    elif args.delete:
            
        if not name in envs:
            print("Look again. " + name + " isn't in there.")
            raise SystemExit
        elif envs == {} or os.stat(file).st_size == 0:
            print("Add an environment with -a, --add first to copy all it's files to destination")
            raise SystemExit

        else:
            with open(file, 'w') as outfile:
                envs.pop(name)
                json.dump(envs, outfile)

    elif args.remap_destination:
        
        if not name:
            print("Give up an environment to copy objects between")
            raise SystemExit
        elif not dest:
            print("Give up an destination folder to copy objects between")
            raise SystemExit
        elif not name in envs:
            print("Look again. " + name + " isn't in there.")
            raise SystemExit
        elif envs == {} or os.stat(file).st_size == 0:
            print("Add an environment with -a, --add first to copy all it's files to destination")
            raise SystemExit
        else:
            with open(file, 'w') as outfile:
                envs[name].update({ "dest" : dest})
                json.dump(envs, outfile)

    elif args.remap_source:
        src = [dest] + src
        if not name:
            print("Give up an environment to copy objects between")
            raise SystemExit
        elif not src:
            print("Give up a new set of source files and folders to copy objects between")
            raise SystemExit
        elif not name in envs:
            print("Look again. " + name + " isn't in there.")
            raise SystemExit
        elif envs == {} or os.stat(file).st_size == 0:
            print("Add an environment with -a, --add first to copy all it's files to destination")
            raise SystemExit
        else:
            with open(file, 'w') as outfile:
                envs[name].update({ "src" : get_src(src) })
                json.dump(envs, outfile)

    elif args.append_source:
        src = [dest] + src
        if not name:
            print("Give up an environment to copy objects between")
            raise SystemExit
        elif not src:
            print("Give up a new set of source files and folders to copy objects between")
            raise SystemExit
        elif not name in envs:
            print("Look again. " + name + " isn't in there.")
            raise SystemExit
        elif envs == {} or os.stat(file).st_size == 0:
            print("Add an environment with -a, --add first to copy all it's files to destination")
            raise SystemExit
        else:
            with open(file, 'w') as outfile:
                src = get_src(src)
                for i in src:
                    envs[name]["src"].append(i)
                json.dump(envs, outfile)
