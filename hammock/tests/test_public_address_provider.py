import unittest
import StringIO
from hammock import public_address_provider


class PublicAddressProviderTest(unittest.TestCase):
    def setUp(self):
        pass

    def test_failure_missing_answer_config_file(self):
        provider = public_address_provider.PublicAddressProvider()
        with self.assertRaises(ValueError):
            provider.get_public_ip('/etbbbbb/answer_file_not_exist.txt')

    def test_failure_missing_(self):
        output = StringIO.StringIO()

        lst = ['[general]\n',
               'gogo = 111']
        output.writelines(lst)

        output.seek(0)

        provider = public_address_provider.PublicAddressProvider()
        public_address = provider.get_public_ip(output)
        self.assertFalse(public_address)
        output.close()

    def test_from_stream_answer_file(self):

        output = StringIO.StringIO()

        lst = ['[general]\n',
               'installationtype = controller\n',
               'npmbanktype = 0\n',
               'tmpsizegb = 35\n',
               'accessgateway = 192.168.1.2\n',
               'rootpassword = rackattack\n',
               'usessdcache = True\n',
               'managementnetworkvlanrange = 1024:1024\n',
               'managementleadermac = e4:1d:2d:00:d1:20\n',
               'usematkinool = False\n',
               'accessaddress = 192.168.1.183/24\n',
               'serialdevice = ttyS0\n',
               'vlanrange = 2:4094\n',
               'dataprivatesubnet = 2.183.0.0/16\n',
               'primarystorage = rack-storage-ng\n',
               'managementprivatesubnet = 1.183.0.0/16\n',
               'clustername = StratoCluster-6267544691596133091\n',
               'accessnic = 00:1e:67:d1:e2:17\n',
               'publicgateway = 192.168.1.2\n',
               'dataleadermac = e4:1d:2d:00:d1:20\n',
               'stratocomputeunitsize = 1000000000\n',
               'storagedeviceminsizeingb = 90\n',
               'northboundaddress = 3.183.0.2/16\n',
               'logsizegb = 15\n',
               'ssddevices = /dev/sda\n',
               'primarydevice = /dev/sda\n',
               'secondarydevices = /dev/sdb,/dev/sdc\n',
               'zfscachedevice = /dev/sda\n',
               'devicestocache = /dev/sdb,/dev/sdc\n',
               'swapdev = /dev/mapper/inaugurator-runtime_swap\n',
               'controlleripaddress = 1.183.168.179\n',
               'publicinterface = br-data\n',
               'stratoappinterface = br-data:dtprv\n',
               'hostname = stratonode0.node.strato\n']

        output.writelines(lst)
        output.seek(0)

        provider = public_address_provider.PublicAddressProvider()
        public_address = provider.get_public_ip(output)
        self.assertEqual(str(public_address), '192.168.1.183')
        output.close()


if __name__ == '__main__':
    unittest.main()
