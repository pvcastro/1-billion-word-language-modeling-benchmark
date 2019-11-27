from elasticsearch import Elasticsearch, helpers


class ElasticsearchIterable(object):

    def __init__(self, elasticsearch_host='localhost', elasticsearch_port=9200, query=None,
                 all_docs=False, step=1000, index=None, doc_type=None, request_timeout=10, limit=None):
        """
        Um generator para jurisprudências a partir de uma consulta ao Elasticsearch.

        :param elasticsearch_host: Host do índice de onde os registros serão consultados
        :param elasticsearch_port: Porta do índice de onde os registros serão consultados
        :param query: Consulta realizada para recuperar as jurisprudências
        :param all_docs: Se for True, será realizada uma consulta em batch que retornará todos os registros que estejam
        em conformidade com a query informada. Se for False, recupera somente aquilo que está exatamente especificado na
        query, respeitando quantidade de registros especificados.
        :param step: Tamanho do batch para retorno dos documentos quando a consulta for em batch (all_docs = True)
        """
        self.elasticsearch_host = elasticsearch_host
        self.elasticsearch_port = elasticsearch_port
        if query is None:
            query = {"query": {"match_all": {}}}
        self.query = query
        self.all_docs = all_docs
        self.step = step
        self.index = index
        self.doc_type = doc_type
        self.hits = None
        self.request_timeout = request_timeout
        self.limit = limit

        self.client = Elasticsearch(self.elasticsearch_host,
                                    port=self.elasticsearch_port,
                                    request_timeout=self.request_timeout)
        if self.all_docs is True:
            self.res = helpers.scan(client=self.client,
                                    size=self.step,
                                    query=self.query,
                                    index=self.index,
                                    doc_type=self.doc_type, request_timeout=self.request_timeout)
        else:
            self.res = self.client.search(index=self.index,
                                          body=self.query,
                                          doc_type=self.doc_type,
                                          request_timeout=request_timeout)
            self.hits = self.res['hits']

    def __iter__(self):
        """
        The iterable interface: return an iterator from __iter__().

        Every generator is an iterator implicitly (but not vice versa!),
        so implementing `__iter__` as a generator is the easiest way
        to create streamed iterables.

        """
        if self.hits is not None:
            res = self.hits['hits']
        else:
            res = self.res
        count = 0
        for doc in res:
            if self.hits is not None:
                total = self.hits['total']
            else:
                total = res.gi_frame.f_locals['resp']['hits']['total']
            count += 1
            if total is not None:
                if (count % 10000 == 0) or (count == total):
                    print('Retrieved %d records from %d so far' % (count, total))
            if self.limit and count == self.limit:
                break
            yield doc['_source']

    def __len__(self):
        if self.hits is not None:
            return self.hits['total']


class AnexoIterable(ElasticsearchIterable):

    def __init__(self, ano, regiao, elasticsearch_host='elastic-bd.avisourgente', all_docs=True,
                 index='processo_documentos', doc_type='processo_documento', request_timeout=10, step=1000, limit=None):
        super().__init__(query=get_query_anexos(ano, regiao), elasticsearch_host=elasticsearch_host,
                         index=index, doc_type=doc_type, all_docs=all_docs, request_timeout=request_timeout,
                         limit=limit, step=step)
        self.ano = ano
        self.regiao = regiao


class RegiaoIterable(object):

    def __init__(self, ano, regioes, limit=None):
        """
        Um generator para jurisprudências a partir de uma consulta ao Elasticsearch.

        :param elasticsearch_host: Host do índice de onde os registros serão consultados
        """
        self.ano = ano
        self.regioes = regioes
        self.limit = limit

    def __iter__(self):
        for regiao in self.regioes:
            print('pesquisando ano %d e região %d' % (self.ano, regiao))
            anexos = AnexoIterable(self.ano, regiao, all_docs=True, request_timeout=60, limit=self.limit)
            for anexo in anexos:
                yield anexo


class AnoIterable(object):

    def __init__(self, anos, regioes, limit=None):
        self.anos = anos
        self.regioes = regioes
        self.limit = limit

    def __iter__(self):
        for ano in self.anos:
            regiao_iterable = RegiaoIterable(ano, self.regioes, limit=self.limit)
            for anexo in regiao_iterable:
                yield anexo['corpo']


def get_query_anexos(ano, regiao):
    return {
        "query": {
            "bool": {
                "must": [
                    {
                        "query_string": {
                            "query": "(NumeroCnj:???????-??." + str(ano) + ".5." + str(regiao).zfill(
                                2) + ".????) AND "
                                     "((TipoDocumento.raw:Ata da Audiência) OR "
                                     "(TipoDocumento.raw:Acórdão) OR "
                                     "(TipoDocumento.raw:Sentença) OR "
                                     "(TipoDocumento.raw:Petição Inicial))"
                        }
                    }
                ]
            }
        }
    }
