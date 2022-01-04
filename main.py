"""
Model exported as python.
Name : piracy hexbin
Group : projects
With QGIS : 31611
"""

from qgis.core import QgsProcessing
from qgis.core import QgsProcessingAlgorithm
from qgis.core import QgsProcessingMultiStepFeedback
from qgis.core import QgsProcessingParameterVectorLayer
from qgis.core import QgsProcessingParameterNumber
from qgis.core import QgsProcessingParameterFeatureSink
from qgis.core import QgsProcessingParameterBoolean
import processing


class PiracyHexbin(QgsProcessingAlgorithm):

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterVectorLayer('BaseLayer', 'Base Layer', types=[QgsProcessing.TypeVectorPolygon], defaultValue=None))
        self.addParameter(QgsProcessingParameterNumber('GridSize', 'Grid Size', type=QgsProcessingParameterNumber.Integer, defaultValue=0))
        self.addParameter(QgsProcessingParameterVectorLayer('InputPoints', 'Input Points', types=[QgsProcessing.TypeVectorPoint], defaultValue=None))
        self.addParameter(QgsProcessingParameterFeatureSink('Aggregated', 'Aggregated', type=QgsProcessing.TypeVectorPolygon, createByDefault=True, supportsAppend=True, defaultValue=None))
        self.addParameter(QgsProcessingParameterBoolean('VERBOSE_LOG', 'Verbose logging', optional=True, defaultValue=False))

    def processAlgorithm(self, parameters, context, model_feedback):
        # Use a multi-step feedback, so that individual child algorithm progress reports are adjusted for the
        # overall progress through the model
        feedback = QgsProcessingMultiStepFeedback(4, model_feedback)
        results = {}
        outputs = {}

        # Reproject layer
        alg_params = {
            'INPUT': parameters['BaseLayer'],
            'OPERATION': '',
            'TARGET_CRS': 'ProjectCrs',
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ReprojectLayer'] = processing.run('native:reprojectlayer', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(1)
        if feedback.isCanceled():
            return {}

        # Create grid
        alg_params = {
            'CRS': 'ProjectCrs',
            'EXTENT': outputs['ReprojectLayer']['OUTPUT'],
            'HOVERLAY': 0,
            'HSPACING': parameters['GridSize'],
            'TYPE': 4,
            'VOVERLAY': 0,
            'VSPACING': parameters['GridSize'],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['CreateGrid'] = processing.run('native:creategrid', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(2)
        if feedback.isCanceled():
            return {}

        # Extract by location
        alg_params = {
            'INPUT': outputs['CreateGrid']['OUTPUT'],
            'INTERSECT': parameters['InputPoints'],
            'PREDICATE': [0],
            'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT
        }
        outputs['ExtractByLocation'] = processing.run('native:extractbylocation', alg_params, context=context, feedback=feedback, is_child_algorithm=True)

        feedback.setCurrentStep(3)
        if feedback.isCanceled():
            return {}

        # Count points in polygon
        alg_params = {
            'CLASSFIELD': '',
            'FIELD': 'NUMPOINTS',
            'POINTS': parameters['InputPoints'],
            'POLYGONS': outputs['ExtractByLocation']['OUTPUT'],
            'WEIGHT': '',
            'OUTPUT': parameters['Aggregated']
        }
        outputs['CountPointsInPolygon'] = processing.run('native:countpointsinpolygon', alg_params, context=context, feedback=feedback, is_child_algorithm=True)
        results['Aggregated'] = outputs['CountPointsInPolygon']['OUTPUT']
        return results

    def name(self):
        return 'piracy hexbin'

    def displayName(self):
        return 'piracy hexbin'

    def group(self):
        return 'projects'

    def groupId(self):
        return 'projects'

    def createInstance(self):
        return PiracyHexbin()
