import os
import unittest
from mock import patch

from six.moves.urllib_parse import quote_plus

from azure.common.credentials import BasicTokenAuthentication

from azure_devtools.scenario_tests import (
    ReplayableTest,
    GeneralNameReplacer,
    SubscriptionRecordingProcessor,
    patch_long_run_operation_delay,
    RecordingProcessor,
)

import sys
sys.path.append(os.path.join(os.path.dirname(__file__), os.pardir))
from example import run_example, STORAGE_ACCOUNT_NAME

TEST_CONFIG = os.path.join(os.path.dirname(__file__), 'testsettings.cfg')


DUMMY_UUID = '11111111-1111-1111-1111-111111111111'
DUMMY_SECRET = '00000000000000000000000000000000000000000000'
DUMMY_STORAGE_NAME = 'storagemgmtexample'

# --- vcr debug
import vcr
import requests
import logging

logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from vcrpy
vcr_log = logging.getLogger("vcr")
vcr_log.setLevel(logging.INFO)
# ---


class AccessTokenProcessor(RecordingProcessor):
    def process_response(self, response):
        import json
        try:
            body = json.loads(response['body']['string'])
            body['access_token'] = 'fake_token'
        except KeyError:
            return response
        except json.JSONDecodeError:
            return response
        response['body']['string'] = json.dumps(body)
        return response


class StorageExampleTest(ReplayableTest):
    def __init__(self, method_name, **kwargs):
        self.scrubber = GeneralNameReplacer()
        super(StorageExampleTest, self).__init__(
            method_name,
            config_file=TEST_CONFIG,
            recording_processors=[
                self.scrubber,
                SubscriptionRecordingProcessor(DUMMY_UUID),
                AccessTokenProcessor(),
            ],
            replay_patches=[
                patch_long_run_operation_delay,
            ]
        )
        if self.is_live:
            constants_to_scrub = [
                (os.environ['AZURE_CLIENT_ID'], DUMMY_UUID),
                (os.environ['AZURE_CLIENT_SECRET'], DUMMY_SECRET),
                (os.environ['AZURE_TENANT_ID'], DUMMY_UUID),
                (STORAGE_ACCOUNT_NAME, DUMMY_STORAGE_NAME)
            ]
            for key, replacement in constants_to_scrub:
                self.scrubber.register_name_pair(key, replacement)
                self.scrubber.register_name_pair(quote_plus(key), replacement)

    @staticmethod
    def fake_credentials():
        return (
            BasicTokenAuthentication({'access_token': 'fake_token'}),
            DUMMY_UUID
        )

    def test_example(self):
        if self.is_live:
            run_example()
        else:
            with patch('example.get_credentials', StorageExampleTest.fake_credentials), \
                 patch('example.STORAGE_ACCOUNT_NAME', DUMMY_STORAGE_NAME):
                run_example()


if __name__ == '__main__':
    unittest.main()
