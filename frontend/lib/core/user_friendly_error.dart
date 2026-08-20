/// Mensajes de error seguros para mostrar al usuario (sin detalles internos del servidor).
class UserFriendlyError {
  UserFriendlyError._();

  static String from(Object error) {
    final text = error.toString();
    if (text.contains("401") || text.contains("403")) {
      return "Sesión expirada o sin permisos. Vuelve a iniciar sesión.";
    }
    if (text.contains("429")) {
      return "Demasiados intentos. Espera un momento e inténtalo de nuevo.";
    }
    if (text.contains("SocketException") || text.contains("Failed host lookup")) {
      return "No se pudo conectar al servidor. Comprueba tu conexión.";
    }
    if (text.contains("TimeoutException")) {
      return "El servidor tardó demasiado en responder.";
    }
    return "No se pudo completar la operación. Inténtalo de nuevo.";
  }
}
