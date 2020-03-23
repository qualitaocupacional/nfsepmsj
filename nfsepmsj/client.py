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
import os
import datetime

from collections import OrderedDict

import requests

import nfsepmsj

from nfsepmsj import xml
from nfsepmsj.utils import pkcs12_data

import xmltodict

from zeep import (
    Client,
    xsd
)

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
                xml.add_element(xml_element, xml_path, xml_tag, text=fields.get(field_name), ns=ns)

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


class NFSeAbrasf(BaseNFSe):

    __api_version__ = '2.02'

    def __init__(self, pfx_file=None, pfx_passwd=None, target='production'):
        super(NFSeAbrasf, self).__init__(pfx_file, pfx_passwd, target)
        self._xsd_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'xsd',
            'abrasf',
            self.__api_version__,
            'nfse_v{}.xsd'.format(self.__api_version__.replace('.', ''))
        )
        self.ws_url = nfsepmsj.ABRASF_WSURL[self.__api_version__][target]

    def _gen_rps_xml(self, rps_fields):
        rps = xml.create_root_element('Rps', ns=self.nsmap)
        inf_declaracao = xml.add_element(
            rps,
            None,
            'InfDeclaracaoPrestacaoServico',
            ns=self.nsmap,
            Id=rps_fields.get('rps.lote.id')
        )
        # Rps
        if rps_fields.get('rps.numero'):
            rps_in = xml.add_element(inf_declaracao, None, 'Rps', ns=self.nsmap)
            xml.add_element(rps_in, None, 'IdentificacaoRps', ns=self.nsmap)
            xml.add_element(rps_in, 'IdentificacaoRps', 'Numero', text=rps_fields.get('rps.numero'), ns=self.nsmap)
            xml.add_element(rps_in, 'IdentificacaoRps', 'Serie', text=rps_fields.get('rps.serie'), ns=self.nsmap)
            xml.add_element(rps_in, 'IdentificacaoRps', 'Tipo', text=rps_fields.get('rps.tipo'), ns=self.nsmap)
            xml.add_element(rps_in, None, 'DataEmissao', text=rps_fields.get('rps.data.emissao'), ns=self.nsmap)
            xml.add_element(rps_in, None, 'Status', text=rps_fields.get('rps.status'), ns=self.nsmap)
            if rps_fields.get('rps.substituido.numero'):
                xml.add_element(rps_in, None, 'RpsSubstituido', ns=self.nsmap)
                xml.add_element(rps_in, 'RpsSubstituido', 'Numero', text=rps_fields.get('rps.substituido.numero'), ns=self.nsmap)
                xml.add_element(rps_in, 'RpsSubstituido', 'Serie', text=rps_fields.get('rps.substituido.serie'), ns=self.nsmap)
                xml.add_element(rps_in, 'RpsSubstituido', 'Tipo', text=rps_fields.get('rps.substituido.tipo'), ns=self.nsmap)
        xml.add_element(inf_declaracao, None, 'Competencia', text=rps_fields.get('nf.data.emissao'), ns=self.nsmap)
        # Servicos
        servicos = xml.add_element(inf_declaracao, None, 'Servico', ns=self.nsmap)
        xml.add_element(servicos, None, 'Valores', ns=self.nsmap)
        xml.add_element(servicos, 'Valores', 'ValorServicos', text=rps_fields.get('nf.total_servicos'), ns=self.nsmap)
        # if rps_fields.get('nf.total_deducoes'):
        #     xml.add_element(servicos, 'Servico/Valores', 'ValorDeducoes', text=rps_fields.get('nf.total_deducoes'), ns=self.nsmap)
        self._add_fields_nullable(
            xml_element=servicos,
            fields_data=(
                ('nf.valor_deducoes', 'Valores', 'ValorDeducoes'),
                ('nf.valor_pis', 'Valores', 'ValorPis'),
                ('nf.valor_cofins', 'Valores', 'ValorCofins'),
                ('nf.valor_inss', 'Valores', 'ValorInss'),
                ('nf.valor_IR', 'Valores', 'ValorIr'),
                ('nf.valor_csll', 'Valores', 'ValorCsll'),
                ('nf.valor_outros', 'Valores', 'OutrasRetencoes'),
                ('nf.valor_iss', 'Valores', 'ValorIss'),
                ('nf.aliquota', 'Valores', 'Aliquota'),
                ('nf.desconto_incondicionado', 'Valores', 'DescontoIncondicionado'),
                ('nf.desconto_condicionado', 'Valores', 'DescontoCondicionado'),
            ),
            fields=rps_fields,
            ns=self.nsmap
        )
        xml.add_element(servicos, None, 'IssRetido', text=rps_fields.get('nf.iss_retido'), ns=self.nsmap)
        if rps_fields.get('nf.responsavel_retencao'):
            xml.add_element(servicos, None, 'ResponsavelRetencao', text=rps_fields.get('nf.responsavel_retencao'), ns=self.nsmap)
        xml.add_element(servicos, None, 'ItemListaServico', text=rps_fields.get('nf.codigo_servico'), ns=self.nsmap)
        self._add_fields_nullable(
            xml_element=servicos,
            fields_data=(
                ('nf.codigo_cnae', None, 'CodigoCnae'),
                ('nf.codigo_tributacao_municipio', None, 'CodigoTributacaoMunicipio'),
            ),
            fields=rps_fields,
            ns=self.nsmap
        )
        xml.add_element(servicos, None, 'Discriminacao', text=rps_fields.get('nf.discriminacao'), ns=self.nsmap)
        xml.add_element(servicos, None, 'CodigoMunicipio', text=rps_fields.get('nf.codigo_municipio'), ns=self.nsmap)
        if rps_fields.get('nf.codigo_pais'):
            xml.add_element(servicos, None, 'CodigoPais', text=rps_fields.get('nf.codigo_pais'), ns=self.nsmap)
        xml.add_element(servicos, None, 'ExigibilidadeISS', text=rps_fields.get('nf.exigibilidade_iss'), ns=self.nsmap)
        if rps_fields.get('nf.exigibilidade_iss') in ('1', '6', '7') or rps_fields.get('nf.codigo_municipio_incidencia'):
            xml.add_element(servicos, None, 'MunicipioIncidencia', text=rps_fields['nf.codigo_municipio_incidencia'])
        xml.add_element(inf_declaracao, None, 'Prestador', ns=self.nsmap)
        xml.add_element(inf_declaracao, 'Prestador', 'CpfCnpj', ns=self.nsmap)
        if rps_fields.get('nf.prestador.documento'):
            if len(rps_fields.get('nf.prestador.documento')) == 11: #CPF
                xml.add_element(inf_declaracao, 'Prestador/CpfCnpj', 'Cpf', text=rps_fields.get('nf.prestador.documento'), ns=self.nsmap)
            else: # CNPJ
                xml.add_element(inf_declaracao, 'Prestador/CpfCnpj', 'Cnpj', text=rps_fields.get('nf.prestador.documento'), ns=self.nsmap)
        if rps_fields.get('nf.prestador.inscricao_municipal'):
            xml.add_element(inf_declaracao, 'Prestador', 'InscricaoMunicipal', text=rps_fields.get('nf.prestador.inscricao_municipal'), ns=self.nsmap)
        if rps_fields.get('nf.tomador.documento'):
            xml.add_element(inf_declaracao, None, 'Tomador', ns=self.nsmap)
            xml.add_element(inf_declaracao, 'Tomador', 'IdentificacaoTomador', ns=self.nsmap)
            xml.add_element(inf_declaracao, 'Tomador/IdentificacaoTomador', 'CpfCnpj', ns=self.nsmap)
            if len(rps_fields.get('nf.tomador.documento')) == 11: #CPF
                xml.add_element(inf_declaracao, 'Tomador/IdentificacaoTomador/CpfCnpj', 'Cpf', text=rps_fields.get('nf.tomador.documento'), ns=self.nsmap)
            else: #CNPJ
                xml.add_element(inf_declaracao, 'Tomador/IdentificacaoTomador/CpfCnpj', 'Cnpj', text=rps_fields.get('nf.tomador.documento'), ns=self.nsmap)
            xml.add_element(inf_declaracao, 'Tomador', 'RazaoSocial', text=rps_fields.get('nf.tomador.razao_social'), ns=self.nsmap)
            if rps_fields.get('nf.tomador.logradouro'):
                xml.add_element(inf_declaracao, 'Tomador', 'Endereco', ns=self.nsmap)
                self._add_fields_nullable(
                    xml_element=inf_declaracao,
                    fields_data=(
                        ('nf.tomador.logradouro', 'Tomador/Endereco', 'Endereco'),
                        ('nf.tomador.numero_logradouro', 'Tomador/Endereco', 'Numero'),
                        ('nf.tomador.complemento', 'Tomador/Endereco', 'Complemento'),
                        ('nf.tomador.bairro', 'Tomador/Endereco', 'Bairro'),
                        ('nf.tomador.codigo_municipio', 'Tomador/Endereco', 'CodigoMunicipio'),
                        ('nf.tomador.uf', 'Tomador/Endereco', 'Uf'),
                        ('nf.tomador.codigo_pais', 'Tomador/Endereco', 'CodigoPais'),
                        ('nf.tomador.cep', 'Tomador/Endereco', 'Cep'),
                    ),
                    fields=rps_fields,
                    ns=self.nsmap
                )
            if rps_fields.get('nf.tomador.contato.telefone') or rps_fields.get('nf.tomador.contato.email'):
                xml.add_element(inf_declaracao, 'Tomador', 'Contato')
                self._add_fields_nullable(
                    xml_element=inf_declaracao,
                    fields_data=(
                        ('nf.tomador.contato.telefone', 'Tomador/Contato', 'Telefone'),
                        ('nf.tomador.contato.email', 'Tomador/Contato', 'Email'),
                    ),
                    fields=rps_fields,
                    ns=self.nsmap
                )
        # Intermediario
        if self._has_fields('nf.intermediario.', rps_fields):
            xml.add_element(rps, None, 'Intermediario', ns=self.nsmap)
            xml.add_element(rps, 'Intermediario', 'IdentificacaoIntermediario', ns=self.nsmap)
            xml.add_element(rps, 'Intermediario/IdentificacaoIntermediario', 'CpfCnpj', ns=self.nsmap)
            if len(rps_fields.get('nf.intermediario.documento')) == 11:
                xml.add_element(rps, 'Intermediario/IdentificacaoIntermediario/CpfCnpj', 'Cpf', text=rps_fields.get('nf.intermediario.documento'), ns=self.nsmap)
            else:
                xml.add_element(rps, 'Intermediario/IdentificacaoIntermediario/CpfCnpj', 'Cnpj', text=rps_fields.get('nf.intermediario.documento'), ns=self.nsmap)
            if rps_fields.get('nf.intermediario.inscricao_municipal'):
                xml.add_element(rps, 'Intermediario/IdentificacaoIntermediario', 'InscricaoMunicipal', text=rps_fields['nf.intermediario.inscricao_municipal'], ns=self.nsmap)
            xml.add_element(rps, 'Intermediario', 'RazaoSocial', text=rps_fields.get('nf.intermediario.razao_social'), ns=self.nsmap)
        # Construcao Civil
        if self._has_fields('nf.construcao_civil.', rps_fields):
            xml.add_element(rps, None, 'ConstrucaoCivil', ns=self.nsmap)
            xml.add_element(rps, 'ConstrucaoCivil', 'CodigoObra', text=rps_fields.get('nf.construcao_civil.codigo_obra'), ns=self.nsmap)
            xml.add_element(rps, 'ConstrucaoCivil', 'Art', text=rps_fields.get('nf.construcao_civil.art'), ns=self.nsmap)
        if rps_fields.get('nf.regime_especial_tributacao'):
            xml.add_element(inf_declaracao, None, 'RegimeEspecialTributacao', text=rps_fields.get('nf.regime_especial_tributacao'), ns=self.nsmap)
        xml.add_element(inf_declaracao, None, 'OptanteSimplesNacional', text=rps_fields.get('nf.optante_simples'), ns=self.nsmap)
        xml.add_element(inf_declaracao, None, 'IncentivoFiscal', text=rps_fields.get('nf.incentivo_fiscal'), ns=self.nsmap)
        return rps

    def connect(self):
        return self._connect(self.ws_url)
    
    def xml_from_rps(self, rps_fields, pretty_print=False):
        rps = self._gen_rps_xml(rps_fields)
        return xml.dump_tostring(rps, xml_declaration=False, pretty_print=pretty_print)

    def add_rps(self, rps_fields):
        rps = self._gen_rps_xml(rps_fields)
        rps_signed = self.sign(rps, reference_uri=rps_fields.get('rps.lote.id'))
        self.rps_batch.append(rps_signed)
        return rps_signed
    
    def send(self):
        ws = self.connect()
        result = []
        errors = []
        for rps in self.rps_batch:
            gerar_nfse_envio = xml.create_root_element('GerarNfseEnvio', ns=self.nsmap)
            gerar_nfse_envio.append(rps.getroot())
            # Find RPS batch ID
            batch_id_tag_path = '{{{xmlns}}}Rps/{{{xmlns}}}InfDeclaracaoPrestacaoServico'.format(xmlns=self.__xmlns__)
            rps_batch_id = gerar_nfse_envio.find(batch_id_tag_path).get('Id')
            # Validate
            xml_data = self._validate_xml(gerar_nfse_envio)
            if xml_data.isvalid():
                nfse_data = xml.dump_tostring(gerar_nfse_envio, xml_declaration=False)
                ws_return = ws.service.GerarNfse(self.__wsdl_header__, nfse_data)
                result.append(
                    {
                        'rps.lote.id': rps_batch_id,
                        'ws.response': ws_return,
                        'xml.request': xml.dump_tostring(gerar_nfse_envio, xml_declaration=False, pretty_print=True),
                    }
                )
            else:
                errors.append(
                    {
                        'rps.lote.id': rps_batch_id,
                        'xml.request': xml.dump_tostring(gerar_nfse_envio, xml_declaration=False, pretty_print=True),
                        'error': xml_data.last_error
                    }
                )
        del ws
        return (result, errors)

    def send_from_xml(self, xml_str):
        ws = self.connect()
        ws_return = ws.service.GerarNfse(self.__wsdl_header__, xml_str)
        del ws
        return ws_return

    def send_batch(self, batch_fields, async_=False):
        result = {}
        errors = {}
        envelop_tag = 'EnviarLoteRpsSincronoEnvio'
        if async_:
            envelop_tag = 'EnviarLoteRpsEnvio'
        batch_fields['lote.rps.quantidade'] = str(len(self.rps_batch))
        lote_rps = xml.create_root_element(
            'LoteRps',
            ns=self.nsmap,
            Id=batch_fields.get('lote.id'),
            versao=self.__api_version__
        )
        xml.add_element(lote_rps, None, 'NumeroLote', text=batch_fields.get('lote.numero'), ns=self.nsmap)
        xml.add_element(lote_rps, None, 'CpfCnpj', ns=self.nsmap)
        if len(batch_fields.get('nf.prestador.documento')) == 11:
            #CPF
            xml.add_element(lote_rps, 'CpfCnpj', 'Cpf', text=batch_fields.get('nf.prestador.documento'), ns=self.nsmap)
        else:
            #CNPJ
            xml.add_element(lote_rps, 'CpfCnpj', 'Cnpj', text=batch_fields.get('nf.prestador.documento'), ns=self.nsmap)
        if batch_fields.get('nf.prestador.inscricao_municipal'):
            xml.add_element(lote_rps, None, 'InscricaoMunicipal', text=batch_fields.get('nf.prestador.inscricao_municipal'), ns=self.nsmap)
        xml.add_element(lote_rps, None, 'QuantidadeRps', text=batch_fields.get('lote.rps.quantidade'), ns=self.nsmap)
        lista_rps = xml.add_element(lote_rps, None, 'ListaRps', ns=self.nsmap)
        for rps in self.rps_batch:
            lista_rps.append(rps.getroot())
        batch_root = xml.create_root_element(envelop_tag, ns=self.nsmap)
        batch_root.append(lote_rps)
        # Sign
        batch_signed = self.sign(batch_root, reference_uri=batch_fields.get('lote.id'))
        xml_data = self._validate_xml(batch_signed)
        if xml_data.isvalid():
            batch_data = xml.dump_tostring(batch_signed, xml_declaration=False)
            ws = self.connect()
            if async_:
                ws_return = ws.service.RecepcionarLoteRps(self.__wsdl_header__, batch_data)
            else:
                ws_return = ws.service.RecepcionarLoteRpsSincrono(self.__wsdl_header__, batch_data)
            result = {
                'lote.id': batch_fields.get('lote.id'),
                'ws.response': ws_return,
                'xml.request': xml.dump_tostring(batch_signed, xml_declaration=False, pretty_print=True),
            }
            del ws
        else:
            errors = {
                'lote.id': batch_fields.get('lote.id'),
                'xml.request': xml.dump_tostring(batch_signed, xml_declaration=False, pretty_print=True),
                'error': xml_data.last_error
            }
        return (result, errors)

    def add_to_cancel(self, nf_fields):
        pedido_root = xml.create_root_element('Pedido', ns=self.nsmap)
        inf_cancel = xml.add_element(
            pedido_root,
            None,
            'InfPedidoCancelamento',
            ns=self.nsmap,
            Id=nf_fields.get('nf.cancela.id')
        )
        identif = xml.add_element(inf_cancel, None, 'IdentificacaoNfse', ns=self.nsmap)
        xml.add_element(identif, None, 'Numero', text=nf_fields.get('nf.numero'), ns=self.nsmap)
        xml.add_element(identif, None, 'CpfCnpj', ns=self.nsmap)
        if len(nf_fields.get('nf.prestador.documento')) == 11: #CPF
            xml.add_element(identif, 'CpfCnpj', 'Cpf', text=nf_fields.get('nf.prestador.documento'), ns=self.nsmap)
        else: # CNPJ
            xml.add_element(identif, 'CpfCnpj', 'Cnpj', text=nf_fields.get('nf.prestador.documento'), ns=self.nsmap)
        if nf_fields.get('nf.prestador.inscricao_municipal'):
            xml.add_element(identif, None, 'InscricaoMunicipal', text=nf_fields.get('nf.prestador.inscricao_municipal'), ns=self.nsmap)
        xml.add_element(identif, None, 'CodigoMunicipio', text=nf_fields.get('nf.codigo_municipio'), ns=self.nsmap)
        if nf_fields.get('nf.codigo_cancelamento'):
            xml.add_element(inf_cancel, None, 'CodigoCancelamento', text=nf_fields.get('nf.codigo_cancelamento'), ns=self.nsmap)
        cancel_signed = self.sign(pedido_root, reference_uri=nf_fields.get('nf.cancela.id'))
        self.cancel_batch.append(cancel_signed)
        return cancel_signed

    def cancel(self):
        result = []
        errors = []
        ws = self.connect()
        for nf_to_cancel in self.cancel_batch:
            cancelar_nfse_envio = xml.create_root_element('CancelarNfseEnvio', ns=self.nsmap)
            cancelar_nfse_envio.append(nf_to_cancel.getroot())
            # Find cancel ID
            cancel_id_tag_path = '{{{xmlns}}}Pedido/{{{xmlns}}}InfPedidoCancelamento'.format(xmlns=self.__xmlns__)
            cancel_id = cancelar_nfse_envio.find(cancel_id_tag_path).get('Id')
            # Validate
            xml_data = self._validate_xml(cancelar_nfse_envio)
            if xml_data.isvalid():
                nfse_cancel_data = xml.dump_tostring(cancelar_nfse_envio, xml_declaration=False)
                ws_return = ws.service.CancelarNfse(self.__wsdl_header__, nfse_cancel_data)
                result.append(
                    {
                        'nf.cancela.id': cancel_id,
                        'ws.response': ws_return,
                        'xml.request': xml.dump_tostring(cancelar_nfse_envio, xml_declaration=False, pretty_print=True),
                    }
                )
            else:
                errors.append(
                    {
                        'nf.cancela.id': cancel_id,
                        'xml.request': xml.dump_tostring(cancelar_nfse_envio, xml_declaration=False, pretty_print=True),
                        'error': xml_data.last_error
                    }
                )
        del ws
        return (result, errors)

    def get_nfse_by_rps(self, params):
        result = {}
        error = {}
        consulta_envio = xml.create_root_element('ConsultarNfseRpsEnvio', ns=self.nsmap)
        xml.add_element(consulta_envio, None, 'IdentificacaoRps', ns=self.nsmap)
        xml.add_element(consulta_envio, 'IdentificacaoRps', 'Numero', text=params.get('rps.numero'), ns=self.nsmap)
        xml.add_element(consulta_envio, 'IdentificacaoRps', 'Serie', text=params.get('rps.serie'), ns=self.nsmap)
        xml.add_element(consulta_envio, 'IdentificacaoRps', 'Tipo', text=params.get('rps.tipo'), ns=self.nsmap)
        xml.add_element(consulta_envio, None, 'Prestador', ns=self.nsmap)
        xml.add_element(consulta_envio, 'Prestador', 'CpfCnpj', ns=self.nsmap)
        if len(params.get('nf.prestador.documento')) == 11: #CPF
            xml.add_element(consulta_envio, 'Prestador/CpfCnpj', 'Cpf', text=params.get('nf.prestador.documento'), ns=self.nsmap)
        else: # CNPJ
            xml.add_element(consulta_envio, 'Prestador/CpfCnpj', 'Cnpj', text=params.get('nf.prestador.documento'), ns=self.nsmap)
        if params.get('nf.prestador.inscricao_municipal'):
            xml.add_element(consulta_envio, 'Prestador', 'InscricaoMunicipal', text=params.get('nf.prestador.inscricao_municipal'), ns=self.nsmap)
        xml_data = self._validate_xml(consulta_envio)
        if xml_data.isvalid():
            ws = self.connect()
            ws_return = ws.service.ConsultarNfsePorRps(self.__wsdl_header__, xml.dump_tostring(consulta_envio, xml_declaration=False))
            del ws
            result = {
                'xml.request': xml.dump_tostring(consulta_envio, xml_declaration=False, pretty_print=True),
                'ws.response': ws_return,
            }
        else:
            error = {
                'xml.request': xml.dump_tostring(consulta_envio, xml_declaration=False, pretty_print=True),
                'error': xml_data.last_error,
            }
        return (result, error)

    def get_nfse(self, params, raw_response=False):
        result = {}
        error = {}
        consulta_nfse = xml.create_root_element('ConsultarNfseFaixaEnvio', ns=self.nsmap)
        xml.add_element(consulta_nfse, None, 'Prestador', ns=self.nsmap)
        xml.add_element(consulta_nfse, 'Prestador', 'CpfCnpj', ns=self.nsmap)
        if len(params.get('nf.prestador.documento')) == 11: #CPF
            xml.add_element(consulta_nfse, 'Prestador/CpfCnpj', 'Cpf', text=params.get('nf.prestador.documento'), ns=self.nsmap)
        else: # CNPJ
            xml.add_element(consulta_nfse, 'Prestador/CpfCnpj', 'Cnpj', text=params.get('nf.prestador.documento'), ns=self.nsmap)
        if params.get('nf.prestador.inscricao_municipal'):
            xml.add_element(consulta_nfse, 'Prestador', 'InscricaoMunicipal', text=params.get('nf.prestador.inscricao_municipal'), ns=self.nsmap)
        xml.add_element(consulta_nfse, None, 'Faixa', ns=self.nsmap)
        xml.add_element(consulta_nfse, 'Faixa', 'NumeroNfseInicial', text=params['nf.numero.inicial'], ns=self.nsmap)
        xml.add_element(consulta_nfse, 'Faixa', 'NumeroNfseFinal', text=params.get('nf.numero.final') or params['nf.numero.inicial'], ns=self.nsmap)
        xml.add_element(consulta_nfse, None, 'Pagina', text=params.get('pagina') or '1', ns=self.nsmap)
        xml_data = self._validate_xml(consulta_nfse)
        if xml_data.isvalid():
            ws = self.connect()
            ws_return = ws.service.ConsultarNfseFaixa(self.__wsdl_header__, xml.dump_tostring(consulta_nfse, xml_declaration=False))
            del ws
            result = {
                'xml.request': xml.dump_tostring(consulta_nfse, xml_declaration=False, pretty_print=True),
                'ws.response': ws_return,
            }
        else:
            error = {
                'xml.request': xml.dump_tostring(consulta_nfse, xml_declaration=False, pretty_print=True),
                'error': xml_data.last_error,
            }
        return (result, error)

    def get_nfse_by_date(self, params, raw_response=False):
        result = {}
        error = {}
        consulta_nfse = xml.create_root_element('ConsultarNfseServicoPrestadoEnvio', ns=self.nsmap)
        xml.add_element(consulta_nfse, None, 'Prestador', ns=self.nsmap)
        xml.add_element(consulta_nfse, 'Prestador', 'CpfCnpj', ns=self.nsmap)
        if len(params.get('nf.prestador.documento')) == 11: #CPF
            xml.add_element(consulta_nfse, 'Prestador/CpfCnpj', 'Cpf', text=params.get('nf.prestador.documento'), ns=self.nsmap)
        else: # CNPJ
            xml.add_element(consulta_nfse, 'Prestador/CpfCnpj', 'Cnpj', text=params.get('nf.prestador.documento'), ns=self.nsmap)
        if params.get('nf.prestador.inscricao_municipal'):
            xml.add_element(consulta_nfse, 'Prestador', 'InscricaoMunicipal', text=params.get('nf.prestador.inscricao_municipal'), ns=self.nsmap)
        if params.get('nf.numero'):
            xml.add_element(consulta_nfse, None, 'NumeroNfse', text=params['nf.numero'], ns=self.nsmap)
        if params.get('nf.data.inicial') and params.get('nf.data.final'):
            xml.add_element(consulta_nfse, None, 'PeriodoEmissao', ns=self.nsmap)
            xml.add_element(consulta_nfse, 'PeriodoEmissao', 'DataInicial', text=params['nf.data.inicial'], ns=self.nsmap)
            xml.add_element(consulta_nfse, 'PeriodoEmissao', 'DataFinal', text=params['nf.data.final'], ns=self.nsmap)
        xml.add_element(consulta_nfse, None, 'Pagina', text=params.get('pagina') or '1', ns=self.nsmap)
        xml_data = self._validate_xml(consulta_nfse)
        if xml_data.isvalid():
            ws = self.connect()
            ws_return = ws.service.ConsultarNfseServicoPrestado(self.__wsdl_header__, xml.dump_tostring(consulta_nfse, xml_declaration=False))
            del ws
            result = {
                'xml.request': xml.dump_tostring(consulta_nfse, xml_declaration=False, pretty_print=True),
                'ws.response': ws_return,
            }
        else:
            error = {
                'xml.request': xml.dump_tostring(consulta_nfse, xml_declaration=False, pretty_print=True),
                'error': xml_data.last_error,
            }
        return (result, error)

    def get_batch_status(self, params):
        result = {}
        error = {}
        consulta_envio = xml.create_root_element('ConsultarLoteRpsEnvio', ns=self.nsmap)
        xml.add_element(consulta_envio, None, 'Prestador', ns=self.nsmap)
        xml.add_element(consulta_envio, 'Prestador', 'CpfCnpj', ns=self.nsmap)
        if len(params.get('nf.prestador.documento')) == 11: #CPF
            xml.add_element(consulta_envio, 'Prestador/CpfCnpj', 'Cpf', text=params.get('nf.prestador.documento'), ns=self.nsmap)
        else: # CNPJ
            xml.add_element(consulta_envio, 'Prestador/CpfCnpj', 'Cnpj', text=params.get('nf.prestador.documento'), ns=self.nsmap)
        if params.get('nf.prestador.inscricao_municipal'):
            xml.add_element(consulta_envio, 'Prestador', 'InscricaoMunicipal', text=params.get('nf.prestador.inscricao_municipal'), ns=self.nsmap)
        xml.add_element(consulta_envio, None, 'Protocolo', text=params.get('lote.protocolo'), ns=self.nsmap)
        xml_data = self._validate_xml(consulta_envio)
        if xml_data.isvalid():
            ws = self.connect()
            ws_return = ws.service.ConsultarLoteRps(self.__wsdl_header__, xml.dump_tostring(consulta_envio, xml_declaration=False))
            del ws
            result = {
                'xml.request': xml.dump_tostring(consulta_envio, xml_declaration=False, pretty_print=True),
                'ws.response': ws_return,
            }
        else:
            error = {
                'xml.request': xml.dump_tostring(consulta_envio, xml_declaration=False, pretty_print=True),
                'error': xml_data.last_error,
            }
        return (result, error)


class NFSeBetha(BaseNFSe):

    __api_version__ = '01'

    def __init__(self, pfx_file=None, pfx_passwd=None, target='production'):
        super(NFSeBetha, self).__init__(pfx_file, pfx_passwd, target)
        self._xsd_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'xsd',
            'betha',
            self.__api_version__,
            'nfse_v{}.xsd'.format(self.__api_version__.replace('.', ''))
        )
        self.ws_url = nfsepmsj.BETHA_WSURL[self.__api_version__][target]

    def connect(self, service):
        url = self.ws_url.format(service=service)
        return self._connect(url)
    
    def add_rps(self, rps_fields):
        rps_id = 'Rps{}{}{}{}'.format(
            rps_fields.get('nf.codigo_municipio'),
            rps_fields.get('rps.numero').rjust(15, '0'),
            rps_fields.get('nf.prestador.documento'),
            datetime.datetime.strptime(rps_fields.get('rps.data.emissao'), '%Y-%m-%dT%H:%M:%S').strftime('%d%m%Y')
        )
        rps_root = xml.create_root_element('Rps', ns=self.nsmap)
        rps = xml.add_element(
            rps_root,
            None,
            'InfRps',
            Id=rps_id,
            ns=self.nsmap
        )
        xml.add_element(rps, None, 'IdentificacaoRps', ns=self.nsmap)
        xml.add_element(rps, 'IdentificacaoRps', 'Numero', text=rps_fields.get('rps.numero'), ns=self.nsmap)
        xml.add_element(rps, 'IdentificacaoRps', 'Serie', text=rps_fields.get('rps.serie'), ns=self.nsmap)
        xml.add_element(rps, 'IdentificacaoRps', 'Tipo', text=rps_fields.get('rps.tipo'), ns=self.nsmap)
        xml.add_element(rps, None, 'DataEmissao', text=rps_fields.get('rps.data.emissao'), ns=self.nsmap)
        xml.add_element(rps, None, 'NaturezaOperacao', text=rps_fields.get('nf.natureza_operacao'), ns=self.nsmap)
        if rps_fields.get('nf.regime_especial_tributacao'):
            xml.add_element(rps, None, 'RegimeEspecialTributacao', text=rps_fields['nf.regime_especial_tributacao'], ns=self.nsmap)
        xml.add_element(rps, None, 'OptanteSimplesNacional', text=rps_fields.get('nf.optante_simples'), ns=self.nsmap)
        xml.add_element(rps, None, 'IncentivadorCultural', text=rps_fields.get('nf.incentivo_fiscal'), ns=self.nsmap)
        xml.add_element(rps, None, 'Status', text=rps_fields.get('rps.status'), ns=self.nsmap)
        if rps_fields.get('rps.substituido.numero'):
            xml.add_element(rps, None, 'RpsSubstituido', ns=self.nsmap)
            xml.add_element(rps, 'RpsSubstituido', 'Numero', text=rps_fields.get('rps.substituido.numero'), ns=self.nsmap)
            xml.add_element(rps, 'RpsSubstituido', 'Serie', text=rps_fields.get('rps.substituido.serie'), ns=self.nsmap)
            xml.add_element(rps, 'RpsSubstituido', 'Tipo', text=rps_fields.get('rps.substituido.tipo'), ns=self.nsmap)
        # Servicos
        servicos = xml.add_element(rps, None, 'Servico', ns=self.nsmap)
        xml.add_element(servicos, None, 'Valores', ns=self.nsmap)
        xml.add_element(servicos, 'Valores', 'ValorServicos', text=rps_fields.get('nf.total_servicos'), ns=self.nsmap)
        self._add_fields_nullable(
            xml_element=servicos,
            fields_data=(
                ('nf.valor_deducoes', 'Valores', 'ValorDeducoes'),
                ('nf.valor_pis', 'Valores', 'ValorPis'),
                ('nf.valor_cofins', 'Valores', 'ValorCofins'),
                ('nf.valor_inss', 'Valores', 'ValorInss'),
                ('nf.valor_IR', 'Valores', 'ValorIr'),
                ('nf.valor_csll', 'Valores', 'ValorCsll'),
            ),
            fields=rps_fields,
            ns=self.nsmap
        )
        xml.add_element(servicos, 'Valores', 'IssRetido', text=rps_fields.get('nf.iss_retido'), ns=self.nsmap)
        self._add_fields_nullable(
            xml_element=servicos,
            fields_data=(
                ('nf.valor_iss', 'Valores', 'ValorIss'),
                ('nf.valor_outros', 'Valores', 'OutrasRetencoes'),
            ),
            fields=rps_fields,
            ns=self.nsmap
        )
        xml.add_element(servicos, 'Valores', 'BaseCalculo', text=rps_fields.get('nf.base_calculo'), ns=self.nsmap)
        self._add_fields_nullable(
            xml_element=servicos,
            fields_data=(
                ('nf.aliquota', 'Valores', 'Aliquota'),
                ('nf.total_nota_liquido', 'Valores', 'ValorLiquidoNfse'),
                ('nf.valor_iss_retido', 'Valores', 'ValorIssRetido'),
                ('nf.desconto_condicionado', 'Valores', 'DescontoCondicionado'),
                ('nf.desconto_incondicionado', 'Valores', 'DescontoIncondicionado'),
            ),
            fields=rps_fields,
            ns=self.nsmap
        )
        xml.add_element(servicos, None, 'ItemListaServico', text=rps_fields.get('nf.codigo_servico'), ns=self.nsmap)
        self._add_fields_nullable(
            xml_element=servicos,
            fields_data=(
                ('nf.codigo_cnae', None, 'CodigoCnae'),
                ('nf.codigo_tributacao_municipio', None, 'CodigoTributacaoMunicipio'),
            ),
            fields=rps_fields,
            ns=self.nsmap
        )
        xml.add_element(servicos, None, 'Discriminacao', text=rps_fields.get('nf.discriminacao'), ns=self.nsmap)
        xml.add_element(servicos, None, 'CodigoMunicipio', text=rps_fields.get('nf.codigo_municipio'), ns=self.nsmap)
        xml.add_element(rps, None, 'Prestador', ns=self.nsmap)
        xml.add_element(rps, 'Prestador', 'Cnpj', text=rps_fields.get('nf.prestador.documento'), ns=self.nsmap)
        if rps_fields.get('nf.prestador.inscricao_municipal'):
            xml.add_element(rps, 'Prestador', 'InscricaoMunicipal', text=rps_fields['nf.prestador.inscricao_municipal'], ns=self.nsmap)
        xml.add_element(rps, None, 'Tomador', ns=self.nsmap)
        if rps_fields.get('nf.tomador.documento'):
            xml.add_element(rps, 'Tomador', 'IdentificacaoTomador', ns=self.nsmap)
            xml.add_element(rps, 'Tomador/IdentificacaoTomador', 'CpfCnpj', ns=self.nsmap)
            if len(rps_fields.get('nf.tomador.documento')) == 11: #CPF
                xml.add_element(rps, 'Tomador/IdentificacaoTomador/CpfCnpj', 'Cpf', text=rps_fields.get('nf.tomador.documento'), ns=self.nsmap)
            else: #CNPJ
                xml.add_element(rps, 'Tomador/IdentificacaoTomador/CpfCnpj', 'Cnpj', text=rps_fields.get('nf.tomador.documento'), ns=self.nsmap)
            self._add_fields_nullable(
                xml_element=rps,
                fields_data=(
                    ('nf.tomador.inscricao_municipal', 'Tomador/IdentificacaoTomador', 'InscricaoMunicipal'),
                    ('nf.tomador.inscricao_estadual', 'Tomador/IdentificacaoTomador', 'InscricaoEstadual'),
                    ('nf.tomador.razao_social', 'Tomador', 'RazaoSocial'),
                ),
                fields=rps_fields,
                ns=self.nsmap
            )
            if rps_fields.get('nf.tomador.logradouro'):
                xml.add_element(rps, 'Tomador', 'Endereco', ns=self.nsmap)
                self._add_fields_nullable(
                    xml_element=rps,
                    fields_data=(
                        ('nf.tomador.logradouro', 'Tomador/Endereco', 'Endereco'),
                        ('nf.tomador.numero_logradouro', 'Tomador/Endereco', 'Numero'),
                        ('nf.tomador.complemento', 'Tomador/Endereco', 'Complemento'),
                        ('nf.tomador.bairro', 'Tomador/Endereco', 'Bairro'),
                        ('nf.tomador.codigo_municipio', 'Tomador/Endereco', 'CodigoMunicipio'),
                        ('nf.tomador.uf', 'Tomador/Endereco', 'Uf'),
                        ('nf.tomador.cep', 'Tomador/Endereco', 'Cep'),
                    ),
                    fields=rps_fields,
                    ns=self.nsmap
                )
            if rps_fields.get('nf.tomador.contato.telefone') or rps_fields.get('nf.tomador.contato.email'):
                xml.add_element(rps, 'Tomador', 'Contato')
                self._add_fields_nullable(
                    xml_element=rps,
                    fields_data=(
                        ('nf.tomador.contato.telefone', 'Tomador/Contato', 'Telefone'),
                        ('nf.tomador.contato.email', 'Tomador/Contato', 'Email'),
                    ),
                    fields=rps_fields,
                    ns=self.nsmap
                )
        # Intermediario
        if self._has_fields('nf.intermediario.', rps_fields):
            xml.add_element(rps, None, 'IntermediarioServico', ns=self.nsmap)
            xml.add_element(rps, 'IntermediarioServico', 'RazaoSocial', text=rps_fields.get('nf.intermediario.razao_social'), ns=self.nsmap)
            xml.add_element(rps, 'IntermediarioServico', 'CpfCnpj', ns=self.nsmap)
            if len(rps_fields.get('nf.intermediario.documento')) == 11:
                xml.add_element(rps, 'IntermediarioServico/CpfCnpj', 'Cpf', text=rps_fields.get('nf.intermediario.documento'), ns=self.nsmap)
            else:
                xml.add_element(rps, 'IntermediarioServico/CpfCnpj', 'Cnpj', text=rps_fields.get('nf.intermediario.documento'), ns=self.nsmap)
            if rps_fields.get('nf.intermediario.inscricao_municipal'):
                xml.add_element(rps, 'IntermediarioServico', 'InscricaoMunicipal', text=rps_fields['nf.intermediario.inscricao_municipal'], ns=self.nsmap)
        # Construcao Civil
        if self._has_fields('nf.construcao_civil.', rps_fields):
            xml.add_element(rps, None, 'ConstrucaoCivil', ns=self.nsmap)
            xml.add_element(rps, 'ConstrucaoCivil', 'CodigoObra', text=rps_fields.get('nf.construcao_civil.codigo_obra'), ns=self.nsmap)
            xml.add_element(rps, 'ConstrucaoCivil', 'Art', text=rps_fields.get('nf.construcao_civil.art'), ns=self.nsmap)
        rps_signed = self.sign(rps_root, reference_uri=rps_id)
        self.rps_batch.append(rps_signed)
        return rps_signed
   
    def send_batch(self, batch_fields, soap_message=False, raw_response=False):
        result = {}
        errors = {}
        batch_fields['lote.rps.quantidade'] = str(len(self.rps_batch))
        lote_rps = xml.create_root_element(
            'LoteRps',
            ns=self.nsmap,
            Id=batch_fields.get('lote.id')
        )
        xml.add_element(lote_rps, None, 'NumeroLote', text=batch_fields.get('lote.numero'), ns=self.nsmap)
        xml.add_element(lote_rps, None, 'Cnpj', text=batch_fields.get('nf.prestador.documento'), ns=self.nsmap)
        xml.add_element(lote_rps, None, 'InscricaoMunicipal', text=batch_fields.get('nf.prestador.inscricao_municipal'), ns=self.nsmap)
        xml.add_element(lote_rps, None, 'QuantidadeRps', text=batch_fields.get('lote.rps.quantidade'), ns=self.nsmap)
        lista_rps = xml.add_element(lote_rps, None, 'ListaRps', ns=self.nsmap)
        for rps in self.rps_batch:
            lista_rps.append(rps.getroot())
        batch_root = xml.create_root_element('EnviarLoteRpsEnvio', ns=self.nsmap)
        batch_root.append(lote_rps)
        # Sign
        batch_signed = self.sign(batch_root, reference_uri=batch_fields.get('lote.id'))
        xml_data = self._validate_xml(batch_signed)
        if xml_data.isvalid():
            # Method EnviarLoteRpsEnvio needs a complex type tcLoteRps, which is a subset of batch_signed element. Zeep can't (as far as I know)
            # send a lxml element or XML string representing that complex type, you need pass a dictionary or instantiate that type with client.get_type() 
            # or similar methods. So we will translate the XML string into a dictionary with "xmltodict" module and than use only the "LoteRps" key.
            batch_data = xmltodict.parse(xml.dump_tostring(batch_signed, xml_declaration=False), attr_prefix='')
            lote_rps_param = batch_data['EnviarLoteRpsEnvio']['LoteRps']
            ws = self.connect('recepcionarLoteRps')
            result = {
                'xml.request': xml.dump_tostring(batch_signed, xml_declaration=False, pretty_print=True),
                'xml.element': batch_signed,
            }
            if soap_message:
                result['soap.message'] = ws.create_message(ws.service, 'EnviarLoteRpsEnvio', lote_rps_param)
            else:
                with ws.settings(strict=False, raw_response=raw_response):
                    ws_result = ws.service.EnviarLoteRpsEnvio(lote_rps_param)
                result['ws.response'] = ws_result
            del ws
        else:
            errors = {
                'xml.request': xml.dump_tostring(batch_signed, xml_declaration=False, pretty_print=True),
                'error': xml_data.last_error,
            }
        return (result, errors)

    def get_batch_status(self, batch_fields):
        # About response:
        # Field "Situacao":
        #   1 - Nao Recebido
        #   2 - Nao Processado
        #   3 - Processado com Erro
        #   4 - Processado com Sucesso
        # However, if batch had errors, "Situacao" is None (???), and the presence of "ListaMensagemRetorno" will tell that:
        # ListaMensagemRetorno: {
        #   MensagemRetorno: [
        #        {
        #            Codigo: 'error code',
        #            Mensagem: 'error message',
        #            Correcao: 'sometimes useful'
        #        }
        #   ]
        # }
        prestador = OrderedDict([
            ('Cnpj', batch_fields.get('nf.prestador.documento'))
        ])
        if batch_fields.get('nf.prestador.inscricao_municipal'):
            prestador['InscricaoMunicipal'] = batch_fields['nf.prestador.inscricao_municipal']
        ws = self.connect('consultarSituacaoLoteRps')
        ws_result = ws.service.ConsultarSituacaoLoteRpsEnvio(prestador, batch_fields.get('lote.protocolo'))
        result = {
            'ws.response': ws_result
        }
        del ws
        return result
    
    def get_nfse_by_rps(self, params, raw_response=False):
        prestador = OrderedDict([
            ('Cnpj', params.get('nf.prestador.documento'))
        ])
        if params.get('nf.prestador.inscricao_municipal'):
            prestador['InscricaoMunicipal'] = params['nf.prestador.inscricao_municipal']
        rps = OrderedDict([
            ('Numero', params.get('rps.numero')),
            ('Serie', params.get('rps.serie')),
            ('Tipo', params.get('rps.tipo')),
        ])
        ws = self.connect('consultarNfsePorRpsV110')
        # The XML response is invalid according their own XSD (!?!?!), so setting the request do not apply validation on response
        with ws.settings(strict=False, raw_response=raw_response):
            ws_result = ws.service.ConsultarNfsePorRpsEnvio(rps, prestador)
        result = {
            'ws.response': ws_result
        }
        del ws
        return result

    def get_nfse(self, params, raw_response=False):
        prestador = OrderedDict([
            ('Cnpj', params.get('nf.prestador.documento'))
        ])
        if params.get('nf.prestador.inscricao_municipal'):
            prestador['InscricaoMunicipal'] = params['nf.prestador.inscricao_municipal']
        numero_nfse = xsd.SkipValue
        if params.get('nf.numero'):
            numero_nfse = params['nf.numero']
        periodo_emissao = xsd.SkipValue
        if params.get('nf.data.inicial') and params.get('nf.data.final'):
            periodo_emissao = OrderedDict([
                ('DataInicial', params['nf.data.inicial']),
                ('DataFinal', params['nf.data.final']),
            ])
        tomador = xsd.SkipValue
        # Tomador fields
        if self._has_fields('nf.tomador.', params):
            tomador = OrderedDict()
            if params.get('nf.tomador.documento'):
                if len(params['nf.tomador.documento']) == 11:
                    tomador['CpfCnpj'] = {'Cpf': params['nf.tomador.documento']}
                else:
                    tomador['CpfCnpj'] = {'Cnpj': params['nf.tomador.documento']}
            if params.get('nf.tomador.inscricao_municipal'):
                tomador['InscricaoMnunicipal'] = params['nf.tomador.inscricao_municipal']
            if params.get('nf.tomador.inscricao_estadual'):
                tomador['InscricaoEstadual'] = params['nf.tomador.inscricao_estadual']
        # Intermediario fields
        intermediario_servico = xsd.SkipValue
        if self._has_fields('nf.intermediario.', params):
            intermediario_servico = OrderedDict([
                ('RazaoSocial', params['nf.intermediario.razao_social']),
            ])
            if len(params['nf.intermediario.documento']) == 11:
                intermediario_servico['CpfCnpj'] = {'Cpf': params['nf.intermediario.documento']}
            else:
                intermediario_servico['CpfCnpj'] = {'Cnpj': params['nf.intermediario.documento']}
            if params.get('nf.intermediario.inscricao_municipal'):
                intermediario_servico['InscricaoMunicipal'] = params['nf.intermediario.inscricao_municipal']
        ws = self.connect('consultarNfseV110')
        # The XML response is invalid according their own XSD (!?!?!), so setting the request do not apply validation on response
        with ws.settings(strict=False, raw_response=raw_response):
            ws_result = ws.service.ConsultarNfseEnvio(prestador, numero_nfse, periodo_emissao, tomador, intermediario_servico)
        result = {
            'ws.response': ws_result
        }
        del ws
        return result

    def add_to_cancel(self, nf_fields):
        cancel_root = xml.create_root_element('CancelarNfseEnvio', ns=self.nsmap)
        pedido = xml.create_root_element('Pedido', ns=self.nsmap)
        xml.add_element(pedido, None, 'InfPedidoCancelamento', ns=self.nsmap)
        xml.add_element(pedido, 'InfPedidoCancelamento', 'IdentificacaoNfse', ns=self.nsmap)
        xml.add_element(pedido, 'InfPedidoCancelamento/IdentificacaoNfse', 'Numero', text=nf_fields.get('nf.numero'), ns=self.nsmap)
        xml.add_element(pedido, 'InfPedidoCancelamento/IdentificacaoNfse', 'Cnpj', text=nf_fields.get('nf.prestador.documento'), ns=self.nsmap)
        if nf_fields.get('nf.prestador.inscricao_municipal'):
            xml.add_element(pedido, 'InfPedidoCancelamento/IdentificacaoNfse', 'InscricaoMunicipal', text=nf_fields.get('nf.prestador.inscricao_municipal'), ns=self.nsmap)
        if self.target == 'test':
            # On test environment, the cancel method only works if CodigoMunicipio is set to '0000000' (?!?!?!)
            xml.add_element(pedido, 'InfPedidoCancelamento/IdentificacaoNfse', 'CodigoMunicipio', text='0000000', ns=self.nsmap)
        else:
            xml.add_element(pedido, 'InfPedidoCancelamento/IdentificacaoNfse', 'CodigoMunicipio', text=nf_fields.get('nf.codigo_municipio'), ns=self.nsmap)
        xml.add_element(pedido, 'InfPedidoCancelamento', 'CodigoCancelamento', text=nf_fields.get('nf.codigo_cancelamento'), ns=self.nsmap)
        pedido_signed = self.sign(pedido)
        cancel_root.append(pedido_signed.getroot())
        self.cancel_batch.append(cancel_root)
        return cancel_root
    
    def cancel(self, strict=True, raw_response=False):
        result = []
        errors = []
        ws = self.connect('cancelarNfse')
        for nf in self.cancel_batch:
            xml_data = self._validate_xml(nf)
            if xml_data.isvalid():
                with ws.settings(strict=strict, raw_response=raw_response):
                    data = xmltodict.parse(xml.dump_tostring(nf,xml_declaration=False), attr_prefix='')
                    ws_result = ws.service.CancelarNfseEnvio(data['CancelarNfseEnvio']['Pedido'])
                    result.append({
                        'xml.request': xml.dump_tostring(nf, xml_declaration=False, pretty_print=True),
                        'ws.response': ws_result,
                    })
            else:
                errors.append({
                    'xml.request': xml.dump_tostring(nf, xml_declaration=False, pretty_print=True),
                    'error': xml_data.last_error,
                })
        del ws
        return (result, errors)