# massive-mimo-simulator

This repository provides a network simulator for a factory floor with a number
of machines with control traffic and a number of alarm nodes with 
alarm traffic.

This README provides a how-to for downloading and running the application. A brief 
introduction to the different design parameters is available under *Customizing*. Please refer
to the in-code documentation for implementation details.

### Cloning the repository
Open CMD or terminal in an appropriate folder.

Enter the command: `git clone https://github.com/jost95/massive-mimo-simulator.git`

### Executing

Within the repository, run: `python main.py`

### Customizing

The different design parameters are:

  * `simulation_name` name of the simulation (groups statistics)
  * `simulation_length` simulation length in seconds
  * `max_attempts` deadline for packets in frames
  * `no_alarm_nodes` number of alarm nodes
  * `no_control_nodes` number of control nodes
  * `no_pilots` number of available pilots
  * `control_nodes_buffer` control node buffer before packets expiring
  * `active_alarm_arrival_distribution` alarm arrival distribution (exponential, uniform, constant) 
  * `active_control_arrival_distribution` control arrival distribution (exponential, uniform, constant)
  * `base_alarm_pilot_share` Base share of dedicated resources for alarm packets in decimals
  * `frame_length` length of one simulation frame, i.e. determines the departure
  * `measurement_period` how often measurements should be taken
  * `use_seed` use a seed for the random generator (to recreate simulation results) \[0, 1]
  * `multi_run` run multiple simulations with changing parameters (configure in main.py) \[0, 1]
  * `custom_alarm_arrivals` custom alarm arrivals (distribution settings and deadline) for every node \[0, 1]
  * `custom_control_arrivals` custom control arrivals (distribution settings and deadline) for every node \[0, 1]

Please see config file for the distributions' parameters, e.g. mean arrival rate.

### Pilot assignment approaches
The main `simulation` class should be inherited required method implemented for the simulation to work. There currently exists two pilot assignment approaches, one reactive and pro-active (named `binary` and `huffman` respectively). Please see in-code comments for implementation details

### License
This repository is maintained under *GNU General Public License v3.0*.

