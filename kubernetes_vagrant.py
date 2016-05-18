"""ShutIt module. See http://shutit.tk
"""

from shutit_module import ShutItModule


class kubernetes_vagrant(ShutItModule):


	def build(self, shutit):
		# Some useful API calls for reference see shutit's docs for more info and options:
		# shutit.send(send) - send a command
		# shutit.multisend(send,send_dict) - send a command, dict contains {expect1:response1,expect2:response2,...}
		# shutit.log(msg) - send a message to the log
		# shutit.run_script(script) - run the passed-in string as a script
		# shutit.send_file(path, contents) - send file to path on target with given contents as a string
		# shutit.send_host_file(path, hostfilepath) - send file from host machine to path on the target
		# shutit.send_host_dir(path, hostfilepath) - send directory and contents to path on the target
		# shutit.host_file_exists(filename, directory=False) - returns True if file exists on host
		# shutit.file_exists(filename, directory=False) - returns True if file exists on target
		# shutit.add_to_bashrc(line) - add a line to bashrc
		# shutit.get_url(filename, locations) - get a file via url from locations specified in a list
		# shutit.user_exists(user) - returns True if the user exists on the target
		# shutit.package_installed(package) - returns True if the package exists on the target
		# shutit.pause_point(msg='') - give control of the terminal to the user
		# shutit.step_through(msg='') - give control to the user and allow them to step through commands
		# shutit.send_and_get_output(send) - returns the output of the sent command
		# shutit.send_and_match_output(self, send, matches, child=None, retry=3, strip=True):
		# shutit.send_and_match_output(send, matches) - returns True if any lines in output match any of 
		#                                               the regexp strings in the matches list
		# shutit.install(package) - install a package
		# shutit.remove(package) - remove a package
		# shutit.login(user='root', command='su -') - log user in with given command, and set up prompt and expects
		# shutit.logout() - clean up from a login
		# shutit.set_password(password, user='') - set password for a given user on target
		# shutit.get_config(module_id,option,default=None) - get configuration value
		# shutit.get_ip_address() - returns the ip address of the target
		# shutit.add_line_to_file(line, filename) - add line (or lines in an array) to the filename
		vagrant_dir        = shutit.cfg[self.module_id]['vagrant_dir']
		kubernetes_version = shutit.cfg[self.module_id]['kubernetes_version']
		num_minions        = shutit.cfg[self.module_id]['num_minions']
		clean_vbox         = shutit.cfg[self.module_id]['clean_vbox']
		master_ip          = shutit.cfg[self.module_id]['master_ip']
		minion_ip_base     = shutit.cfg[self.module_id]['minion_ip_base']
		shutit.send('mkdir -p ' + vagrant_dir)
		shutit.send('cd ' + vagrant_dir)
		if clean_vbox:
			shutit.send("VBoxManage list runningvms | awk '{print $1}'  | xargs -IXXX VBoxManage controlvm XXX poweroff",check_exit=False)
			shutit.send("VBoxManage list vms | awk '{print $1}'  | xargs -IXXX VBoxManage unregistervm --delete XXX",check_exit=False)
			shutit.send('''vagrant global-status | grep virtualbox | awk '{print $1}' | xargs vagrant destroy -f''',check_exit=False)
			if shutit.file_exists('kubernetes',directory=True):
				shutit.send('rm -rf kubernetes')
		if not shutit.file_exists('kubernetes',directory=True):
			shutit.send('wget -qO- https://github.com/GoogleCloudPlatform/kubernetes/releases/download/' + kubernetes_version + '/kubernetes.tar.gz | tar -zxf -')
		shutit.send('cd kubernetes')
		shutit.send('export KUBERNETES_PROVIDER=vagrant')
		shutit.send('export NUM_MINIONS=' + num_minions)
		shutit.send('export MASTER_IP=' + master_ip)
		shutit.send('export MINION_IP_BASE=' + minion_ip_base)
		if shutit.send_and_match_output('vagrant status',['.*poweroff.*','.*not created.*','.*aborted.*']):
			shutit.send('./cluster/kube-up.sh',timeout=99999)
		shutit.pause_point('vagrant status, vagrant ssh if all ok')
		return True

	def get_config(self, shutit):
		shutit.get_config(self.module_id, 'vagrant_dir', '/space/vagrant')
		shutit.get_config(self.module_id, 'kubernetes_version', 'v0.16.2')
		shutit.get_config(self.module_id, 'num_minions', '2')
		shutit.get_config(self.module_id, 'clean_vbox', boolean=True, hint='Whether to wipe out all virtualbox and vagrant boxes')
		shutit.get_config(self.module_id, 'master_ip','10.245.1.2')
		shutit.get_config(self.module_id, 'minion_ip_base','10.245.1.3')
		return True


def module():
	return kubernetes_vagrant(
		'shutit.tk.kubernetes_vagrant.kubernetes_vagrant', 782914092.00,
		description='',
		maintainer='',
		delivery_methods=['bash'],
		depends=['shutit.tk.setup','tk.shutit.vagrant.vagrant.vagrant','shutit-library.virtualbox.virtualbox.virtualbox']
	)

