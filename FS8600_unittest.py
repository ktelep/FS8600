#!/bin/env python26

import sys
import unittest
import logging
from FS8600 import FS8600


class TestConnection(unittest.TestCase):
  
    def testConnection(self):
        test = FS8600(test_ip,test_user,test_pass)
        output = test.system_general_info_cluster__id_view()
        self.assertTrue('Cluster ID' in output)

class TestVolumeFunctions(unittest.TestCase):
    def setUp(self):
        self.test = FS8600(test_ip,test_user,test_pass)
        self.test.create_volume("Test_Volume",1,"GB")

    def testVolumeList(self):
        output = self.test.list_volumes()
        expected =  {'volume_allocated': '1,024.00', 
                     'volume_used': '0.01', 
                     'volume_free': '1,023.99', 
                     'volume_snap': '0.00', 
                     'volume_name': 'Test_Volume'}

        self.assertTrue(output['Test_Volume'] == expected)

    def tearDown(self):
        self.test.delete_volume("Test_Volume")

class TestGetClusterInfo(unittest.TestCase):
    def setUp(self):
        self.test = FS8600(test_ip,test_user,test_pass)
        
    def testGetClusterName(self):
        output = self.test.get_cluster_name()
        self.assertTrue(type(output) == str)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "Missing arguments"
        print "Please provide ip, username, password for testing"
        sys.exit() 
    
    test_ip = sys.argv[1]
    test_user = sys.argv[2]
    test_pass = sys.argv[3]
   
    del sys.argv[1:]
    logging.getLogger("FS8600").setLevel(logging.DEBUG)
    unittest.main()
