import "dart:typed_data";

import "plaga_classifier_stub.dart" as stub_impl;
import "plaga_result.dart";

Future<PlagaResult> classifyWithTflite(Uint8List imageBytes) =>
    stub_impl.classifyPlaga(imageBytes);
