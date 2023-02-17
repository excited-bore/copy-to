# copy-to

A little python script i use in conjunction with git so you can easily copy config files from anywhere in an instant to do whatever with!

Depends on [argcomplete](https://pypi.org/project/argcomplete/)

Install it with:
`pip3 install argcomplete`

List configured paths and files with `copy-to list myname` 
or just `copy-to list`

Add a config with `copy-to add myname destination_folder sourcefile1 (sourcefolder1 sourcefile2 sourcefile3 sourcefolder2/*) ...`

Copy the files by running `copy-to run myname1 (myname2)`

Delete conf name with `copy-to delete myname1 (myname2)`

Add sources with `copy-to add_source myname folder1 file1`

Reset source and destination folders
`copy-to reset_source myname`
and
`copy-to reset_destination myname`

Groups are based on names. For copying to multiple directories in one go.
Takes up 'group' as config namespace.

Add groupname
`copy-to add_group mygroupname myname1 myname2`

Delete groupname
`copy-to delete_group mygroupname`

Configuration files at `~/.config/copy-to/confs.json` for Linux 

Don't forget to add to path in `~/.bashrc` with:

`export PATH=$PATH:$(python -m site --user-site)/copy-to/copy-to`
if installed in default python package site

Windows and mac not tested
