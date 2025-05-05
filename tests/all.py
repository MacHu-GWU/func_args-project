# -*- coding: utf-8 -*-

if __name__ == "__main__":
    from func_args.tests import run_cov_test

    run_cov_test(
        __file__,
        "func_args",
        is_folder=True,
        preview=False,
    )
