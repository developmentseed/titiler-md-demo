"""titiler.xarray Extensions."""

from typing import Callable, Dict, Type

import xarray
from attrs import define
from fastapi import Depends, Query
from typing_extensions import Annotated

from titiler.core.dependencies import DefaultDependency
from titiler.core.factory import FactoryExtension
from titiler.xarray.dependencies import XarrayIOParams
from titiler.xarray.factory import TilerFactory
from titiler.xarray.io import xarray_open_dataset


def VariableParams(
    variable: Annotated[str, Query(description="Xarray Variable name")],
) -> str:
    """Dataset variable name"""
    return variable


@define
class DimsExtension(FactoryExtension):
    """Add /dims endpoint to a Xarray TilerFactory."""

    # Custom dependency for /variables
    io_dependency: Type[DefaultDependency] = XarrayIOParams
    dataset_opener: Callable[..., xarray.Dataset] = xarray_open_dataset

    def register(self, factory: TilerFactory):
        """Register endpoint to the tiler factory."""

        @factory.router.get(
            "/dims",
            response_model=Dict,
            responses={200: {"description": "Return Xarray Dataset variables."}},
        )
        def dims(
            src_path=Depends(factory.path_dependency),
            variable=Depends(VariableParams),
            io_params=Depends(self.io_dependency),
        ):
            """return available variables."""
            with self.dataset_opener(src_path, **io_params.as_dict()) as ds:
                da = ds[variable]
                out = {}
                for dim in da.dims:
                    out[dim] = {
                        "min": str(min(da[dim].data)),
                        "max": str(max(da[dim].data)),
                        "len": len(da[dim].data),
                    }

                return out
