# coding:utf-8

import unittest
from unittest import mock

from xargproject import command


class TestCommand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch.object(command.Project, "create", mock.MagicMock(side_effect=[123]))  # noqa:E501
    def test_main(self):
        self.assertEqual(command.main(["init", "unittest"]), 123)


if __name__ == "__main__":
    unittest.main()
