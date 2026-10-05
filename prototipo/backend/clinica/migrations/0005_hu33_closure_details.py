from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [('clinica', '0004_conversacionchatbot_mensajechatbot')]

    operations = [
        migrations.AlterField(
            model_name='derivacioncaso', name='historia_clinica',
            field=models.ForeignKey(on_delete=models.PROTECT, related_name='derivaciones', to='clinica.historiaclinica', verbose_name='Historia Clínica'),
        ),
        migrations.AddField(
            model_name='derivacioncaso', name='logros_alcanzados',
            field=models.TextField(blank=True, default='', verbose_name='Logros Alcanzados'),
        ),
        migrations.AddField(
            model_name='derivacioncaso', name='recomendaciones_mantenimiento',
            field=models.TextField(blank=True, default='', verbose_name='Recomendaciones de Mantenimiento'),
        ),
        migrations.AlterField(
            model_name='derivacioncaso', name='tipo_derivacion',
            field=models.CharField(choices=[('INTERNA_COLEGA', 'Derivación Interna a Colega'), ('EXTERNA_PSIQUIATRIA', 'Referencia Médica Externa a Psiquiatría'), ('EXTERNA_NEUROLOGIA', 'Referencia Externa a Neurología'), ('CIERRE_ALTA', 'Alta Terapéutica por Cumplimiento de Metas'), ('DESERCION', 'Cierre por Abandono / Deserción'), ('MUTUO_ACUERDO', 'Cierre por Mutuo Acuerdo'), ('REACTIVACION', 'Reactivación de Caso')], max_length=30, verbose_name='Tipo de Derivación / Cierre'),
        ),
    ]
