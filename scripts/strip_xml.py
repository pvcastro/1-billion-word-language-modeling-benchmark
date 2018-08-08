import re, sys

if len(sys.argv) == 2:
    caminho_arquivo = sys.argv[1]
    print(sys.argv)
else:
    print("Usage: python strip_xml.py caminho_arquivo")
    sys.exit()


def remover_tags_xml(caminho):
    print("Removendo tags XML de %s" % caminho)
    text = re.sub('<[^<]+>', "", open(caminho).read())
    with open(caminho, "w") as f:
        f.write(text)
        print("Tags XML removidas de %s" % caminho)


remover_tags_xml(caminho_arquivo)
