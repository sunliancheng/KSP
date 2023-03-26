import krpc

from dev.connect.ConnectionConfig import ConnectionConfig
from dev.spaceCraft.common.singleStage.SingleStageRocket import SingleStageRocket

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    conn = krpc.connect(name='hello', address=ConnectionConfig.address, stream_port=ConnectionConfig.stream_port)
    vessel = SingleStageRocket(conn)
    vessel.launch()
