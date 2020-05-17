from ts.DAG import DAG


def test_dag_acyclic():
    DAG([], [])
    g = DAG(['A', 'B', 'C'], [('A', 'B'), ('A', 'C'), ('B', 'C')])
    # noinspection PyUnusedLocal
    try:
        DAG(['A', 'B', 'C'], [('A', 'B'), ('B', 'C'), ('C', 'A')])
    except DAG.NotDAGError as e:
        pass
    else:
        raise AssertionError("Not checked DAG properly")
    try:
        DAG(['A', 'B', 'C', 'D'], [('A', 'B'), ('B', 'C'), ('C', 'A'), ('A', 'D')])
    except DAG.NotDAGError:
        pass
    else:
        raise AssertionError("Not checked DAG properly")
    assert g.source == 'A'
    assert g.sink == 'C'
    assert g.in_edges("A") == set()
    assert g.in_edges("B") == {('A', 'B')}
    assert g.in_edges("C") == {('B', 'C'), ('A', 'C')}
    assert g.out_edges("A") == {('A', 'B'), ('A', 'C')}
    assert g.out_edges("B") == {('B', 'C')}
    assert g.out_edges("C") == set()


def test_dag_remove_node():
    g1 = DAG(['A', 'B', 'C'], [('A', 'B'), ('A', 'C'), ('B', 'C')])
    g2 = DAG(['A', 'B'], [('A', 'B')])
    g3 = DAG(['A', 'C'], [('A', 'C')])
    assert g1.remove_node('C') == g2
    assert g1.remove_node('B') == g3
    assert g1.remove_nodes(['A', 'B']) == DAG(['C'], [])


def test_dag_others():
    g1 = DAG(['A', 'B', 'C'], [('A', 'B'), ('A', 'C'), ('B', 'C')])
    assert g1 != ('A', 'B', 'C')
    g2 = DAG(['A', 'B'], [('A', 'B')])
    assert repr(g2) == "nodes: B,A edges: ('A', 'B')" or repr(g2) == "nodes: A,B edges: ('A', 'B')"


def test_dependency_graph():
    g1 = DAG(['A', 'B', 'C'], [('A', 'B'), ('A', 'C'), ('B', 'C')])
    assert g1.dependency_subgraph('A') == g1
    assert g1.dependency_subgraph('C') == DAG(['C'], [])
    assert g1.dependency_subgraph('B') == DAG(['C', 'B'], [('B', 'C')])


def test_format_dag():
    g = DAG(
        [
            '/path/to/folder/',
            'a-first.html',
            'b-second.html',
            'subfolder',
            'readme.html',
            'code.cpp',
            'code.h',
            'z-last-file.html',
        ],
        [
            ('/path/to/folder/', 'a-first.html'),
            ('/path/to/folder/', 'b-second.html'),
            ('/path/to/folder/', 'subfolder'),
            ('subfolder', 'readme.html'),
            ('subfolder', 'code.cpp'),
            ('subfolder', 'code.h'),
            ('/path/to/folder/', 'z-last-file.html'),
        ],
    )
    target = \
        """/path/to/folder/
├── a-first.html
├── b-second.html
├── subfolder
│   ├── readme.html
│   ├── code.cpp
│   └── code.h
└── z-last-file.html"""
    # print(target)
    # print(g.format_subtree("/path/to/folder/"))
    assert g.format_subtree("/path/to/folder/") == target
    target = \
        """└── /path/to/folder/
    ├── a-first.html
    ├── b-second.html
    ├── subfolder
    │   ├── readme.html
    │   ├── code.cpp
    │   └── code.h
    └── z-last-file.html"""
    # print(target)
    # print(g.format_tree())
    assert g.format_tree() == target
    g = DAG(
        [
            '/path/to/folder/',
            'a-first.html',
            'b-second.html',
            'subfolder',
            'readme.html',
            'code.cpp',
            'deep_folder',
            'da', 'db', 'dc',
            'code.h',
            'z-last-file.html',
        ],
        [
            ('/path/to/folder/', 'a-first.html'),
            ('/path/to/folder/', 'b-second.html'),
            ('/path/to/folder/', 'subfolder'),
            ('subfolder', 'readme.html'),
            ('subfolder', 'code.cpp'),
            ('subfolder', 'deep_folder'),
            ('deep_folder', 'da'),
            ('deep_folder', 'db'),
            ('deep_folder', 'dc'),
            ('subfolder', 'code.h'),
            ('/path/to/folder/', 'z-last-file.html'),
        ],
    )
    target = \
        """/path/to/folder/
├── a-first.html
├── b-second.html
├── subfolder
│   ├── readme.html
│   ├── code.cpp
│   ├── deep_folder
│   │   ├── da
│   │   ├── db
│   │   └── dc
│   └── code.h
└── z-last-file.html"""
    # print(target)
    # print(g.format_subtree("/path/to/folder/"))
    assert g.format_subtree("/path/to/folder/") == target
