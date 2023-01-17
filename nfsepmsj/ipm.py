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
import datetime
from nfsepmsj import xml
from nfsepmsj.base import BaseNFSe

class IPMDataFormat:

    def __init__(self) -> None:
        self.data = {
            'nf.data.emissao': {
                'required': False,
                'format': self.date_format
            },
            'nf.total_servicos': {
                'required': True,
                'format': self.currency_format
            },
            'nf.prestador.documento': {
                'required': True,
                'format': None
            },
            'nf.codigo_municipio': {
                'required': True,
                'format': None
            },
            'nf.tomador.documento': {
                'required': True,
                'format': None
            },
            'item.tributa_prestador': {
                'required': True,
                'format': None
            },
            'item.codigo_municipio': {
                'required': True,
                'format': None
            },
            'item.quatidade': {
                'required': False,
                'format': self.currency_format
            },
            'item.valor_unitario': {
                'required': False,
                'format': self.currency_format
            },
            'item.codigo_servico': {
                'required': True,
                'format': None
            },
            'item.descricao': {
                'required': True,
                'format': None
            },
            'item.aliquota_iss': {
                'required': True,
                'format': self.currency_format
            },
            'item.situacao_tributaria': {
                'required': True,
                'format': None
            },
            'item.base_calculo': {
                'required': True,
                'format': self.currency_format
            }
        }
    
    def currency_format(self, value: str) -> str:
        decimal_value = float(value)
        return '{:.2f}'.format(decimal_value).replace('.', ',')

    def date_format(self, value: str) -> str:
        # Default format is YYYY-MM-DD
        date_value = datetime.datetime.strptime(value, '%Y-%m-%d').date()
        return date_value.strftime('%d/%m/%Y')

class NFSeIPM(BaseNFSe):

    def __init__(self, ws_url, pfx_file: str = None, pfx_passwd: str = None, target: str = 'production'):
        super(NFSeIPM, self).__init__(pfx_file, pfx_passwd, target)
        self.ws_url = ws_url
        self._data = {}
        self.data_format = IPMDataFormat()

    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, value: dict):
        # validate??
        self._data = value

    def _data_format(self, field_name: str, field_value: str):
        attr = self.data_format.data.get(field_name)
        if attr is not None:
            if attr['format'] and callable(attr['format']):
                return attr['format'](field_value)
        return field_value

    def xml(self):
        root = xml.create_root_element('nfse')
        if self.target == 'test':
            xml.add_element(root, None, 'nfse_teste', text='1')
        xml.add_element(root, None, 'nf')
        self._add_fields_nullable(
            xml_element=root,
            fields_data=(
                ('nf.serie', 'nf', 'serie_nfse'),
                ('nf.data.emissao', 'nf', 'data_fato_gerador')
            ),
            fields=self.data
        )
        xml.add_element(root, 'nf', 'valor_total', text=self._data_format('nf.total_servicos', self.data['nf.total_servicos']))
        xml.add_element(root, None, 'prestador')
        xml.add_element(root, 'prestador', 'cpfcnpj', text=self.data['nf.prestador.documento'])
        xml.add_element(root, 'prestador', 'cidade', text=self.data['nf.codigo_municipio'])
        xml.add_element(root, None, 'tomador')
        if self.data.get('nf.tomador.usar_endereco'):
            xml.add_element(root, 'tomador', 'endereco_informado', text=self.data['nf.tomador.usar_endereco'])
        xml.add_element(root, 'tomador', 'tipo', text=self.data['nf.tomador.tipo'])
        self._add_fields_nullable(
            xml_element=root,
            fields_data=(
                ('nf.tomador.identificador', 'tomador', 'identificador'),
                ('nf.tomador.documento', 'tomador', 'cpfcnpj'),
                ('nf.tomador.razao_social', 'tomador', 'nome_razao_social'),
                ('nf.tomador.codigo_municipio', 'tomador', 'cidade'),
            ),
            fields=self.data
        )
        xml.add_element(root, None, 'itens')
        for item in self.data.get('nf.servicos'):
            servico = xml.add_element(root, 'itens', 'lista')
            xml.add_element(servico, None, 'tributa_municipio_prestador', text=self._data_format('item.tributa_prestador', item['item.tributa_prestador']))
            xml.add_element(servico, None, 'codigo_local_prestacao_servico', text=self._data_format('item.codigo_municipio', item['item.codigo_municipio']))
            xml.add_element(servico, None, 'unidade_quantidade', text=self._data_format('item.quantidade', item['item.quantidade']))
            xml.add_element(servico, None, 'unidade_valor_unitario', text=self._data_format('item.valor_unitario', item['item.valor_unitario']))
            xml.add_element(servico, None, 'codigo_item_lista_servico', text=self._data_format('item.codigo_servico', item['item.codigo_servico']))
            xml.add_element(servico, None, 'descritivo', text=self._data_format('item.descricao', item['item.descricao']))
            xml.add_element(servico, None, 'aliquota_item_lista_servico', text=self._data_format('item.aliquota_iss', item['item.aliquota_iss']))
            xml.add_element(servico, None, 'situacao_tributaria', text=self._data_format('item.situacao_tributaria', item['item.situacao_tributaria']))
            xml.add_element(servico, None, 'valor_tributavel', text=self._data_format('item.base_calculo', item['item.base_calculo']))
        return root
    
    def add_rps(self, rps_fields):
        self.data = rps_fields
        xml_data_signed = self.xml()
        return xml_data_signed