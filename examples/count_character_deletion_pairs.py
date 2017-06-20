import gdocrevisions
from collections import Counter, namedtuple

FILE_ID = ...
gdoc = gdocrevisions.GoogleDoc(FILE_ID, ...)


content_state = gdocrevisions.Content()
counter = Counter()
Pair = namedtuple('Pair',['deleter','author'])


for revision in gdoc.revisions:
    for operation in revision.operations:
        if operation.__class__.__name__ == 'DeleteString':
            for i in range(operation.start_index-1,operation.end_index):
                deleter = revision.user_id
                author = content_state.elements[i].revision.user_id
                counter[Pair(deleter=deleter, author=author)]+=1
        content_state.apply_operation(operation)
    
print counter
