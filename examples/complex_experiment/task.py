"""
Assume that we are going to run a experiment:
Input test files are f1, f2, and a training set t1, t2
The experiment has the following steps:
1. Build training corpus from t* to t*.B
2. Anomaly Detection
    We need to detect anomaly in each input files with the following algorithms:
    1. algorithm A
        1. encode each input file f* to f*.A
        2. run algorithm A, generate f*.A.ad for f*.A
    2. algorithm B
        1. build a model B.model from training corpus t*.B
        2. encode each input file f* to f*.B
        3. run algorithm B, generate f*.B.ad for f*.B
    Then we collect all algorithms' results and generate a report data f.ad
3. Localization
    we need to run the following three algorithms on each input file
    1. algorithm C
        Based on f.ad, generate f*.C.lclz for each f*.A
    2. algorithm D
        1. Build a model D.model from t*.B
        2. Run the model and generate f*.D.lclz for each f*.B
    3. algorithm E
        Based on f*, generate f*.E.lclz for each.
    Then we collect all algorithms' results and generate a report data f.lclz
"""
from pathlib import Path

from ts import task, str_product, task_product

working_dir = Path(".")
output_path = working_dir / "output"
train_dir = working_dir / "input_train_files"
test_dir = working_dir / "input_test_files"

train_files = list(train_dir.glob("t*"))
test_files = list(test_dir.glob("f*"))
train_file_names = list(map(lambda _: _.name, train_files))
test_file_names = list(map(lambda _: _.name, test_files))

lclz_result = task(
    "python exp.py -m collect -s lclz -o {{ __t }} -i {{ __d|join(' -i ') }}",
    depend=str_product(
        output_path / "{{ f }}.{{ alg }}.lclz",
        f=test_file_names,
        alg=['C', 'D', 'E']
    ),
    target=output_path / 'f.lclz',
    name="collect localization result"
)

e_results = task_product(
    "python exp.py -m run_model -a e "
    "-i {{ __d }} -o {{ __t }}",
    depend=test_dir / "{{ f }}",
    target=output_path / "{{ f }}.E.lclz",
    f=test_file_names,
    name="E-result of {{ f }}"
)

d_results = task_product(
    "python exp.py -m run_model -a d "
    "-i {{ __d[0] }} -o {{ __t }} -f {{ __d[1] }}",
    depend=[output_path / "{{ f }}.B", output_path / "D.model"],
    target=output_path / "{{ f }}.D.lclz",
    f=test_file_names,
    name="D-result of {{ f }}"
)

c_results = task_product(
    "python exp.py -m run_model -a c "
    "-i {{ __d[0] }} -o {{ __t }} -f {{ __d[1] }}",
    depend=[output_path / "{{ f }}.A", output_path / "f.ad"],
    target=output_path / "{{ f }}.C.lclz",
    f=test_file_names,
    name="C-result of {{ f }}"
)

ad_result = task(
    "python exp.py -m collect --step ad -o {{ __t }} -i {{ __d|join(' -i ') }}",
    depend=str_product(
        output_path / "{{ f }}.{{ alg }}.ad",
        f=test_file_names,
        alg=['A', 'B']
    ),
    target=output_path / 'f.ad',
    name="collect anomaly detection result"
)

a_results = task_product(
    "python exp.py -m run_model -a a "
    "-i {{ __d }} -o {{ __t }}",
    depend=output_path / "{{ f }}.A",
    target=output_path / "{{ f }}.A.ad",
    f=test_file_names,
    name="A-result of {{ f }}"
)

b_results = task_product(
    "python exp.py -m run_model -a b "
    "-i {{ __d[0] }} -o {{ __t }} -f {{ __d[1] }}",
    depend=[output_path / "{{ f }}.B", output_path / "B.model"],
    target=output_path / "{{ f }}.B.ad",
    f=test_file_names,
    name="B-result of {{ f }}"
)

build_model = task_product(
    "python exp.py -m build_model -a {{ alg }} "
    "-i {{ __d|join(' -i ') }} -o {{ __t }}",
    depend=str_product(output_path / "{{ f }}.B", f=train_file_names),
    target=output_path / "{{ alg }}.model",
    alg=['B', 'D'],
    name="build model {{ alg }}"
)

encode_files = task_product(
    "python exp.py -m encode -a {{ alg }} "
    "-i {{ __d }} -o {{ __t }}",
    depend="{{ path }}",
    target=output_path / "{{ path.name }}.{{ alg }}",
    path=train_files + test_files,
    alg=['B', 'A'],
    name="encode {{ path.name }} of {{ alg }}"
)
