# Copyright 2018, Qualita Seguranca e Saude Ocupacional. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import unittest
import os

from nfsepmsj import utils

class TestUtils(unittest.TestCase):

    def test_pfx_file(self):
        passw = 'cert@test'
        here = os.path.dirname(os.path.abspath(__file__))
        cert_file = os.path.join(here, 'fixtures', 'cert-test.pfx')
        cert_data = utils.pkcs12_data(cert_file=cert_file, password=passw)
        expected_pkey = b'-----BEGIN PRIVATE KEY-----\nMIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBALeLfY9iMPbhrlFY\neKzA/KEYkLXGO3c/Bw/mYfDqapGqt3NFAKGbxfKRjtHfjl46F+hhNlIMrUyVJO8I\nhs2pXkYEKBogi6+JYvyJvcJlxrgmaaiDhgbGERHoi7jec+SLhQg62693GmIfj5om\nWzHl6Ca0q3OICx/xEeWcrqhsvI0TAgMBAAECgYBY1Utc5TI7mvjKaB5nxjO/KGuJ\nfrrzOO8LE/7dIieX/t8xC/mFPiZtA2PzUdbO5iECGGK5DWemxByPEDpmOY3lVQbA\n4LkT9K7xHHedUWsVFX5oTWoAJGqRQiK8DbanQsCcEm4L6DzHZ+nEpN4twqVFS16C\nrTeKF5azXzrRgfxpIQJBAOcK8cnCH17LwJZIuEjM4tjPoEhC8JNb9DTQZFb8rZXO\nhA+T7t7/5pSQJoKAMx4pTzkr50RF5kgBuN60rxzVFvECQQDLXxTLq4rG5nGBif5D\nz0mfvChOfAOfpoS4mTquv71gfdw0sKFuIy+VF9ZfvRyeo+ji2OqTN+TJPEAIM+aQ\nqExDAkEA0KDeYsyrHSOp3Ur/NaXlddhOqNHhgX84TnSbFr2GVc8tCxAPVEkJwr9E\nNvVis2qkAkE1zT29SupbMKdBtSxqUQJAGeSJKUU17gz49p0zGj8SCJxUJWn0rCbv\nTvFzXzxaSCa+GpdCdltUe48FZDsXobsMs5UaiJPdNSHOpTy2ZkSHMQJBAN/CsFZk\nD91FaIr8jS86n2Gj3pXujLprfxBGASFoX41cTBWkrYVfOb1HiBvExZL8TXFfnQ84\nMuyCM4rb36R7SUI=\n-----END PRIVATE KEY-----\n'
        self.assertEqual(cert_data['key_str'], expected_pkey)
    
    def test_normalize_text(self):
        test_texts = (
            ('"M&M"', '&quot;M&M&quot;'),
            ("D'agua", 'D&apos;agua')
        )
        for input_text, expected_text in test_texts:
            out_text = utils.normalize_text(input_text)
            self.assertEqual(out_text, expected_text)


if __name__ == '__main__':
    unittest.main()