"""Define the unit tests for the :mod:`colour.recovery.mallett2019` module."""

from __future__ import annotations

import numpy as np
import pytest

from colour.characterisation import SDS_COLOURCHECKERS
from colour.colorimetry import (
    CCS_ILLUMINANTS,
    MSDS_CMFS,
    SDS_ILLUMINANTS,
    SpectralShape,
    reshape_msds,
    reshape_sd,
    sd_to_XYZ,
)
from colour.difference import JND_CIE1976, delta_E_CIE1976
from colour.models import (
    RGB_COLOURSPACE_PAL_SECAM,
    RGB_COLOURSPACE_sRGB,
    XYZ_to_Lab,
    XYZ_to_RGB,
)
from colour.recovery import (
    MSDS_BASIS_FUNCTIONS_sRGB_MALLETT2019,
    RGB_to_sd_Mallett2019,
    spectral_primary_decomposition_Mallett2019,
)

__author__ = "Colour Developers"
__copyright__ = "Copyright 2013 Colour Developers"
__license__ = "BSD-3-Clause - https://opensource.org/licenses/BSD-3-Clause"
__maintainer__ = "Colour Developers"
__email__ = "colour-developers@colour-science.org"
__status__ = "Production"

__all__ = [
    "FixtureMallett2019",
    "TestSpectralPrimaryDecompositionMallett2019",
    "TestRGB_to_sd_Mallett2019",
]


class FixtureMallett2019:
    """A fixture for testing the :mod:`colour.recovery.mallett2019` module."""

    def __init__(self) -> None:
        self._basis = MSDS_BASIS_FUNCTIONS_sRGB_MALLETT2019
        self._RGB_colourspace = RGB_COLOURSPACE_sRGB
        self._cmfs = reshape_msds(
            MSDS_CMFS["CIE 1931 2 Degree Standard Observer"],
            SpectralShape(360, 780, 10),
        )
        self._sd_D65 = reshape_sd(SDS_ILLUMINANTS["D65"], self._cmfs.shape)
        self._xy_D65 = CCS_ILLUMINANTS["CIE 1931 2 Degree Standard Observer"]["D65"]

    @pytest.fixture(autouse=True)
    def setup_fixture_mallett_2019(self) -> None:
        """Configure the class instance."""

        self.__init__()

    def check_basis_functions(self) -> None:
        """
        Test :func:`colour.recovery.RGB_to_sd_Mallett2019` definition or the
        more specialised :func:`colour.recovery.RGB_to_sd_Mallett2019`
        definition.
        """

        # Make sure the white point is reconstructed as a perfectly flat
        # spectrum.
        RGB = np.full(3, 1.0)
        sd = RGB_to_sd_Mallett2019(RGB, self._basis)
        assert np.var(sd.values) < 1e-5

        # Check if the primaries or their combination exceeds the [0, 1] range.
        lower = np.zeros_like(sd.values) - 1e-12
        upper = np.ones_like(sd.values) + 1e12
        for RGB in [[1, 1, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1]]:
            sd = RGB_to_sd_Mallett2019(RGB, self._basis)
            np.testing.assert_array_less(sd.values, upper)
            np.testing.assert_array_less(lower, sd.values)

        # Check Delta E's using a colour checker.
        for name, sd in SDS_COLOURCHECKERS["ColorChecker N Ohta"].items():
            XYZ = sd_to_XYZ(sd, self._cmfs, self._sd_D65) / 100
            Lab = XYZ_to_Lab(XYZ, self._xy_D65)
            RGB = XYZ_to_RGB(XYZ, self._RGB_colourspace, self._xy_D65)

            recovered_sd = RGB_to_sd_Mallett2019(RGB, self._basis)
            recovered_XYZ = sd_to_XYZ(recovered_sd, self._cmfs, self._sd_D65) / 100
            recovered_Lab = XYZ_to_Lab(recovered_XYZ, self._xy_D65)

            error = delta_E_CIE1976(Lab, recovered_Lab)

            if error > 4 * JND_CIE1976 / 100:  # pragma: no cover
                pytest.fail(f'Delta E for "{name}" is {error}!')


class TestSpectralPrimaryDecompositionMallett2019(FixtureMallett2019):
    """
    Define :func:`colour.recovery.mallett2019.\
spectral_primary_decomposition_Mallett2019` definition unit tests methods.
    """

    def setup_method(self) -> None:
        """Initialise the common tests attributes."""

        FixtureMallett2019.__init__(self)

        self._RGB_colourspace = RGB_COLOURSPACE_PAL_SECAM

    def test_spectral_primary_decomposition_Mallett2019(self) -> None:
        """
        Test :func:`colour.recovery.mallett2019.\
test_spectral_primary_decomposition_Mallett2019` definition.
        """

        self._basis = spectral_primary_decomposition_Mallett2019(
            self._RGB_colourspace, self._cmfs, self._sd_D65
        )

        self.check_basis_functions()


class TestRGB_to_sd_Mallett2019(FixtureMallett2019):
    """
    Define :func:`colour.recovery.mallett2019.RGB_to_sd_Mallett2019` definition
    unit tests methods.
    """

    def setup_method(self) -> None:
        """Initialise the common tests attributes."""

        FixtureMallett2019.__init__(self)

        self._RGB_colourspace = RGB_COLOURSPACE_sRGB
        self._basis = MSDS_BASIS_FUNCTIONS_sRGB_MALLETT2019

    def test_RGB_to_sd_Mallett2019(self) -> None:
        """
        Test :func:`colour.recovery.mallett2019.RGB_to_sd_Mallett2019`
        definition.
        """

        self.check_basis_functions()
