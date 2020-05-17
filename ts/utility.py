from collections import OrderedDict
from itertools import product
from typing import List

from jinja2 import Template


def str_product(template: str, **kwargs) -> List[str]:
    def apply(_template):
        return list(
            Template(str(_template)).render(
                **{k: v for k, v in zip(keys, values)}
            ) for values in product(*values_list))

    kwargs = OrderedDict(kwargs)
    keys = list(kwargs.keys())
    values_list = list(kwargs.values())
    return apply(str(template))

