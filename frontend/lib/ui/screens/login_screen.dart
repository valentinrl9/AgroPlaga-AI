import "package:flutter/material.dart";

import "../../core/api_config.dart";
import "../../core/routes.dart";
import "../../data/repositories/auth_repository.dart";
import "../widgets/app_logo.dart";
import "../widgets/primary_button.dart";

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _authRepository = AuthRepository();
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _login() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final success = await _authRepository.login(
        _emailController.text.trim(),
        _passwordController.text.trim(),
      );

      if (success) {
        if (!mounted) return;
        Navigator.pushReplacementNamed(context, Routes.home);
        return;
      }

      if (mounted) {
        setState(() {
          _errorMessage = "Credenciales inválidas, inténtalo de nuevo.";
        });
      }
    } catch (error) {
      if (mounted) {
        setState(() {
          final detail = error.toString();
          if (detail.contains("SocketException") ||
              detail.contains("Failed host lookup") ||
              detail.contains("Connection refused")) {
            _errorMessage =
                "No se puede conectar al servidor (${ApiConfig.baseUrl}). "
                "En móvil físico configura la IP de tu PC en Ajustes antes de entrar.";
          } else {
            _errorMessage = detail;
          }
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Login")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 16),
            const Center(child: AppLogo(size: 88, borderRadius: 18)),
            const SizedBox(height: 20),
            const Text("Bienvenido a NEXO Agro", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            const SizedBox(height: 24),
            TextField(
              controller: _emailController,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(labelText: "Email"),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              obscureText: true,
              decoration: const InputDecoration(labelText: "Contraseña"),
            ),
            const SizedBox(height: 8),
            Text(
              "Servidor: ${ApiConfig.baseUrl}",
              style: const TextStyle(fontSize: 12, color: Color(0xFF757575)),
            ),
            const SizedBox(height: 16),
            OutlinedButton(
              onPressed: () => Navigator.pushNamed(context, Routes.settings),
              child: const Text("Configurar servidor API"),
            ),
            const SizedBox(height: 24),
            if (_errorMessage != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
              ),
            PrimaryButton(
              label: _isLoading ? "Ingresando..." : "Ingresar",
              onPressed: _isLoading ? null : _login,
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text("¿No tienes cuenta? "),
                GestureDetector(
                  onTap: () => Navigator.pushNamed(context, Routes.register),
                    child: const Text(
                      "Regístrate",
                      style: TextStyle(
                        color: Color(0xFF00A86B),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
          ],
        ),
      ),
    );
  }
}
