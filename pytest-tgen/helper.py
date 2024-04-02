"""This module collect pytest required configurations and parameters."""
from __future__ import annotations

import datetime
import json
import logging
import os
import re
import sys
import time

import serial
import yaml

# pylint: disable=line-too-long  # C0301
# Disabling:Too many branches, Too many statements
# pylint: disable=R0912,R0915
# Disabling Pylint docstring, class and function errors.
# pylint: disable=R0903, C0114, C0115, E0102
# Disabling function, argument and file length errors.
# pylint: disable=E0011, C0302, C0103, C0116
# Disabling line too long.
# noqa: E501


class DataCollector:
    """data collation container"""

    def __init__(
        self,
        test_directory: str = 'tests',
        test_global_configs: str = 'test_global_configs',
    ):
        self.directory = test_directory
        self.configs_filename = test_global_configs
        self.configs, self.tcs = self._read_configuration_files(self.directory)
        self.datetime_stamp = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M')

    def _read_configuration_files(self, tests_directory: str):
        """import testcases parameters and configurations from yaml files"""
        configures_dict, parameters_dict = {}, {}
        if os.path.isdir(tests_directory):
            for filename in os.listdir(tests_directory):
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    file_path = os.path.join(tests_directory, filename)
                    with open(file_path, encoding='utf-8') as file:
                        try:
                            if filename.startswith(self.configs_filename):
                                configures_dict[str(filename.split('.')[0])] = yaml.safe_load(file)
                                # configur_dict.update(yaml.safe_load(file))
                            else:
                                parameters_dict[str(filename.split('.')[0])] = yaml.safe_load(file)
                                # combined_dict.update(yaml.safe_load(file))
                                # combined_dict.append(yaml.safe_load(file))
                        except yaml.YAMLError as err:
                            print(err)
                            logging.error('\nCan not open the yaml file.')
                else:
                    logging.error('\nThere was no yaml tests file.')
        with open('parameter.json', 'w') as fd:
            json.dump(parameters_dict, fd, indent=4)
        return configures_dict, parameters_dict


def open_port(comport: str, baud: int, prompt: str):
    """open the port"""
    try:
        serial_obj = serial.Serial(comport, baud, timeout=0.1)
    except OSError as os_err:
        print(os_err)
        logging.error('OS can not open the port. port is busy or device is not ready.')
        raise OSError('OS can not open the port. port is busy or device is not ready.')

    # check the prompt
    serial_obj.write(b'\n\n')
    time.sleep(0.5)
    data = serial_obj.readlines()
    for line in data:
        print(line.decode())
    if data:
        match = re.search(
            pattern=r'login:|password:',
            string=data[-1].decode().strip('\r\n').casefold(),
            flags=re.IGNORECASE,
        )
    else:
        print('\nport is busy or device is not ready.', file=sys.stderr)
        logging.error('\nport is busy or device is not ready.')
        raise OSError('\nport is busy or device is not ready.')

    if match:
        if match[0] == 'password:':
            serial_obj.write(b'\n')
            time.sleep(1)

        serial_obj.write(b'root\n\n')
        time.sleep(0.5)
        data = serial_obj.readlines()
        for line in data:
            print(line.decode())
        if data:
            ret_prompt = data[-1].decode().strip('\r\n').casefold()
            match = re.search(pattern=prompt, string=ret_prompt)
            if not match:
                print('\nthe prompt is not matched. prompt=' + ret_prompt, file=sys.stderr)
                logging.error('the prompt is not matched. prompt=%s', ret_prompt)
                raise ReferenceError(f'the prompt is not matched. prompt = {ret_prompt}')
    return serial_obj
