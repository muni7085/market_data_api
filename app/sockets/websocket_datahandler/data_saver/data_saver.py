from abc import ABC, abstractmethod

from registrable import Registrable


class DataSaver(ABC, Registrable):
    """
    This is the base class for all the data savers. The data savers are
    responsible for retrieving the data from the respective sources and
    saving the data to the respective databases.The subclasses of this
    class should implement the `retrieve_and_save` method to retrieve the
    data from the respective sources and save the data to the respective
    databases
    """

    @abstractmethod
    def retrieve_and_save(self):
        """
        This method retrieves the data from the respective sources and
        saves the data to the respective databases
        """
        raise NotImplementedError

    @abstractmethod
    def from_cfg(cls, cfg) -> "DataSaver":
        pass
