from types import MethodType
import quantities
import os
import matplotlib.pyplot as plt

import sciunit
import sciunit.scores as scores
import neuronunit.capabilities as cap

class LayerHeightTest(sciunit.Test):
    """Tests the height of model layers"""
    score_type = scores.CombineZScores

    def __init__(self,
                 observation={},
                 name="Layer Height Test"):
        observation = self.format_data(observation)

        required_capabilities = (cap.ProvidesLayerInfo,)
        description = ("Tests the heights of all layers in model")
        units = quantities.um

        self.figures = []
        sciunit.Test.__init__(self, observation, name)

        self.directory_output = './output/'

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

    def generate_prediction(self, model, verbose=False):
        """Implementation of sciunit.Test.generate_prediction."""
        self.model_name = model.name
        prediction = model.get_layer_info()
        prediction = self.format_data(prediction)
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction, verbose=False):
        """Implementation of sciunit.Test.score_prediction."""
        try:
            assert len(observation) == len(prediction)
        except Exception as e:
            # or return InsufficientDataScore ??
            raise sciunit.InvalidScoreError(("Difference in # of layers."
                                    " Cannot continue test for layer heights."))

        zscores = {}
        for key0 in observation.keys():
            zscores[key0] = sciunit.scores.ZScore.compute(observation[key0]["height"], prediction[key0]["height"]).score
        score = sciunit.scores.CombineZScores.compute(zscores.values())

        # create output directory
        path_test_output = self.directory_output + 'layer_height/' + self.model_name + '/'
        if not os.path.exists(path_test_output):
            os.makedirs(path_test_output)

        # save figure with mean, std, value for observation and prediction
        fig = plt.figure()
        x = range(len(zscores))
        ix = 0
        for key0 in observation.keys():
            y_mean = observation[key0]["height"]["mean"]
            y_std = observation[key0]["height"]["std"]
            y_value = prediction[key0]["height"]["value"]
            ax_o = plt.errorbar(ix, y_mean, yerr=y_std, ecolor='black', elinewidth=2,
                            capsize=5, capthick=2, fmt='ob', markersize='5', mew=5)
            ax_p = plt.plot(ix, y_value, 'rx', markersize='8', mew=2)
            ix = ix + 1
        xlabels = observation.keys()
        plt.xticks(x, xlabels, rotation=20)
        plt.tick_params(labelsize=11)
        plt.figlegend((ax_o,ax_p[0]), ('Observation', 'Prediction',), 'upper right')
        plt.margins(0.1)
        plt.ylabel("Layer Height (um)")
        fig = plt.gcf()
        fig.set_size_inches(8, 6)
        filename = path_test_output + 'data_plot' + '.pdf'
        plt.savefig(filename, dpi=600,)
        self.figures.append(filename)

        # save document with Z-score data
        filename = path_test_output + 'score_summary' + '.txt'
        dataFile = open(filename, 'w')
        dataFile.write("==============================================================================\n")
        dataFile.write("Test Name: %s\n" % self.name)
        dataFile.write("Model Name: %s\n" % self.model_name)
        dataFile.write("------------------------------------------------------------------------------\n")
        dataFile.write("Layer #\tExpt. mean\tExpt. std\tModel value\tZ-score\n")
        dataFile.write("..............................................................................\n")
        for key0 in zscores.keys():
            o_mean = observation[key0]["height"]["mean"]
            o_std = observation[key0]["height"]["std"]
            p_value = prediction[key0]["height"]["value"]
            dataFile.write("%s\t%s\t%s\t%s\t%s\n" % (key0, o_mean, o_std, p_value, zscores[key0]))
        dataFile.write("------------------------------------------------------------------------------\n")
        dataFile.write("Combined Score: %s\n" % score)
        dataFile.write("==============================================================================\n")
        dataFile.close()
        self.figures.append(filename)

        return score

    #----------------------------------------------------------------------

    def bind_score(self, score, model, observation, prediction):
        score.related_data["figures"] = self.figures
        return score
