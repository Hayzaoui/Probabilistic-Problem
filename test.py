import utils
import Graph

small_inputs = [
    {
        "map": [['P', 'P', 'P', 'P', 'P'],
                ['P', 'I', 'P', 'P', 'P'],
                ['P', 'I', 'I', 'I', 'P'],
                ['P', 'P', 'P', 'I', 'P'], ],
        "drones": {'drone 1': (3, 0),
                   'drone 2': (0, 3)},
        "packages": {'package 1': 'drone 1',
                     'package 2': (3, 4)},
        "clients": {'Alice': {"location": (0, 0),
                              "packages": ('package 1',),
                              "probabilities": (0.3, 0.3, 0.15, 0.15, 0.1)},
                    'Bob': {"location": (2, 1),
                            "packages": ('package 2',),
                            "probabilities": (0.15, 0.15, 0.3, 0.3, 0.1)}
                    },
        "turns to go": 150
    },
]
pack_to_deliver = 'package 1'
state = small_inputs[0]
#client_to_deliver = \
#[[client, val['location']] for client, val in state['clients'].items() if pack_to_deliver in val['packages']][0]

for client, val in state['clients'].items():
        print("client=", client)
        print("val=", val['location'])