import "dart:typed_data";

import "plaga_classifier_stub.dart"
    if (dart.library.io) "plaga_classifier_mobile.dart" as classifier_impl;

import "plaga_result.dart";

export "plaga_result.dart";

Future<PlagaResult> classifyPlaga(Uint8List imageBytes) =>
    classifier_impl.classifyPlaga(imageBytes);
