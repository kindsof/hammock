from __future__ import absolute_import
import six
import tests.cli.base as base
import tests.resources1.cli_names as cli_names


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
        self.assertRaises(base.CLIException, self.run_json_command, 'dict get C')
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
        self.assertRaises(base.CLIException, self.run_command, 'list remove 3')
        # missing argument
        self.assertRaises(SystemExit, self.run_command, 'list remove')

    def test_nested_resources(self):
        self.assertEqual('sub-in-sub1\n', self.run_command('sub-resource sub get'))
        self.assertEqual('sub2-in-sub1\n', self.run_command('sub-resource sub2 get'))
        self.assertEqual('sub-in-nested-in-sub\n', self.run_command('sub-resource nested sub get'))
        self.assertEqual('sub-in-sub2\n', self.run_command('sub-resource2-modified sub get'))

    def test_method_name(self):
        for method_name, translated_name in six.iteritems(cli_names.NAMES):
            self.assertEqual(method_name + '\n', self.run_command('cli-names {}'.format(translated_name)))
        self.assertEqual('modified-in-modified\n', self.run_command('different-path different-sub get'))
        self.assertEqual('modified-in-modified-in-modified\n', self.run_command('different-path different-sub post-modified'))
        self.assertEqual('moshe\n', self.run_command('variable-in-url-variable-name get moshe'))
        self.assertEqual('moshe\n', self.run_command('variable-name-variable-in-url get moshe'))

    def assert_list_of_dicts_equal(self, list1, list2):
        assert len(list1) == len(list2)
        for elem1, elem2 in zip(sorted(list1), sorted(list2)):
            self.assertDictEqual(elem1, elem2)

    def test_headers(self):
        self.assertEqual('True\n', self.run_command('--headers a:b headers request-headers a b'))
        self.assertEqual('False\n', self.run_command('--headers a:b headers request-headers a c'))
