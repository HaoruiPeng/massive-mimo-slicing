import json
import node

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
        alarm_nodes[i] = node.Node(alarm_arrival_distribution, settings)

    # Initialize control nodes
    control_nodes = []
    for i in range(no_control_nodes):
        settings = config.get('control_arrival_distributions').get(control_arrival_distribution)
        control_nodes[i] = node.Node(control_arrival_distribution, settings)

    for i in range(iterations):
        pilot_counter = 1

        if pilots > no_alarm_nodes + no_control_nodes:
            # Assign one pilot to all nodes
            for j in range(no_alarm_nodes):
                alarm_nodes[j].pilotNo = pilot_counter
                pilot_counter += 1

            for j in range(no_control_nodes):
                control_nodes[j].pilotNo = pilot_counter
                pilot_counter += 1

        else:
            # Determine pilot share
            alarm_pilots = alarm_pilot_share * pilots
            control_pilots = pilots - alarm_pilots

            # Adjust pilot share
            if control_nodes == 0:
                control_pilots = 1
                alarm_pilots -= 1

            # Calculate number of nodes per pilot
            alarm_nodes_per_pilot = int(no_alarm_nodes / alarm_pilots)
            extra_alarm_nodes = no_alarm_nodes % alarm_pilots
            control_nodes_per_pilot = int(no_control_nodes / control_pilots)
            extra_control_nodes = no_control_nodes % control_pilots

            # Assign the alarm pilots

            alarm_pilot_counter = 1
            for j in range(alarm_pilots):
                for k in range(alarm_nodes_per_pilot):
                    alarm_nodes[j]

                for k in range(alarm_nodes_per_pilot):
                    alarm_nodes[j].pilotNo = pilot_counter

                pilot_counter += 1

            alarm_counter = 0
            while alarm_counter < no_alarm_nodes:
                if alarm_counter < alarm_pilots:
                    for k in range(alarm_nodes_per_pilot):
                        alarm_nodes[alarm_counter].pilotNo = pilot_counter
                else

                alarm_counter += 1
                pilot_counter += 1

            # If any alarm nodes left, add additional pilots
