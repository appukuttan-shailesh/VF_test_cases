from types import MethodType
import quantities

import sciunit
import sciunit.scores as scores

import neuronunit.capabilities as cap

'''
class LayerTest(sciunit.Test):
    """Base class for tests involving models with layers in neural circuit"""

class NumLayerTest(LayerTest):
'''

class LayerHeightTest(sciunit.Test):
    """Tests the height of model layers"""
    def __init__(self,
                 observation={},
                 name="Layer Height Test"):
        observation = self.format_data(observation)

        required_capabilities = (cap.ProvidesLayerInfo,)
        description = ("Tests the heights of all layers in model")
        units = quantities.um
        score_type = scores.StoufferScore

        sciunit.Test.__init__(self, observation, name)

    #----------------------------------------------------------------------

    def format_data(self, data):
        """
        This accepts data input in the form:
        ***** (observation) *****
        {'Layer 1': {'height': {'mean': 'X0 um', 'std': 'Y0 um'}},
         'Layer 2/3': {'height': {'mean': 'X1 um', 'std': 'Y1 um'}},
         ...                                                       }
        ***** (prediction) *****
        { 'Layer 1': {'height': {'value': 'X0 um'}},
          'Layer 2/3': {'height': {'value': 'X1 um'}},
          ...                                        }
        and splits the values of mean and std to numeric quantities
        and their units (via quantities package).
        """
        for key0 in data.keys():
            for key, val in data[key0]["height"].items():
                try:
                    data[key0]["height"][key] = int(val)
                except ValueError:
                    try:
                        data[key0]["height"][key] = float(val)
                    except ValueError:
                        quantity_parts = val.split(" ")
                        number = float(quantity_parts[0])
                        units = " ".join(quantity_parts[1:])
                        data[key0]["height"][key] = quantities.Quantity(number, units)

        return data

    #----------------------------------------------------------------------

    def convert_to_list(self, observation, prediction):
        """
        This accepts the data format output by format_data() and converts it
        into the format required by StoufferScore for scoring. The output
        is of the form:

        observation = [{'mean':'X0', 'std':'Y0'},
                       {'mean':'X1', 'std':'Y1'},
                       ...                      ]
        prediction = [{'value':'Z0'}, {'value':'Z1'}, ...]

        where Xi, Yi, Zi correspond to values for specific entities
        to be compared (e.g. height for Layer i of cortical column)
        """
        list_observation = []
        list_prediction = []

        for key0 in observation.keys():
            temp_dict = {}
            for key, val in observation[key0]["height"].items():
                temp_dict[key] = val
            list_observation.append(temp_dict)
            list_prediction.append(prediction[key0]["height"])

        return list_observation, list_prediction

    #----------------------------------------------------------------------

    def validate_observation(self, observation):
        try:
            for key0 in observation.keys():
                for key, val in observation[key0]["height"].items():
                    assert type(observation[key0]["height"][key]) is quantities.Quantity
        except Exception as e:
            raise sciunit.ObservationError(
                ("Observation must return a dictionary of the form:"
                "{'Layer 1': {'height': {'mean': 'X0 um', 'std': 'Y0 um'}},"
                " 'Layer 2/3': {'height': {'mean': 'X1 um', 'std': 'Y1 um'}},"
                " ...                                                       }))"))

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=True):
        """Implementation of sciunit.Test.generate_prediction."""
        prediction = model.get_layer_info()
        prediction = self.format_data(self, prediction)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction):
        """Implementation of sciunit.Test.score_prediction."""
        try:
            assert len(observation) == len(prediction)
        except Exception as e:
            # or return InsufficientDataScore ??
            raise sciunit.InvalidScoreError(("Difference in # of layers."
                                    " Cannot continue test for layer heights."))

        observation, prediction = self.convert_to_list(self, observation, prediction)
        score = sciunit.scores.StoufferScore.compute(self, observation, prediction)
        return score

    #----------------------------------------------------------------------

    def bind_score(self, score, model, observation, prediction):
        score.related_data['model_name'] = '%s_%s' % (model.name, self.name)
