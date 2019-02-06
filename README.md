## ERPNext Backup

App for auto backup of ERPNext files/database to remote server using rclone

#### Pre requisite
Install rclone on source computer whose backup is to be taken \
Following are steps for ubuntu \

    sudo apt-get update \
    sudo apt-get install zip \
    curl https://rclone.org/install.sh | sudo bash \
Configure rclone for SFTP upload \
It should be run with frappe user \
    https://rclone.org/sftp/ \
    note the name of remote config  \
        n) New remote \
        s) Set configuration password \
        q) Quit config \
        n/s/q> n \
        name> remote \
rclone mkdir remote:path/to/directory \
rclone mkdir greycubelive:backup_from_sitename \
Install App \
    Update Backup Settings--> RClone Remote Name--> with name noted above \
     Update Backup Settings--> RClone Remote Directory Path--> with directory noted above 
#### License

MIT

