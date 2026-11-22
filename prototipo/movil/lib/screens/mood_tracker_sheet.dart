// ==============================================================================
// MÓDULO: mood_tracker_sheet.dart
// CAPA BCE: BOUNDARY — selectorEmocional de IU_SeguimientoTerapeuticoMovil
// CASO DE USO: CU17 Móvil – Mood Tracker Diario (HU-46)
// Usado tras la teleconsulta (HU-44 c) y dentro de la entrega de tareas (HU-45).
// ponytail: duplica el diálogo privado de dashboard_screen.dart; unificar cuando
//           ese archivo deje de editarse en paralelo.
// ==============================================================================
import 'package:flutter/material.dart';
import '../core/theme/app_theme.dart';
import '../services/auth_service.dart';
import '../services/clinica_service.dart';

/// Escala 1-5 con los mismos códigos que envía el Mood Tracker del dashboard.
const List<Map<String, Object>> kMoodOpciones = [
  {'val': 1, 'code': 'MUY_BAJO', 'emoji': '😢', 'label': 'Muy mal'},
  {'val': 2, 'code': 'BAJO', 'emoji': '😔', 'label': 'Desanimado'},
  {'val': 3, 'code': 'NEUTRAL', 'emoji': '😐', 'label': 'Regular'},
  {'val': 4, 'code': 'BUENO', 'emoji': '🙂', 'label': 'Bien'},
  {'val': 5, 'code': 'EXCELENTE', 'emoji': '😄', 'label': 'Excelente'},
];

const Color kMoodColor = Color(0xFFEC4899);

/// Fila de emojis seleccionables. [seleccionado] null = sin elegir.
class MoodSelector extends StatelessWidget {
  final int? seleccionado;
  final ValueChanged<int> onChanged;

  const MoodSelector({super.key, required this.seleccionado, required this.onChanged});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceAround,
      children: kMoodOpciones.map((m) {
        final val = m['val'] as int;
        final sel = seleccionado == val;
        return Semantics(
          button: true,
          selected: sel,
          label: m['label'] as String,
          child: GestureDetector(
            onTap: () => onChanged(val),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
              decoration: BoxDecoration(
                color: sel ? kMoodColor.withOpacity(0.2) : Colors.transparent,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: sel ? kMoodColor : Colors.transparent, width: 2),
              ),
              child: Column(children: [
                Text(m['emoji'] as String, style: const TextStyle(fontSize: 28)),
                const SizedBox(height: 2),
                Text(
                  m['label'] as String,
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: sel ? FontWeight.bold : FontWeight.normal,
                    color: sel ? kMoodColor : AppTheme.textMuted,
                  ),
                ),
              ]),
            ),
          ),
        );
      }).toList(),
    );
  }
}

/// HU-46: registro diario de estado de ánimo (POST /clinica/registro-animo/).
Future<void> mostrarMoodTrackerSheet(BuildContext context, AuthService authService) {
  int? valor;
  final notaController = TextEditingController();
  bool guardando = false;
  final messenger = ScaffoldMessenger.of(context);

  return showModalBottomSheet(
    context: context,
    isScrollControlled: true,
    backgroundColor: AppTheme.cardBg,
    shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(24))),
    builder: (ctx) => StatefulBuilder(
      builder: (ctx, setSheet) => Padding(
        padding: EdgeInsets.fromLTRB(20, 20, 20, MediaQuery.of(ctx).viewInsets.bottom + 20),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Row(children: [
                Icon(Icons.mood_rounded, color: kMoodColor, size: 26),
                SizedBox(width: 10),
                Text('¿Cómo te sientes hoy?',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: AppTheme.textMain)),
              ]),
              const SizedBox(height: 6),
              const Text(
                'Tu psicólogo/a verá este registro para acompañar tu evolución entre sesiones.',
                style: TextStyle(color: AppTheme.textMuted, fontSize: 12),
              ),
              const SizedBox(height: 18),
              MoodSelector(seleccionado: valor, onChanged: (v) => setSheet(() => valor = v)),
              const SizedBox(height: 18),
              TextField(
                controller: notaController,
                maxLines: 2,
                maxLength: 300,
                decoration: InputDecoration(
                  labelText: 'Comentario (opcional)',
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 12),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: kMoodColor,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                onPressed: valor == null || guardando
                    ? null
                    : () async {
                        setSheet(() => guardando = true);
                        final opcion = kMoodOpciones.firstWhere((m) => m['val'] == valor);
                        final res = await ClinicaService(authService: authService).registrarEstadoAnimo(
                          estadoAnimo: opcion['code'] as String,
                          escalaValor: valor!,
                          factoresContexto: const [],
                          notaReflexiva: notaController.text.trim(),
                        );
                        if (ctx.mounted) Navigator.pop(ctx);
                        messenger.showSnackBar(SnackBar(
                          content: Text(res['success'] == true
                              ? 'Estado de ánimo registrado. ¡Gracias!'
                              : (res['error'] ?? 'No se pudo guardar tu estado de ánimo.').toString()),
                          backgroundColor: res['success'] == true ? AppTheme.success : AppTheme.danger,
                          behavior: SnackBarBehavior.floating,
                        ));
                      },
                icon: guardando
                    ? const SizedBox(
                        width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.check_circle_rounded),
                label: Text(guardando ? 'Guardando...' : 'Guardar estado de ánimo'),
              ),
            ],
          ),
        ),
      ),
    ),
  );
}
