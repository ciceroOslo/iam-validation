"""Module for loading nomenclature definitions and region mappings."""
from collections.abc import Sequence
import copy
from pathlib import Path
import tempfile
import typing as tp

from nomenclature import (
    DataStructureDefinition,
    RegionProcessor,
)
import pyam

from ..dims import DsdDim



class NomenclatureDefs:
    """Class to load and use nomenclature definitinos and region mappings.
    
    This class is a convenient wrapper around `nomenclature-iamd` functionality,
    and validation functionality found here in the `validation` module. It
    allows loading datastructure definitions and region mappings directly from
    a remote repository URL without the need for a yaml configuration file
    (which `nomenclature` requires), or from a local directory (like
    `nomenclature`). After loading, it provides methods that can be used to
    scan IAMC-formatted model output files for any model, scnario, variable or
    region names that are not defined in the datastructure definitions or region
    mappings, and provide convenient wrappers around some other `nomenclature`
    functionality.

    Instances of this class are usually created by reading a repository from a
    url with the `.from_url` class method, or from a local directory with the
    `.from_path` method. The class can be instantiated directly from an existing
    `nomenclature` `DataStructureDefinition` and optionally a `RegionProcessor`
    object if present, or from an existing `NomenclatureDefs` object to make a
    copy.

    Attributes
    ----------
    dsd : DataStructureDefinition
        The `DataStructureDefinition` used by the instance.
    region_processor : RegionProcessor, optional
        The `RegionProcessor` used, if present. If the instance was created
        without a `RegionProcessor` or loaded from data that did not include
        region mappings, this attribute will not be present.
    """

    def __init__(
            self,
            dsd: DataStructureDefinition,
            *,
            region_processor: tp.Optional[RegionProcessor] = None,
            deep_copy: bool = True,
    ):
        """
        Parameters
        ----------
        dsd : DataStructureDefinition
            The `DataStructureDefinition` to use.
        region_processor : RegionProcessor, optional
            The `RegionProcessor` to use. This parameter is optional, but must
            be provided if methods related to region mappping are to be used.
        deep_copy : bool, optional
            Whether to make a deep copy of the `DataStructureDefinition` and
            `RegionProcessor` objects. By default, this is True, to avoid that
            any changes made to the objects will affect external callers.
            Usually the copying only takes a few tenths of a second, but if you
            encounter performance issues, you can set this to False.
        """
        if deep_copy:
            dsd = copy.deepcopy(dsd)
            if region_processor is not None:
                region_processor = copy.deepcopy(region_processor)
        self.dsd: DataStructureDefinition = dsd
        if region_processor is not None:
            self.region_processor: RegionProcessor = region_processor
    ###END NomnomenclatureDefs.__init__


    @classmethod
    def from_url(
            cls,
            url: str,
            *,
            dimensions: Sequence[DsdDim],
            load_mappings: bool = True,
    ) -> tp.Self:
        """Create an instance by loading from an external repository URL.

        Parameters
        ----------
        url : str
            The URL of the repository to load.
        dimensions : sequence of str or DsdDim enums
            The dimensions to load. This argument must be provided, and each of
            the named dimensions must be present as a subdirectory under the
            `/definitions` directory of the repository, or a ValueError will be
            raised.
        load_mappings : bool, optional
            Whether to load region mappings from the repository. This parameter
            is optional and defaults to True, but this will fail if there is
            no `/mappings` directory in the repository. If the repository does
            not have one, you *must* set this parameter to False, or an error
            will be raised.

        Returns
        -------
        NomenclatureDefs
            The loaded instance. If `load_mappings` is True, it will have a
            `region_processor` attribute, but not if `load_mappings` is False.
        """
        # Create config data that can be dumped to a temporary nomenclature.yaml
        # file, which `nomenclature.DataStructureDefinition` can then use to
        # load from the repository.


###END class NomenclatureDefs
