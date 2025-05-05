# -*- coding: utf-8 -*-

from func_args import api


def test():
    _ = api
    _ = api.T_KWARGS
    _ = api.T_OPT_KWARGS
    _ = api.REQ
    _ = api.OPT
    _ = api.check_required
    _ = api.remove_optional
    _ = api.prepare_kwargs


if __name__ == "__main__":
    from func_args.tests import run_cov_test

    run_cov_test(
        __file__,
        "func_args.api",
        preview=False,
    )
