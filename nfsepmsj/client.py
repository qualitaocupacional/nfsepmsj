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

from zeep import Client

from lxml import etree

class NFSe(object):

    __xmlns__ = 'http://www.betha.com.br/e-nota-contribuinte-ws'
    __wsdl_header__ = '<cabecalho xmlns="http://www.betha.com.br/e-nota-contribuinte-ws" versao="2.02"><versaoDados>2.02</versaoDados></cabecalho>'

    def __init__(self, pfx_file, pfx_passwd, target='production'):
        if pfx_file is not None:
            self.cert_data = pkcs12_data(pfx_file, pfx_passwd)
        else:
            self.cert_data = None
        self.rps_batch = []
        self.cancel_batch = []
        self.ws_url = nfsepmsj.WSURL[target]

    def _connect(self):
        return Client(self.ws_url)

    def _validate_xml(self, xml_element):
        if not isinstance(xml_element, etree._ElementTree):
            xml_element = etree.ElementTree(xml_element)
        return xml.XMLValidate(xml_element)

    def _add_rps_nullable(self, xml_element, fields_data, rps_fields, ns=None):
        '''Check nullable fields to add to XML tree.

        *xml_element*: A lxml._ElementTree
        *fields_data*: ((field_name, xml_path, xml_tag), ...)
        *rps_fields*: Dictionary with RPS fields = {'field_name': 'field_value'}
        *ns*: Namespace map
        '''
        for row in fields_data:
            field_name, xml_path, xml_tag = row
            if rps_fields.get(field_name):
                xml.add_element(xml_element, xml_path, xml_tag, text=rps_fields.get(field_name), ns=ns)

    def add_rps(self, rps_fields=None):
        nsmap = {None: self.__xmlns__}
        if rps_fields is not None:
            rps = xml.create_root_element('Rps', ns=nsmap)
            inf_declaracao = xml.add_element(
                rps,
                None,
                'InfDeclaracaoPrestacaoServico',
                ns=nsmap,
                Id=rps_fields.get('rps.lote.id')
            )
            # Rps
            if rps_fields.get('rps.numero'):
                rps_in = xml.add_element(inf_declaracao, None, 'Rps', ns=nsmap)
                xml.add_element(rps_in, None, 'IdentificacaoRps', ns=nsmap)
                xml.add_element(rps_in, 'IdentificacaoRps', 'Numero', text=rps_fields.get('rps.numero'), ns=nsmap)
                xml.add_element(rps_in, 'IdentificacaoRps', 'Serie', text=rps_fields.get('rps.serie'), ns=nsmap)
                xml.add_element(rps_in, 'IdentificacaoRps', 'Tipo', text=rps_fields.get('rps.tipo'), ns=nsmap)
                xml.add_element(rps_in, None, 'DataEmissao', text=rps_fields.get('rps.data.emissao'), ns=nsmap)
                xml.add_element(rps_in, None, 'Status', text=rps_fields.get('rps.status'), ns=nsmap)
                if rps_fields.get('rps.substituido.numero'):
                    xml.add_element(rps_in, None, 'RpsSubstituido', ns=nsmap)
                    xml.add_element(rps_in, 'RpsSubstituido', 'Numero', text=rps_fields.get('rps.substituido.numero'), ns=nsmap)
                    xml.add_element(rps_in, 'RpsSubstituido', 'Serie', text=rps_fields.get('rps.substituido.serie'), ns=nsmap)
                    xml.add_element(rps_in, 'RpsSubstituido', 'Tipo', text=rps_fields.get('rps.substituido.tipo'), ns=nsmap)
            xml.add_element(inf_declaracao, None, 'Competencia', text=rps_fields.get('nf.data.emissao'), ns=nsmap)
            # Servicos
            servicos = xml.add_element(inf_declaracao, None, 'Servico', ns=nsmap)
            xml.add_element(servicos, None, 'Valores', ns=nsmap)
            xml.add_element(servicos, 'Valores', 'ValorServicos', text=rps_fields.get('nf.total_nota'), ns=nsmap)
            # if rps_fields.get('nf.total_deducoes'):
            #     xml.add_element(servicos, 'Servico/Valores', 'ValorDeducoes', text=rps_fields.get('nf.total_deducoes'), ns=nsmap)
            self._add_rps_nullable(
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
                rps_fields=rps_fields,
                ns=nsmap
            )
            xml.add_element(servicos, None, 'IssRetido', text=rps_fields.get('nf.iss_retido'), ns=nsmap)
            if rps_fields.get('nf.responsavel_retencao'):
                xml.add_element(servicos, None, 'ResponsavelRetencao', text=rps_fields.get('nf.responsavel_retencao'), ns=nsmap)
            xml.add_element(servicos, None, 'ItemListaServico', text=rps_fields.get('nf.codigo_servico'), ns=nsmap)
            self._add_rps_nullable(
                xml_element=servicos,
                fields_data=(
                    ('nf.codigo_cnae', None, 'CodigoCnae'),
                    ('nf.codigo_tributacao_municipio', None, 'CodigoTributacaoMunicipio'),
                ),
                rps_fields=rps_fields,
                ns=nsmap
            )
            xml.add_element(servicos, None, 'Discriminacao', text=rps_fields.get('nf.discriminacao'), ns=nsmap)
            xml.add_element(servicos, None, 'CodigoMunicipio', text=rps_fields.get('nf.codigo_municipio'), ns=nsmap)
            if rps_fields.get('nf.codigo_pais'):
                xml.add_element(servicos, None, 'CodigoPais', text=rps_fields.get('nf.codigo_pais'), ns=nsmap)
            xml.add_element(servicos, None, 'ExigibilidadeISS', text=rps_fields.get('nf.exigibilidade_iss'), ns=nsmap)
            self._add_rps_nullable(
                xml_element=servicos,
                fields_data=(
                    ('nf.codigo_municipio_incidencia', None, 'MunicipioIncidencia'),
                    ('nf.numero_processo', None, 'NumeroProcesso'),
                ),
                rps_fields=rps_fields,
                ns=nsmap
            )
            xml.add_element(inf_declaracao, None, 'Prestador', ns=nsmap)
            xml.add_element(inf_declaracao, 'Prestador', 'CpfCnpj', ns=nsmap)
            if rps_fields.get('nf.prestador.documento'):
                if len(rps_fields.get('nf.prestador.documento')) == 11: #CPF
                    xml.add_element(inf_declaracao, 'Prestador/CpfCnpj', 'Cpf', text=rps_fields.get('nf.prestador.documento'), ns=nsmap)
                else: # CNPJ
                    xml.add_element(inf_declaracao, 'Prestador/CpfCnpj', 'Cnpj', text=rps_fields.get('nf.prestador.documento'), ns=nsmap)
            if rps_fields.get('nf.prestador.inscricao_municipal'):
                xml.add_element(inf_declaracao, 'Prestador', 'InscricaoMunicipal', text=rps_fields.get('nf.prestador.inscricao_municipal'), ns=nsmap)
            if rps_fields.get('nf.tomador.documento'):
                xml.add_element(inf_declaracao, None, 'Tomador', ns=nsmap)
                xml.add_element(inf_declaracao, 'Tomador', 'IdentificacaoTomador', ns=nsmap)
                xml.add_element(inf_declaracao, 'Tomador/IdentificacaoTomador', 'CpfCnpj', ns=nsmap)
                if len(rps_fields.get('nf.tomador.documento')) == 11: #CPF
                    xml.add_element(inf_declaracao, 'Tomador/IdentificacaoTomador/CpfCnpj', 'Cpf', text=rps_fields.get('nf.tomador.documento'), ns=nsmap)
                else: #CNPJ
                    xml.add_element(inf_declaracao, 'Tomador/IdentificacaoTomador/CpfCnpj', 'Cnpj', text=rps_fields.get('nf.tomador.documento'), ns=nsmap)
                self._add_rps_nullable(
                    xml_element=inf_declaracao,
                    fields_data=(
                        ('nf.tomador.inscricao_municipal', 'Tomador/IdentificacaoTomador', 'InscricaoMunicipal'),
                        ('nf.tomador.razao_social', 'Tomador', 'RazaoSocial'),
                    ),
                    rps_fields=rps_fields,
                    ns=nsmap
                )
                if rps_fields.get('nf.tomador.logradouro'):
                    xml.add_element(inf_declaracao, 'Tomador', 'Endereco', ns=nsmap)
                    self._add_rps_nullable(
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
                        rps_fields=rps_fields,
                        ns=nsmap
                    )
                if rps_fields.get('nf.tomador.contato.telefone') or rps_fields.get('nf.tomador.contato.email'):
                    xml.add_element(inf_declaracao, 'Tomador', 'Contato')
                    self._add_rps_nullable(
                        xml_element=inf_declaracao,
                        fields_data=(
                            ('nf.tomador.contato.telefone', 'Tomador/Contato', 'Telefone'),
                            ('nf.tomador.contato.email', 'Tomador/Contato', 'Email'),
                        ),
                        rps_fields=rps_fields,
                        ns=nsmap
                    )
            # Intermediario

            # Construcao Civil

            if rps_fields.get('nf.regime_especial_tributacao'):
                xml.add_element(inf_declaracao, None, 'RegimeEspecialTributacao', text=rps_fields.get('nf.regime_especial_tributacao'), ns=nsmap)
            xml.add_element(inf_declaracao, None, 'OptanteSimplesNacional', text=rps_fields.get('nf.optante_simples'), ns=nsmap)
            xml.add_element(inf_declaracao, None, 'IncentivoFiscal', text=rps_fields.get('nf.incentivo_fiscal'), ns=nsmap)
            rps_signed = xml.sign(etree.ElementTree(rps), self.cert_data, reference_uri=rps_fields.get('rps.lote.id'))
            self.rps_batch.append(rps_signed)

    def clear_rps_batch(self):
        del self.rps_batch
        self.rps_batch = []

    def clear_cancel_batch(self):
        del self.cancel_batch
        self.cancel_batch = []

    def send(self):
        ws = self._connect()
        result = []
        errors = []
        nsmap = {None: self.__xmlns__}
        for rps in self.rps_batch:
            gerar_nfse_envio = xml.create_root_element('GerarNfseEnvio', ns=nsmap)
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
                        'xml.response': ws_return,
                        'xml': xml.dump_tostring(gerar_nfse_envio, xml_declaration=False, pretty_print=True),
                    }
                )
            else:
                errors.append(
                    {
                        'rps.lote.id': rps_batch_id,
                        'xml': xml.dump_tostring(gerar_nfse_envio, xml_declaration=False, pretty_print=True),
                        'error': xml_data.last_error
                    }
                )
        del ws
        return (result, errors)

    def send_batch(self, batch_fields):
        result = {}
        errors = {}
        nsmap = {None: self.__xmlns__}
        batch_fields['lote.rps.quantidade'] = str(len(self.rps_batch))
        lote_rps = xml.create_root_element(
            'LoteRps',
            ns=nsmap,
            Id=batch_fields.get('lote.id'),
            versao='2.02'
        )
        xml.add_element(lote_rps, None, 'NumeroLote', text=batch_fields.get('lote.numero'), ns=nsmap)
        xml.add_element(lote_rps, None, 'CpfCnpj', ns=nsmap)
        if len(batch_fields.get('nf.prestador.documento')) == 11:
            #CPF
            xml.add_element(lote_rps, 'CpfCnpj', 'Cpf', text=batch_fields.get('nf.prestador.documento'), ns=nsmap)
        else:
            #CNPJ
            xml.add_element(lote_rps, 'CpfCnpj', 'Cnpj', text=batch_fields.get('nf.prestador.documento'), ns=nsmap)
        if batch_fields.get('nf.prestador.inscricao_municipal'):
            xml.add_element(lote_rps, None, 'InscricaoMunicipal', text=batch_fields.get('nf.prestador.inscricao_municipal'), ns=nsmap)
        xml.add_element(lote_rps, None, 'QuantidadeRps', text=batch_fields.get('lote.rps.quantidade'), ns=nsmap)
        lista_rps = xml.add_element(lote_rps, None, 'ListaRps', ns=nsmap)
        for rps in self.rps_batch:
            lista_rps.append(rps.getroot())
        batch_root = xml.create_root_element('EnviarLoteRpsSincronoEnvio', ns=nsmap)
        batch_root.append(lote_rps)
        # Sign
        batch_signed = xml.sign(etree.ElementTree(batch_root), self.cert_data, reference_uri=batch_fields.get('lote.id'))
        xml_data = self._validate_xml(batch_signed)
        if xml_data.isvalid():
            batch_data = xml.dump_tostring(batch_signed, xml_declaration=False)
            ws = self._connect()
            ws_return = ws.service.RecepcionarLoteRpsSincrono(self.__wsdl_header__, batch_data)
            result = {
                'lote.id': batch_fields.get('lote.id'),
                'xml.response': ws_return,
                'xml': xml.dump_tostring(batch_signed, xml_declaration=False, pretty_print=True),
            }
            del ws
        else:
            errors = {
                'lote.id': batch_fields.get('lote.id'),
                'xml': xml.dump_tostring(batch_signed, xml_declaration=False, pretty_print=True),
                'error': xml_data.last_error
            }
        return (result, errors)

    def add_to_cancel(self, nf_fields):
        nsmap = {None: self.__xmlns__}
        pedido_root = xml.create_root_element('Pedido', ns=nsmap)
        inf_cancel = xml.add_element(
            pedido_root,
            None,
            'InfPedidoCancelamento',
            ns=nsmap,
            Id=nf_fields.get('nf.cancela.id')
        )
        identif = xml.add_element(inf_cancel, None, 'IdentificacaoNfse', ns=nsmap)
        xml.add_element(identif, None, 'Numero', text=nf_fields.get('nf.numero'), ns=nsmap)
        xml.add_element(identif, None, 'CpfCnpj', ns=nsmap)
        if len(nf_fields.get('nf.prestador.documento')) == 11: #CPF
            xml.add_element(identif, 'CpfCnpj', 'Cpf', text=nf_fields.get('nf.prestador.documento'), ns=nsmap)
        else: # CNPJ
            xml.add_element(identif, 'CpfCnpj', 'Cnpj', text=nf_fields.get('nf.prestador.documento'), ns=nsmap)
        if nf_fields.get('nf.prestador.inscricao_municipal'):
            xml.add_element(identif, None, 'InscricaoMunicipal', text=nf_fields.get('nf.prestador.inscricao_municipal'), ns=nsmap)
        xml.add_element(identif, None, 'CodigoMunicipio', text=nf_fields.get('nf.codigo_municipio'), ns=nsmap)
        if nf_fields.get('nf.codigo_cancelamento'):
            xml.add_element(inf_cancel, None, 'CodigoCancelamento', text=nf_fields.get('nf.codigo_cancelamento'), ns=nsmap)
        cancel_signed = xml.sign(etree.ElementTree(pedido_root), self.cert_data, reference_uri=nf_fields.get('nf.cancela.id'))
        self.cancel_batch.append(cancel_signed)

    def cancel(self):
        result = []
        errors = []
        nsmap = {None: self.__xmlns__}
        ws = self._connect()
        for nf_to_cancel in self.cancel_batch:
            cancelar_nfse_envio = xml.create_root_element('CancelarNfseEnvio', ns=nsmap)
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
                        'xml.response': ws_return,
                        'xml': xml.dump_tostring(cancelar_nfse_envio, xml_declaration=False, pretty_print=True),
                    }
                )
            else:
                errors.append(
                    {
                        'nf.cancela.id': cancel_id,
                        'xml': xml.dump_tostring(cancelar_nfse_envio, xml_declaration=False, pretty_print=True),
                        'error': xml_data.last_error
                    }
                )
        del ws
        return (result, errors)
        
