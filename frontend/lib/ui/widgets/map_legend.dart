import "package:flutter/material.dart";

class MapLegend extends StatelessWidget {
  const MapLegend({super.key});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "Leyenda",
              style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF616161)),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: const [
                _LegendItem(color: Color(0xFF2E7D32), label: "Leve"),
                _LegendItem(color: Color(0xFFFBC02D), label: "Moderado"),
                _LegendItem(color: Color(0xFFC62828), label: "Alto"),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Container(
                  width: 48,
                  height: 10,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(4),
                    gradient: LinearGradient(
                      colors: [
                        const Color(0xFFFBC02D).withValues(alpha: 0.5),
                        const Color(0xFFC62828).withValues(alpha: 0.85),
                      ],
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    "Calor: amarillo → rojo según intensidad",
                    style: TextStyle(fontSize: 11, color: Color(0xFF616161)),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 6),
            const Row(
              children: [
                _BadgeSample(count: "3"),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    "Número = reportes en la zona",
                    style: TextStyle(fontSize: 11, color: Color(0xFF616161)),
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

class _BadgeSample extends StatelessWidget {
  final String count;

  const _BadgeSample({required this.count});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 28,
      height: 28,
      alignment: Alignment.center,
      decoration: BoxDecoration(
        color: const Color(0xFFC62828),
        shape: BoxShape.circle,
        border: Border.all(color: Colors.white, width: 2),
      ),
      child: Text(
        count,
        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 11),
      ),
    );
  }
}

class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendItem({required this.color, required this.label});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 14,
          height: 14,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 6),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }
}
