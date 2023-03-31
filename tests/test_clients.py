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

from nfsepmsj import xml
from nfsepmsj.client import (
    NFSeAbrasf,
    NFSeIPM,
)


class TestClients(unittest.TestCase):

    def setUp(self):
        self.cert_passw = 'cert@test'
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.cert_file = os.path.join(self.here, 'fixtures', 'cert-test.pfx')
        self.nfse_data = {
            'rps.lote.id': 'RPS123456',
            'rps.data.emissao': '2022-12-01',
            'nf.serie': '1',
            'nf.data.emissao': '2022-12-01',
            'nf.exigibilidade_iss': '1',
            'nf.codigo_municipio_incidencia': '40532',
            'nf.total_servicos': '2022.12',
            'nf.desconto_incondicionado': '10.00',
            'nf.codigo_servico': '1001',
            'nf.codigo_municipio': '40532',
            'nf.codigo_municipio_incidencia': '40532',
            'nf.discriminacao': 'Descrição do Serviço',
            'nf.prestador.documento': '12345678901234',
            'nf.tomador.tipo': 'J',
            'nf.tomador.documento': '12345678901234',
            'nf.tomador.razao_social': 'Empresa Tomador',
            'nf.tomador.codigo_municipio': '8327',
            'nf.tomador.logradouro': 'Rua do Tomador',
            'nf.tomador.numero_logradouro': '123',
            'nf.tomador.cep': '12345678',
            'nf.tomador.bairro': 'Bairro Tomador',
            'nf.tomador.codigo_municipio': '40532',
            'nf.tomador.uf': 'SC',
            'nf.tomador.contato.email': 'tomador@empresa.com.br',
            'nf.servicos': [
                {
                    'item.tributa_prestador': 'S',
                    'item.codigo_municipio': '8327',
                    'item.quantidade': '1',
                    'item.valor_unitario': '1000.06',
                    'item.codigo_servico': '1709',
                    'item.descricao': 'Descrição do Serviço 1',
                    'item.aliquota_iss': '3.00',
                    'item.situacao_tributaria': '0',
                    'item.base_calculo': '1000.06',
                },
                {
                    'item.tributa_prestador': 'S',
                    'item.codigo_municipio': '8327',
                    'item.quantidade': '1',
                    'item.valor_unitario': '1022.06',
                    'item.codigo_servico': '1709',
                    'item.descricao': 'Descrição do Serviço 2',
                    'item.aliquota_iss': '3.00',
                    'item.situacao_tributaria': '0',
                    'item.base_calculo': '1022.06',
                }
            ]
        }

    def test_abrasf(self):
        nfse = NFSeAbrasf(
            pfx_file=self.cert_file,
            pfx_passwd=self.cert_passw,
            target='test'
        )
        signed_nfse = nfse.add_rps(self.nfse_data)
        xml_expec_tree = xml.load_fromfile(os.path.join(self.here, 'fixtures', 'abrasf-nfse.xml'), clean=True)
        # save output
        # xml.dump_tofile(signed_nfse, xml_file=os.path.join(self.here, 'fixtures', 'abrasf-out.xml'), pretty_print=True)
        xml_out = xml.dump_tostring(signed_nfse)
        xml_expected = xml.dump_tostring(xml_expec_tree)
        self.assertEqual(xml_out, xml_expected)
        self.assertEqual(len(nfse.rps_batch), 1)

    def test_ipm_xml(self):
        nfse = NFSeIPM(
            ws_url='https://',
            pfx_file=self.cert_file,
            pfx_passwd=self.cert_passw,
            target='test'
        )
        xml_nfse = nfse.add_rps(self.nfse_data)
        xml_expec_tree = xml.load_fromfile(os.path.join(self.here, 'fixtures', 'ipm-nfse-full-test.xml'), clean=True)
        # save output
        # xml.dump_tofile(xml_nfse, xml_file=os.path.join(self.here, 'fixtures', 'ipm-out.xml'), pretty_print=True)
        xml_out = xml.dump_tostring(xml_nfse)
        xml_expected = xml.dump_tostring(xml_expec_tree)
        self.assertEqual(xml_out, xml_expected)


    def test_ipm_xml_signed(self):
        nfse = NFSeIPM(
            ws_url='https://',
            pfx_file=self.cert_file,
            pfx_passwd=self.cert_passw,
            target='test'
        )
        signed_nfse = nfse.add_rps(self.nfse_data, sign_xml=True)
        xml_expec_tree = xml.load_fromfile(os.path.join(self.here, 'fixtures', 'ipm-nfse-signed-test.xml'), clean=True)
        # save output
        # xml.dump_tofile(signed_nfse, xml_file=os.path.join(self.here, 'fixtures', 'ipm-signed-out.xml'), pretty_print=True)
        xml_out = xml.dump_tostring(signed_nfse)
        xml_expected = xml.dump_tostring(xml_expec_tree)
        self.assertEqual(xml_out, xml_expected)


if __name__ == '__main__':
    unittest.main()