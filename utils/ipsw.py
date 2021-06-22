from utils.api import API
import hashlib
import json
import os
import shutil
import sys
import zipfile


class IPSW(object):
	def __init__(self, identifier, ipsw):
		self.device = identifier
		self.ipsw = ipsw

	def create_ipsw(self, path, output, update, bootloader):
		os.makedirs('IPSW', exist_ok=True)

		info = {
			'update_support': update,
			'bootloader': bootloader
		}

		with open(f'{path}/.Inferius', 'w') as f:
			json.dump(info, f)

		try:
			shutil.make_archive(f'IPSW/{output}', 'zip', path)
		except:
			sys.exit('[ERROR] Failed to create custom IPSW. Exiting.')

		os.rename(f'IPSWs/{output}.zip', '/'.join(('IPSWs', output)))
		return '/'.join(('IPSWs', output))

	def extract_file(self, file, path):
		try:
			with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
				fbuf = ipsw.read(file)
			
			with open('/'.join((path, file)), 'wb') as f:
				f.write(fbuf)
		except:
			sys.exit(f"[ERROR] Failed to extract '{file}' from IPSW. Exiting.")

	def extract_ipsw(self, path):
		with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
			try:
				ipsw.extractall(path)
			except:
				sys.exit(f"[ERROR] Failed to extract '{self.ipsw}'. Exiting.")

	def verify_ipsw(self, ipsw_sha1):
		if not os.path.isfile(self.ipsw):
			sys.exit(f"[ERROR] '{self.ipsw}' does not exist. Exiting.")

		if not zipfile.is_zipfile(self.ipsw):
			sys.exit(f"[ERROR] '{self.ipsw}' is not a valid IPSW. Exiting.")

		with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
			if '.Inferius' in ipsw.namelist():
				sys.exit(f"[ERROR] '{self.ipsw}' is not a stock IPSW. Exiting.")

		sha1 = hashlib.sha1()
		with open(self.ipsw, 'rb') as ipsw:
			fbuf = ipsw.read(8192)
			while len(fbuf) != 0:
				sha1.update(fbuf)
				fbuf = ipsw.read(8192)

		if ipsw_sha1 != sha1.hexdigest():
			sys.exit(f"[ERROR] '{self.ipsw}' is not a valid IPSW. Exiting.")

	def verify_custom_ipsw(self, update):
		if not os.path.isfile(self.ipsw):
			sys.exit(f"[ERROR] '{self.ipsw}' does not exist. Exiting.")

		if not zipfile.is_zipfile(self.ipsw):
			sys.exit(f"[ERROR] '{self.ipsw}' is not a valid IPSW. Exiting.")

		with zipfile.ZipFile(self.ipsw, 'r') as ipsw:
			if '.Inferius' not in ipsw.namelist():
				sys.exit(f"[ERROR] '{self.ipsw}' is not a custom IPSW. Exiting.")

			info = json.loads(ipsw.read('.Inferius'))

		if (info['update_support'] == False) and (update == True):
			sys.exit('[ERROR] This IPSW does not have support for update restores. Exiting.')

		api = API(self.device)
		if api.is_signed(info['bootloader']) == False:
			sys.exit('[ERROR] This IPSW is too old to be used with Inferius. Create a new custom IPSW. Exiting.')