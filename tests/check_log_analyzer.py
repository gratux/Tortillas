import logging

from tortillas.log_parser import LogParser
from tortillas.test_specification import TestSpec
from tortillas.tortillas_config import AnalyzeConfigEntry
from tortillas.log_analyzer import LogAnalyzer, TestStatus


def _get_log_data(config_entry: AnalyzeConfigEntry):
    log_parser = LogParser(log_file_path='./tests/assets/out_log.txt',
                           logger=logging.getLogger(),
                           config=[config_entry])

    return log_parser.parse()


def _get_test_spec():
    return TestSpec('pytest', './tests/assets/test_spec.txt')


def test_analzye_add_as_error():
    config_entry = AnalyzeConfigEntry(name='test',
                                      scope='SYSCALL',
                                      pattern=r'(.*)',
                                      mode='add_as_error',
                                      set_status='PANIC').compile_pattern()

    log_data = _get_log_data(config_entry)

    analyzer = LogAnalyzer(test_repr='pytest',
                           test_spec=_get_test_spec(),
                           config=[config_entry])

    analyzer.analyze(log_data)

    assert analyzer.result.errors
    assert analyzer.result.status == TestStatus.PANIC


def test_analzye_exit_codes():
    log_data = {'test': ['1', '2', '3', '4']}

    config_entry = AnalyzeConfigEntry(name='test',
                                      scope='',
                                      pattern='',
                                      mode='exit_codes',
                                      set_status='FAILED')

    analyzer = LogAnalyzer(test_repr='pytest',
                           test_spec=_get_test_spec(),
                           config=[config_entry])

    analyzer.analyze(log_data)

    # test_result.errors:
    # 5x Unexpected exit code {code}
    # 1x Expected exit code(s) {codes}
    assert len(analyzer.result.errors) == 5

    assert analyzer.result.status == TestStatus.FAILED

def test_expect_stdout():
    log_data = {'test': ['TORTILLAS EXPECT: A', 'A',
                         'TORTILLAS EXPECT: B']}

    config_entry = AnalyzeConfigEntry(name='test',
                                      scope='',
                                      pattern='',
                                      mode='expect_stdout',
                                      set_status='FAILED')

    analyzer = LogAnalyzer(test_repr='pytest',
                           test_spec=_get_test_spec(),
                           config=[config_entry])

    analyzer.analyze(log_data)

    # test_result.errors:
    # 1x Expected ouput: B
    # 1x Actual output: A
    assert len(analyzer.result.errors) == 2

    assert analyzer.result.status == TestStatus.FAILED