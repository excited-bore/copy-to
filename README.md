# copy_to

A little python script i use in conjunction with git so you can easily copy config files from anywhere in an instant to do whatever with!
alias this with `alias copy_to='python /path/to/copy_to_setup.py'`

List configured paths and files with `copy_to list myname` 
or just `copy_to list`

Add a config with `copy_to add myname destination_folder sourcefile1 sourcefolder2 ...`

Copy the files by running `copy_to run myname1 myname2`

Delete conf name with `copy_to delete myname1 myname2`

Add sources with `copy_to add_source myname folder1 file2`
`copy_to reset_source myname newfile1 newfolder2`
and
`copy_to reset_destination myname newfolder`

Groups are based on names. For copying to multiple directories in one go.
Takes up 'group' as config namespace.

Add groupname
`copy_to add_group mygroupname myname1 myname2`

Delete groupname
`Copy_to delete_group mygroupname`


Configuration files at `~/.copy_to_confs.json` for Linux 

Windows and mac not tested