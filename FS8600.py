#!/bin/env python26

import re
import sys
import paramiko
import logging
from collections import defaultdict

class FS8600:

    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password
	self.ssh = paramiko.SSHClient() 
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ansi_escape = re.compile(r'\x1b[^m]*m')
        self.logger = logging.getLogger("FS8600")
        logging.basicConfig()

    def __getattr__(self,key):
        # We use getattr to dynamically build the function based on what "function" was
        # called.
        def dyn_function(*args, **kwargs):
            return self._make_nas_call(key,args,kwargs)
        return dyn_function

    def _connect(self):
        # I'd like to do pooling here, only reconnect if there isn't already a connection
	self.ssh.connect(self.ip,username=self.user,password=self.password)        
        self.logger.debug("Connection Successful to: %s" % (self.ip,))

    def _make_nas_call(self, key, args, kwargs):
        # Perform a function all to the NAS
        nas_function = key.replace('__','-')
        nas_function = nas_function.replace('_',' ')
        nas_function = nas_function + " " + " ".join(args) 
        for arg in kwargs.keys():
            nas_function = nas_function + " -" + arg + " " + kwargs[arg]
        self.logger.debug("Calling Function: %s" % (nas_function,))
        self._connect()

        # Execute command with parameters, we always answer yes if asked.... be cautious
        (stdin, stdout, stderr) = self.ssh.exec_command(nas_function)
        stdin.write("Yes\n")
        stdin.flush()

        # Cleanup the stdout and send it back.  Note stderr doesn't appear to be used
        cmd_output = self.ansi_escape.sub('', stdout.read())
        return cmd_output
    
    def raw_nas_call(self, cmd):
        # A raw nas command, literally passed on to the nas and literal output returned
        self.logger.debug("Raw Command Sent To Nas: %s" % (cmd,))
        self._connect()
        (stdin, stdout, stderr) = self.ssh.exec_command(cmd)
        cmd_output = self.ansi_escape.sub('', stdout.read())
        return cmd_output

    def get_cluster_name(self):
        # Simple grab of the cluster
        output = self.system_general_cluster__name_view()
        res = re.findall('name  =  (.*)',output)
        self.logger.debug(res)
        return res[0]

    def create_volume(self,volume_name,volume_size,volume_unit,sec_style="NTFS"):
        return self.access_nas__volumes_add(volume_name,str(volume_size),volume_unit,security_style=sec_style)
        
    def delete_volume(self,volume_name):
        return self.access_nas__volumes_delete(volume_name)

    def resize_volume(self,volume_name,new_volume_size,size_u):
        return self.access_nas__volumes_edit(volume_name,size=str(new_volume_size),size_unit=size_u)

    def view_volume(self,volume_name):
        return self.access_nas__volumes_view(volume_name)
 
    def rename_volume(self,volume_name,new_volume_name):
        return self.access_nas__volumes_edit(volume_name,new_name=new_volume_name)

    def list_volumes(self): 
        return self.access_nas__volumes_list()

    def create_cifs_share(self,share_name,volume_name,volume_path=None,desc=None):
        if volume_path == None:
            volume_path='/'

        if desc:
            desc = "\""+desc+"\""   # We have to wrap the description in double quotes since it may
            return self.access_cifs__shares_add(share_name,volume_name,volume_path,description=desc)
        else:
            return self.access_cifs__shares_add(share_name,volume_name,volume_path)

    def delete_cifs_share(self,share_name):
        return self.access_cifs__shares_delete(share_name)

    def list_shares(self):
        share_dict = defaultdict(dict)
        share_list = self.access_cifs__shares_list().split('\n')
        for share in share_list[3:]:
            if '|' in share:
                share_data  = [x.strip() for x in share.split('|')]
                self.logger.debug(share_data)
                share_dict[share_data[0]]['volume_name'] = share_data[1]
                share_dict[share_data[0]]['volume_path'] = share_data[2]
                share_dict[share_data[0]]['share_comment'] = share_data[3]

        return share_dict

    def get_share_info(self,share_name):
        shares = self.list_shares()
        return shares[share_name]
 
    def list_volumes(self):
        vol_dict = defaultdict(dict)
        vol_list = self.access_nas__volumes_list().split('\n')
        for vol in vol_list[3:]:
            if '|' in vol: 
                vol_data = [x.strip() for x in vol.split('|')]
                self.logger.debug(vol_data)
                vol_dict[vol_data[0]]['volume_name']  = vol_data[0]
                vol_dict[vol_data[0]]['volume_allocated'] = vol_data[1]
                vol_dict[vol_data[0]]['volume_used'] = vol_data[2]
                vol_dict[vol_data[0]]['volume_free'] = vol_data[3]
                vol_dict[vol_data[0]]['volume_snap'] = vol_data[4]

        return vol_dict

    def get_volume_info(self,volume_name):
        volumes = self.list_volumes()
        return volumes[volume_name]

    def get_volume_shares(self,volume_name):
        share_list = []
        shares = self.list_shares()
        for share, share_info in shares.iteritems():
            if share_info['volume_name'] == volume_name:
                share_list.append(share)

        return share_list
   
