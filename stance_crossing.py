import networkx as nx
import matplotlib.pyplot as plt
import pickle
from fa2 import ForceAtlas2
from matplotlib.backends.backend_pdf import PdfPages
from collections import Counter
import matplotlib.patches as mpatches


def easier_indexing(Gs):
    """
        Quick tool for easier indexing 
    """
    keys = [Gs[i][1][:-5] for i in range(len(Gs))]
    topic_dict = dict(zip(keys, list(range(len(keys)))))
    return topic_dict

def side_renaming(network1, network2):
    """ 
        Rename stances of nodes on the topic.

        Parameters
        ----------
        network1 : networkx.classes.graph.Graph
            The first network
        network2 : networkx.classes.graph.Graph
            The second network
    """

    # There is probably faster way to perform this, optimize later if needed
    for i in range(len(network1.nodes)):
    
        if (network1.nodes[i]["group"] == "#fcae91FF"):
            network1.nodes[i]["T1"] = "0"

        elif (network1.nodes[i]["group"] == "#7828a0FF"):
            network1.nodes[i]["T1"] = "1"
            
        else:
            print("Error with group encoding!")
        
        
    for i in range(len(network2.nodes)):
        
        if (network2.nodes[i]["group"] == "#fcae91FF"):
            network2.nodes[i]["T2"] = "0"
            
        elif (network2.nodes[i]["group"] == "#7828a0FF"):
            network2.nodes[i]["T2"] = "1"
            
        else:
            print("This should not be printed! Error with group encoding!")

    return network1, network2

def pos_fa_layout(network_union):
    """
        ForceAtlas2 to get the layout of the network (the positions)

        Parameters
        ----------
        network_union : networkx.classes.graph.Graph
            The union of network1 and network1

        Copyright (C) 2017 Bhargav Chippada bhargavchippada19@gmail.com.
        Licensed under the GNU GPLv3.
    """
    forceatlas2 = ForceAtlas2(
                        # Behavior alternatives
                        outboundAttractionDistribution=True,  # Dissuade hubs
                        linLogMode=False,  # NOT IMPLEMENTED
                        adjustSizes=False,  # Prevent overlap (NOT IMPLEMENTED)
                        edgeWeightInfluence=1.0,

                        # Performance
                        jitterTolerance=1.0,  # Tolerance
                        barnesHutOptimize=True,
                        barnesHutTheta=1.2,
                        multiThreaded=False,  # NOT IMPLEMENTED

                        # Tuning
                        scalingRatio=2.0,
                        strongGravityMode=False,
                        gravity=1.0,

                        # Log
                        verbose=True)

    pos = forceatlas2.forceatlas2_networkx_layout(network_union, pos=None, iterations=3000)
    return pos

def encode_sides(network_union):
    """
        This function encodes all the possible combinations of different supporting behaviour

        Parameters
        ----------
        network_union : networkx.classes.graph.Graph
            The union of network1 and network1
    """
    user_stances = dict()

    for node in network_union.nodes.data():
        if ("T1" in node[1] and "T2" in node[1]):
            user_stances[node[1]["handle"]] = (node[1]["T1"], node[1]["T2"])
        else:
            if ("T1" not in node[1]):
                user_stances[node[1]["handle"]] = ("NA", node[1]["T2"])
                
            if ("T2" not in node[1]):
                user_stances[node[1]["handle"]] = (node[1]["T1"], "NA")

    assert len(user_stances) == len(network_union), "Check the side encoding"

    return user_stances

def get_statistics(network_union, user_sides):
    
    N_tweeting_on_either = len(network_union)
    stance_counts = Counter(user_sides.values())

    # How the stances on second topic differ among the users that agreed on the first topic
    try:
        T1G1_T2G1 = stance_counts[('0', '0')]/(stance_counts[('0', '0')] + stance_counts[('0', '1')])   
        T1G1_T2G2 = 1 - T1G1_T2G1
    except ZeroDivisionError:
        T1G1_T2G1 = "NA"
        T1G1_T2G2 = "NA"

    # How the stances on second topic differ among the users that disagreed on the first topic
    try:
        T1G2_T2G1 = stance_counts[('1', '0')]/(stance_counts[('1', '1')] + stance_counts[('1', '0')])
        T1G2_T2G2 = 1 - T1G2_T2G1
    except ZeroDivisionError:
        T1G2_T2G1 = "NA"
        T1G2_T2G2 = "NA"

    N_tweeting_on_both = stance_counts[('0', '0')] + stance_counts[('1', '1')] + stance_counts[('1', '0')] + stance_counts[('0', '1')]
    stats_dict = {"N_tweeting_on_either": N_tweeting_on_either, "N_tweeting_on_both": N_tweeting_on_both, "T1G1_T2G1": T1G1_T2G1, "T1G1_T2G2": T1G1_T2G2, "T1G2_T2G1": T1G2_T2G1, "T1G2_T2G2": T1G2_T2G2}

    return stats_dict

def encode_colors(network_union, user_sides):

    color_encoding = dict()

    for node in network_union.nodes:
        
        if user_sides[node] == ('0', '0'):
            color_encoding[node] = '#d62728'
            
        elif user_sides[node] == ('0', '1'):
            color_encoding[node] = '#ff7f0e'
            
        elif user_sides[node] == ('1', '0'):
            color_encoding[node] = '#1f77b4'
            
        elif user_sides[node] == ('1', '1'):
            color_encoding[node] = '#17becf'
            
        else:
            color_encoding[node] = '#7f7f7f'

    return color_encoding

def visualize_network(network_union, user_sides, T1, T2):
    
    color_encoding = encode_colors(network_union, user_sides)
    stance_stats = get_statistics(network_union, user_sides)
    pos = pos_fa_layout(network_union)

    textstr = '\n'.join((
        r'# users tweeting on either topic = %.2f' % (stance_stats["N_tweeting_on_either"], ),
        r'# users tweeting on both topic = %.2f' % (stance_stats["N_tweeting_on_both"], ),
        r'T1G1_T2G1 = %.2f' % (stance_stats["T1G1_T2G1"], ),
        r'T1G1_T2G2 = %.2f' % (stance_stats["T1G1_T2G2"], ),
        r'T1G2_T2G1 = %.2f' % (stance_stats["T1G2_T2G1"], ),
        r'T1G2_T2G2 = %.2f' % (stance_stats["T1G2_T2G2"], )))

    fig = plt.figure(figsize=(20,10))

    nx.draw(network_union, pos, node_size = 3, width= 0.2, node_color = color_encoding.values(), edge_color = "#333333FF")

    fig.suptitle(T1 + " and " + T2, fontsize=14)
    fig.text(0.05, 0.95, textstr, fontsize=14, verticalalignment='top')

    legend_dict = { "T1G1_T2G1" : '#d62728', "T1G1_T2G2" : '#ff7f0e', "T1G2_T2G1" : '#1f77b4', "T1G2_T2G2" :  '#17becf', "Tweeted only on one topic" : '#7f7f7f'}
    patchList = []
    for key in legend_dict:
            data_key = mpatches.Patch(color=legend_dict[key], label=key)
            patchList.append(data_key)

    plt.legend(handles=patchList)

    return fig

def main():

    plot_filename = 'bistance_plots_2.pdf'
    # Select the topics
    #TOPIC1 = "vihreät"
    #TOPIC2 = "maahanmuutto"

    PARTIES = ["kokoomus", "vihreät", "keskusta", "perussuomalaiset", "vasemmisto", "sdp"]
    THEMES = ["ilmastonmuutos", "sote", "maahanmuutto", "hallitus", "vihapuhe", "rasismi", "tekoäly", "yle", "talous"]

    with PdfPages(plot_filename) as pdf:

        for TOPIC1 in PARTIES:
            for TOPIC2 in THEMES: 
                
                # Load the nested list of graphs that the pipeline outputs as a pickle
                Gs = pickle.load(open("graphlist.pickle", "rb"))

                # Easier indexing
                topic_dict = easier_indexing(Gs)

                # Load the corresponding networks
                network1 = Gs[topic_dict[TOPIC1]][0][0][0]
                network2 = Gs[topic_dict[TOPIC2]][0][0][0]

                # Rename the sides of each node
                network1, network2 = side_renaming(network1, network2)

                # Use handle names as node IDs
                network1 = nx.relabel_nodes(network1, nx.get_node_attributes(network1, "handle"))
                network2 = nx.relabel_nodes(network2, nx.get_node_attributes(network2, "handle"))

                # Take the union of the two networks
                network_union = nx.compose(network1, network2)

                # Get the positions of nodes
                #positions = pos_fa_layout(network_union)

                # Side encoding
                user_sides = encode_sides(network_union)

                # Compute the selected stats
                #stance_stats = get_statistics(network_union, user_sides)

                # Draw the network
                fig = visualize_network(network_union, user_sides, TOPIC1, TOPIC2)

                # Save the fig to pdf
                
                
                pdf.savefig(fig)
                print(TOPIC1 + " and " + TOPIC2 + " completed.")

                #print(stance_stats)
                #print(nx.info(network_union))
                #print(network_union.nodes.data())

if __name__ == '__main__':
    main()
    