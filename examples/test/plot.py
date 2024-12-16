import math

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.figure import Figure

from examples.utils.db import get_db

sns.set_theme(style="whitegrid")


def plot(results, window_size=10):
    fig: Figure
    fig, axs = plt.subplots(int(math.ceil(len(results) / 2)), 2, figsize=(8, 6), dpi=120)
    fig.suptitle("Pending Attack Packet Send and Receive Distribution")
    for i in range(len(results) // 2):
        for j in range(2):
            if i * 2 + j >= len(results):
                return
            data = results[i * 2 + j]
            ax1: [plt.Axes] = axs[i, j]
            ax2: plt.Axes = ax1.twinx()
            weights = [1 for _ in range(len(data['sends']))]
            weights[-1] = 0
            send_ax = sns.histplot(x=data['sends'], binwidth=window_size, weights=weights, ax=ax1, kde=False,
                                   color='#86bf91',
                                   edgecolor='#007acc', label='Sender I/O')
            send_max = max([patch.get_height() for patch in send_ax.patches])
            recv_ax = sns.histplot(x=data['recvs'], binwidth=window_size, ax=ax2, kde=False, color='red',
                                   edgecolor='#007acc', label='Receiver I/O')
            recv_max = max([patch.get_height() for patch in recv_ax.patches])
            ax1.axhline(y=send_max, color='#86bf91', linestyle='--', label='Sender Max', linewidth=3)
            ax2.axhline(y=recv_max, color='red', linestyle='--', label='Receiver Max', linewidth=3)
            ax1.set_title(f"delay={data['max_delay']}")

            h1s, l1s = ax1.get_legend_handles_labels()
            h2s, l2s = ax2.get_legend_handles_labels()
            ax1.legend([h1s[1], h2s[1]], ['Sender', 'Receiver'], loc='center left')

            # ax2.get_yaxis().set_visible(False)
            ax2.set_ylabel("")
            ax1.set_ylabel("")
            texts = [
                f"Magnification: {recv_max / send_max:.2f}x",
                # f'Send Max: {send_max}, Recv Max: {recv_max}'
            ]
            print(f"Sender Max: {send_max}, Receiver Max: {recv_max}")
            print(f"Max Delay: {data['max_delay']}, Magnification: {recv_max / send_max:.2f}x")
            plt.text(0.40, 0.85, '\n'.join(texts),
                     fontsize=10, verticalalignment='top', transform=ax1.transAxes,
                     bbox=dict(facecolor='white', alpha=0.5))
            ax1.set_ylim(0, send_max * 10)
    fig.tight_layout(pad=2, rect=(0, 0, 1, 1.05))

    fig.supylabel('Packet Count')
    fig.supxlabel('Time (ms)')
    plt.savefig(f"../results/graphs/sender_vs_receiver_pending_compare.svg")
    plt.savefig(f"../results/graphs/sender_vs_receiver_pending_compare.png")
    plt.show()


def layers_plot(results: list[dict], window_size=10):
    sns.set_theme(style="whitegrid")

    fig: Figure
    fig, axs = plt.subplots(int(math.ceil(len(results) / 2)), 2, figsize=(8, 6), dpi=120)
    fig.suptitle("Cascade Layer Packet Send and Receive Distribution")
    for i in range(len(results) // 2):
        for j in range(2):
            if i * 2 + j >= len(results):
                break
            data = results[i * 2 + j]
            ax: plt.Axes = axs[i, j]
            send_ax = sns.histplot(x=data['sends'], ax=ax, binwidth=window_size, kde=False, color='#86bf91',
                                   edgecolor='#007acc', label='Sender I/O')
            send_max = max([patch.get_height() for patch in send_ax.patches])
            recv_ax = sns.histplot(x=data['recvs'], ax=ax, binwidth=window_size, kde=False, color='red',
                                   edgecolor='#007acc', label='Receiver I/O')
            recv_max = max([patch.get_height() for patch in recv_ax.patches])
            ax.legend(["Send", "Receive"])
            ax.axhline(y=send_max, color='#86bf91', linestyle='--', label='Sender Max', linewidth=3)
            ax.axhline(y=recv_max, color='red', linestyle='--', label='Receiver Max', linewidth=3)
            ax.set_title(f"layers={data['layers']}")
            # format xticks to .1f
            # ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x:.1f}'))
            print(f"Sender Max: {send_max}, Receiver Max: {recv_max}")
            print(f"Layers: {data['layers']}, Magnification: {recv_max / send_max:.2f}x")
            # ax2.set_ylabel("")
            ax.set_ylabel("")
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
    fig.supylabel('Packet Count')
    fig.supxlabel('Time (ms)')
    fig.tight_layout()
    plt.savefig(f'../results/graphs/layers_compare.svg', bbox_inches='tight')
    plt.show()


db = get_db()
collection = db['result']
# results = list(collection.find({
#     'max_delay': {'$in': [10, 1000, 5000, 9000]},
#     'layers': 2,
#     # 'sigma': 0.1
# }))
# plot(results)

results = list(collection.find({
    'layers': {'$in': [2, 3, 4, 5]},
    'max_delay': 0
}))

layers_plot(results)
