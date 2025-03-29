# coding:utf-8

from argparse import Namespace
from errno import ECANCELED
from errno import ENOENT
from errno import ENOTRECOVERABLE
import os
import sys
from tempfile import TemporaryDirectory
from typing import Tuple
import unittest
from unittest import mock

from xkits_command import ArgParser
from xkits_command import Command
from xkits_command import CommandArgument
from xkits_command import CommandCreation
from xkits_command import CommandDeletion
from xkits_command import CommandExecutor
from xkits_command.attribute import __version__


@CommandArgument("debug", help="test logger level")
def add_cmd_debug(_arg: ArgParser):
    Command.stderr_red("debug")
    _arg.add_opt_on("-d", "--debug")


@CommandExecutor(add_cmd_debug)
def run_cmd_debug(cmds: Command) -> int:
    cmds.logger.debug("debug")
    return 0


@CommandArgument("known", help="test preparse")
def add_cmd_known(_arg: ArgParser):
    Command.stdout_green("known")
    _arg.preparse_from_sys_argv()


@CommandExecutor(add_cmd_known)
def run_cmd_known(cmds: Command) -> int:
    cmds.logger.debug("known")
    return 0


@CommandArgument("list", description="test list")
def add_cmd_list(_arg: ArgParser):
    Command.stdout("list")


@CommandExecutor(add_cmd_list, add_cmd_debug, add_cmd_known)
def run_cmd_list(cmds: Command) -> int:
    cmds.logger.info("list")
    return 0


@CommandArgument("incomplete", help="test incomplete")
def add_cmd_incomplete(_arg: ArgParser):
    Command.stderr("error")


@CommandExecutor(add_cmd_incomplete)
def run_cmd_incomplete(cmds: Command) -> int:
    cmds.logger.error("incomplete")
    return -1


@CommandArgument("keyboard", help="test KeyboardInterrupt")
def add_cmd_keyboard(_arg: ArgParser):
    Command.stdout("keyboard")


@CommandExecutor(add_cmd_keyboard)
def run_cmd_keyboard(cmds: Command) -> int:
    cmds.logger.error("keyboard")
    raise KeyboardInterrupt


@CommandArgument("exception", help="test BaseException")
def add_cmd_exception(_arg: ArgParser):
    Command.stdout("exception")


@CommandExecutor(add_cmd_exception)
def run_cmd_exception(cmds: Command) -> int:
    cmds.logger.error("exception")
    raise BaseException


@CommandArgument("prepare", help="test prepare")
def add_cmd_prepare(_arg: ArgParser):
    Command.stdout("prepare")


@CommandExecutor(add_cmd_prepare)
def run_cmd_prepare(cmds: Command) -> int:
    return 0


@CommandCreation(run_cmd_prepare)
def pre_cmd_prepare(cmds: Command) -> int:
    cmds.logger.info("prepare")
    return -1


@CommandArgument("purge", help="test purge")
def add_cmd_purge(_arg: ArgParser):
    Command.stdout("purge")


@CommandExecutor(add_cmd_purge)
def run_cmd_purge(cmds: Command) -> int:
    return 0


@CommandDeletion(run_cmd_purge)
def end_cmd_purge(cmds: Command) -> int:
    cmds.logger.info("purge")
    return 1


@CommandArgument("example", description="example")
def add_cmd(_arg: ArgParser):
    Command.stdout("test")


@CommandExecutor(add_cmd, add_cmd_list, add_cmd_incomplete,
                 add_cmd_keyboard, add_cmd_exception,
                 add_cmd_prepare, add_cmd_purge)
def run_cmd(cmds: Command) -> int:
    cmds.logger.debug("main")
    return 0


@CommandCreation(run_cmd)
def pre_cmd(cmds: Command) -> int:
    cmds.logger.debug("prepare")
    return 0


@CommandDeletion(run_cmd)
def end_cmd(cmds: Command) -> int:
    cmds.logger.debug("purge")
    return 0


class TestCommand(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.cmds = Command()

    def tearDown(self):
        pass

    @mock.patch.object(sys, "exit")
    def test_help_action(self, mock_exit: mock.Mock):
        mock_exit.side_effect = [Exception("xkits-test")]
        self.assertRaises(Exception, self.cmds.run, add_cmd, "--help".split())
        mock_exit.assert_called_once_with(0)

    @mock.patch.object(sys, "exit")
    def test_help_action_h(self, mock_exit: mock.Mock):
        mock_exit.side_effect = [Exception("xkits-test")]
        self.assertRaises(Exception, self.cmds.run, add_cmd, "-h".split())
        mock_exit.assert_called_once_with(0)

    @mock.patch.object(sys, "exit")
    def test_version_action(self, mock_exit: mock.Mock):
        self.cmds.version = __version__
        mock_exit.side_effect = [Exception("xkits-test")]
        self.assertRaises(Exception, self.cmds.run, add_cmd,
                          "--version".split())
        mock_exit.assert_called_once_with(0)

    def test_version_debug(self):
        self.cmds.version = __version__
        ret = self.cmds.run(argv="--stderr --debug".split())
        self.assertEqual(ret, 0)

    def test_root(self):
        self.assertIsInstance(self.cmds.root, CommandArgument)
        assert isinstance(self.cmds.root, CommandArgument)
        self.assertIs(self.cmds.root.cmds, self.cmds)
        self.assertIsInstance(self.cmds.root.bind, CommandExecutor)
        assert isinstance(self.cmds.root.bind, CommandExecutor)
        self.assertIsInstance(self.cmds.root.bind.bind, CommandArgument)
        self.assertIs(self.cmds.root.bind.bind, self.cmds.root)
        if self.cmds.root.bind.prep:
            self.assertIsInstance(self.cmds.root.bind.prep, CommandCreation)
            self.assertIs(self.cmds.root.bind.prep.main, self.cmds.root.bind)
        if self.cmds.root.bind.done:
            self.assertIsInstance(self.cmds.root.bind.done, CommandDeletion)
            self.assertIs(self.cmds.root.bind.done.main, self.cmds.root.bind)
        self.assertIsInstance(self.cmds.root.subs, Tuple)
        assert isinstance(self.cmds.root.subs, Tuple)
        for _sub in self.cmds.root.subs:
            self.assertIsInstance(_sub, CommandArgument)
            self.assertIs(_sub.root, self.cmds.root)
            self.assertIs(_sub.prev, self.cmds.root)
            self.assertIsInstance(_sub.bind, CommandExecutor)
            assert isinstance(_sub.bind, CommandExecutor)
            if _sub.bind.prep:
                self.assertIsInstance(_sub.bind.prep, CommandCreation)
                self.assertIs(_sub.bind.prep.main, _sub.bind)
            if _sub.bind.done:
                self.assertIsInstance(_sub.bind.done, CommandDeletion)
                self.assertIs(_sub.bind.done.main, _sub.bind)
            if _sub.subs:
                for _son in _sub.subs:
                    self.assertIsInstance(_son, CommandArgument)
                    self.assertIs(_son.root, self.cmds.root)
                    self.assertIs(_son.prev, _sub)

    def test_parse_root(self):
        ret = self.cmds.parse(argv="--stdout --debug".split())
        self.assertIsInstance(ret, Namespace)

    def test_run_root_error(self):
        ret = self.cmds.run(mock.Mock(), argv="--stdout -d".split())
        self.assertEqual(ret, ENOENT)

    def test_run_KeyboardInterrupt(self):
        ret = self.cmds.run(argv="keyboard --stderr -d".split())
        self.assertEqual(ret, ECANCELED)

    def test_run_BaseException(self):
        with TemporaryDirectory() as _tmp:
            path = os.path.join(_tmp, "log.txt")
            ret = self.cmds.run(argv=f"exception --log {path}".split())
            self.assertEqual(ret, ENOTRECOVERABLE)

    def test_run_prepare(self):
        ret = self.cmds.run(argv="prepare --stdout --debug".split())
        self.assertEqual(ret, -1)

    def test_run_purge(self):
        ret = self.cmds.run(argv="purge --stderr --debug".split())
        self.assertEqual(ret, 1)

    @mock.patch.object(ArgParser, "filter_optional_name")
    def test_filter_optional_name(self, mock_filter_optional_name: mock.Mock):
        mock_filter_optional_name.return_value = []
        ret = self.cmds.run(add_cmd, [], prog="example",
                            description="unittest")
        self.assertEqual(ret, 0)

    def test_has_sub(self):
        ret = self.cmds.has_sub(add_cmd)
        self.assertIsInstance(ret, bool)

    def test_subcommand_list(self):
        ret = self.cmds.run(add_cmd, "incomplete".split(), prog="example")
        self.assertEqual(ret, -1)


class TestCommandsLogger(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.cmds = Command()

    def tearDown(self):
        pass

    def test_disable_logger(self):
        self.cmds.enabled_logger = False
        ret = self.cmds.run(argv=[])
        self.assertEqual(ret, 0)


if __name__ == "__main__":
    unittest.main()
