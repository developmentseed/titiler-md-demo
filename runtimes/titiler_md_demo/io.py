"""Custom reader."""

import pickle
from typing import Any, Callable, List, Optional

import attr
import xarray
from diskcache import Cache
from morecantile import TileMatrixSet
from rio_tiler.constants import WEB_MERCATOR_TMS
from rio_tiler.io.xarray import XarrayReader
from titiler.xarray.io import get_variable, xarray_open_dataset

from .settings import CacheSettings

cache_settings = CacheSettings()
cache_client = Cache(
    directory=cache_settings.directory,
    size_limit=cache_settings.maxsize,
)


@attr.s
class CustomReader(XarrayReader):
    """Reader: Open Zarr file and access DataArray."""

    src_path: str = attr.ib()
    variable: str = attr.ib()

    # xarray.Dataset options
    opener: Callable[..., xarray.Dataset] = attr.ib(default=xarray_open_dataset)

    group: Optional[Any] = attr.ib(default=None)
    decode_times: bool = attr.ib(default=False)

    # xarray.DataArray options
    datetime: Optional[str] = attr.ib(default=None)
    drop_dim: Optional[str] = attr.ib(default=None)

    tms: TileMatrixSet = attr.ib(default=WEB_MERCATOR_TMS)

    ds: xarray.Dataset = attr.ib(init=False)
    input: xarray.DataArray = attr.ib(init=False)

    _dims: List = attr.ib(init=False, factory=list)

    def __attrs_post_init__(self):
        """Set bounds and CRS."""
        ds = None
        # Generate cache key and attempt to fetch the dataset from cache
        cache_key = f"{self.src_path}_group:{self.group}_time:{self.decode_times}"
        data_bytes = cache_client.get(cache_key)
        if data_bytes:
            ds = pickle.loads(data_bytes)

        self.ds = ds or self.opener(
            self.src_path,
            group=self.group,
            decode_times=self.decode_times,
        )
        if not ds:
            # Serialize the dataset to bytes using pickle
            cache_key = f"{self.src_path}_group:{self.group}_time:{self.decode_times}"
            data_bytes = pickle.dumps(self.ds)
            cache_client.set(
                cache_key,
                data_bytes,
                tag="data",
                expire=cache_settings.ttl,
            )

        self.input = get_variable(
            self.ds,
            self.variable,
            datetime=self.datetime,
            drop_dim=self.drop_dim,
        )
        super().__attrs_post_init__()
