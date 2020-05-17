# TaskScheduler (TS)
|Branch|Build|Coverage|
|---   |---  |---     |
|master|![Python package](https://github.com/lizeyan/TaskScheduler/workflows/Python%20package/badge.svg?branch=master)|[![Coverage Status](https://coveralls.io/repos/github/lizeyan/TaskScheduler/badge.svg?branch=master&t=lYjJ0E)](https://coveralls.io/github/lizeyan/TaskScheduler?branch=master&service=github)|
|dev|![Python package](https://github.com/lizeyan/TaskScheduler/workflows/Python%20package/badge.svg?branch=dev)|[![Coverage Status](https://coveralls.io/repos/github/lizeyan/TaskScheduler/badge.svg?branch=dev&t=lYjJ0E)](https://coveralls.io/github/lizeyan/TaskScheduler?branch=dev&service=github)|
## Introduction
This package focus on build a task scheduler via Python scripts.
With TaskScheduler you can define a project with tasks which have some dependency on each other, and run this project.

A task means a runnable job: bash command, python callable.
A task can produce files.
Task can depend on other tasks or files.

TS is able to run tasks and automatically run dependency tasks when necessary.

A task need to be rerun when:
1. its dependency tasks reran after target filed last updated
2. its dependency files updated after target filed last updated


### An example
The example is given in [`examples/complex_experiment`](examples/complex_experiment).
With `ts -w examples/complex_experiment tree`, we get such a dependency tree:

```
[2020-05-17T20:13:29.021066+0800   INFO] tree:
└── collect localization result
    ├── output/f1.E.lclz
    │   └── Generate output/f1.E.lclz<-E-result of f1
    │       └── input_test_files/f1
    ├── output/f1.C.lclz
    │   └── Generate output/f1.C.lclz<-C-result of f1
    │       ├── output/f.ad
    │       │   └── Generate output/f.ad<-collect anomaly detection result
    │       │       ├── output/f2.B.ad
    │       │       │   └── Generate output/f2.B.ad<-B-result of f2
    │       │       │       ├── output/f2.B
    │       │       │       │   └── Generate output/f2.B<-encode f2 of B
    │       │       │       │       └── input_test_files/f2
    │       │       │       └── output/B.model
    │       │       │           └── Generate output/B.model<-build model B
    │       │       │               ├── output/t2.B
    │       │       │               │   └── Generate output/t2.B<-encode t2 of B
    │       │       │               │       └── input_train_files/t2
    │       │       │               └── output/t1.B
    │       │       │                   └── Generate output/t1.B<-encode t1 of B
    │       │       │                       └── input_train_files/t1
    │       │       ├── output/f1.B.ad
    │       │       │   └── Generate output/f1.B.ad<-B-result of f1
    │       │       │       ├── output/f1.B
    │       │       │       │   └── Generate output/f1.B<-encode f1 of B
    │       │       │       │       └── input_test_files/f1
    │       │       │       └── output/B.model
    │       │       │           └── Generate output/B.model<-build model B
    │       │       │               ├── output/t2.B
    │       │       │               │   └── Generate output/t2.B<-encode t2 of B
    │       │       │               │       └── input_train_files/t2
    │       │       │               └── output/t1.B
    │       │       │                   └── Generate output/t1.B<-encode t1 of B
    │       │       │                       └── input_train_files/t1
    │       │       ├── output/f1.A.ad
    │       │       │   └── Generate output/f1.A.ad<-A-result of f1
    │       │       │       └── output/f1.A
    │       │       │           └── Generate output/f1.A<-encode f1 of A
    │       │       │               └── input_test_files/f1
    │       │       └── output/f2.A.ad
    │       │           └── Generate output/f2.A.ad<-A-result of f2
    │       │               └── output/f2.A
    │       │                   └── Generate output/f2.A<-encode f2 of A
    │       │                       └── input_test_files/f2
    │       └── output/f1.A
    │           └── Generate output/f1.A<-encode f1 of A
    │               └── input_test_files/f1
    ├── output/f2.E.lclz
    │   └── Generate output/f2.E.lclz<-E-result of f2
    │       └── input_test_files/f2
    ├── output/f2.C.lclz
    │   └── Generate output/f2.C.lclz<-C-result of f2
    │       ├── output/f.ad
    │       │   └── Generate output/f.ad<-collect anomaly detection result
    │       │       ├── output/f2.B.ad
    │       │       │   └── Generate output/f2.B.ad<-B-result of f2
    │       │       │       ├── output/f2.B
    │       │       │       │   └── Generate output/f2.B<-encode f2 of B
    │       │       │       │       └── input_test_files/f2
    │       │       │       └── output/B.model
    │       │       │           └── Generate output/B.model<-build model B
    │       │       │               ├── output/t2.B
    │       │       │               │   └── Generate output/t2.B<-encode t2 of B
    │       │       │               │       └── input_train_files/t2
    │       │       │               └── output/t1.B
    │       │       │                   └── Generate output/t1.B<-encode t1 of B
    │       │       │                       └── input_train_files/t1
    │       │       ├── output/f1.B.ad
    │       │       │   └── Generate output/f1.B.ad<-B-result of f1
    │       │       │       ├── output/f1.B
    │       │       │       │   └── Generate output/f1.B<-encode f1 of B
    │       │       │       │       └── input_test_files/f1
    │       │       │       └── output/B.model
    │       │       │           └── Generate output/B.model<-build model B
    │       │       │               ├── output/t2.B
    │       │       │               │   └── Generate output/t2.B<-encode t2 of B
    │       │       │               │       └── input_train_files/t2
    │       │       │               └── output/t1.B
    │       │       │                   └── Generate output/t1.B<-encode t1 of B
    │       │       │                       └── input_train_files/t1
    │       │       ├── output/f1.A.ad
    │       │       │   └── Generate output/f1.A.ad<-A-result of f1
    │       │       │       └── output/f1.A
    │       │       │           └── Generate output/f1.A<-encode f1 of A
    │       │       │               └── input_test_files/f1
    │       │       └── output/f2.A.ad
    │       │           └── Generate output/f2.A.ad<-A-result of f2
    │       │               └── output/f2.A
    │       │                   └── Generate output/f2.A<-encode f2 of A
    │       │                       └── input_test_files/f2
    │       └── output/f2.A
    │           └── Generate output/f2.A<-encode f2 of A
    │               └── input_test_files/f2
    ├── output/f2.D.lclz
    │   └── Generate output/f2.D.lclz<-D-result of f2
    │       ├── output/f2.B
    │       │   └── Generate output/f2.B<-encode f2 of B
    │       │       └── input_test_files/f2
    │       └── output/D.model
    │           └── Generate output/D.model<-build model D
    │               ├── output/t2.B
    │               │   └── Generate output/t2.B<-encode t2 of B
    │               │       └── input_train_files/t2
    │               └── output/t1.B
    │                   └── Generate output/t1.B<-encode t1 of B
    │                       └── input_train_files/t1
    └── output/f1.D.lclz
        └── Generate output/f1.D.lclz<-D-result of f1
            ├── output/D.model
            │   └── Generate output/D.model<-build model D
            │       ├── output/t2.B
            │       │   └── Generate output/t2.B<-encode t2 of B
            │       │       └── input_train_files/t2
            │       └── output/t1.B
            │           └── Generate output/t1.B<-encode t1 of B
            │               └── input_train_files/t1
            └── output/f1.B
                └── Generate output/f1.B<-encode f1 of B
                    └── input_test_files/f1
```

With `ts -w examples/complex_experiment run -j 10`, we run this experiment with 10 workers simutaneously.

## Install

```bash
pip install PyTaskScheduler
```
or
```bash
git clone https://github.com/lizeyan/TaskScheduler.git
cd TaskScheduler
python setup.py install
```
## Usage
```bash
ts --help
```
## Development Setup
```bash
pip install -r requirements-dev.txt
```
## Contributing
### TODO Features
- [ ] record function outputs
- [ ] function style examples
- [ ] lazy evaluation task templates

