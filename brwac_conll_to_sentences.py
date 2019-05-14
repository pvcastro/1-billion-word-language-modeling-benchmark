def get_password(line, delimiter):
    return line.split(delimiter)[1].replace('\r', '')


def write_password(line, delimiter, out_file):
    password = get_password(line, delimiter)
    if len(password) > 0:
        out_file.write(password)


def is_number(value):
    try:
        value = int(value)
        return True
    except ValueError:
        return False


out_file = open('/media/discoD/Corpora/brwac/brwac.txt', mode='w')
count = 0
sentence = list()
with open('/media/discoD/Corpora/brwac/brwac.conll', mode='r') as in_file:
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
                    # if count == 50:
                    #     break
                    if count % 10000 == 0:
                        print('Written %d sentences' % count)
                sentence = list()
            sentence.append(token)
        else:
            print(line)
    print('Finished writing %d sentences' % count)
    #     try:
    #         write_password(email_password, ':', out_file)
    #         count += 1
    #         if count % 10000 == 0:
    #             print 'Written %d passwords' % count
    #     except IndexError:
    #         print email_password
    #         try:
    #             write_password(email_password, ';', out_file)
    #             count += 1
    #             if count % 10000 == 0:
    #                 print 'Written %d passwords' % count
    #             continue
    #         except IndexError:
    #             print email_password
    #             continue
out_file.close()
