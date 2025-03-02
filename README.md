## Copy-to

A little python script I use in conjunction with git so you can easily copy (config) files located outside of a git repository to one (or to wherever you want to). Useful for configuration files.  

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
python -m pip install --user pipx
python -m pipx ensurepath
python -m pipx install copy-to
```  

Then, restart you shell.  

For autocompletion on Windows Powershell v5.1, first run (to enable run files as scripts, this should be the default if it has not been changed yet ..):  
```
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted
```  

Then, for Powershell autocompletion in general, run:  
```
mkdir -p $HOME\Documents\WindowsPowerShell\Modules
python ((where.exe register-python-argcomplete).Split([Environment]::NewLine) | Select -First 1) --shell powershell copy-to.exe > $HOME\Documents\WindowsPowerShell\Modules\copy-to.psm1
```

Then check your Profile folder using `echo $PSHOME`, and (using for example notepad) open a file in that path called `Profile.ps1`. This requires administrator access.   
For powershell v5.1, this is `C:\Windows\System32\WindowsPowerShell\v1.0\Profile.ps1`. Open notepad as an administrator and create the file if it doesn't exist yet.  
Then in that file, put this:  
```
Import-Module $HOME\Documents\WindowsPowerShell\Modules/copy-to.psm1
```  

For Linux / MacOs, try running it once if autocompletions aren't working  

You can also run:  
```
sudo activate-global-python-argcomplete
```  

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

Run and run-reverse can also run without arguments when git is installed and present in a git local repository that has configured copy-to. This is so it can be hooked to a git macro more easily, f.ex. with an alias/function  

Windows Powershell: (put in your profile - `notepad $PSHOME\Profile.ps1`)  
```
function git-status { copy-to.exe run && git.exe status }
```  

Linux bash (put in your .bashrc - `nano ~/.bashrc`):  
```
alias git-status="copy-to run && git status"
```  

or for those who use it, on startup of [Lazygit](https://github.com/jesseduffield/lazygit):  

Windows Powershell:  
```
function lazygit { copy-to.exe run && lazygit.exe }
```  

Linux bash:  
```
alias lazygit="copy-to run && lazygit"
```  

Local git config:  
```
[copy-to]  
    run = myname1 myname2  
    file = myconf.json
```  
This can be setup with `copy-to add myname` and `copy-to set-git myname` or  
`copy-to add myname` and `copy-to run`/`copy-to run-reverse` after wich a prompt will ask if you want to set it up with git. Both `copy-to run` and `copy-to run-reverse` will run using the same `run` arguments possibly given in a local gitconfig. A custom conf.json can be also be setup and will always take precedence over other file options when set up.  


## Quick setup for firefox dotfiles  

This will setup a git repository for your firefox configuration files using copy-to on Windows.  

### Install git, initialize git repository and setup copy-to

We start with installing git if it's not installed already.  

```
winget install Git.Git
```  

(Optional: get latest version of PowerShell)  

```
winget install Microsoft.PowerShell
```  

![Setup git](https://raw.githubusercontent.com/excited-bore/copy-to/main/images/Setup_git.gif "Setup git")  

This guide shows you how to use copy-to to and git to backup (and restore) your firefox profile following the [officical mozilla docs](https://support.mozilla.org/en-US/kb/back-and-restore-information-firefox-profiles)

First we create a local git repository and cd into it.  

We can make this repostitory for firefox only `firefox`, or make it for all our dotfiles `dotfiles`  

```
git init dotfiles  
cd dotfiles
```  

Now, we could just start and copy-to will put all your configurations in the default location (`$HOME/.config/copy-to/confs.json`), or we could set it up so our configuration file is also in our git repository.  

Since we're in a git repostitory, we could accomplish this using `copy-to set-git file confs.json` and copy-to will make the config file `confs.json` in our current folder while also using this specific file to read files and folders from when we `cd` into this git repository. You can see this whether or not this is done by running `git config -e`.   

We could change the confs.json file from the default path by setting the environment variable `COPY_TO` or by using the `--file` parameter.  

Then we add everything in the firefox 'profile' folder programmatically using copy-to:  
    - First we open the profile folder by opening firefox-> Help-> More Troubleshooting Information-> Open 'Profile' Folder and copy the folder path.  
    - Then we run `copy-to add firefox firefox ` to add a the target folder but without the source files. This will also create a subfolder `firefox` in our git repository wich will be our destination.  

We can handpick what parts of our firefox config we want to backup, for example to keep only our bookmarks, we could store <em>places.sqlite</em>, <em>bookmarksbackups/</em> and <em>favicons.sqlite</em> (See [this](https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data)) from  
`"C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\random_release\"`.  
Don't forget to *close* firefox <em>first</em> and change this folder to *your* <em>profile folder</em> and/or <em>username</em>.  

```
copy-to add-source firefox "C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\random_release\places.sqlite" "C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\random_release\bookmarksbackups/" "C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\random_release\favicons.sqlite"
```  

Folders added to source will automatically copy recursively.  

On the other hand, we could also iterate over each file in our profile folder (dont forget to replace the path with the path you copied earlier):  

```
Get-ChildItem "C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\random_release" -Filter * |  
ForEach-Object {copy-to add-source firefox "C:\Users\username\AppData\Roaming\Mozilla\Firefox\Profiles\random_release\$_" }
```  

For Linux (and presumably MacOs), this would be:
```
copy-to add-source firefox /home/username/.mozilla/firefox/random_release/*
```  
If you get an error along the lines of `The file/directory /home/username/.mozilla/firefox/9mw2xroo.default-release/lock does not exist!`, try removing the file and running the command again.  

Then we run `copy-to run firefox` to copy the files to the target folder.  

Now that everything we want related to firefox is inside our local git repository, we can start setting up our remote repository.  

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
    - Back inside a regular powershell, we add our private key using  
    `ssh-add C:\Users\username\.ssh\id_ed25519`.  
    - Then we add the ssh key to our github account and test our connecting using `ssh -T git@github.com`.  

### Setup remote repository

![Setup git_remote](https://raw.githubusercontent.com/excited-bore/copy-to/main/images/Setup_git_remote.gif "Setup git remote")  

First we make sure we've made our first commit adding every new change:  

```
git add --all  
git commit -m "Initial commit"
```  

Next we got to our github account and create a new private repository.  
After that, we configure the remote repository using `git remote add origin git@github.com/username/dotfiles.git`.  
Then if everything went well, we can just push to our remote repository using `git push -u origin main`.  

We can keep this up-to-date regularly by running `copy-to run firefox`, `cd C:/Users/username/dotfiles` and `git push` whenever we make changes.  

Now, if we ever need to freshly install firefox, we have a backup ready to go that we can use by running `copy-to run-reverse`.  
Or, if we ever decide to use a different operating system, we clone our repository after installing firefox and relocate the firefox profile folder.  
If we made a private repository we use:
```
git clone git@github.com:<username>/dotfiles  
```  
because otherwise we run into authentication problems.  

Then we run:  
```
copy-to set-git file confs.json
copy-to reset-destination firefox "new-profile-folder"  
copy-to run-reverse firefox
```  

We have reconfigure our file because git doesn't upload the local .git/ files.  
As an alternative for backing up application configurationfiles accross operating systems, you could add multiple configuration names for each os. (`copy-to add firefox-windows .. ` / `copy-to add firefox-linux ..`)  

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
You can also use 'all' to list/run all known configurations  


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

Set the path of source files/folders by index with  
```
copy-to set-source-path myname1 /home/user/ 1 2-4  
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
