## Copy-to

A little python script I use in conjunction with git so you can easily copy (config) files located outside of a git repository to one (or to wherever you want to). Useful for dotfiles and such.  

Available on with pip/pipx: https://pypi.org/project/copy-to/  

Depends on [argcomplete](https://pypi.org/project/argcomplete/), [GitPython](https://pypi.org/project/GitPython/), [prompt_toolkit](https://pypi.org/project/prompt_toolkit/)  

## Install it with:  

Linux:  
```
sudo apt install pipx / sudo pacman -S python-pipx
pipx install copy-to
```  
Windows Powershell:  
```
winget install python3
python3 -m pip install --user pipx
python3 -m pipx ensurepath
python3 -m pipx install copy-to
```  

On linux, try running it once if autocompletions aren't working

You can also run:  
```
sudo activate-global-python-argcomplete
```  

Sadly I have been unable to figure out as of now how to setup autocompletions on Windows.  

## How to use it:

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

When the destination is missing, a prompt will ask you if you want to create the destination folder.

Run and run-reverse can also run without arguments when present in a git repository that has configured copy-to (Excluding global gitconfig). This is so it can be hooked to a git macro more easily, f.ex. with an alias (alias git-status="git status && copy-to run") or on startup of [Lazygit](https://github.com/jesseduffield/lazygit).  
```
[copy-to]  
    run = myname1 myname2  
    file = myconf.json
```  
This can be setup with `copy-to add myname` and `copy-to set-git myname` or  
`copy-to add myname` and `copy-to run`/`copy-to run-reverse` after wich a prompt will ask if you want to set it up with git. Both `copy-to run` and `copy-to run-reverse` will run using the same `run` arguments. A custom conf.json can be also be setup and will always take precedence over other file options when set up.  


## Quick setup for dotfiles  

This will setup a git repository for your firefox configuration files using copy-to on Windows.  

### Initialize git repository and setup copy-to

![Setup git](https://raw.githubusercontent.com/excited-bore/copy-to/main/images/Setup_git.gif "Setup git")  

First we create a local git repository and cd into it.  

```
git init firefox-files  
cd firefox-files
```   

Then we add everything in the firefox 'profile' folder programmatically using copy-to:  
    - First we open the profile folder by opening firefox-> Help-> More Troubleshooting Information-> Open 'Profile' Folder and copy the folder path.  
    - Then we run `copy-to add firefox-profiles firefox ""` to add a the target folder but without the source files. This will also create a subfolder in our git repository.  
    - Then we iterate over each file in our profile folder (dont forget to replace the path with the path you copied earlier):  

```
Get-ChildItem "C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\release" -Filter * |  
ForEach-Object {copy-to add-source firefox-profiles "C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\release\$_" }
```  

Then we run `copy-to run firefox-profiles` to copy the files to the target folder.  

Now that everything related to firefox is inside our local git repository, we can start setting up our remote repository.  

### Setup ssh for github  

![Setup git_ssh](https://raw.githubusercontent.com/excited-bore/copy-to/main/images/Setup_git_ssh.gif "Setup git ssh")  

Following the instructions on [Github](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent):  
    - We create a public/private keypair using `ssh-keygen -t ed25519`. This will save our keypair inside `C:\Users\username\.ssh\id_ed25519` and `C:\Users\username\.ssh\id_ed25519.pub` respectively.  
    - Then we open up an administrator powershell and run:  

```
Get-Service -Name ssh-agent | Set-Service -StartupType Manual  
Start-Service ssh-agent
```  

to startup the ssh-agent.  
    - Back inside a regular powershell, we add our private key using `ssh-add C:\Users\username\.ssh\id_ed25519`.  
    - Then we add the ssh key to our github account and test our connecting using `ssh -T git@github.com`.  

### Setup remote repository

![Setup git_remote](https://raw.githubusercontent.com/excited-bore/copy-to/main/images/Setup_git_remote.gif "Setup git remote")  

First we make sure we've made our first commit adding every new change:  

```
git add --all  
git commit -m "Initial commit"
```  

Next we got to our github account and create a new private repository.  
After that, we configure the remote repository using `git remote add origin git@github.com/username/firefox-files.git`.  
Then if everything went well, we can just push to our remote repository using `git push -u origin main`.  

We can keep this up-to-date regularly by running `copy-to run firefox-profiles`, `cd C:/Users/username/firefox-files` and `git push` whenever we make changes.  

Now, if we ever need to freshly install firefox, we have a backup ready to go that we can use byrunning `copy-to run-reverse`.  Or, if we ever decide to use a different operating system, we copy over the copy-to confs.json (at default located at `C:/Users/username/.config/copy-to/confs.json`), clone our repository after installing firefox and relocate the firefox profile folder, then run:  

```
copy-to --file confs.json reset-destination firefox-profiles "new-profile-folder"  
copy-to --file confs.json run-reverse firefox-profiles
```  

## Other commands

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

Mac not tested
