from pathlib import Path


class FakeFilesystem(list):

    def copy(self, src, dest):
        self.append(('COPY', src, dest))

    def move(self, src, dest):
        self.append(('MOVE', src, dest))

    def delete(self, dest):
        self.append(('DELETE', dest))


def sync(reader, filesystem: FakeFilesystem, source_root: str, dest_root: str):
    source_hashes = reader(source_root)
    dest_hashes = reader(dest_root)

    for sha, filename in source_hashes.items():
        if sha not in dest_hashes:
            sourcepath = Path(source_root) / filename
            destpath = Path(dest_root) / filename
            filesystem.copy(sourcepath, destpath)
        elif dest_hashes[sha] != filename:
            olddestpath = Path(dest_root) / dest_hashes[sha]
            newdestpath = Path(dest_root) / filename
            filesystem.move(olddestpath, newdestpath)

    for sha, filename in dest_hashes.items():
        if sha not in source_hashes:
            filesystem.delete(Path(dest_root)/filename)


def test_when_a_file_exists_in_the_source_but_not_in_the_destination():
    source = {'sha1': 'myfile'}
    dest = {}
    filesystem = FakeFilesystem()

    reader = {'/source': source, '/dest': dest}
    sync(reader.pop, filesystem, '/source', '/dest')

    assert filesystem == [('COPY', Path('/source/myfile'), Path('/dest/myfile'))]


def test_when_a_file_has_been_renamed_in_the_source():
    source = {'sha1': 'my-renamed-file'}
    dest = {'sha1': 'my-original-file'}
    filesystem = FakeFilesystem()

    reader = {'/source': source, '/dest': dest}
    sync(reader.pop, filesystem, '/source', '/dest')

    assert filesystem == [('MOVE', Path('/dest/my-original-file'), Path('/dest/my-renamed-file'))]
