import random
from typing import Optional

from ns.packet.packet import Packet, PendingPacket
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
        outs = sorted(self.outs, key=lambda x: x.stt, reverse=True)
        # Calculate the diff between the delays of the wires
        for i in range(1, len(outs)):
            intervals.append(outs[i - 1].stt - outs[i].stt)
        print(f'intervals: {intervals}')
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


class PendingPulsingPacketGenerator(PulsingPacketGenerator):
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
            max_delay: int = 9000,
            window_size: int = 10,
    ):
        super().__init__(env, element_id, size_dist, finish, size, flow_id, rec_flow, debug)
        self.max_delay = max_delay
        self.window_size = window_size

    @property
    def max_stt(self):
        return int(self.outs[0].stt)

    @property
    def min_stt(self):
        return int(self.outs[-1].stt)

    @property
    def arrive(self):
        return self.max_stt + self.max_delay

    def get_t_list(self):
        t_list = [[] for _ in range(0, self.max_stt + 1)]
        for out in self.outs:
            t_list[int(out.stt)].append(out)
        return t_list

    def find_usable_path(self, t_list: list[list[GaussianDelayWire]], t: int) -> Optional[dict]:
        r_min = max(self.min_stt, self.arrive - self.max_delay - t)
        r_max = min(self.max_stt, self.arrive - t)
        stt_list = list(range(r_min, r_max + 1))

        # Find the nearest RS to the arrive time
        random.shuffle(stt_list)
        for stt in stt_list:
            if item_list := t_list[stt]:
                path: GaussianDelayWire = random.choice(item_list)
                return {
                    'wire': path,
                    "delay": self.arrive - stt - t,
                    'send_time': t,
                }

    def run(self):
        self.outs = sorted(self.outs, key=lambda x: x.stt, reverse=True)
        print(f"Send dura: {self.arrive}ms")
        send_times_expect = []
        arrival_times_expect = []

        prepared_list = []
        for t in range(0, int(self.arrive) + 1, self.window_size):
            if path := self.find_usable_path(self.get_t_list(), t):
                send_times_expect.append(t)
                arrival_times_expect.append(self.arrive)
                prepared_list.append(path)

        print(f"Prepare {len(prepared_list)} packets")
        for i, path in enumerate(prepared_list):
            if self.finish is not None and self.env.now >= self.finish:
                return
            packet = PendingPacket(
                self.env.now,
                self.size_dist(),
                self.packets_sent,
                src=self.element_id,
                flow_id=self.flow_id,
                delay=path['delay'],
            )
            self.sends.append(path['send_time'])
            path['wire'].put(packet)
            self.packets_sent += 1
            self.sent_size += packet.size

            if i + 1 < len(prepared_list):
                interval = prepared_list[i + 1]['send_time'] - path['send_time']
                yield self.env.timeout(interval)
