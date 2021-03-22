from flask import Flask, request
import json


class UnitCommitmentProblem:
    """
    This class represents the unit commitment problem which consists of finding the merit-order
    and deciding, for each powerplant in the merit-order, how much power each powerplant should deliver.
    """

    def __init__(self, payload):
        """
        :param payload: The payload containing the load, fuels and powerplants
        """
        self.payload = payload
        self.load = payload["load"]
        self.powerplants = payload["powerplants"]
        self.fuels = payload['fuels']

    def compute_merit_order(self):
        """
        Computes the merit-order based on the cost of the fuels of each powerplant

        :return: The found merit-order
        """
        for pp in self.powerplants:
            self.compute_cost_per_mwh(pp)  # compute the cost of the powerplant
            if pp["type"] == "windturbine":
                # if it is a windturbine, update its minimum and maximum power based on wind %
                pp["pmin"] = pp['pmax'] * self.fuels['wind(%)'] / 100
                pp["pmax"] = pp["pmin"]

        # sort the powerplants based on their cost per MWh
        merit_order = sorted(self.powerplants, key=lambda k: k['ppm'])

        return merit_order

    def compute_cost_per_mwh(self, powerplant):
        """
        Computes the cost per MWh for each plant

        :param powerplant: The powerplant for which we compute the cost
        """
        if powerplant["type"] == "windturbine":  # windturbines are considered to generate power at zero price
            powerplant["ppm"] = 0
        elif powerplant["type"] == "turbojet":
            powerplant["ppm"] = self.fuels["kerosine(euro/MWh)"] / powerplant["efficiency"]
        elif powerplant["type"] == "gasfired":
            powerplant["ppm"] = self.fuels["gas(euro/MWh)"] / powerplant["efficiency"]

    def solve(self):
        """
        Solves the unit-commitment problem by founding the merit-order and assigning a power to each powerplant
        in the merit-order so that the sum of the power produced by all the powerplants together should equal the load.
        When assigning a power to a powerplant, we take into account the minimal power produced by the next powerplant.

        :return: The response as json specifying for each powerplant how much power each powerplant should deliver
        :rtype:
        """
        merit_order = self.compute_merit_order()  # computes the merit-order
        result = [{"name": pp["name"], "p": 0} for pp in merit_order]  # assign a power of 0 to each powerplant
        total_power = 0  # total power produced by all active powerplants

        for i, pp in enumerate(merit_order):
            if pp["pmin"] + total_power <= self.load:
                if pp["type"] == "windturbine":
                    # we do not care about next powerplant since windturbines have pmin=pmax, so we assign full power
                    result[i]["p"] = pp["pmax"]
                    total_power += result[i]["p"]
                else:
                    # we have reached the load, solution found, we can stop iterating
                    if pp["pmax"] + total_power >= self.load:
                        result[i]["p"] = self.load - total_power  # generate the power to exactly match the load
                        break
                    else:
                        if i < (len(merit_order) - 1):
                            # do not assign the maximum power so that the power of the next powerplant is not wasted
                            # assign the difference between max power of current powerplant and min power of next one
                            result[i]["p"] = pp["pmax"] - merit_order[i + 1]["pmin"]
                            total_power += result[i]["p"]

        return json.dumps(result, indent=2)


app = Flask(__name__)


@app.route('/productionplan', methods=['POST'])
def solve_unit_commitment_problem():
    payload = request.get_json()
    ucp = UnitCommitmentProblem(payload)
    result = ucp.solve()
    return result


if __name__ == '__main__':
    app.run(port=8888, debug=True)
