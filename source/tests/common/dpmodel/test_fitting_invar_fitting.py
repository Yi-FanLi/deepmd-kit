# SPDX-License-Identifier: LGPL-3.0-or-later
import itertools
import unittest

import numpy as np

from deepmd.dpmodel.descriptor import (
    DescrptSeA,
)
from deepmd.dpmodel.fitting import (
    InvarFitting,
)

from .case_single_frame_with_nlist import (
    TestCaseSingleFrameWithNlist,
)


class TestInvarFitting(unittest.TestCase, TestCaseSingleFrameWithNlist):
    def setUp(self):
        TestCaseSingleFrameWithNlist.setUp(self)

    def test_self_consistency(
        self,
    ):
        rng = np.random.default_rng()
        nf, nloc, nnei = self.nlist.shape
        ds = DescrptSeA(self.rcut, self.rcut_smth, self.sel)
        dd = ds.call(self.coord_ext, self.atype_ext, self.nlist)
        atype = self.atype_ext[:, :nloc]

        for (
            distinguish_types,
            od,
            nfp,
            nap,
            et,
        ) in itertools.product(
            [True, False],
            [1, 2],
            [0, 3],
            [0, 4],
            [[], [0], [1]],
        ):
            ifn0 = InvarFitting(
                "energy",
                self.nt,
                ds.dim_out,
                od,
                numb_fparam=nfp,
                numb_aparam=nap,
                distinguish_types=distinguish_types,
                exclude_types=et,
            )
            ifn1 = InvarFitting.deserialize(ifn0.serialize())
            if nfp > 0:
                ifp = rng.normal(size=(self.nf, nfp))
            else:
                ifp = None
            if nap > 0:
                iap = rng.normal(size=(self.nf, self.nloc, nap))
            else:
                iap = None
            ret0 = ifn0(dd[0], atype, fparam=ifp, aparam=iap)
            ret1 = ifn1(dd[0], atype, fparam=ifp, aparam=iap)
            np.testing.assert_allclose(ret0["energy"], ret1["energy"])

    def test_mask(self):
        nf, nloc, nnei = self.nlist.shape
        ds = DescrptSeA(self.rcut, self.rcut_smth, self.sel)
        dd = ds.call(self.coord_ext, self.atype_ext, self.nlist)
        atype = self.atype_ext[:, :nloc]
        od = 2
        distinguish_types = False
        # exclude type 1
        et = [1]
        ifn0 = InvarFitting(
            "energy",
            self.nt,
            ds.dim_out,
            od,
            distinguish_types=distinguish_types,
            exclude_types=et,
        )
        ret0 = ifn0(dd[0], atype)
        # atom index 2 is of type 1 that is excluded
        zero_idx = 2
        np.testing.assert_allclose(
            ret0["energy"][:, zero_idx, :],
            np.zeros_like(ret0["energy"][:, zero_idx, :]),
        )

    def test_self_exception(
        self,
    ):
        rng = np.random.default_rng()
        nf, nloc, nnei = self.nlist.shape
        ds = DescrptSeA(self.rcut, self.rcut_smth, self.sel)
        dd = ds.call(self.coord_ext, self.atype_ext, self.nlist)
        atype = self.atype_ext[:, :nloc]

        for (
            distinguish_types,
            od,
            nfp,
            nap,
        ) in itertools.product(
            [True, False],
            [1, 2],
            [0, 3],
            [0, 4],
        ):
            ifn0 = InvarFitting(
                "energy",
                self.nt,
                ds.dim_out,
                od,
                numb_fparam=nfp,
                numb_aparam=nap,
                distinguish_types=distinguish_types,
            )

            if nfp > 0:
                ifp = rng.normal(size=(self.nf, nfp))
            else:
                ifp = None
            if nap > 0:
                iap = rng.normal(size=(self.nf, self.nloc, nap))
            else:
                iap = None
            with self.assertRaises(ValueError) as context:
                ret0 = ifn0(dd[0][:, :, :-2], atype, fparam=ifp, aparam=iap)
                self.assertIn("input descriptor", context.exception)

            if nfp > 0:
                ifp = rng.normal(size=(self.nf, nfp - 1))
                with self.assertRaises(ValueError) as context:
                    ret0 = ifn0(dd[0], atype, fparam=ifp, aparam=iap)
                    self.assertIn("input fparam", context.exception)

            if nap > 0:
                iap = rng.normal(size=(self.nf, self.nloc, nap - 1))
                with self.assertRaises(ValueError) as context:
                    ifn0(dd[0], atype, fparam=ifp, aparam=iap)
                    self.assertIn("input aparam", context.exception)

    def test_get_set(self):
        ifn0 = InvarFitting(
            "energy",
            self.nt,
            3,
            1,
        )
        rng = np.random.default_rng()
        foo = rng.normal([3, 4])
        for ii in [
            "bias_atom_e",
            "fparam_avg",
            "fparam_inv_std",
            "aparam_avg",
            "aparam_inv_std",
        ]:
            ifn0[ii] = foo
            np.testing.assert_allclose(foo, ifn0[ii])