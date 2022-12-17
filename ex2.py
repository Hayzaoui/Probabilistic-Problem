import itertools
import random

random.seed(25)
import utils

ids = ["111111111", "111111111"]


class DroneAgent:

    def __init__(self, initial):
        self.map = initial["map"]
        self.n = len(self.map)  # number of rows
        self.m = len(self.map[0])  # number of cols
        self.t = 0
        self.deliverPerDrone = {}
        self.pickupPerDrone = {}
        self.prededent_position = tuple()
        for key in initial['drones'].keys():
            self.deliverPerDrone.update({key: 0})
            self.pickupPerDrone.update({key: 0})
        self.reset_list = list()
        self.turns = initial["turns to go"]

    def act(self, state):

        max_rounds = self.turns
        if len(state['packages'].values()) == 0:
            if len(self.reset_list) == 0:
                self.reset_list.append(max_rounds - state["turns to go"])
            else:
                this_turn = max_rounds - state["turns to go"] - sum(self.reset_list)
                self.reset_list.append(this_turn)
            meanReset = sum(self.reset_list) / len(self.reset_list)
            if state["turns to go"] > meanReset:
                print('reset', state["turns to go"])
                self.t = 0
                return "reset"
            else:
                print("TERMINATE")
                return "terminate"

        pack_available = []
        pack_per_drone = {}
        actions = []
        actions_list = []
        new_act = []
        pack_list_picked = []
        package_not_delivered = state["packages"]

        for key in state['drones'].keys():
            pack_per_drone.update({key: []})
        for pack in state['packages'].keys():
            if type(state['packages'][pack]) == tuple:
                pack_available.append(pack)
            else:
                pack_per_drone[state['packages'][pack]].append(pack)

        for key, pos in state["drones"].items():
            actions.append(tuple(
                self.allPosibilityOneDrone(key, pos, package_not_delivered, state["clients"])))  # on tuple apres

        for act_per_drone in actions:
            new_act_per_drone = []
            name_drone = act_per_drone[0][1]

            if self.deliverPerDrone[name_drone] == 1:  # deliver
                for atomic_action in act_per_drone:
                    if atomic_action[0] == 'deliver':
                        new_act_per_drone.append(atomic_action)
            if self.pickupPerDrone[name_drone] == 1:  # pick up
                for atomic_action in act_per_drone:
                    if atomic_action[0] == 'pick up':
                        if atomic_action[2] in pack_list_picked:
                            self.pickupPerDrone[name_drone] = 0
                            continue
                        else:
                            pack_list_picked.append(atomic_action[2])
                            new_act_per_drone.append(atomic_action)

            if self.deliverPerDrone[name_drone] == 0 and self.pickupPerDrone[name_drone] == 0:
                position_actual_drone = state['drones'][name_drone]
                min_at_act = act_per_drone[0]
                if pack_available:
                    if len(pack_per_drone[name_drone]) < 2:
                        nearest_pack, dist_nearest_pack = self.specialmin(
                            [[pack, utils.distance_squared(position_actual_drone, val)] for pack, val in
                             state['packages'].items() if type(val) == tuple])
                        position_nearest_pack = state['packages'][nearest_pack]
                        for atomic_action in act_per_drone:
                            if atomic_action[0] == 'move':  # on rajoute que les moves vers les pack dispo
                                future_pos = atomic_action[2]
                                if utils.distance_squared(future_pos, position_nearest_pack) <= dist_nearest_pack:
                                    min_at_act = atomic_action
                                    dist_nearest_pack = utils.distance_squared(future_pos, position_nearest_pack)
                new_act_per_drone.append(min_at_act)
                if len(pack_per_drone[name_drone]) == 1 or len(pack_per_drone[name_drone]) == 2:
                    min_at_act = act_per_drone[0]
                    min_dist = 100
                    client_to_deliver = []
                    for pack_to_deliver in pack_per_drone[name_drone]:
                        client_to_deliver = [[client, val['location']] for client, val in
                                             state['clients'].items() if pack_to_deliver in val['packages']][0]
                        min_dist = utils.distance_squared(state['drones'][name_drone], client_to_deliver[1])

                    for atomic_action in act_per_drone:
                        if atomic_action[0] == 'move':
                            future_pos = atomic_action[2]
                            if utils.distance_squared(future_pos, client_to_deliver[1]) <= min_dist:
                                min_at_act = atomic_action
                                min_dist = utils.distance_squared(future_pos, client_to_deliver[1])

                    new_act_per_drone.append(min_at_act)
            print(self.t)
            if self.t > 0:
                #print("NewAct avant=", new_act_per_drone)
                for atomic_action in new_act_per_drone:
                    if atomic_action[0] == 'move':
                        #print("atomation=", atomic_action)
                        #print("Precedent position=", self.prededent_position)
                        if atomic_action[2] == self.prededent_position[new_act_per_drone[0][1]] and len(new_act_per_drone) >= 2:
                            new_act_per_drone.remove(atomic_action)
                        elif atomic_action[2] == self.prededent_position[new_act_per_drone[0][1]] and len(new_act_per_drone) < 2:
                            new_act_per_drone.append(("wait", new_act_per_drone[0][1]))
                            new_act_per_drone.remove(atomic_action)
                #print("NewAct apres=", set(new_act_per_drone))
            new_act.append(tuple(set(new_act_per_drone)))
        # print("New Act", new_act)

        for action in itertools.product(*new_act):
            duplicate = 0
            l = []
            for act in action:
                if act[0] == "pick up":
                    if act[2] in l:
                        duplicate = 1
                        break
                    l.append(act[2])
            if duplicate == 1:
                continue
            actions_list.append(action)
        actions = tuple(actions_list)
        #print("Actions", actions)
        if self.t % 2 == 0:
            self.prededent_position = state['drones']
        self.t += 1
        act_final = random.choice(actions)
        #print("Choosen Action=", act_final)
        #print("Precedent position=", self.prededent_position)
        return act_final

        # Timeout: 5 seconds

    def distance(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def specialmin(self, ls):
        min = ls[0][1]
        argmin = ls[0][0]
        for l in ls:
            if l[1] < min:
                min = l[1]
                argmin = l[0]

        return argmin, min

    def allPosibilityOneDrone(self, key, pos, package_not_delivered, clients):  # enlever les map

        moves = []
        pick_up = []
        delivery = []
        name_drone = key
        self.deliverPerDrone[name_drone] = 0
        self.pickupPerDrone[name_drone] = 0
        position_drone = pos
        i = position_drone[0]
        j = position_drone[1]
        bagage_drone = []
        pack_available = []
        for pack in package_not_delivered.keys():
            if package_not_delivered[pack] == name_drone:
                bagage_drone.append(pack)
            if type(package_not_delivered[pack]) == tuple:
                pack_available.append(pack)

        legal_moves = []

        """check all legal moves for a given drone and add all of them (max 4) to list moves"""

        if self.check_legal_position(i - 1, j):
            legal_moves.append((i - 1, j))
        if self.check_legal_position(i + 1, j):
            legal_moves.append((i + 1, j))
        if self.check_legal_position(i, j - 1):
            legal_moves.append((i, j - 1))
        if self.check_legal_position(i, j + 1):
            legal_moves.append((i, j + 1))
        if self.check_legal_position(i + 1, j + 1):
            legal_moves.append((i + 1, j + 1))
        if self.check_legal_position(i - 1, j + 1):
            legal_moves.append((i - 1, j + 1))
        if self.check_legal_position(i + 1, j - 1):
            legal_moves.append((i + 1, j - 1))
        if self.check_legal_position(i - 1, j - 1):
            legal_moves.append((i - 1, j - 1))
        for legal_move in legal_moves:
            moves.append(("move", name_drone, legal_move))

        """first check if the drone baggage is full (=2), if <2 continue to check pickup options"""
        if len(bagage_drone) < 2:
            """if the list of package available to pick up on the floor is not empty, continue"""
            if pack_available:
                for pack in pack_available:
                    """check if the given pack position is on the same tile than the drone position"""
                    if package_not_delivered[pack] == position_drone:
                        """check if we already added this option to the pick up list, if not add option"""
                        if ("pick up", name_drone, pack) not in pick_up:
                            pick_up.append(("pick up", name_drone, pack))
                            self.pickupPerDrone[name_drone] = 1

        """vérifier si le drone a un pack dans son baggage, compare pos_client & pos_drone, si egales, on verifie si le client
        doit recevoir ce baggage b et on ajoute possibilité de deliver """
        if bagage_drone:
            for client in clients.keys():
                position_client = clients[client]["location"]
                if position_drone == position_client:
                    for b in bagage_drone:
                        if b in clients[client]["packages"]:
                            delivery.append(("deliver", name_drone, client, b))
                            self.deliverPerDrone[name_drone] = 1

        moves.extend(pick_up)
        moves.extend(delivery)
        # moves.append(("wait", name_drone))
        # print("move=", moves)
        return moves

    def check_legal_position(self, i, j):  # enlever le map des inputs et changer le map par self.map dans la fct
        if i < 0 or i > self.n - 1:
            return False
        if j < 0 or j > self.m - 1:
            return False
        if self.map[i][j] == "I":
            return False
        return True
