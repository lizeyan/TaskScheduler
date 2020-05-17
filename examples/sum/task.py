from ts import task, task_product


def product(i, j, **kwargs):
    return i * j


bases = task_product(
    runner=product,
    name="{{ i }}*{{ j }}",
    i=range(1, 10),
    j=range(1, 10),
)

task(
    lambda *args: print(f"Result: {sum(args)}"),
    name='Sum',
    depend=bases
)
