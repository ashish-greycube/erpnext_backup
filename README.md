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

<hr>

#### Contact Us  

<a href="https://greycube.in"><img src="https://greycube.in/files/greycube_logo09eade.jpg" width="250" height="auto"></a> <br>
1<sup>st</sup> ERPNext [Certified Partner](https://frappe.io/api/method/frappe.utils.print_format.download_pdf?doctype=Certification&name=PARTCRTF00002&format=Partner%20Certificate&no_letterhead=0&letterhead=Blank&settings=%7B%7D&_lang=en#toolbar=0)
<sub> <img src="https://greycube.in/files/certificate.svg" width="20" height="20"> </sub>
& winner of the [Best Partner Award](https://frappe.io/partners/india/greycube-technologies) <sub> <img src="https://greycube.in/files/award.svg" width="25" height="25"> </sub>

<h5>
<sub><img src="https://greycube.in/files/link.svg" width="20" height="auto"> </sub> <a href="https://greycube.in"> greycube.in</a><br>
<sub><img src="https://greycube.in/files/8665305_envelope_email_icon.svg" width="20" height="18"> </sub> <a href="mailto:sales@greycube.in"> 
 sales@greycube.in</a><br>
<sub><img src="https://greycube.in/files/linkedin1.svg" width="20" height="18"> </sub> <a href="https://www.linkedin.com/company/greycube-technologies"> LinkedIn</a><br>
<sub><img src="https://greycube.in/files/blog.svg" width="20" height="18"> </sub><a href="https://greycube.in/blog"> Blogs</a> </h5>
