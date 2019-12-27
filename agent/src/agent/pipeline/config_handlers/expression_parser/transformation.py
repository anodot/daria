from collections import namedtuple


TransformationFunction = namedtuple('TransformationFunction', ['name', 'n_args'])
TRANSFORMATION_FUNCTIONS = [TransformationFunction('replace', 3),
                            TransformationFunction('replaceAll', 3),
                            TransformationFunction('substring', 3),
                            TransformationFunction('toLower', 1),
                            TransformationFunction('toUpper', 1),
                            TransformationFunction('trim', 1)]


