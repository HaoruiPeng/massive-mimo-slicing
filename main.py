import json
import node


def assign_pilots(pilot_no, available_pilots, nodes):
    # Determine nodes per pilot
    nodes_per_pilot = int(available_pilots / len(nodes))

    # Assign pilots to primary nodes
    pilot_start = pilot_no
    for ni in range(available_pilots):
        for nj in range(nodes_per_pilot):
            nodes[ni + nj].pilot_no = pilot_no

        pilot_no += 1

    # Assign pilots to residual nodes
    for ni in range(len(nodes) - nodes_per_pilot * available_pilots):
        nodes[ni].pilot_no = pilot_start
        pilot_start += 1

    return nodes, pilot_no


def advance_time(nodes):
    # Loop alarm nodes and handle arrival events
    # Set flag if nodes want to send
    for n in nodes:
        n.handle_arrival()
        n.try_to_depart()

    return nodes


def check_collisions(nodes):
    no_collisions = 0

    # Loop through all nodes that have tried to send data
    for nsi in range(len(nodes)):
        # Only check nodes that have data to send
        if not nodes[nsi].want_to_send:
            continue

        base_pilot = nodes[nsi].pilot_no
        collision = False

        for nsj in range(len(nodes)):
            # Only check nodes that have data to send
            if not nodes[nsj].want_to_send:
                continue

            target_pilot = nodes[nsj].pilot_no

            # If collision, add the packet back to the queue
            if base_pilot == target_pilot:
                no_collisions += 1
                collision = True

        if not collision:
            nodes[nsi].handle_departure()

    return nodes, no_collisions


def run():
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
        alarm_nodes.append(node.Node(alarm_arrival_distribution, settings, buffer_size=0))

    # Initialize control nodes
    control_nodes = []
    for i in range(no_control_nodes):
        settings = config.get('control_arrival_distributions').get(control_arrival_distribution)
        control_nodes.append(node.Node(control_arrival_distribution, settings, buffer_size=5))

    # System performance variables
    total_alarm_collisions = 0
    total_control_collisions = 0

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
            alarm_pilots = int(alarm_pilot_share * pilots)
            control_pilots = int(pilots - alarm_pilots)

            # Adjust pilot share
            if control_nodes == 0:
                control_pilots = 1
                alarm_pilots -= 1

            # Assign alarm and control nodes
            alarm_nodes, pilot_counter = assign_pilots(pilot_counter, alarm_pilots, alarm_nodes)

            # Sort the control nodes by number of items in the system
            control_nodes = sorted(control_nodes, key=lambda x: x.num_in_system)

            # Assign pilots, no need to retrieve the pilot counter
            control_nodes, pilot_counter = assign_pilots(pilot_counter, control_pilots, control_nodes)

            # Handle arrival and departure for all nodes
            alarm_nodes = advance_time(alarm_nodes)
            control_nodes = advance_time(control_nodes)

            # Check collisions for alarm and control nodes
            alarm_nodes, no_alarm_collisions = check_collisions(alarm_nodes)
            control_nodes, no_control_collisions = check_collisions(control_nodes)

            # Add to statistics
            total_alarm_collisions += no_alarm_collisions
            total_control_collisions += no_control_collisions

    print("No alarm collisions: {}".format(total_alarm_collisions))
    print("No control collisions: {}".format(total_control_collisions))


run()
