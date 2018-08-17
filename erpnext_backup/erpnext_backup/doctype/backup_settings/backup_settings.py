# -*- coding: utf-8 -*-
# Copyright (c) 2018, GreyCube Technologies and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue
from frappe.utils import cint, split_emails, get_site_base_path, cstr, today,get_backups_path,get_datetime
from datetime import datetime, timedelta

import os
from frappe import _
#Global constants
verbose = 0
ignore_list = [".DS_Store"]

class BackupSettings(Document):
	pass

def take_backups_hourly():
	take_backups_if("Hourly")

def take_backups_daily():
	take_backups_if("Daily")

def take_backups_weekly():
	take_backups_if("Weekly")

def take_backups_if(freq):
	if cint(frappe.db.get_value("Backup Settings", None, "enable_backup")):
		upload_frequency = frappe.db.get_value("Backup Settings", None, "upload_frequency")
		if upload_frequency == freq:
			take_backup()
		elif freq == "Hourly" and upload_frequency in ["Every 6 Hours","Every 12 Hours"]:
			last_backup_date = frappe.db.get_value('Backup Settings', None, 'last_backup_date')
			upload_interval = 12
			if upload_frequency == "Every 6 Hours":
				upload_interval = 6
			elif upload_frequency == "Every 12 Hours":
				upload_interval = 12
		
			if datetime.now() - get_datetime(last_backup_date) >= timedelta(hours = upload_interval):
				take_backup()
		

@frappe.whitelist()
def take_backup():
	# "Enqueue longjob for taking backup to dropbox"
	enqueue("erpnext_backup.erpnext_backup.doctype.backup_settings.backup_settings.take_backup_to_service", queue='short', timeout=1500)
	# take_backup_to_service()
	return
	

def take_backup_to_service():
	
	did_not_upload, error_log = [], []
	try:
		did_not_upload, error_log = backup_to_service()
		if did_not_upload: raise Exception
		
		frappe.db.begin()
		frappe.db.set_value('Backup Settings', 'Backup Settings', 'last_backup_date', datetime.now())
		frappe.db.commit()

		#send_email(True, "Backup")
	except Exception:
		file_and_error = [" - ".join(f) for f in zip(did_not_upload, error_log)]
		error_message = ("\n".join(file_and_error) + "\n" + frappe.get_traceback())
		# frappe.errprint(error_message)
		send_email(False, "Backup", error_message)
		

		
	

def send_email(success, service_name, error_status=None):
	if success:
		subject = "Backup Upload Successful"
		message ="""<h3>Backup Uploaded Successfully</h3><p>Hi there, this is just to inform you
		that your backup was successfully uploaded to your %s account.</p>
		""" % service_name

	else:
		subject = "[Warning] Backup Upload Failed"
		message ="""<h3>Backup Upload Failed</h3><p>Oops, your automated backup to %s
		failed.</p>
		<p>Error message: %s</p>
		<p>Please contact your system manager for more information.</p>
		""" % (service_name, error_status)

	if not frappe.db:
		frappe.connect()
		

	recipients = split_emails(frappe.db.get_value("Backup Settings", None, "send_notifications_to"))
	frappe.sendmail(recipients=recipients, subject=subject, message=message)


def backup_to_service():
	from frappe.utils.backups import new_backup
	from frappe.utils import get_files_path
	
	# upload files to files folder
	did_not_upload = []
	error_log = []
	
	if not frappe.db:
		frappe.connect()
	
	older_than = cint(frappe.db.get_value('Backup Settings', None, 'older_than'))
	cloud_sync = cint(frappe.db.get_value('Backup Settings', None, 'cloud_sync'))

	site = frappe.db.get_value('Global Defaults', None, 'default_company')
	if cint(frappe.db.get_value("Backup Settings", None, "enable_database")):
		# upload database
		backup = new_backup(older_than,ignore_files=True)
		# filename = os.path.join(get_backups_path(), os.path.basename(backup.backup_path_db))
		if cloud_sync:
			sync_folder(site,older_than,get_backups_path(), "database",did_not_upload,error_log)

	BASE_DIR = os.path.join( get_backups_path(), '../file_backups' )

	if cint(frappe.db.get_value("Backup Settings", None, "enable_files")):
		Backup_DIR = os.path.join(BASE_DIR, "files")
		compress_files(get_files_path(), Backup_DIR)
		if cloud_sync:
			sync_folder(site,older_than,Backup_DIR, "public-files",did_not_upload,error_log)

	
	if cint(frappe.db.get_value("Backup Settings", None, "enable_private_files")):
		Backup_DIR = os.path.join(BASE_DIR, "private/files")
		compress_files(get_files_path(is_private=1), Backup_DIR)
		if cloud_sync:
			sync_folder(site,older_than,Backup_DIR, "private-files",did_not_upload,error_log)
		
	frappe.db.close()
	# frappe.connect()
	return did_not_upload, list(set(error_log))

def compress_files(file_DIR, Backup_DIR):
	if not os.path.exists(file_DIR):
		return
	
	from shutil import make_archive	
	archivename = datetime.today().strftime("%d%m%Y_%H%M%S")+'_files'
	archivepath = os.path.join(Backup_DIR,archivename)
	make_archive(archivepath,'zip',file_DIR)

	
def sync_folder(site,older_than,sourcepath, destfolder,did_not_upload,error_log):
	# destpath = "gdrive:" + destfolder + " --drive-use-trash"
	from frappe.utils import get_bench_path
	sourcepath=get_bench_path()+"/sites"+sourcepath.replace("./", "/")
	final_dest = str(site) + "/" + destfolder
	final_dest = final_dest.replace(" ", "_")
	rclone_remote_name=frappe.db.get_value('Backup Settings', None, 'rclone_remote_name')
	rclone_remote_directory=frappe.db.get_value('Backup Settings', None, 'rclone_remote_directory_path')

	# destpath = rclone_remote_name+":"+rclone_remote_directory+'/'+final_dest
	destpath = rclone_remote_name+":"+final_dest

	delete_temp_backups(older_than,sourcepath)
	cmd_string = "rclone sync " + sourcepath + " " + destpath
	print cmd_string
	# frappe.errprint(cmd_string)
	try:
		err, out = frappe.utils.execute_in_shell(cmd_string)
		if err: raise Exception
	except Exception:
		did_not_upload  = True
		error_log.append(Exception)

		
		 
def delete_temp_backups(older_than, path):
	"""
		Cleans up the backup_link_path directory by deleting files older than x hours
	"""
	file_list = os.listdir(path)
	for this_file in file_list:
		this_file_path = os.path.join(path, this_file)
		if is_file_old(this_file_path, older_than):
			os.remove(this_file_path)
			
			

def is_file_old(db_file_name, older_than=24):
		"""
			Checks if file exists and is older than specified hours
			Returns ->
			True: file does not exist or file is old
			False: file is new
		"""
		if os.path.isfile(db_file_name):
			from datetime import timedelta
			#Get timestamp of the file
			file_datetime = datetime.fromtimestamp\
						(os.stat(db_file_name).st_ctime)
			if datetime.today() - file_datetime >= timedelta(hours = older_than):
				if verbose: print "File is old"
				return True
			else:
				if verbose: print "File is recent"
				return False
		else:
			if verbose: print "File does not exist"
			return True
			
def cleanup_old_backups(site_path, files, limit):
	backup_paths = []
	for f in files:
		if f.endswith('sql.gz'):
			_path = os.path.abspath(os.path.join(site_path, f))
			backup_paths.append(_path)

	backup_paths = sorted(backup_paths, key=os.path.getctime)
	files_to_delete = len(backup_paths) - limit

	for idx in range(0, files_to_delete):
		f = os.path.basename(backup_paths[idx])
		files.remove(f)

		os.remove(backup_paths[idx])

def delete_downloadable_backups():
	path = get_site_path('private', 'backups')
	files = [x for x in os.listdir(path) if os.path.isfile(os.path.join(path, x))]
	backup_limit = get_scheduled_backup_limit()

	if len(files) > backup_limit:
		cleanup_old_backups(path, files, backup_limit)
			
if __name__=="__main__":
	backup_to_service()
