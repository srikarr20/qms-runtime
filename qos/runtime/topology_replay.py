import json
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import imageio.v2 as imageio

from pathlib import Path


class TopologyReplay:

    def __init__(

        self,

        runtime_tensor,

    ):

        self.runtime_tensor = runtime_tensor

        self.topology_state = (
            runtime_tensor[0]
            .topology_state
        )

        self.detector_count = (
            self.topology_state[
                "detector_count"
            ]
        )

        self.topology = (
            self.topology_state[
                "topology"
            ]
        )

    # ======================================================
    # BUILD GRAPH
    # ======================================================

    def build_graph(self):

        n = self.detector_count

        G = nx.Graph()

        for i in range(n):

            G.add_node(i)

        # ==================================================
        # RING
        # ==================================================

        if self.topology == "ring":

            for i in range(n):

                G.add_edge(
                    i,
                    (i + 1) % n,
                )

        # ==================================================
        # LINE
        # ==================================================

        elif self.topology == "line":

            for i in range(n - 1):

                G.add_edge(
                    i,
                    i + 1,
                )

        # ==================================================
        # FULLY CONNECTED
        # ==================================================

        elif self.topology == "fully_connected":

            for i in range(n):

                for j in range(i + 1, n):

                    G.add_edge(i, j)

        # ==================================================
        # RANDOM
        # ==================================================

        else:

            np.random.seed(42)

            for i in range(n):

                for j in range(i + 1, n):

                    if np.random.rand() > 0.7:

                        G.add_edge(i, j)

        return G

    # ======================================================
    # FRAME RENDER
    # ======================================================

    def render_frame(

        self,

        frame,

        export_path=None,

    ):

        G = self.build_graph()

        detector_states = np.array(

            self.runtime_tensor[frame]
            .detector_states

        )

        fig = plt.figure(
            figsize=(8, 8)
        )

        pos = nx.circular_layout(G)

        nx.draw_networkx_edges(

            G,

            pos,

            alpha=0.4,

        )

        nodes = nx.draw_networkx_nodes(

            G,

            pos,

            node_size=1000,

            node_color=
            detector_states,

            cmap="plasma",

        )

        nx.draw_networkx_labels(

            G,

            pos,

        )

        plt.colorbar(nodes)

        plt.title(

            f"Topology Replay "
            f"({self.topology}) "
            f"Frame {frame}"

        )

        plt.axis("off")

        if export_path:

            plt.savefig(

                export_path,

                dpi=150,

            )

        plt.close()

    # ======================================================
    # TEMPORAL REPLAY
    # ======================================================

    def temporal_replay(

        self,

        step=5,

        fps=8,

    ):

        export_dir = Path(

            "qos/artifacts/topology_replays"

        )

        export_dir.mkdir(

            parents=True,

            exist_ok=True,

        )

        frames = []

        # ==============================================
        # GENERATE FRAMES
        # ==============================================

        for frame in range(

            0,

            len(self.runtime_tensor),

            step,

        ):

            frame_path = (

                export_dir
                / f"frame_{frame:04d}.png"

            )

            self.render_frame(

                frame,

                export_path=frame_path,

            )

            frames.append(

                imageio.imread(
                    frame_path
                )

            )

        # ==============================================
        # EXPORT GIF
        # ==============================================

        gif_path = (

            export_dir
            / "topology_temporal_replay.gif"

        )

        imageio.mimsave(

            gif_path,

            frames,

            fps=fps,

        )

        metadata = {

            "topology":
            self.topology,

            "frames":
            len(frames),

            "detector_count":
            self.detector_count,

        }

        with open(

            export_dir
            / "temporal_metadata.json",

            "w",

        ) as f:

            json.dump(

                metadata,

                f,

                indent=4,

            )

        print(
            "\n=== Temporal Replay Exported ==="
        )

        print(gif_path)
