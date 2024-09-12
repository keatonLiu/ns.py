"""
A basic example that connects two packet generators to a network wire with
a propagation delay distribution, and then to a packet sink.
"""
import dataclasses
import math
from random import expovariate
from typing import Optional

import simpy
from matplotlib.figure import Figure

from ns.packet.PulsingPacketGenerator import PulsingPacketGenerator
from ns.packet.sink import PacketSink
from ns.port.wire import GaussianDelayWire
import matplotlib.pyplot as plt
import seaborn as sns

from ns.utils.generators.NormPacketGenerator import NormPacketGenerator

sns.set()


@dataclasses.dataclass
class SimulateResult:
    sends: list
    recvs: list
    sigma: float


def plot(results: list[SimulateResult], window_size=0.01):
    sns.set_theme(style="whitegrid")

    fig: Figure
    fig, axs = plt.subplots(int(math.ceil(len(results) / 2)), 2, figsize=(8, 6), dpi=120)
    fig.suptitle("Packet Send and Receive Distribution")
    for i in range(len(results) // 2):
        for j in range(2):
            if i * 2 + j >= len(results):
                break
            result = results[i * 2 + j]
            ax: plt.Axes = axs[i, j]

            send_ax = sns.histplot(result.sends, ax=ax, binwidth=window_size, kde=False, color='#86bf91',
                                   edgecolor='#007acc', label='Sender I/O')
            send_max = max([patch.get_height() for patch in send_ax.patches])
            recv_ax = sns.histplot(result.recvs, ax=ax, binwidth=window_size, kde=False, color='red',
                                   edgecolor='#007acc', label='Receiver I/O')
            recv_max = max([patch.get_height() for patch in recv_ax.patches])
            ax.legend(["Send", "Receive"])
            ax.axhline(y=send_max, color='#86bf91', linestyle='--', label='Sender Max', linewidth=3)
            ax.axhline(y=recv_max, color='red', linestyle='--', label='Receiver Max', linewidth=3)
            ax.set_title(f"σ={result.sigma}")
            # format xticks to .1f
            ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}'))

            # plt.xlim(0, min(ps.arrivals["flow_1"][-1], 2000))

            # ax.title(f"Packet Send and Receive Distribution(σ={result.sigma})")
            # ax.xlabel('Timestamp(ms)')
            # ax.ylabel('Number of Packets')

            # 添加文字
            ax.text(0.45, 0.85, f'Magnification: {recv_max / send_max:.2f}x',
                    transform=ax.transAxes, fontsize=10, verticalalignment='top',
                    bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))

            # plt.text(0.35, 0.85, f'Packet number magnification: {len(recvs) / len(sends):.2f}',
            #          transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
            #          bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))
    # plt.title(f"Packet Send and Receive Distribution")
    # for ax in fig.get_axes():
    #     ax.label_outer()
    fig.tight_layout()
    plt.savefig(f'results/graphs/packet_send_receive.png', bbox_inches='tight')
    plt.show()


class ODnsSimulator:
    def __init__(self):
        self.env = simpy.Environment()

    @staticmethod
    def packet_size_dist():
        return int(expovariate(0.01))

    def simulate(self, sigma=0.02, num_paths=10, layers=4):
        norm_gen = NormPacketGenerator(0.100, 3.000, 0.010, 3.000)
        wires: list[Optional[GaussianDelayWire]] = [None for _ in range(num_paths)]
        paths = []
        for i in range(layers):
            for j in range(num_paths):
                delay = norm_gen.get_next()
                # each wire has a gaussian distribution of delays
                wires[j] = GaussianDelayWire(self.env, delay, sigma, wire_id=j)
            if not paths:
                paths = wires
            else:
                new_paths = []
                for path in paths:
                    for wire in wires:
                        new_paths.append(path + wire)
                paths = new_paths

        ps = PacketSink(self.env, rec_flow_ids=False, debug=True)
        pg = PulsingPacketGenerator(self.env, "flow_1", self.packet_size_dist, finish=10, flow_id=0)
        pg.outs = paths
        for path in paths:
            path.out = ps
        self.env.run(until=3500)

        print(
            "Packet send times in flow 1: "
            + ", ".join(["{:.3f}".format(x) for x in pg.sends])
        )
        print(len(pg.sends))
        print(
            "Packet arrival times in flow 1: "
            + ", ".join(["{:.3f}".format(x) for x in ps.arrivals["flow_1"]])
        )
        print(len(ps.arrivals["flow_1"]))

        return SimulateResult(pg.sends, ps.arrivals["flow_1"], sigma)


if __name__ == '__main__':
    env = simpy.Environment()
    results = [ODnsSimulator().simulate(sigma=s) for s in [0.02, 0.04, 0.06, 0.08]]
    plot(results)
