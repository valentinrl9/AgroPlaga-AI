import "dart:typed_data";

import "package:image/image.dart" as img;

/// Comprueba resolución mínima antes de enviar al modelo.
class ImageQualityGate {
  ImageQualityGate._();

  static const minSidePx = 200;

  static String? validate(Uint8List bytes) {
    final decoded = img.decodeImage(bytes);
    if (decoded == null) {
      return "No se pudo leer la imagen. Prueba otra foto.";
    }
    if (decoded.width < minSidePx || decoded.height < minSidePx) {
      return "Foto demasiado pequeña. Acerca la cámara a la hoja o fruto afectado.";
    }
    return null;
  }
}
