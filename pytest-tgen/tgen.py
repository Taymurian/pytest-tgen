"""This is Pytest test suit generator"""
from __future__ import annotations

import argparse
import re

import helper


# pylint: disable=line-too-long  # C0301
# Disabling:Too many branches, Too many statements
# pylint: disable=R0912,R0915
# Disabling Pylint docstring, class and function errors.
# pylint: disable=R0903, C0114, C0115, E0102
# Disabling function, argument and file length errors.
# pylint: disable=E0011, C0302, C0103, C0116


def auto_tgen_header_template() -> [str]:
    """generate test_suit header"""
    data = [
        "\"\"\"Test_suite generated automatically, do not change it manually.\"\"\"\n\n",
        'import logging\n',
        'import re\n',
        'import time\n',
        'import pytest\n',
        'import helper\n',
    ]
    return data


def auto_tgen_data_blob_template() -> [str]:
    """generate test_suit data blob object"""
    data = [
        '\n\n',
        '@pytest.fixture()\n',
        'def parameters():\n',
        "    \"\"\"Database container fixture\"\"\"\n",
        '    return helper.DataCollector()\n',
    ]
    return data


def auto_tgen_com_obj_template() -> [str]:
    """generate test_suit com port object"""
    data = [
        '\n\n',
        "ser_object = helper.open_port(comport='COM5',\n"
        '                               baud=115200,\n'
        "                               prompt='root@imx8mm-var-dart:~# ')\n",
    ]
    return data


def auto_tgen_main_template(tc_name: str, sequence: str, desc: str) -> [str]:
    """generate test_suit main testcase body"""
    data = [
        '\n\n'
        "# @pytest.mark.skipif(parameters.tcs['{tc_name}']['skip'], reason='The test case skipped by user.')\n"
        f'def test_{tc_name}_{sequence}(parameters):\n',
        f"    \"\"\"test description: {desc} \"\"\"\n",
        f"    tc = parameters.tcs['{tc_name}']\n",
        '    if tc:\n',
        "        for _ in range(int(tc['repeat'])):\n",
        '            _steps_loop(tc, ser_object)\n',
        '    else:\n',
        "        print('\\n  The test case parameters is empty.')\n",
        "        logging.error('The test case parameters is empty.')\n",
        '        pytest.raises(KeyError)\n',
    ]
    return data


def auto_tgen_steps_loop_template() -> [str]:
    """generate test_suit steps loop sections"""
    data = [
        '\n\n',
        'def _steps_loop(tc, ser_obj):\n',
        "    for step in tc['steps']:\n",
        "        print(f\"\\nstep {step['step']}> {step['desc']}\")\n",
        "        if step['active']:\n"
        "            for _ in range(int(step['repeat'])):\n",
        "                ser_obj.write(f\"{step['cmd']}\\n\".encode())\n",
        "                if step['wait']:\n",
        "                    print('waiting for ' + str(step['wait']) + ' sec')\n",
        "                    time.sleep(int(step['wait']))\n",
        '                console_output = ser_obj.readall().decode()\n',
        "                print(f'console return:\\n{console_output}')\n",
    ]
    return data


def auto_tgen_step_assertion_template() -> [str]:
    """generate test_suit steps assertion section"""
    data = [
        "                match = re.search(pattern=step['regex'],\n",
        '                  string=console_output,\n',
        '                  flags=re.IGNORECASE)\n',
        'if match:\n',
        "    print(f\"\\nassert '{match[0]}' {step['assertion']} '{step['limit']}'\")\n",
        "    assert eval(f\"'{match[0]}' {step['assertion']} '{step['limit']}'\",\n",
        "                {'__builtins__': {}},\n",
        '                {})\n',
        "    # exec(f\"\\n assert '{match[0]}' {step['assertion']} '{step['limit']}'\")\n",
        'else:\n',
        "    print('\\n  there was no matching with the pattern.')\n",
        "    logging.error('there was no matching with the pattern.')\n"
        '                    pytest.raises(ReferenceError)\n',
    ]

    return data


def auto_test_suit_generator(configs: dict, database: dict):
    """generate the test suit script"""
    aggregator = ''.join(auto_tgen_header_template())
    aggregator += ''.join(auto_tgen_data_blob_template())
    if configs['flags']['has_com_obj']:
        aggregator += ''.join(auto_tgen_com_obj_template())
    aggregator += ''.join(auto_tgen_steps_loop_template())
    aggregator += (' ' * 16).join(auto_tgen_step_assertion_template())
    for tc in database:
        if tc:
            sequence = f'{database[tc]["sequences"]["major"]}_{database[tc]["sequences"]["minor"]}'
            desc = database[tc]['test_case_description']
            aggregator += ''.join(auto_tgen_main_template(tc, sequence, desc))
        else:
            raise KeyError('test case keys are not available.')

    try:
        with open(configs['output_file_name'], 'w', encoding='utf-8') as f:
            # for line in header_template():
            f.write(aggregator)
    except OSError as os_err:
        print(os_err)

    print(f'  The {configs["output_file_name"]} testsuit generated successfully')


def arg_parser(configuration):
    """Parsing the arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', '--file', help='python pytgen -f <output_filename_test.py>',
    )
    args = parser.parse_args()

    if args.file:
        if args.file[:5] != 'test_' or args.file[-5:] != '_test':
            print('pytest generator required a file that started with "test_" or ended with "_test"')
            raise ValueError('pytest generator required a file that started with "test_" or ended with "_test"')
        if re.search('.py', args.file):
            configuration['output_file_name'] = args.file
        else:
            configuration['output_file_name'] = args.file + '.py'


def runner() -> int:
    """The main test generator function"""
    inventory = helper.DataCollector(
        test_directory='tests',
        test_global_configs='test_global_configs',
    )
    collections = inventory.tcs
    configs = inventory.configs['test_global_configs']
    time_stamp = inventory.datetime_stamp
    print(f'  Testsuit generation start at: {time_stamp}')
    arg_parser(configs)
    if configs['run_test_suit_generator']:
        print(f'  Preparing to generate testsuit: {configs["output_file_name"]}')
        auto_test_suit_generator(configs, collections)
    else:
        print('  The test generator is disabled by configuration.')
    return 0


if __name__ == '__main__':
    raise SystemExit(runner())
