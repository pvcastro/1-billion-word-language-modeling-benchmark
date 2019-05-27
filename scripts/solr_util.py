from pysolr import Solr


class SolrIterable(object):

    def __init__(self, solr_host='solr.datalawyer', solr_port=8983, query=None, step=1000, index=None, limit=None):
        """
        Um generator para jurisprudências a partir de uma consulta ao Elasticsearch.

        :param solr_host: Host do índice de onde os registros serão consultados
        :param solr_port: Porta do índice de onde os registros serão consultados
        :param query: Consulta realizada para recuperar as jurisprudências
        :param all_docs: Se for True, será realizada uma consulta em batch que retornará todos os registros que estejam
        em conformidade com a query informada. Se for False, recupera somente aquilo que está exatamente especificado na
        query, respeitando quantidade de registros especificados.
        :param step: Tamanho do batch para retorno dos documentos quando a consulta for em batch (all_docs = True)
        """

        if query is None:
            query = {"query": {"match_all": {}}}
        self.query = query
        self.step = step
        self.index = index
        self.hits = None
        self.limit = limit

        self.client = Solr('http://' + solr_host + ':' + str(solr_port) + '/solr/' + index)

        self.documents = self.client.search(query, **{'start': 0, 'rows': limit, 'sort': "tamanho_texto DESC"})

    def __iter__(self):
        """
        The iterable interface: return an iterator from __iter__().

        Every generator is an iterator implicitly (but not vice versa!),
        so implementing `__iter__` as a generator is the easiest way
        to create streamed iterables.

        """
        count = 0
        #total = self.documents.hits
        for doc in self.documents:
            #count += 1
            if count % 10000 == 0:
                print('Retrieved %d records so far' % (count))
            yield doc

    #def __len__(self):
    #    if self.documents is not None:
    #        return self.documents.hits


class AnexoIterable(SolrIterable):

    def __init__(self, ano, tipo, regiao, index='documentos', limit=10000):
        super().__init__(query=get_query_anexos(ano, tipo, regiao), index=index, limit=limit)


class RegiaoIterable(object):

    def __init__(self, ano, tipo, regioes, limit=None):
        """
        Um generator para jurisprudências a partir de uma consulta ao Elasticsearch.

        :param elasticsearch_host: Host do índice de onde os registros serão consultados
        """
        self.ano = ano
        self.tipo = tipo
        self.regioes = regioes
        self.limit = limit

    def __iter__(self):
        for regiao in self.regioes:
            print('pesquisando ano %d, tipo %s e região %d' % (self.ano, self.tipo, regiao))
            anexos = AnexoIterable(ano=self.ano, tipo=self.tipo, regiao=regiao, limit=self.limit)
            for anexo in anexos:
                yield anexo


class TipoIterable(object):

    def __init__(self, ano, tipos, regioes, limit=None):
        self.ano = ano
        self.tipos = tipos
        self.regioes = regioes
        self.limit = limit

    def __iter__(self):
        for tipo in self.tipos:
            regiao_iterable = RegiaoIterable(self.ano, tipo, self.regioes, limit=self.limit)
            for anexo in regiao_iterable:
                yield anexo


class AnoIterable(object):

    def __init__(self, anos, tipos, regioes, limit=None):
        self.anos = anos
        self.tipos = tipos
        self.regioes = regioes
        self.limit = limit

    def __iter__(self):
        for ano in self.anos:
            tipo_iterable = TipoIterable(ano, self.tipos, self.regioes, limit=self.limit)
            for anexo in tipo_iterable:
                yield anexo['texto']


def get_query_anexos(ano, tipo, regiao):
    return '(ano:{0}) AND (tipo: {1}) AND (tribunal: {2})'.format(ano, tipo, regiao)
