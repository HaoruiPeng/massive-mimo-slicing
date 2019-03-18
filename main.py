import json
import node


def assign_pilots(pilot_no, available_pilots, nodes):
    # Determine nodes per pilot
    nodes_per_pilot = int(available_pilots / len(nodes))

    # Assign pilots to primary nodes
    pilot_start = pilot_no
    for ni in range(available_pilots):
        for nj in range(nodes_per_pilot):
            nodes[ni + nj].pilot_no = pilot_counter

        pilot_no += 1

    # Assign pilots to residual nodes
    for ni in range(len(nodes) - nodes_per_pilot * available_pilots):
        nodes[ni].pilot_no = pilot_start
        pilot_start += 1

    return nodes, pilot_counter


if __name__ == 'main':
    # Load default configuration
    with open("config.json") as f:
        config = json.load(f)

    simulation_time = config.get('simulation_time')
    frame_length = config.get('frame_length')
    no_alarm_nodes = config.get('alarm_nodes')
    no_control_nodes = config.get('control_nodes')
    pilots = config.get('pilots')
    alarm_arrival_distribution = config.get('alarm_arrival_distribution')
    control_arrival_distribution = config.get('control_arrival_distribution')
    alarm_pilot_share = config.get('alarm_pilot_share')

    # Determine number of simulation iterations
    iterations = int(simulation_time * 1000 / frame_length)

    # Initialize alarm nodes
    alarm_nodes = []
    for i in range(no_alarm_nodes):
        settings = config.get('alarm_arrival_distributions').get(alarm_arrival_distribution)
        alarm_nodes[i] = node.Node(alarm_arrival_distribution, settings, buffer_size=0)

    # Initialize control nodes
    control_nodes = []
    for i in range(no_control_nodes):
        settings = config.get('control_arrival_distributions').get(control_arrival_distribution)
        control_nodes[i] = node.Node(control_arrival_distribution, settings, buffer_size=5)

    for i in range(iterations):
        pilot_counter = 0

        if pilots > no_alarm_nodes + no_control_nodes:
            # Assign one pilot to all nodes
            for j in range(no_alarm_nodes):
                alarm_nodes[j].pilot_no = pilot_counter
                pilot_counter += 1

            for j in range(no_control_nodes):
                control_nodes[j].pilot_no = pilot_counter
                pilot_counter += 1

        else:
            # Determine pilot share
            alarm_pilots = alarm_pilot_share * pilots
            control_pilots = pilots - alarm_pilots

            # Adjust pilot share
            if control_nodes == 0:
                control_pilots = 1
                alarm_pilots -= 1

            # Assign alarm and control nodes
            alarm_nodes, pilot_counter = assign_pilots(pilot_counter, alarm_pilots, alarm_nodes)

            # Sort the control nodes by number of items in the system
            control_nodes = sorted(control_nodes, key=lambda a, b: a.num_in_system - b.num_in_system)

            # Assign pilots
            control_nodes, pilot_counter = assign_pilots(pilot_counter, control_pilots, control_nodes)
