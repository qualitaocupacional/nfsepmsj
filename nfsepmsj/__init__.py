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

__version__ = '0.0.4'

ABRASF_WSURL = {
    '2.02': {
        'production': 'https://e-gov.betha.com.br/e-nota-contribuinte-ws/nfseWS?wsdl',
        'test': 'https://e-gov.betha.com.br/e-nota-contribuinte-test-ws/nfseWS?wsdl',
    }
}

BETHA_WSURL = {
    '01': {
        'production': 'https://e-gov.betha.com.br/e-nota-contribuinte-ws/{service}?wsdl',
        'test': 'https://e-gov.betha.com.br/e-nota-contribuinte-test-ws/{service}?wsdl',
    }
}

# Betha Services available:
# ## Recepcao e Processamento de RPS
# recepcionarLoteRps

# ## Consulta de Situacao de Lote de RPS
# consultarSituacaoLoteRps

# ## Consulta de Lote de RPS (com condicao de pagamento)
# consultarLoteRpsV110

# ## Consulta de NFS-e por RPS (com condicao de pagamento)
# consultarNfsePorRpsV110

# ## Consulta de NFS-e (com condicao de pagamento)
# consultarNfseV110

# ## Cancelamento de NFS-e
# cancelarNfse

# ## Consulta de Taxas Diversas
# consultarTaxasDiversas

