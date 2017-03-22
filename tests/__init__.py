from types import MethodType
import quantities as pq

import sciunit
import sciunit.scores as scores

import neuronunit.capabilities as cap

class LayerTest(sciunit.Test):
    """Base class for tests involving models with layers in neural circuit"""

class NumLayerTest(TestLayer):


class LayerHeightTest(TestLayer):
    """Tests the height of model layers"""
    def __init__(self,
                 observation=[],
                 name="Layer Height Test"):
        sciunit.Test.__init__(self, observation, name)

        required_capabilities = (cap.ProvidesLayerInfo,)
        description = ("Tests the heights of all layers in model")
        units = pq.um
        score_type = scores.FloatScore

    #----------------------------------------------------------------------

    def validate_observation(self, observation):
        try:
            for i in len(observation):
                assert type(observation[i][0]) is StringType
                assert type(observation[i][1]) is Quantity
                assert type(observation[i][2]) is Quantity
        except Exception as e:
            raise sciunit.ObservationError(("Observation must return a list"
            "with each element being a sub-list of the form:"
            "[ ['layer_0_name', 'layer_0_height_mean', 'layer_0_height_std'],"
            "  ['layer_1_name', 'layer_1_height_mean', 'layer_1_height_std'],"
            "  ['layer_2_name', 'layer_2_height_mean', 'layer_2_height_std'],"
            "   ...              ...                    ...                 ]"))

    #----------------------------------------------------------------------

    def generate_prediction(self, model, verbose=True):
        """Implementation of sciunit.Test.generate_prediction."""
        prediction = model.get_layer_info()
        return prediction

    #----------------------------------------------------------------------

    def compute_score(self, observation, prediction):
		"""Implementation of sciunit.Test.score_prediction."""
        try:
            assert len(observation) == len(prediction)
        except Exception as e:
            # or return InsufficientDataScore ??
            raise sciunit.InvalidScoreError(("Difference in # of layers."
                                    "Cannot continue test for layer heights."))

        for i in len(observation):
		      z_score[i] = sciunit.comparators.zscore({'mean':observation[i][1], 'std':observation[i][2]}, {'value':prediction[i][1]})	# Computes a decimal Z score.

        # using Stouffer's Z-score method (two-tailed) to combine Z-scores. Refs:
        # 1) Whitlock, M. C. (2005). Combining probability from independent
        #       tests: the weighted Z‐method is superior to Fisher's approach.
        #       Journal of evolutionary biology, 18(5), 1368-1373.
        # 2) http://stats.stackexchange.com/questions/20126/testing-two-tailed-p-values-using-stouffers-approach
        score = sum(z_score) / (len(observation)**0.5)

		score = sciunit.scores.FloatScore(score) # Wraps it in a sciunit.Score type.
		return score

    #----------------------------------------------------------------------

    def bind_score(self, score, model, observation, prediction):        
        score.related_data['model_name'] = '%s_%s' % (model.name,self.name)
