import unittest
from common.common import port_check, address_check
from common.settings_old import DEFAULT_IP_ADDRESS


class TestsPort(unittest.TestCase):
    min_port_ok, max_port_ok = 1024, 65535
    min_port_error, max_port_error = 443, 66666

    def test_port_check_min_port_ok(self):
        args = ['-p', self.min_port_ok]
        self.assertEqual(port_check(args), self.min_port_ok)

    def test_port_check_max_port_ok(self):
        args = ['-p', self.max_port_ok]
        self.assertEqual(port_check(args), self.max_port_ok)

    # def test_port_check_min_port_less(self):
    #     args = ['-p', self.min_port_error]
    #     self.assertRaises(ValueError, port_check(args))

    # def test_port_check_empty_port(self):
    #     args = ['-p']
    #     self.assertRaises(IndexError, port_check(args))


class TestsAddress(unittest.TestCase):
    address_ok = DEFAULT_IP_ADDRESS

    def test_address_check_ok(self):
        args = ['-a', self.address_ok]
        self.assertEqual(address_check(args), self.address_ok)

    # def test_address_check_empty_address(self):
    #     args = ['-a']
    #     self.assertRaises(IndexError, address_check, args)


if __name__ == '__main__':
    unittest.main()
