from document import Document, Content

class RevisionReplayer(object):
    """
    Document/content wrapper optimized for stepping forwards and backwards through revisions
    """
    def __init__(self, document, initial_revision_id=1):
        """
        Arguments:
            document (Document)
            intitial revision (int): revision id to initialized document to
        """
        self.document = document
        self.content = Content()
        self.current_revision_id = 0
        self.to_revision(initial_revision_id)

    def to_revision(self, target_revision_id):
        """
        check current revision
        if target is ahead of current state, apply
        if its ahead of target revision, undo
        """
        if self.current_revision_id < target_revision_id:
            for revision in self.document.revisions[self.current_revision_id+1:target_revision_id+1]:
                self.content.apply(revision)

        elif self.current_revision_id > target_revision_id:
            for revision in reversed(self.document.revisions[target_revision_id+1:self.current_revision_id+1]):
                self.content.undo(revision)

        self.current_revision_id = target_revision_id
