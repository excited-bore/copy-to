## Copy-to

A little python script I use in conjunction with git so you can easily copy (config) files located outside of a git repository to one (or to wherever you want to).  

Depends on [argcomplete](https://pypi.org/project/argcomplete/), [GitPython](https://pypi.org/project/GitPython/), [prompt_toolkit](https://pypi.org/project/prompt_toolkit/)  

## Install it with:  

Linux:  
```
sudo apt install pipx / sudo pacman -S python-pipx
pipx install copy-to
```  
Windows:  
```
iwr -useb get.scoop.sh | iex
scoop install pipx
pipx install copy-to
```  

Try running it once if autocompletions aren't working

You can also run (on Linux):  
```
sudo activate-global-python-argcomplete
```  
for installing pythoncompletions globally.  


Add a pairset of destination folder - source files and/or directories with  
```
copy-to add myname destination_folder sourcefile1 (sourcefolder1 sourcefile2 sourcefile3 sourcefolder2/*) ...
```  

Copy the files to their destination by running  
```
copy-to run myname1 (myname2)
```  

Or copy the files back to source by running  
```
copy-to run-reverse myname1 (myname2)
```  

Run and run-reverse can run without arguments when present in a git repository that has configured copy-to (Excluding global gitconfig). This is so it can be hooked to a git macro more easily, f.ex. on startup of [Lazygit](https://github.com/jesseduffield/lazygit).  
```
[copy-to]
    run = myname1 myname2
```  
This can be setup with `copy-to add myname` and `copy-to set-git myname` or  
`copy-to add myname` and `copy-to run`/`copy-to run-reverse` after wich a prompt will ask if you want to set it up with git. Both `copy-to run` and `copy-to run-reverse` will run using the same `run` arguments  


List configured paths and files with  
```
copy-to list myname/mygroupname/all/all-no-group/groups/all-groups/names/groupnames/all-names
```  
or as a flag  
```
copy-to --list othercommand
```
'all-no-group' and 'groups' to list all regular configs and groups respectively  
'names' and 'groupnames' to list just the regular names and groupnames respectively  
You can also use 'all' to list/run all known configurartions  


Delete set of dest/src by name with  
```
copy-to delete myname1 (myname2)
```  

Add sources with  
```
copy-to add-source myname folder1 file1
```  

Delete source by index with  
```
copy-to delete-source myname 1 4 7
```  

Reset source and destination folders  
```
copy-to reset-source myname
copy-to reset-destination myname newDest
```  

Groups are based on names. For copying to multiple directories in one go.  
Groupnames 'group'/'all' cannot be used.  

Add groupname  
```
copy-to add-group mygroupname myname1 myname2
```  

Delete groupname
```
copy-to delete-group mygroupname
```  

Add name to group  
```
copy-to add-to-group mygroupname myname1 myname2
```  

Delete name from group  
```
copy-to delete-from-group mygroupname myname1 myname2
```  

At default the configuration file is located at `~/.config/copy-to/confs.json`, but you can set a environment variable `COPY_TO` to change this, or pass a `-f, --file` flag.  

Windows and mac not tested
