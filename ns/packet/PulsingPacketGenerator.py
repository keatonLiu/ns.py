from ns.packet.packet import Packet
from ns.port.wire import GaussianDelayWire


class PulsingPacketGenerator:
    def __init__(
            self,
            env,
            element_id,
            size_dist,
            finish=None,
            size=None,
            flow_id=0,
            rec_flow=False,
            debug=False,
    ):
        self.element_id = element_id
        self.env = env
        self.size_dist = size_dist
        self.finish = float("inf") if finish is None else finish
        self.size = float("inf") if size is None else size
        self.outs: list[GaussianDelayWire] = []
        self.packets_sent = 0
        self.sent_size = 0
        self.action = env.process(self.run())
        self.flow_id = flow_id
        self.sends = []

    def run(self):
        intervals = []
        outs = sorted(self.outs, key=lambda x: x.delay, reverse=True)
        # Calculate the diff between the delays of the wires
        for i in range(1, len(outs)):
            intervals.append(outs[i - 1].delay - outs[i].delay)

        wire_index = 0
        while self.env.now < self.finish:
            if wire_index >= len(outs):
                return
            wire = outs[wire_index]
            packet = Packet(
                self.env.now,
                self.size_dist(),
                self.packets_sent,
                src=self.element_id,
                flow_id=self.flow_id,
            )
            self.sends.append(self.env.now)
            wire.put(packet)
            self.packets_sent += 1
            self.sent_size += packet.size
            wire_index += 1

            # Sleep for the interval between the wires
            if wire_index < len(outs):
                yield self.env.timeout(intervals[wire_index - 1])
