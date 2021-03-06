from oeqa.selftest.base import oeSelfTest
from oeqa.utils.commands import runCmd, bitbake, get_bb_var, runqemu
from oeqa.utils.decorators import testcase
import os

class TestExport(oeSelfTest):

    def test_testexport_basic(self):
        """
        Summary: Check basic testexport functionality with only ping test enabled.
        Expected: 1. testexport directory must be created.
                  2. runexported.py must run without any error/exception.
                  3. ping test must succeed.
        Product: oe-core
        Author: Mariano Lopez <mariano.lopez@intel.com>
        """

        features = 'INHERIT += "testexport"\n'
        # These aren't the actual IP addresses but testexport class needs something defined
        features += 'TEST_SERVER_IP = "192.168.7.1"\n'
        features += 'TEST_TARGET_IP = "192.168.7.1"\n'
        features += 'TEST_SUITES = "ping"\n'
        self.write_config(features)

        # Build tesexport for core-image-minimal
        bitbake('core-image-minimal')
        bitbake('-c testexport core-image-minimal')

        # Verify if TEST_EXPORT_DIR was created
        testexport_dir = get_bb_var('TEST_EXPORT_DIR', 'core-image-minimal')
        isdir = os.path.isdir(testexport_dir)
        self.assertEqual(True, isdir, 'Failed to create testexport dir: %s' % testexport_dir)

        with runqemu('core-image-minimal') as qemu:
            # Attempt to run runexported.py to perform ping test
            runexported_path = os.path.join(testexport_dir, "runexported.py")
            testdata_path = os.path.join(testexport_dir, "testdata.json")
            cmd = "%s -t %s -s %s %s" % (runexported_path, qemu.ip, qemu.server_ip, testdata_path)
            result = runCmd(cmd)
            self.assertEqual(0, result.status, 'runexported.py returned a non 0 status')

            # Verify ping test was succesful
            failure = True if 'FAIL' in result.output else False
            self.assertNotEqual(True, failure, 'ping test failed')


class TestImage(oeSelfTest):

    def test_testimage_install(self):
        """
        Summary: Check install packages functionality for testimage/testexport.
        Expected: 1. Import tests from a directory other than meta.
                  2. Check install/unistall of socat.
        Product: oe-core
        Author: Mariano Lopez <mariano.lopez@intel.com>
        """

        features = 'INHERIT += "testimage"\n'
        features += 'TEST_SUITES = "ping ssh selftest"\n'
        self.write_config(features)

        # Build core-image-sato and testimage
        bitbake('core-image-full-cmdline socat')
        bitbake('-c testimage core-image-full-cmdline')
