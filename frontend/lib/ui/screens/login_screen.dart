import "package:flutter/material.dart";

import "../../core/api_config.dart";
import "../../core/nexo_colors.dart";
import "../../core/routes.dart";
import "../../data/repositories/auth_repository.dart";
import "../widgets/app_logo.dart";
import "../widgets/nexo_wordmark.dart";
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
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [NexoColors.deepBlue, NexoColors.surfaceBase],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const SizedBox(height: 24),
                const Center(child: AppLogo(size: 88, borderRadius: 18)),
                const SizedBox(height: 20),
                const Center(child: NexoWordmark(fontSize: 28, onDark: true)),
                const SizedBox(height: 8),
                const Text(
                  "Bienvenido al ecosistema agrícola unificado",
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 14, color: NexoColors.textSecondary),
                ),
                const SizedBox(height: 28),
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: NexoColors.surfaceCard,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: NexoColors.borderSubtle),
                    boxShadow: [
                      BoxShadow(
                        color: NexoColors.techCyan.withValues(alpha: 0.06),
                        blurRadius: 32,
                        offset: const Offset(0, 12),
                      ),
                    ],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
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
                        style: const TextStyle(fontSize: 12, color: NexoColors.textSecondary),
                      ),
                      const SizedBox(height: 16),
                      OutlinedButton(
                        onPressed: () => Navigator.pushNamed(context, Routes.settings),
                        child: const Text("Configurar servidor API"),
                      ),
                      const SizedBox(height: 20),
                      if (_errorMessage != null)
                        Padding(
                          padding: const EdgeInsets.only(bottom: 12),
                          child: Text(_errorMessage!, style: const TextStyle(color: NexoColors.errorRed)),
                        ),
                      PrimaryButton(
                        label: _isLoading ? "Ingresando..." : "Ingresar",
                        onPressed: _isLoading ? null : _login,
                      ),
                      const SizedBox(height: 16),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Text("¿No tienes cuenta? ", style: TextStyle(color: NexoColors.textSecondary)),
                          GestureDetector(
                            onTap: () => Navigator.pushNamed(context, Routes.register),
                            child: const Text(
                              "Regístrate",
                              style: TextStyle(
                                color: NexoColors.techCyan,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
