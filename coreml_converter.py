# import necessary packages
from keras.models import load_model
import coremltools
import argparse
import pickle

# construct argument parser and parse arguments
ap = argparse.ArgumentParser()
ap.add_argument('-m', '--model', required=True,
        help='path to trained model')
ap.add_argument('-l', '--labelbin', required=True,
        help='path to label binarizer')
args = vars(ap.parse_args())

# load class labels
print('[INFO] loading class labels from label binarizer')
lb = pickle.loads(open(args['labelbin'], 'rb').read())
class_labels = lb.classes_.tolist()
print('[INFO] class labels: {}'.format(class_labels))

# load trained convolutional neural network
print('[INFO] loading model....')
model = load_model(args['model'])

print('[INFO] converting model....')
coreml_model = coremltools.converters.keras.convert(model,
    input_names='image',
    image_input_names='image',
    image_scale=1/255.0,
    class_labels=class_labels,
    is_bgr=True)

# save model to disk
output = args['model'].rsplit('.', 1)[0] + '.mlmodel'
print('[INFO] saving model as {}'.format(output))
coreml_model.save(output)