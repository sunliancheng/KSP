# Press the green button in the gutter to run the script.

import krpc

from dev.connect.ConnectionConfig import ConnectionConfig
from dev.spaceCraft.common.singleStage.SingleStageRocket import SingleStageRocket
from dev.spaceCraft.common.singleStage.configs.SampleSingleStageRocketConfig import SampleSingleStageRocketConfig
from dev.utils.vessel.VesselControlUtils import VesselControlUtils


def handleCommand(cmd):
    match cmd:
        case "quit":
            pass
        case "sample_launch":
            # This is for single stage rocket with infinite fuel.
            conn = krpc.connect(name='hello', address=ConnectionConfig.address,
                                stream_port=ConnectionConfig.stream_port)
            vessel = SingleStageRocket(conn, SampleSingleStageRocketConfig())
            vessel.launch()
        case "circularize":
            pass


if __name__ == '__main__':
    vc = VesselControlUtils()
    conn = krpc.connect(name='hello', address=ConnectionConfig.address,
                        stream_port=ConnectionConfig.stream_port)
    vessel = SingleStageRocket(conn, SampleSingleStageRocketConfig())
    vc.circularize(conn, vessel.vessel)
