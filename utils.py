from itertools import chain


def create_imap_search_string(uid_max = None, criteria = {}):
    # Produce search string in IMAP format:
    #   e.g. (FROM "me@gmail.com" SUBJECT "abcde" BODY "123456789" UID 9999:*)
    c = list(map(lambda t: (t[0], '"'+str(t[1])+'"'), criteria.items()))
    if uid_max is not None:
        c += [('UID', '%d:*' % (uid_max+1))]
    return '(%s)' % ' '.join(chain(*c))


def imap_get_max_uid(server):
    result, data = server.uid('search', None, create_imap_search_string(0, {}))
    uids = [int(s) for s in data[0].split()]
    return max(uids) if uids else 0

