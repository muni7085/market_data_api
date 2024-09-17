from copy import deepcopy

from hydra.utils import instantiate
from omegaconf import DictConfig, OmegaConf
from registrable import Registrable
from registrable.exceptions import RegistrationError


def pop_name(cfg: DictConfig) -> str:
    """
    Pop the name from the configuration object

    Parameters
    ----------
    cfg: ``DictConfig``
        The configuration object

    Returns
    -------
    name: ``str``
        The name of the configuration object
    """
    cfg_copy = deepcopy(cfg)
    OmegaConf.set_struct(cfg_copy, False)
    cfg_copy.pop("name", None)
    OmegaConf.set_struct(cfg_copy, True)
    return cfg_copy


def init_from_cfg(cfg, base_class=None, *args, **kwargs):
    """
    Initialize a class instance from a configuration object

    Parameters
    ----------
    cfg: ``DictConfig``
        The configuration object
    base_class: ``class``
        The base class from which the instance should be initialized
    args: ``Any``
        The arguments to pass to the class constructor when initializing the instance
    kwargs: ``Any``
        The keyword arguments to pass to the class constructor

    Returns
    -------
    instance: ``Any``
        The instance of the class initialized
    """

    if "_target_" in cfg:
        return instantiate(cfg, *args, **kwargs)
    else:
        name = cfg.get("name", None)

        if name is None and base_class in None:
            raise ValueError("name and base_class cannot be None")

        if name and not base_class:
            try:
                base_class = Registrable.by_name(name)
            except RegistrationError as e:
                raise RegistrationError(
                    f"`{name}` is not a registered name for Registrable. "
                    "Please provide a proper base_class under which the class is registered."
                )

        elif name and base_class:
            base_class = base_class.by_name(name)

        if base_class is None:
            raise ValueError("base_class cannot be None")

        get_from_cfg = getattr(base_class, "from_cfg", None)

        if get_from_cfg and callable(base_class.from_cfg):
            return base_class.from_cfg(cfg, *args, **kwargs)

        cfg = pop_name(cfg)
        cfg = OmegaConf.to_container(cfg, resolve=True)

        return base_class(*args, **kwargs, **cfg)
