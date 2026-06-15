import "dart:typed_data";

import "package:image/image.dart" as img;

const int modelInputSize = 224;

/// Preprocesa JPEG/PNG a tensor [1, 224, 224, 3] normalizado 0–1.
List<List<List<List<double>>>> preprocessImage(Uint8List imageBytes) {
  final decoded = img.decodeImage(imageBytes);
  if (decoded == null) {
    throw const FormatException("No se pudo decodificar la imagen");
  }

  final resized = img.copyResize(decoded, width: modelInputSize, height: modelInputSize);
  return [
    List.generate(modelInputSize, (y) {
      return List.generate(modelInputSize, (x) {
        final pixel = resized.getPixel(x, y);
        return [
          pixel.r / 255.0,
          pixel.g / 255.0,
          pixel.b / 255.0,
        ];
      });
    }),
  ];
}
