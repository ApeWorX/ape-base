from typing import cast

from ape_ethereum.ecosystem import NetworkConfig, create_network_config
from ape_optimism import Optimism, OptimismConfig

NETWORKS = {
    # chain_id, network_id
    "mainnet": (8453, 8453),
    "sepolia": (84532, 84532),
}


class BaseConfig(OptimismConfig):
    mainnet: NetworkConfig = create_network_config(block_time=2)
    sepolia: NetworkConfig = create_network_config(block_time=2)


class Base(Optimism):
    """
    Base is built on the OP-Stack, so `Base` inherits directly from `Optimism`.
    """

    @property
    def config(self) -> BaseConfig:  # type: ignore
        return cast(BaseConfig, self.config_manager.get_config("base"))
