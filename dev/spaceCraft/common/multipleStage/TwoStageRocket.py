from krpc import Client

from dev.spaceCraft.SpaceCraft import SpaceCraft


class TwoStageRocket(SpaceCraft):
    def __init__(self, conn: Client):
        super().__init__(conn)
        pass

    def launch(self):
        pass
