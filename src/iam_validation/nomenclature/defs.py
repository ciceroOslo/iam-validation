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
import yaml

from ..dims import DsdDim



_DEFINITIONS_SUBDIR_NAME: str = "definitions"
"""The subdirectory name for `DataStructureDefinition` definitions in
nomenclature.
"""
_MAPPINGS_SUBDIR_NAME: str = "mappings"
"""The subdirectory name for `RegionProcessor` region mappings in nomenclature.
"""



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
            git_revision: tp.Optional[str] = None,
            git_hash: tp.Optional[str] = None,
    ) -> tp.Self:
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
            load_mappings=load_mappings,
            git_revision=git_revision,
            git_hash=git_hash,
        )
        local_dir: tempfile.TemporaryDirectory = cls.make_tmp_load_dir(
            config_content=config_yaml_content,
        )
        with local_dir as local_dir_name:
            local_path: Path = Path(local_dir_name)
            dsd: DataStructureDefinition = DataStructureDefinition(
                local_path / _DEFINITIONS_SUBDIR_NAME, dimensions=dimensions
            )
            if load_mappings:
                region_processor = RegionProcessor.from_directory(
                    path=local_path / _MAPPINGS_SUBDIR_NAME,
                    dsd=dsd
                )
                return cls(dsd=dsd, region_processor=region_processor)
            else:
                return cls(dsd=dsd)
    ###END NomnomenclatureDefs.from_url


    @staticmethod
    def create_config_yaml_str_from_url(
            url: str,
            *,
            repo_id: str,
            dimensions: tp.Optional[Sequence[DsdDim]] = None,
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
        """
        temp_dir = tempfile.TemporaryDirectory()
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

###END class NomenclatureDefs
