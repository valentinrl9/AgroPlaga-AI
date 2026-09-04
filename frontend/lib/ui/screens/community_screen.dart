import "package:flutter/material.dart";

import "../../core/nexo_colors.dart";
import "../../data/repositories/activity_repository.dart";
import "../../data/repositories/community_repository.dart";
import "../../models/community.dart";
class CommunityScreen extends StatefulWidget {
  const CommunityScreen({super.key});

  @override
  State<CommunityScreen> createState() => _CommunityScreenState();
}

class _CommunityScreenState extends State<CommunityScreen> {
  final _repository = CommunityRepository();
  late Future<CommunityProfile> _future;

  @override
  void initState() {
    super.initState();
    _future = _repository.fetchProfile();
    ActivityRepository().markSectionRead("community").catchError((_) {});
  }

  void _reload() {
    final newFuture = _repository.fetchProfile();
    setState(() {
      _future = newFuture;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Comunidad"),
        actions: [IconButton(icon: const Icon(Icons.refresh), onPressed: _reload)],
      ),
      body: FutureBuilder<CommunityProfile>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text("Error: ${snapshot.error}"));
          }

          final data = snapshot.data!;
          final vigilance = data.weeklyVigilance;
          final pilot = data.pilotCollective;

          return ListView(
            padding: const EdgeInsets.all(16),
            children: [
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "Piloto Almería",
                        style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16),
                      ),
                      const SizedBox(height: 8),
                      LinearProgressIndicator(
                        value: pilot.progress,
                        backgroundColor: NexoColors.borderSubtle,
                        color: NexoColors.bioGreen,
                        minHeight: 8,
                        borderRadius: BorderRadius.circular(4),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        "${pilot.totalScans} / ${pilot.goal} escaneos · ${pilot.activeFarmers} agricultores activos (30 d)",
                        style: const TextStyle(fontSize: 13, color: NexoColors.textSecondary),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Card(
                child: ListTile(
                  leading: const CircleAvatar(child: Icon(Icons.volunteer_activism)),
                  title: Text("${data.contributionCount} contribuciones"),
                  subtitle: const Text("Tu impacto en el mapa colaborativo"),
                ),
              ),
              const SizedBox(height: 16),
              const Text("Vigilancia semanal", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(vigilance.description),
                      const SizedBox(height: 12),
                      LinearProgressIndicator(
                        value: vigilance.goal > 0
                            ? (vigilance.current / vigilance.goal).clamp(0.0, 1.0)
                            : 0,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        vigilance.completed
                            ? "${vigilance.current}/${vigilance.goal} escaneo esta semana · Completado"
                            : "${vigilance.current}/${vigilance.goal} escaneo esta semana",
                      ),
                      if (vigilance.streakWeeks > 0) ...[
                        const SizedBox(height: 6),
                        Text(
                          "Racha: ${vigilance.streakWeeks} semana(s) consecutivas",
                          style: const TextStyle(
                            fontSize: 13,
                            color: NexoColors.warningAmber,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
              const Text("Insignias", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              if (data.badges.isEmpty)
                const Text("Aún no tienes insignias. ¡Contribuye al mapa!")
              else
                Wrap(
                  spacing: 8,
                  runSpacing: 8,
                  children: data.badges
                      .map(
                        (b) => Chip(
                          avatar: const Icon(Icons.military_tech, size: 18),
                          label: Text(b.label),
                        ),
                      )
                      .toList(),
                ),
              const SizedBox(height: 16),
              const Text("Ranking por zona (7 días)", style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              ...data.zoneRanking.asMap().entries.map((entry) {
                final rank = entry.key + 1;
                final zone = entry.value;
                return Card(
                  child: ListTile(
                    leading: CircleAvatar(child: Text("$rank")),
                    title: Text(zone.zoneName),
                    subtitle: Text("${zone.validatedCount} validados"),
                    trailing: Text("${zone.contributions} rep."),
                  ),
                );
              }),
            ],
          );
        },
      ),
    );
  }
}
