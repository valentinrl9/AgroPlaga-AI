import "dart:io" show Platform;
import "dart:typed_data";

import "plaga_classifier_stub.dart" as stub_impl;
import "plaga_result.dart";

import "tflite_runner.dart" if (dart.library.html) "tflite_runner_stub.dart" as tflite;

/// Inferencia TFLite en Android/iOS; resto de plataformas usa heurística.
Future<PlagaResult> classifyPlaga(Uint8List imageBytes) async {
  final isMobile = Platform.isAndroid || Platform.isIOS;
  if (!isMobile) {
    return stub_impl.classifyPlaga(imageBytes);
  }
  return tflite.classifyWithTflite(imageBytes);
}
