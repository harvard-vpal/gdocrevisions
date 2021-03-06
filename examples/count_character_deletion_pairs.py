import gdocrevisions
from collections import Counter, namedtuple

FILE_ID = "" # fill in google doc file id
KEYFILE = "" # fill in keyfile path/filename

gdoc = gdocrevisions.GoogleDoc(FILE_ID, keyfile=KEYFILE)

content_state = gdocrevisions.Content()
counter = Counter()
Deletions = namedtuple('Deletions',['deleter','author'])

for revision in gdoc.revisions:
    for suboperation in revision.iter_suboperations():
        if suboperation.type == 'DeleteElement':
            deleter = revision.user_id
            author = content_state.elements[suboperation.index-1].revision.user_id
            counter[Deletions(deleter=deleter, author=author)]+=1
        content_state.apply(suboperation)
        
print counter
