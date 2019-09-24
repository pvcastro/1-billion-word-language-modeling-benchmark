import fire


def generate_brwac_sentences(in_path, out_path):

    def is_number(value):
        try:
            value = int(value)
            return True
        except ValueError:
            return False

    # out_file = open('/media/discoD/Corpora/brwac/brwac.txt', mode='w')
    with open(out_path, mode='w', encoding='utf8') as out_file:
        count = 0
        sentence = list()
        # with open('/media/discoD/Corpora/brwac/brwac.conll', mode='r') as in_file:
        with open(in_path, mode='r', encoding='utf8') as in_file:
            for line in in_file:
                if line.startswith('#'):
                    continue
                tokens = line.split('\t')
                if len(tokens) > 0:
                    if not is_number(tokens[0]):
                        continue
                    token = tokens[1]
                    if '=' in token and len(token.split('=')) > 1:
                        token = token.replace('=', ' ')
                    token = token.replace("'", " ' ").strip()
                    if tokens[0] == "1":
                        if len(sentence) > 0:
                            out_file.write(' '.join(sentence) + '\n\n')
                            count += 1
                            if count % 10000 == 0:
                                print('Written %d sentences' % count)
                        sentence = list()
                    sentence.append(token)
                else:
                    print(line)
            print('Finished writing %d sentences' % count)
        out_file.close()


if __name__ == '__main__': fire.Fire(generate_brwac_sentences)