
# Generated manually for CU10 (AlertaPriorizacion) and CU13 (Teleconsulta)

import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_cita'),
    ]

    operations = [
        # ─── CU10: Alertas de priorización ───────────────────────────────
        migrations.CreateModel(
            name='AlertaPriorizacion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('tipo', models.CharField(
                    choices=[
                        ('inasistencia',   'Inasistencia consecutiva'),
                        ('riesgo_abandono','Riesgo de abandono'),
                        ('senal_riesgo',   'Señal de riesgo clínico'),
                        ('estancamiento',  'Estancamiento terapéutico'),
                    ],
                    max_length=30,
                )),
                ('descripcion', models.TextField()),
                ('estado', models.CharField(
                    choices=[
                        ('pendiente',   'Pendiente'),
                        ('en_revision', 'En revisión'),
                        ('resuelta',    'Resuelta'),
                    ],
                    default='pendiente',
                    max_length=20,
                )),
                ('accion_tomada', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('paciente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='alertas',
                    to='users.paciente',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),

        # ─── CU13: Teleconsultas / Videoconferencias ──────────────────────
        migrations.CreateModel(
            name='Teleconsulta',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('room_name', models.CharField(max_length=255, unique=True)),
                ('enlace_psicologo', models.URLField(max_length=500)),
                ('enlace_paciente',  models.URLField(max_length=500)),
                ('estado', models.CharField(
                    choices=[
                        ('programada', 'Programada'),
                        ('en_curso',   'En curso'),
                        ('finalizada', 'Finalizada'),
                        ('cancelada',  'Cancelada'),
                    ],
                    default='programada',
                    max_length=20,
                )),
                ('iniciada_at',   models.DateTimeField(blank=True, null=True)),
                ('finalizada_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('cita', models.OneToOneField(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='teleconsulta',
                    to='users.cita',
                )),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
