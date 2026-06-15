import "dart:typed_data";

import "package:tflite_flutter/tflite_flutter.dart";

import "image_preprocessor.dart";
import "label_loader.dart";
import "plaga_classifier_stub.dart" as stub_impl;
import "plaga_result.dart";
import "severity_helper.dart";

const _modelAsset = "assets/ml/plaga_model.tflite";
const _modelVersion = "v1.0-tflite";

Interpreter? _interpreter;

Future<Interpreter?> _loadInterpreter() async {
  if (_interpreter != null) return _interpreter;
  try {
    _interpreter = await Interpreter.fromAsset(_modelAsset);
    return _interpreter;
  } catch (_) {
    return null;
  }
}

Future<PlagaResult> classifyWithTflite(Uint8List imageBytes) async {
  final interpreter = await _loadInterpreter();
  if (interpreter == null) {
    final fallback = await stub_impl.classifyPlaga(imageBytes);
    return PlagaResult(
      plague: fallback.plague,
      confidence: fallback.confidence,
      suggestedSeverity: fallback.suggestedSeverity,
      modelVersion: "${fallback.modelVersion} (sin .tflite)",
    );
  }

  final labels = await LabelLoader.load();
  if (labels.isEmpty) {
    throw StateError("labels.txt vacío");
  }

  final input = preprocessImage(imageBytes);
  final output = List.generate(1, (_) => List.filled(labels.length, 0.0));

  interpreter.run(input, output);

  final scores = output.first;
  var bestIndex = 0;
  var bestScore = scores.first;
  for (var i = 1; i < scores.length; i++) {
    if (scores[i] > bestScore) {
      bestScore = scores[i];
      bestIndex = i;
    }
  }

  final plague = labels[bestIndex].toLowerCase();
  final confidence = bestScore.clamp(0.0, 1.0);

  return PlagaResult(
    plague: plague,
    confidence: confidence,
    suggestedSeverity: severityFromConfidence(plague, confidence),
    modelVersion: _modelVersion,
  );
}
