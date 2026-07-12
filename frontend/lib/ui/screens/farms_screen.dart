import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../data/repositories/farm_repository.dart";
import "../../models/farm.dart";
import "../widgets/primary_button.dart";

class FarmsScreen extends StatefulWidget {
  const FarmsScreen({super.key});

  @override
  State<FarmsScreen> createState() => _FarmsScreenState();
}

class _FarmsScreenState extends State<FarmsScreen> {
  final _repository = FarmRepository();
  late Future<List<Farm>> _future;

  final _nameController = TextEditingController();
  final _cropController = TextEditingController();
  String _farmType = "farm";

  @override
  void initState() {
    super.initState();
    _future = _repository.fetchFarms();
  }

  @override
  void dispose() {
    _nameController.dispose();
    _cropController.dispose();
    super.dispose();
  }

  void _reload() {
    final newFuture = _repository.fetchFarms();
    setState(() {
      _future = newFuture;
    });
  }

  Future<void> _createFarm() async {
    if (_nameController.text.trim().isEmpty || _cropController.text.trim().isEmpty) return;
    await _repository.createFarm(
      name: _nameController.text.trim(),
      crop: _cropController.text.trim(),
      farmType: _farmType,
    );
    _nameController.clear();
    _cropController.clear();
    _reload();
  }

  Future<void> _deleteFarm(Farm farm) async {
    await _repository.deleteFarm(farm.id);
    _reload();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("Mis fincas")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              "Registra fincas o invernaderos para diagnósticos privados.",
              style: TextStyle(color: NexoColors.textPrimary),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _nameController,
              decoration: const InputDecoration(labelText: "Nombre", border: OutlineInputBorder()),
            ),
            const SizedBox(height: 8),
            TextField(
              controller: _cropController,
              decoration: const InputDecoration(labelText: "Cultivo", border: OutlineInputBorder()),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              initialValue: _farmType,
              decoration: const InputDecoration(labelText: "Tipo", border: OutlineInputBorder()),
              items: const [
                DropdownMenuItem(value: "farm", child: Text("Finca")),
                DropdownMenuItem(value: "greenhouse", child: Text("Invernadero")),
              ],
              onChanged: (v) => setState(() => _farmType = v ?? "farm"),
            ),
            const SizedBox(height: 12),
            PrimaryButton(label: "Añadir", onPressed: _createFarm),
            const SizedBox(height: 20),
            Expanded(
              child: FutureBuilder<List<Farm>>(
                future: _future,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  }
                  if (snapshot.hasError) {
                    return Center(child: Text("Error: ${snapshot.error}"));
                  }
                  final farms = snapshot.data ?? [];
                  if (farms.isEmpty) {
                    return const Center(child: Text("No tienes fincas registradas."));
                  }
                  return ListView.separated(
                    itemCount: farms.length,
                    separatorBuilder: (_, __) => const SizedBox(height: 8),
                    itemBuilder: (context, index) {
                      final farm = farms[index];
                      return Card(
                        child: ListTile(
                          title: Text(farm.name),
                          subtitle: Text("${farm.typeLabel} · ${farm.crop}"),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete_outline),
                            onPressed: () => _deleteFarm(farm),
                          ),
                        ),
                      );
                    },
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
