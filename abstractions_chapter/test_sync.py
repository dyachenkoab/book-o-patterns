import shutil
from pathlib import Path, PosixPath
import tempfile
from sync import synch, determine_actions


def test_when_a_file_exists_in_the_source_but_not_in_the_destination_old():
    source = tempfile.mkdtemp()
    dest = tempfile.mkdtemp()
    try:
        content = "I am a very useful file"
        (Path(source) / 'my_file').write_text(content)

        synch(source, dest)

        expected_path = Path(dest) / 'my_file'

        assert expected_path.exists()
        assert expected_path.read_text() == content

    finally:
        shutil.rmtree(source)
        shutil.rmtree(dest)


def test_when_a_file_has_been_renamed_in_the_source_old():
    source = tempfile.mkdtemp()
    dest = tempfile.mkdtemp()
    try:
        content = "I am the file who has been renamed"
        source_path = Path(source) / 'source_file'
        old_dest_path = Path(dest) / 'dest_file'
        expected_dest_path = Path(dest) / 'source_file'

        source_path.write_text(content)
        old_dest_path.write_text(content)

        synch(source, dest)

        assert old_dest_path.exists() is False
        assert expected_dest_path.read_text() == content

    finally:
        shutil.rmtree(source)
        shutil.rmtree(dest)


def test_when_a_file_exists_in_the_source_but_not_in_the_destination():
    src_hashes = {'hash1': 'fn1'}
    dest_hashes = {}
    actions = determine_actions(src_hashes, dest_hashes, '/src', '/dst')

    assert next(actions) == ('COPY', Path('/src/fn1'), Path('/dst/fn1'))


def test_when_a_file_has_been_renamed_in_the_source():
    src_hashes = {'hash1': 'fn1'}
    dest_hashes = {'hash1': 'fn2'}

    actions = determine_actions(src_hashes, dest_hashes, '/src', '/dst')

    assert next(actions) == ('MOVE', Path('/dst/fn2'), Path('/dst/fn1'))


