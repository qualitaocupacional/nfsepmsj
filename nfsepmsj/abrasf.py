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

import nfsepmsj
from nfsepmsj import xml
from nfsepmsj.base import BaseNFSe


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
