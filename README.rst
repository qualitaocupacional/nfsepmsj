NFSe de São José - Santa Catarina
=================================

Biblioteca para auxiliar a assinar, gerar e consultar NFSe da Prefeitura Municipal de São José.
Padrão **ABRASF** da **Betha Software**.

Instalação
----------

A biblioteca está disponível no PyPi:

.. code::

    user@host:~$ pip install nfsepmsj

Desenvolvimento
---------------

Clonar o repositório:

.. code::

    user@host:~$ git clone https://github.com/qualitaocupacional/nfsepmsj.git

Instalar a lib em modo desenvolvimento:

.. code::

    (virtualenv) user@host:~/nfsepmsj$ pip install -e ".[testing]"

Usando
------

.. code:: python

    from nfsepmsj.client import NFSeAbrasf

    pfx_file = '/caminho/do/arquivo.pfx'
    pfx_passwd = 'Senha do arquivo pfx'

    nfse = NFSeAbrasf(pfx_file, pfx_passwd)
    nf_data = {
        'rps.lote.id': 'loteid',
        'nf.data.emissao': 'AAAA-MM-DD',
        'nf.total_nota': '100.30'
        # demais campos...
    }
    nfse.add_rps(data)
    result, errors = nfse.send()

*result* vai ser uma lista de dicionários com a estrutura:

.. code:: javascript

    [
        {
            'rps.lote.id': 'loteid',
            'xml.response': 'XML com a resposta do webservices',
            'xml.request': 'o XML que foi gerado para envio',
        }
    ]

E *errors*, se houver algum, como, por exemplo, erro de validação do XML, vai ser:

.. code:: javascript

    [
        {
            'rps.lote.id': 'loteid',
            'xml.request': 'o XML que foi gerado para envio',
            'error': 'a mensagem do erro'
        }
    ]

Para utilizar o ambiente de **Testes** ao invés do de **Produção**:

.. code:: python

    from nfsepmsj.client import NFSeAbrasf

    nfse = NFSeAbrasf(pfx_file, pfx_passwd, 'test')
    # ...

Estrutura do dicionário com os campos da nota fiscal:

+---------------------------------------+------------------------------+
| Nome                                  | Descrição                    |
+=======================================+==============================+
| 'rps.lote.id'                         | Identificação única do lote  |
+---------------------------------------+------------------------------+
| 'rps.numero'                          |                              |
+---------------------------------------+------------------------------+
| 'rps.serie'                           |                              |
+---------------------------------------+------------------------------+
| 'rps.tipo'                            |                              |
+---------------------------------------+------------------------------+
| 'rps.data.emissao'                    |                              |
+---------------------------------------+------------------------------+
| 'rps.status'                          | 1-Normal, 2-Cancelado        |
+---------------------------------------+------------------------------+
| 'rps.substituido.numero'              |                              |
+---------------------------------------+------------------------------+
| 'rps.substituido.serie'               |                              |
+---------------------------------------+------------------------------+
| 'rps.substituido.tipo'                |                              |
+---------------------------------------+------------------------------+
| 'nf.data.emissao'                     |                              |
+---------------------------------------+------------------------------+
| 'nf.total_servicos'                   |                              |
+---------------------------------------+------------------------------+
| 'nf.valor_deducoes'                   |                              |
+---------------------------------------+------------------------------+
| 'nf.valor_pis'                        |                              |
+---------------------------------------+------------------------------+
| 'nf.valor_cofins'                     |                              |
+---------------------------------------+------------------------------+
| 'nf.valor_inss'                       |                              |
+---------------------------------------+------------------------------+
| 'nf.valor_IR'                         |                              |
+---------------------------------------+------------------------------+
| 'nf.valor_csll'                       |                              |
+---------------------------------------+------------------------------+
| 'nf.valor_outros'                     |                              |
+---------------------------------------+------------------------------+
| 'nf.valor_iss'                        |                              |
+---------------------------------------+------------------------------+
| 'nf.aliquota'                         |                              |
+---------------------------------------+------------------------------+
| 'nf.desconto_incondicionado'          |                              |
+---------------------------------------+------------------------------+
| 'nf.desconto_condicionado'            |                              |
+---------------------------------------+------------------------------+
| 'nf.iss_retido'                       |                              |
+---------------------------------------+------------------------------+
| 'nf.responsavel_retencao'             |                              |
+---------------------------------------+------------------------------+
| 'nf.codigo_servico'                   |                              |
+---------------------------------------+------------------------------+
| 'nf.codigo_cnae'                      |                              |
+---------------------------------------+------------------------------+
| 'nf.codigo_tributacao_municipio'      |                              |
+---------------------------------------+------------------------------+
| 'nf.discriminacao'                    |                              |
+---------------------------------------+------------------------------+
| 'nf.codigo_municipio'                 |                              |
+---------------------------------------+------------------------------+
| 'nf.codigo_pais'                      |                              |
+---------------------------------------+------------------------------+
| 'nf.exigibilidade_iss'                |                              |
+---------------------------------------+------------------------------+
| 'nf.codigo_municipio_incidencia'      |                              |
+---------------------------------------+------------------------------+
| 'nf.numero_processo'                  |                              |
+---------------------------------------+------------------------------+
| 'nf.prestador.documento'              |                              |
+---------------------------------------+------------------------------+
| 'nf.prestador.inscricao_municipal'    |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.documento'                |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.inscricao_municipal'      |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.razao_social'             |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.logradouro'               |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.numero_logradouro'        |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.complemento'              |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.bairro'                   |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.codigo_municipio'         |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.uf'                       |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.codigo_pais'              |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.cep'                      |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.contato.telefone'         |                              |
+---------------------------------------+------------------------------+
| 'nf.tomador.contato.email'            |                              |
+---------------------------------------+------------------------------+
| 'nf.regime_especial_tributacao'       |                              |
+---------------------------------------+------------------------------+
| 'nf.optante_simples'                  |                              |
+---------------------------------------+------------------------------+
| 'nf.incentivo_fiscal'                 |                              |
+---------------------------------------+------------------------------+
| 'nf.intermediario.razao_social        |                              |
+---------------------------------------+------------------------------+
| 'nf.intermediario.documento           |                              |
+---------------------------------------+------------------------------+
| 'nf.intermediario.inscricao_municipal |                              |
+---------------------------------------+------------------------------+
| 'nf.construcao_civil.codigo_obra      |                              |
+---------------------------------------+------------------------------+
| 'nf.construcao_civil.art              |                              |
+---------------------------------------+------------------------------+

Campos adicionais para **Cancelamento** de NFSe:

+-------------------------------------+--------------------------------------+
| Nome                                | Descrição                            |
+=====================================+======================================+
| 'nf.cancela.id'                     | Identificação única do cancelamento  |
+-------------------------------------+--------------------------------------+
| 'nf.numero'                         | Número da NFSe gerada                |
+-------------------------------------+--------------------------------------+
| 'nf.codigo_cancelamento'            | Código do cancelamento               |
+-------------------------------------+--------------------------------------+

O **Código do Cancelamento** é obrigatório, apesar que na documentação da versão **2.02** informar que esse código é opcional.
Sem esse código o webservices retorna **"Erro desconhecido"**.

Os valores possíveis são:

* 1 - Erro na emissão
* 2 - Serviço não prestado
* 3 - Erro de assinatura
* 4 - Duplicidade da nota
* 5 - Erro de processamento

Sendo que os códigos **3** e **5** são de uso restrito da Administração Tributária Municipal.

**Cancelando uma NFSe**

.. code:: python

    from nfsepmsj.client import NFSeAbrasf

    pfx_file = '/caminho/do/arquivo.pfx'
    pfx_passwd = 'Senha do arquivo pfx'

    nfse = NFSeAbrasf(pfx_file, pfx_passwd)
    cancel_data = {
        'nf.cancela.id': 'cancel_id1',
        'nf.codigo_cancelamento': '1',
        'nf.numero': '1',
        'nf.prestador.documento': '99999999999999',
        'nf.prestador.inscricao_municipal': '9999999',
        'nf.codigo_municipio': '4216602',
    }
    nfse.add_to_cancel(cancel_data)
    result, errors = nfse.cancel()

*result* vai ser uma lista de dicionários com a estrutura:

.. code:: javascript

    [
        {
            'nf.cancela.id': 'cancel_id1',
            'xml.response': 'XML com a resposta do webservices',
            'xml.request': 'o XML que foi gerado para envio',
        }
    ]

E *errors*, se houver algum, como, por exemplo, erro de validação do XML, vai ser:

.. code:: javascript

    [
        {
            'nf.cancela.id': 'cancel_id1',
            'xml.request': 'o XML que foi gerado para envio',
            'error': 'a mensagem do erro'
        }
    ]


Campos adicionais para **Envio em Lote** de NFSe:

+-------------------------------------+--------------------------------------+
| Nome                                | Descrição                            |
+=====================================+======================================+
| 'lote.id'                           | Identificação única do lote          |
+-------------------------------------+--------------------------------------+
| 'lote.numero'                       | Número do lote                       |
+-------------------------------------+--------------------------------------+
| 'nf.prestador.documento'            | CPF/CNPJ do prestador                |
+-------------------------------------+--------------------------------------+
| 'nf.prestador.inscricao_municipal'  | Inscrição municipal do prestador     |
+-------------------------------------+--------------------------------------+

Lembrando que nesta modalidade os dados de RPS devem conter os campos:

* 'rps.numero'
* 'rps.serie'
* 'rps.tipo'
* 'rps.data.emissao'
* 'rps.status'

**Enviando um lote (sincrono)**

.. code:: python

    from nfsepmsj.client import NFSeAbrasf

    pfx_file = '/caminho/do/arquivo.pfx'
    pfx_passwd = 'Senha do arquivo pfx'

    nfse = NFSeAbrasf(pfx_file, pfx_passwd)
    # ...

    nfse.add_rps(rps01_data)
    nfse.add_rps(rps02_data)
    # ...
    batch_data = {
        'lote.id': 'lote_id',
        'lote.numero': '201901',
        'nf.prestador.documento': '99999999999999',
        'nf.prestador.inscricao_municipal': '9999999',
    }
    result, errors = nfse.send_batch(batch_data)


*result* vai ser um dicionário com a estrutura:

.. code:: javascript

    {
        'lote.id': 'lote_id',
        'xml.response': 'XML com a resposta do webservices',
        'xml.request': 'o XML que foi gerado para envio',
    }

E *errors*, se houver algum, como, por exemplo, erro de validação do XML, vai ser:

.. code:: javascript

    {
        'lote.id': 'lote_id',
        'xml.request': 'o XML que foi gerado para envio',
        'error': 'a mensagem do erro'
    }

**Consultando o Status de um Lote**

Campos adicionais para **Consulta de Lote** de NFSe:

+-------------------------------------+-----------------------------------------------------------------------+
| Nome                                | Descrição                                                             |
+=====================================+=======================================================================+
| 'lote.protocolo'                    | Número do protocolo recebido (geralmente ao enviar lotes assíncronos) |
+-------------------------------------+-----------------------------------------------------------------------+

.. code:: python

    from nfsepmsj.client import NFSeAbrasf

    pfx_file = '/caminho/do/arquivo.pfx'
    pfx_passwd = 'Senha do arquivo pfx'

    nfse = NFSeAbrasf(pfx_file, pfx_passwd)
    params = {
        'lote.protocolo': '12346',
        'nf.prestador.documento': '99999999999999',
        'nf.prestador.inscricao_municipal': '9999999',
    }
    result, error = nfse.get_batch_status(params)


*result* vai ser um dicionário com a estrutura:

.. code:: javascript

    {
        'xml.response': 'XML com a resposta do webservices',
        'xml.request': 'o XML que foi gerado para envio',
    }

E *error*, se houver algum, como, por exemplo, erro de validação do XML, vai ser:

.. code:: javascript

    {
        'xml.request': 'o XML que foi gerado para envio',
        'error': 'a mensagem do erro'
    }
