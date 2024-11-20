from ape import plugins


@plugins.register(plugins.Config)
def config_class():
    from .ecosystem import BaseConfig

    return BaseConfig


@plugins.register(plugins.EcosystemPlugin)
def ecosystems():
    from .ecosystem import Base

    yield Base


@plugins.register(plugins.NetworkPlugin)
def networks():
    from ape.api.networks import (
        LOCAL_NETWORK_NAME,
        ForkedNetworkAPI,
        NetworkAPI,
        create_network_type,
    )

    from .ecosystem import NETWORKS

    for network_name, network_params in NETWORKS.items():
        yield "base", network_name, create_network_type(*network_params)
        yield "base", f"{network_name}-fork", ForkedNetworkAPI

    # NOTE: This works for local providers, as they get chain_id from themselves
    yield "base", LOCAL_NETWORK_NAME, NetworkAPI


@plugins.register(plugins.ProviderPlugin)
def providers():
    from ape.api.networks import LOCAL_NETWORK_NAME
    from ape_node import Node
    from ape_test import LocalProvider

    from .ecosystem import NETWORKS

    for network_name in NETWORKS:
        yield "base", network_name, Node

    yield "base", LOCAL_NETWORK_NAME, LocalProvider


def __getattr__(name: str):
    if name == "NETWORKS":
        from .ecosystem import NETWORKS

        return NETWORKS

    elif name == "Base":
        from .ecosystem import Base

        return Base

    elif name == "BaseConfig":
        from .ecosystem import BaseConfig

        return BaseConfig

    else:
        raise AttributeError(name)


__all__ = [
    "NETWORKS",
    "Base",
    "BaseConfig",
]
