from __future__ import absolute_import
import six
import hammock.cli
import tests.cli.base as base
import tests.resources1.cli_names as cli_names


SUCCESS = 'Success'


class TestCli(base.Base):

    def test_dict(self):
        self.assertListEqual([], self.run_json_command('dict list'))
        self.assertDictEqual({'key': 'A', 'value': 'a'}, self.run_json_command('dict insert A a'))
        self.assertDictEqual({'key': 'B', 'value': 'b'}, self.run_json_command('dict insert B b'))
        self.assertDictEqual({'key': 'A', 'value': 'a'}, self.run_json_command('dict get A'))
        self.assert_list_of_dicts_equal(
            [{'key': 'A', 'value': 'a'}, {'key': 'B', 'value': 'b'}],
            self.run_json_command('dict list')
        )
        self.assertEqual({'key': 'A', 'value': 'a'}, self.run_json_command('dict update A new-a'))
        self.assertDictEqual({'key': 'A', 'value': 'new-a'}, self.run_json_command('dict get A'))
        self.assertDictEqual({'key': 'C', 'value': 'c'}, self.run_json_command('dict get C --default c'))
        self.assertDictEqual({'key': 'B', 'value': 'b'}, self.run_json_command('dict remove B'))
        self.assert_list_of_dicts_equal([{'key': 'A', 'value': 'new-a'}], self.run_json_command('dict list'))

        # get key that does not exists
        self.assertRaises(hammock.cli.CLIException, self.run_json_command, 'dict get C')
        # missing argument
        self.assertRaises(SystemExit, self.run_json_command, 'dict insert A')

    def test_list(self):
        self.assertListEqual([], self.run_json_command('list list'))
        self.run_command('list append 1')
        self.run_command('list append 2')
        self.assert_list_of_dicts_equal(
            [{'value': '1'}, {'value': '2'}],
            self.run_json_command('list list')
        )
        self.run_command('list remove 1')
        self.assert_list_of_dicts_equal([{'value': '2'}], self.run_json_command('list list'))

        # remove value that does not exists
        self.assertRaises(hammock.cli.CLIException, self.run_command, 'list remove 3')
        # missing argument
        self.assertRaises(SystemExit, self.run_command, 'list remove')

    def test_nested_resources(self):
        self.assertEqual('sub-in-sub1', self.run_command('sub-resource sub get'))
        self.assertEqual('sub2-in-sub1', self.run_command('sub-resource sub2 get'))
        self.assertEqual('sub-in-nested-in-sub', self.run_command('sub-resource nested sub get'))
        self.assertEqual('sub-in-sub2', self.run_command('sub-resource2-modified sub get'))

    def test_method_name(self):
        for method_name, translated_name in six.iteritems(cli_names.NAMES):
            self.assertEqual(method_name, self.run_command('cli-names {}'.format(translated_name)))
        self.assertEqual('moshe', self.run_command('cli-names optional-variable-with-underscores --optional-variable moshe'))
        self.assertEqual(SUCCESS, self.run_command('cli-names optional-variable-with-underscores'))
        self.assertEqual(True, self.run_command('cli-names set-false'))
        self.assertEqual(False, self.run_command('cli-names set-false --set-false'))
        self.assertEqual(False, self.run_command('cli-names set-true'))
        self.assertEqual(True, self.run_command('cli-names set-true --set-true'))
        self.assertEqual(True, self.run_command('cli-names bool-type --value True'))
        self.assertEqual(True, self.run_command('cli-names bool-type --value true'))
        self.assertEqual(False, self.run_command('cli-names bool-type --value False'))
        self.assertEqual(False, self.run_command('cli-names bool-type --value some-string'))

        self.assertEqual('modified-in-modified', self.run_command('different-path different-sub get'))
        self.assertEqual('modified-in-modified-in-modified', self.run_command('different-path different-sub post-modified'))
        self.assertEqual('moshe', self.run_command('variable-in-url-1 get moshe'))
        self.assertEqual('moshe', self.run_command('variable-in-url-2 get moshe'))

    def test_headers(self):
        self.assertEqual(True, self.run_command('--headers a:b headers request-headers a b'))
        self.assertEqual(False, self.run_command('--headers a:b headers request-headers a c'))

    def test_ignores(self):
        self.assertRaises(hammock.cli.CLIException, self.run_command, 'cli-ignored-package sub get')
        self.assertRaises(hammock.cli.CLIException, self.run_command, 'cli-ignored-resource sub get')
        self.assertRaises(hammock.cli.CLIException, self.run_command, 'cli-names ignored-method')

        self.assertEqual('sub-in-ignored', self.run_command('cli-ignored-package sub get', remove_ignored_commands=False))
        self.assertEqual('cli-ignored-resource', self.run_command('cli-ignored-resource get', remove_ignored_commands=False))
        self.assertEqual('ignored-method', self.run_command('cli-names ignored-method', remove_ignored_commands=False))

    def test_result_type(self):
        self.assertEqual(SUCCESS, self.run_command('cli-names returns-nothing-type'))

    def test_argument_with_underscores(self):
        self.assertDictEqual(
            self.run_json_command(['cli-names', 'argument-with-underscores', '1', '--second-arg', '2']),
            {'arg': 1, 'second': 2}
        )

    def test_empty_resources(self):
        self.assertEqual('additional', self.run_command('sub-resource nested additional'))
        self.assertEqual('additional-2', self.run_command('sub-resource nested additional-2'))

    def test_keywords(self):
        command = ['keywords', 'get', '--kwargs', '{"a": "b", "c": "d"}', '--default', 'f', 'k']
        result = self.run_json_command(command)
        self.assertEquals(result['a'], 'b')
        self.assertEquals(result['c'], 'd')
        self.assertEquals(result['arg'], 'k')
        self.assertEquals(result['default'], 'f')

    def test_client_methods(self):
        self.assertEqual(3, self.run_command('client-methods jump 3'))
        # Test missing argument
        self.assertRaises(SystemExit, self.run_command, 'client-methods run')
        # Test invalid argument type in client
        self.assertRaises(SystemExit, self.run_command, 'client-methods run string')
        self.assertEqual(3.0, self.run_command('client-methods run 3'))
        self.assertEqual(30.0, self.run_command('client-methods run 3 --distance 10'))
        self.assertRaises(hammock.cli.CLIException, self.run_command, 'client-methods no-such-action')

    def assert_list_of_dicts_equal(self, list1, list2):
        assert len(list1) == len(list2)
        for elem1, elem2 in zip(sorted(list1), sorted(list2)):
            self.assertDictEqual(elem1, elem2)
