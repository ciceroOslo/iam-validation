"""Module for loading nomenclature definitions and region mappings."""
from collections.abc import Sequence
import copy
import enum
from pathlib import Path
import tempfile
import typing as tp

from nomenclature import (
    DataStructureDefinition,
    RegionProcessor,
)
import pandas as pd
import pyam
import yaml

from ..dims import (
    DIM,
    DsdDim,
)

from . import multi_load
from . import validation



_DEFINITIONS_SUBDIR_NAME: str = "definitions"
"""The subdirectory name for `DataStructureDefinition` definitions in
nomenclature.
"""
_MAPPINGS_SUBDIR_NAME: str = "mappings"
"""The subdirectory name for `RegionProcessor` region mappings in nomenclature.
"""

class TmpDirCleanup(enum.StrEnum):
    """Whether and how to clean up temporary directories used to hold repos."""
    IMMEDIATE = 'immediate'
    """Clean up a temporary directory as soon as it has been used to load a
    DataStructureDefinition, do not return it to the caller.
    """
    RETURN = 'return'
    """Return the temporary directory to the caller, but let it be deleted when
    Python exits.
    """
    KEEP_PERMANENTLY = 'keep_permanently'
    """Return the temporary directory to the caller, and do not mark it to be
    deleted when Python exits (call `tempfile.TemporaryDirectory` with
    `delete=False`). The caller must then explicitly call the `cleanup` method
    of the `tempfile.TemporaryDirectory` object if the temporary directory is
    to be deleted.
    """
###END enum TmpDirCleanup


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


    @tp.overload
    @classmethod
    def from_url(
            cls,
            url: str,
            *,
            dimensions: Sequence[DsdDim|str],
            region_mappings: bool = True,
            git_revision: tp.Optional[str] = None,
            git_hash: tp.Optional[str] = None,
            tmp_dir_cleanup: tp.Literal[TmpDirCleanup.RETURN] \
                | tp.Literal[TmpDirCleanup.KEEP_PERMANENTLY],
    ) -> tuple[tp.Self, tempfile.TemporaryDirectory]:
        ...
    @tp.overload
    @classmethod
    def from_url(
            cls,
            url: str,
            *,
            dimensions: Sequence[DsdDim|str],
            region_mappings: bool = True,
            git_revision: tp.Optional[str] = None,
            git_hash: tp.Optional[str] = None,
            tmp_dir_cleanup: tp.Literal[TmpDirCleanup.IMMEDIATE] \
                = TmpDirCleanup.IMMEDIATE,
    ) -> tp.Self:
        ...
    @classmethod
    def from_url(
            cls,
            url: str,
            *,
            dimensions: Sequence[DsdDim|str],
            region_mappings: bool = True,
            git_revision: tp.Optional[str] = None,
            git_hash: tp.Optional[str] = None,
            tmp_dir_cleanup: TmpDirCleanup = TmpDirCleanup.IMMEDIATE,
    ) -> tp.Self | tuple[tp.Self, tempfile.TemporaryDirectory]:
        """Create an instance by loading from an external repository URL.

        Parameters
        ----------
        url : str
            The URL of the repository to load. It must start with `"https://"`,
            and end with `".git"`.
        dimensions : sequence of str or DsdDim enums
            The dimensions to load. This argument must be provided, and each of
            the named dimensions must be present as a subdirectory under the
            `/definitions` directory of the repository, or a ValueError will be
            raised.
        git_revision : str, optional
            The git revision to load, which can be either a tag or a branch name
            in the git repository. Optinoal. Will be ignored if `git_hash` is
            also provided.
        git_hash : str, optional
            The hash of a specific git commit to load. Optional. Will override
            `git_revision` if provided.
        load_mappings : bool, optional
            Whether to load region mappings from the repository. This parameter
            is optional and defaults to True, but this will fail if there is
            no `/mappings` directory in the repository. If the repository does
            not have one, you *must* set this parameter to False, or an error
            will be raised.
        tmp_dir_cleanup : TmpDirCleanup enum or str
            Whether and how to clean up temporary directories used to hold
            repos. Can be given as a `TmpDirCleanup` enum or a string with one
            of the following values:
            * `"immediate"`: Delete the temporary directory before returning.
              This is the default.
            * `"return"`: Do not delete the temporary directory, but return it
              to the caller. The temporary directory will normally be deleted
              when the Python session exits, unless its `.cleanup()` method is
              called explicitly.
            * `"keep_permanently"`: Do not delete the temporary directory, and
              return it to the caller. The directory will not be deleted when
              the Python session exits, and the user must either call its
              `.cleanup()` method before Python exits, or delete it manually.

        Returns
        -------
        NomenclatureDefs
            The loaded instance. If `load_mappings` is True, it will have a
            `region_processor` attribute, but not if `load_mappings` is False.
        """
        # Create config data that can be dumped to a temporary nomenclature.yaml
        # file, which `nomenclature.DataStructureDefinition` can then use to
        # load from the repository.
        _REPO_TEMP_ID: str = 'tmp_repo'
        config_yaml_content: str = cls.create_config_yaml_str_from_url(
            url,
            repo_id=_REPO_TEMP_ID,
            dimensions=dimensions,
            load_mappings=region_mappings,
            git_revision=git_revision,
            git_hash=git_hash,
        )
        local_dir: tempfile.TemporaryDirectory = cls.make_tmp_load_dir(
            config_content=config_yaml_content,
            delete=not (tmp_dir_cleanup == TmpDirCleanup.KEEP_PERMANENTLY),
        )
        local_dir_name: str = local_dir.name
        try:
            local_path: Path = Path(local_dir_name)
            dsd: DataStructureDefinition = DataStructureDefinition(
                local_path / _DEFINITIONS_SUBDIR_NAME, dimensions=dimensions
            )
            if region_mappings:
                region_processor = RegionProcessor.from_directory(
                    path=local_path / _MAPPINGS_SUBDIR_NAME,
                    dsd=dsd
                )
                instance: tp.Self = cls(dsd=dsd, region_processor=region_processor)
            else:
                instance: tp.Self = cls(dsd=dsd)
        except:
            local_dir.cleanup()
            raise
        if tmp_dir_cleanup == TmpDirCleanup.IMMEDIATE:
            local_dir.cleanup()
            return instance
        return instance, local_dir
    ###END NomnomenclatureDefs.from_url


    @staticmethod
    def create_config_yaml_str_from_url(
            url: str,
            *,
            repo_id: str,
            dimensions: tp.Optional[Sequence[DsdDim|str]] = None,
            load_mappings: bool = True,
            git_revision: tp.Optional[str] = None,
            git_hash: tp.Optional[str] = None,
    ) -> str:
        """Create content of nomenclature.yaml to load from external repo

        Parameters
        ----------
        url : str
            The URL of the repository to load. It must start with `"https://"`,
            and end with `".git"`.
        repo_id: str
            The id to use for the repository in the nomenclature.yaml file
        dimensions : sequence of str or DsdDim enums
            The dimensions to load. Each of the dimensions should have a
            corresponding subdirectory under the `/definitions` directory of
            the repository, or a ValueError will be raised when you try to
            load the repository. Optional, by default `['region', 'variable']`,
            which requires that both of those dimensions be present in the
            repository.
        git_revision : str, optional
            The git revision to load, which can be either a tag or a branch name
            in the git repository. Optinoal. Will be ignored if `git_hash` is
            also provided.
        git_hash : str, optional
            The hash of a specific git commit to load. Optional. Will override
            `git_revision` if provided.
        load_mappings : bool, optional
            Whether to load region mappings from the repository. Optional, True
            by default (but should be set explicitly to False if the repository
            does not have a `/mappings` directory).
        """
        if dimensions is None:
            dimensions = [DsdDim.region, DsdDim.variable]
        config_dict: dict = {}
        repos_dict = {
            repo_id: {
                'url': url,
            }
        }
        if git_hash is not None:
            repos_dict[repo_id]['hash'] = git_hash
        elif git_revision is not None:
            repos_dict[repo_id]['release'] = git_revision
        config_dict['repositories'] = repos_dict
        definitions_dict: dict[str, dict[str, str]] = {
            str(_dim): {
                'repository': repo_id
            } for _dim in dimensions
        }
        config_dict['definitions'] = definitions_dict
        if load_mappings:
            mappings_dict = {
                'repository': repo_id,
            }
            config_dict['mappings'] = mappings_dict
        return yaml.dump(config_dict)
    ###END def staticmethod NomeclatureDefs.create_config_yaml_str_from_url

    @staticmethod
    def make_tmp_load_dir(
            config_content: tp.Optional[str] = None,
            delete: bool = True,
    ) -> tempfile.TemporaryDirectory:
        """Create a temporary directory to load the repository into.

        The directory will contain a `'definitions'` and a `'mappings'`
        subdirectory. Normally, these will be left empty. If `config_content`
        is provided, it will be written to the `nomenclature.yaml` file in
        the root of the directory.

        The temporary directory and anything loaded into it will persist for the
        remainder of the Python session.

        Parameters
        ----------
        config_content : str, optional
            The content of the `nomenclature.yaml` file to write to the root of
            the directory. Optional. Normally, this should be provided, unless
            you want to create the file and put it in the root directory
            yourself. The nomenclature.yaml file is required for nomenclature to
            load content from an external repository. The content can be
            created using the `create_config_yaml_str_from_url` method.

        Returns
        -------
        tempfile.TemporaryDirectory
            The temporary directory, as a `tempfile.TemporaryDirectory` object.
            The directory will persist. It is the responsibility of the caller
            to ensure that its `.cleanup()` method is called to clean it up and
            delete it. It should therefore be used in `with` statements, or in
            `try`/`except`/`finally` blocks.
        delete : bool, optional
            Passed to `tmpfile.TemporaryDirectory`. If True, the temporary
            directory will be deleted when the Python session ends. If False,
            the directory will not be deleted unless the caller explicitly
            calls `.cleanup()`. Defaults to True.
        """
        temp_dir = tempfile.TemporaryDirectory(delete=delete)
        # Make sure the temporary directory is cleaned up if something fails
        try:
            temp_dir_path: Path = Path(temp_dir.name)
            if not temp_dir_path.exists():
                raise RuntimeError(
                    'Was not able to create the temporary directory '
                    f'{temp_dir} for loading the repository.'
                )
            (temp_dir_path / _DEFINITIONS_SUBDIR_NAME).mkdir()
            (temp_dir_path / _MAPPINGS_SUBDIR_NAME).mkdir()
            if config_content is not None:
                config_path: Path = temp_dir_path / 'nomenclature.yaml'
                config_path.write_text(config_content, encoding='utf-8')
        except Exception:
            temp_dir.cleanup()
            raise
        return temp_dir
    ###END def staticmethod NomenclatureDefs.make_tmp_load_dir

    def update(self, other: tp.Self) -> "MergedDefs":
        """Update this NomenclatureDefs with another NomenclatureDefs.
        
        Parameters
        ----------
        other : NomenclatureDefs
            The NomenclatureDefs to merge with this one. Overlapping definitions
            in `other` will override those in `self`.
        """
        return MergedDefs([other, self])
    ###END def MergedDefs.update

    def get_invalid_names(
            self,
            df: pyam.IamDataFrame,
            dimensions: tp.Optional[Sequence[str]] = None,
            raw_model_regions: bool = False,
    ) -> dict[str, list[str]] | dict[str, list[str]|dict[str, list[str]]]:
        """Returns a dictionary of invalid names for each dimension in a given
        `IamDataFrame`.
        """
        if not raw_model_regions:
            return validation.get_invalid_names(
                df,
                dsd=self.dsd,
                dimensions=dimensions,
            )
        else:
            invalid_names: dict[str, list[str]] | dict[str, list[str]|dict[str, list[str]]] \
                = validation.get_invalid_names(
                    df,
                    dsd=self.dsd,
                    dimensions=dimensions,
                )
            if str(DIM.REGION) in invalid_names:
                invalid_names[str(DIM.REGION)] = \
                    validation.get_invalid_model_regions(
                        df,
                        dsd=self.dsd,
                        region_processor=self.region_processor,
                        return_valid_native_combos=False,
                    )
            return invalid_names
    ###END def NOmenclatureDefs.get_invalid_names

    def get_invalid_variable_units(self, df: pyam.IamDataFrame) \
            -> pd.DataFrame | None:
        """Returns a DataFrame of invalid variable/unit combos, and valid alternatives.
        
        Returns
        -------
        pandas.DataFrame or None
            DataFrame with invalid and expected units for each variable in `df` that
            has an invalid unit. The DataFrame has the variable names in the index,
            and two columns that each contain strings or lists of strings. See
            the documentation of `.validation.get_invalid_variable_units` for
            details.
            Returns None if there are no invalid variable/unit combinations were
            found among known variables.
        """
        return validation.get_invalid_variable_units(df, dsd=self.dsd)
    ###END def NomenclatureDefs.get_invalid_variable_units


###END class NomenclatureDefs


class MergedDefs(NomenclatureDefs):
    """A merger of multiple NomenclatureDefs.
    
    Can be instantiated by passing a list of NomenclatureDefs, or by using the
    `.update` method of the `NomenclatureDefs` class. If definitions overlap,
    the ones that come earlier in the list will take precedence.
    """

    def __init__(
            self,
            defs_objects: Sequence[NomenclatureDefs],
    ):
        self.defs_objects: tp.Final[list[NomenclatureDefs]] = list(defs_objects)
        merged_dsd = multi_load.MergedDataStructureDefinition(
            [_defs.dsd for _defs in self.defs_objects]
        )
        # processor_dsd_pairs: list[tuple[DataStructureDefinition, RegionProcessor]] = [
        #     (_defs.dsd, _defs.region_processor)
        #     for _defs in self.defs_objects if hasattr(_defs, 'region_processor')
        # ]
        region_processors: list[RegionProcessor] = [
            _defs.region_processor for _defs in self.defs_objects
            if hasattr(_defs, 'region_processor')
        ]
        if len(region_processors) > 1:
            merged_processor = multi_load.merge_region_processors(
                region_processors,
                merged_dsd=merged_dsd,
            )
            super().__init__(merged_dsd, region_processor=merged_processor)
        elif len(region_processors) == 1:
            super().__init__(merged_dsd, region_processor=region_processors[0])
        else:
            super().__init__(merged_dsd)
    ###END def MergedDefs.__init__

    @classmethod
    def from_url(*args, **kwargs) -> tp.Self:
        raise TypeError(
            'MergedDefs cannot be instantiated using `.from_url()`. Please use '
            'the main NomenclatureDefs class instead.'
        )
    ###END def MergedDefs.from_url

    def update(self, other: NomenclatureDefs) -> tp.Self:
        """Update this MergedDefs with another NomenclatureDefs."""
        return type(self)([other, *self.defs_objects])
    ###END def MergedDefs.update

###END class MergedDefs
