
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function


class OperationNames(object):
  """Names of operations."""

  # Reader.

  parse_single_example = "parse_single_example"
  decode_image = "decode_image"
  decode_caption = "decode_caption"

  # Prediction.

  image_model = "image_model"
  text_model = "text_model"
  image_l2_norm = "image_l2_norm"
  text_l2_norm = "text_l2_norm"

  calc_pairwise_similarity = "calc_pairwise_similarity"

  # Training.

  mine_in_batch_triplet = "mine_in_batch_triplet"

  # Validation.

  caption_retrieval = "caption_retrieval"


class TFExampleDataFields(object):
  """Names for the fields defined in the tf::Example."""
  image_id = "image/source_id"
  image_encoded = "image/encoded"
  caption_string = "image/caption/string"
  caption_offset = "image/caption/offset"
  caption_length = "image/caption/length"


class InputDataFields(object):
  """Names of the input tensors."""
  image = "image"
  image_id = "image_id"
  num_captions = "num_captions"
  caption_strings = "caption_strings"
  caption_lengths = "caption_lengths"


class GAPVariableScopes(object):
  """Variable scopes used in GAP model."""
  cnn = "CNN"
  image_proj = "image_proj"
  word_embedding = "coco_word_embedding"
  image_saliency = "image_saliency"
  word_saliency = "word_saliency"


class GAPPredictions(object):
  """Predictions in the GAP model."""
  image = "image"
  image_id = "image_id"
  image_feature = "image_feature"
  image_saliency_score = "image_saliency_score"

  image_ids_gathered = "image_ids_gathered"
  caption_features_gathered = "caption_features_gathered"
  caption_lengths_gathered = "caption_lengths_gathered"
  caption_saliency_scores_gathered = "caption_saliency_scores_gathered"

  similarity = "similarity"
