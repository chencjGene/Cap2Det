
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import numpy as np
import tensorflow as tf
from google.protobuf import text_format

from protos import pipeline_pb2
from models import builder
import cv2
from core import plotlib
from core import imgproc
from core.standard_fields import InputDataFields
from core.standard_fields import GAPPredictions
from core.standard_fields import GAPPredictionTasks

flags = tf.app.flags

flags.DEFINE_string('pipeline_proto', 
    '', 'Path to the pipeline proto file.')

flags.DEFINE_string('image_path', 
    'testdata', 
    'Path to the directory storing image files.')

flags.DEFINE_string('demo_path', 
    'tmp', 
    'Path to the directory storing demo results.')

FLAGS = flags.FLAGS

_SMALL_NUMBER = 1e-8

tf.logging.set_verbosity(tf.logging.INFO)


def _load_pipeline_proto(filename):
  """Loads pipeline proto from file.

  Args:
    filename: path to the pipeline config file.

  Returns:
    an instance of pipeline_pb2.Pipeline.
  """
  pipeline_proto = pipeline_pb2.Pipeline()
  with tf.gfile.GFile(filename, 'r') as fp:
    text_format.Merge(fp.read(), pipeline_proto)
  return pipeline_proto


def _get_score_map(input_path, output_path, names, score_map_func):
  """Gets the score map and save it to visualization file.

  Args:
    input_path: path to the input jpeg file.
    output_path: path to the output jpeg file.
    names: name of each score map.
    score_map_func: a callable that takes [height, width, 3] RGB numpy image as
      input and outputs the [height, width] float array denoting saliency map 
      and a [height, width, num_classes] float array denoting score maps.
  """
  image_data = cv2.imread(input_path)[:, :, ::-1]  # To RGB.
  score_map_list = score_map_func(image_data)

  outputs = []
  outputs.append(image_data)
  for i, score_map in enumerate(score_map_list):
    outputs.append(
        (255.0 * plotlib._py_convert_to_heatmap(score_map, normalize=(i==0))
         ).astype(np.uint8))

  output = np.concatenate(outputs, axis=1)
  cv2.imwrite(output_path, output[:, :, ::-1])  # To BGR.


def main(_):
  pipeline_proto = _load_pipeline_proto(FLAGS.pipeline_proto)
  tf.logging.info("Pipeline configure: %s", '=' * 128)
  tf.logging.info(pipeline_proto)

  categories = ['bear', 'beach', 'car', 'motorcycle', 'light', 'donut', 'plate']

  g = tf.Graph()
  with g.as_default():

    image = tf.placeholder(tf.uint8, shape=[None, None, 3])
    image_resized = tf.image.resize_images(
        image, [pipeline_proto.eval_reader.image_height,
        pipeline_proto.eval_reader.image_width])

    model = builder.build(pipeline_proto.model, is_training=False)
    prediction_dict = model.build_prediction(
        examples={ 
          InputDataFields.image: tf.expand_dims(image_resized, 0),
          InputDataFields.category_strings: tf.constant(categories) },
        prediction_task=GAPPredictionTasks.image_score_map)

    height, width = tf.shape(image)[0], tf.shape(image)[1]
    (saliency_map, score_maps) = (
        prediction_dict[GAPPredictions.image_saliency],
        prediction_dict[GAPPredictions.image_score_map])

    def resize_fn(feature_map):
      feature_map = tf.image.resize_images(
          tf.expand_dims(feature_map, axis=-1), [height, width])
      return tf.squeeze(
          imgproc.gaussian_filter(feature_map, ksize=32), axis=-1)[0]

    score_map_list = [resize_fn(saliency_map)] + [resize_fn(x) for x in tf.unstack(score_maps, axis=-1)]

    saver = tf.train.Saver()
    invalid_variable_names = tf.report_uninitialized_variables()

  with tf.Session(graph=g) as sess:

    sess.run(tf.tables_initializer())

    # Load the latest checkpoint.

    checkpoint_path = tf.train.latest_checkpoint(pipeline_proto.model_dir)
    assert checkpoint_path is not None

    saver.restore(sess, checkpoint_path)
    assert len(sess.run(invalid_variable_names)) == 0

    # Iterate the testdir to generate the demo results.

    score_map_func = lambda x: sess.run(
        score_map_list, feed_dict={ image: x })

    for filename in os.listdir(FLAGS.image_path):
      tf.logging.info('On processing %s', filename)

      _get_score_map(
          input_path=os.path.join(FLAGS.image_path, filename),
          output_path=os.path.join(FLAGS.demo_path, filename),
          names=['saliency'] + categories,
          score_map_func=score_map_func)

  tf.logging.info('Done')

if __name__ == '__main__':
  tf.app.run()
