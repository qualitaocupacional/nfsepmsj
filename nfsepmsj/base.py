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
from nfsepmsj import xml
from nfsepmsj.utils import pkcs12_data

from zeep import Client

from lxml import etree


class BaseNFSe(object):
    __xmlns__ = 'http://www.betha.com.br/e-nota-contribuinte-ws'
    __wsdl_header__ = '<cabecalho xmlns="http://www.betha.com.br/e-nota-contribuinte-ws" versao="2.02"><versaoDados>2.02</versaoDados></cabecalho>'
    __api_version__ = ''

    def __init__(self, pfx_file=None, pfx_passwd=None, target='production'):
        if pfx_file is not None:
            self.cert_data = pkcs12_data(pfx_file, pfx_passwd)
        else:
            self.cert_data = None
        self.rps_batch = []
        self.cancel_batch = []
        self._xsd_file = None
        self.nsmap = {None: self.__xmlns__}
        # Properties
        self.target = target

    def _connect(self, url):
        return Client(url)

    def _validate_xml(self, xml_element):
        if not isinstance(xml_element, etree._ElementTree):
            xml_element = etree.ElementTree(xml_element)
        _xsd = xml.xsd_fromfile(self._xsd_file)
        return xml.XMLValidate(xml_element, _xsd)

    def _data_format(self, field_name, field_value):
        # To be implemented on derivated classes
        if field_name is not None:
            return field_value
        return None
        
    def _add_fields_nullable(self, xml_element, fields_data, fields, ns=None):
        '''Check nullable fields to add to XML tree.

        *xml_element*: A lxml._ElementTree
        *fields_data*: ((field_name, xml_path, xml_tag), ...)
        *fields*: Dictionary with RPS fields = {'field_name': 'field_value'}
        *ns*: Namespace map
        '''
        for row in fields_data:
            field_name, xml_path, xml_tag = row
            if fields.get(field_name):
                xml.add_element(xml_element, xml_path, xml_tag, text=self._data_format(field_name, fields.get(field_name)), ns=ns)

    def _has_fields(self, start_key, fields_dict):
        has_key = False
        for key in fields_dict:
            has_key = key.startswith(start_key)
            if has_key:
                break
        return has_key

    def clear_rps_batch(self):
        del self.rps_batch
        self.rps_batch = []

    def clear_cancel_batch(self):
        del self.cancel_batch
        self.cancel_batch = []

    def sign(self, xml_element, reference_uri=None):
        return xml.sign(etree.ElementTree(xml_element), self.cert_data, reference_uri=reference_uri)
