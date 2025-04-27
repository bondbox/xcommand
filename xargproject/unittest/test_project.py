# coding:utf-8

import unittest
from unittest import mock

from xargproject import project


class TestProject(unittest.TestCase):

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

    def test_init(self):
        self.assertRaises(ValueError, project.Project, "unit test", "GPLv2")

    @mock.patch.object(project, "open")
    def test_write(self, mock_open: mock.Mock):
        with mock.mock_open(mock_open):
            project.Project("unittest", "GPLv2").write("test.txt", " ")

    @mock.patch.object(project, "open")
    def test_create(self, mock_open: mock.Mock):
        with mock.mock_open(mock_open):
            project.Project.create(project.__project__, "GPLv2")


if __name__ == "__main__":
    unittest.main()
