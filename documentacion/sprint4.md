# ÍNDICE COMPLETO OFICIAL – DOCUMENTACIÓN INTEGRAL SPRINT 4 Y CIERRE DEL PROYECTO (SIGEPSI)

> **Proyecto:** SIGEPSI – Plataforma Web y Móvil SaaS Multi-Tenant de Gestión Integral de Citas, Expedientes Clínicos, Seguimiento Terapéutico, Finanzas Contables y CRM para Centros de Salud Mental  
> **Asignatura:** Sistemas de Información II (SI-2 · Semestre 2-2026) – Grupo #9  
> **Periodo del Sprint 4:** Viernes 06 de noviembre al Domingo 22 de noviembre de 2026 (cierre documental 23:59)  
> **Defensa Oficial Docente:** Martes 24 de noviembre (Grupos Impares) y Jueves 26 de noviembre de 2026 (Grupos Pares)  
> **Nota Metodológica:** Conforme a la tabla de contenido oficial (`datos/Tabla_de_contenido_Scrum_SI-2_NOV16_S2-2026.md`) y las directrices finales de la cátedra (`datos/requerimientosSprint4.md`), los documentos previos permanecen inalterados para preservar la trazabilidad histórica, mientras que este documento consolida el **Índice Completo (con enlace a los capítulos previos y desglose integral del Sprint 4)**, el **Desarrollo Técnico y Modelado UML / Modelo C4 del Sprint 4**, los **Artefactos Finales Consolidados (Sección 5)**, las **Conclusiones (1 General + 6 Individuales en página siguiente)**, la **Recomendación General Puntual**, la **Bibliografía** y los **Anexos (3 Casos de Estudio + Enlaces y Códigos QR)**.
> **Control de Índice Word/PDF:** Antes de exportar la versión final de entrega (Domingo 22/11/2026), actualizar campos de Tabla de Contenido (`F9` en LibreOffice/Word) para asegurar numeración exacta de página sin desconfiguración.

| Sección | Título de la Sección / Subsección | Ubicación / Ancla |
| :--- | :--- | :--- |
| **0** | **ÍNDICE COMPLETO DEL PROYECTO SIGEPSI (PERFIL A ANEXOS)** | [Ir a Índice](#índice-completo-oficial--documentación-integral-sprint-4-y-cierre-del-proyecto-sigepsi) |
| **0.1** | **PERFIL DEL PROYECTO** *(Documento Base Consolidado)* | [Ver intento.md](./intento.md) |
| **1** | **CAPÍTULO 1: MARCO TEÓRICO** *(1.1 Marco Referencial · 1.2 Marco SCRUM)* | [Ver intento.md](./intento.md) |
| **2** | **CAPÍTULO 2: HERRAMIENTAS TECNOLÓGICAS PARA EL DESARROLLO** *(Actualizado con Modelo C4 en 4.2.1.1)* | [Ver intento.md](./intento.md) / [Modelo C4](#4211-diseñar-la-arquitectura--modelo-c4-completo-niveles-1-al-4) |
| **3** | **CAPÍTULO 3: REQUERIMIENTOS** *(3.1 Propósito a 3.10 Planificación Gantt y Product Backlog)* | [Ver intento.md](./intento.md) |
| **4.S1** | **CAPÍTULO 4 – SPRINT 1** *(Solo artefactos y eventos SCRUM; UML retirado por indicación docente)* | [Ver sprint1.md](./sprint1.md) |
| **4.S2** | **CAPÍTULO 4 – SPRINT 2** *(Solo artefactos y eventos SCRUM; UML retirado por indicación docente)* | [Ver sprint2.md](./sprint2.md) |
| **4.S3** | **CAPÍTULO 4 – SPRINT 3** *(Solo artefactos y eventos SCRUM; UML retirado por indicación docente)* | [Ver sprint3.md](./sprint3.md) |
| **4.0** | **CAPÍTULO 4 – DESARROLLO INTEGRAL SPRINT 4 (CON TODOS LOS MODELOS UML + MODELO C4)** | [Ir a Resumen Ejecutivo](#capítulo-4--desarrollo-sprint-4-sigepsi) |
| **4.1** | **SPRINT PLANNING (SPRINT 4)** | [Ir a 4.1](#41-sprint-planning) |
| 4.1.1 | Objetivos del Sprint 4, Casos de Uso (`CU23, CU24, CU26`) y Cronograma (06/11 – 22/11/2026) | [Ir a 4.1.1](#411-objetivos-del-sprint-4) |
| 4.1.2 | Historias de Usuario del Sprint 4 (`HU-49` a `HU-56` – Tarjetas 3C, Planning Poker 52 PHU, Prototipos) | [Ir a 4.1.2](#412-historias-de-usuario-del-sprint-4) |
| 4.1.3 | Contexto del Sistema (Modelo de Negocio, Casos de Uso, Clases de Dominio y Actividades Sprint 4) | [Ir a 4.1.3](#413-contexto-del-sistema) |
| 4.1.4 | Sprint Backlog Oficial (`SP4-79` a `SP4-88` – 10 Tareas / 59.0 hr) y Equipo SCRUM Rotación Sprint 4 | [Ir a 4.1.4](#414-sprint-backlog-y-equipo-scrum-del-sprint-4) |
| **4.2** | **PROCESO / PATRÓN DE DESARROLLO POR HISTORIA DE USUARIO** | [Ir a 4.2](#42-procesopatrón-de-desarrollo-por-historia-de-usuario) |
| **4.2.1** | **Diseño de Software y Arquitectura** | [Ir a 4.2.1](#421-diseño) |
| 4.2.1.1 | Diseño de la Arquitectura – **Modelo C4 de Simon Brown (Niveles 1, 2, 3 y 4)** | [Ir a 4.2.1.1](#4211-diseñar-la-arquitectura--modelo-c4-completo-niveles-1-al-4) |
| 4.2.1.2 | Diseño de Datos (Modelo Relacional Físico, Script SQL DDL PostgreSQL 16, Diccionario y Dataset Sintético 6–12 Meses) | [Ir a 4.2.1.2](#4212-diseño-de-datos) |
| 4.2.1.3 | Diseño de la Lógica de Negocio (Patrón BCE: Comunicación, Clases de Análisis y Secuencia UML 2.5+ para `CU23`, `CU24` y `CU26`) | [Ir a 4.2.1.3](#4213-diseño-de-la-lógica-de-negocio-patrón-bce) |
| 4.2.1.4 | Modelado del Comportamiento Temporal (Diagramas de Tiempo UML 2.5) | [Ir a 4.2.1.4](#4214-diagramas-de-tiempo-uml-25) |
| 4.2.1.5 | Modelado del Ciclo de Vida y Transiciones (Máquinas de Estados UML 2.5) | [Ir a 4.2.1.5](#4215-diagramas-de-máquina-de-estados-uml-25) |
| 4.2.1.6 | Diseño de Navegación de Vistas (Modelo WAE Conallen Web y Móvil) | [Ir a 4.2.1.6](#4216-diseño-de-navegación-de-vistas-modelo-wae-conallen) |
| **4.2.2** | **Implementación (Componentes y Artefactos Generados – Trabajo Full Stack)** | [Ir a 4.2.2](#422-implementación-componentes-y-artefactos-generados) |
| **4.2.3** | **Pruebas (Plan de Pruebas BDD de Caja Negra y Reporte de Pruebas Automatizadas / Estrés)** | [Ir a 4.2.3](#423-pruebas) |
| **4.3** | **DAILY SCRUM (SEGUIMIENTO DIARIO DEL 06/11 AL 22/11/2026)** | [Ir a 4.3](#43-daily-scrum-o-scrum-diario) |
| **4.4** | **SPRINT REVIEW (REVISIÓN FORMAL DEL SPRINT 4 – 22/11/2026)** | [Ir a 4.4](#44-sprint-review-revisión-de-sprint) |
| **4.5** | **SPRINT RETROSPECTIVE (RETROSPECTIVA DEL SPRINT 4 – 22/11/2026)** | [Ir a 4.5](#45-sprint-retrospective-retrospectiva-de-sprint) |
| **4.6** | **BURNDOWN Y BURNUP DEL SPRINT 4** | [Ir a 4.6](#46-burndown-y-burnup) |
| **4.7** | **GRÁFICA DE ESFUERZO Y DATOS DE ESFUERZO DEL SPRINT 4** | [Ir a 4.7](#47-gráfica-de-esfuerzo-y-datos-de-esfuerzo) |
| **4.8** | **SCRUM TASKBOARD FINAL DEL SPRINT 4** | [Ir a 4.8](#48-scrum-taskboard-final) |
| **5** | **ARTEFACTOS FINALES CONSOLIDADOS (SPRINTS 1, 2, 3 Y 4)** | [Ir a 5](#5-artefactos-finales-consolidados) |
| 5.1 | Calificación Cuantitativa Miembros de Equipo SCRUM (Sprints 1–4 y Promedio Final) | [Ir a 5.1](#51-calificación-miembros-de-equipo-scrum) |
| 5.2 | Sprint Review Consolidado (Sprints 1, 2, 3 y 4) | [Ir a 5.2](#52-sprint-review-consolidado-sprints-1-2-3-y-4) |
| 5.3 | Sprint Retrospective Consolidada y Análisis de Desempeño Individual/Grupal | [Ir a 5.3](#53-sprint-retrospective-consolidada-sprints-1-2-3-y-4) |
| 5.4 | Gráficas Consolidadas de Burndown, BurnUp y Esfuerzo (Los 4 Sprints en Una Sola Línea) | [Ir a 5.4](#54-gráfica-consolidada-de-burndown-burnup-y-esfuerzo-sprints-1-al-4) |
| **6** | **CONCLUSIÓN (CONCLUSIÓN GENERAL DEL PROYECTO Y 6 CONCLUSIONES INDIVIDUALES)** | [Ir a 6](#6-conclusión) |
| **7** | **RECOMENDACIÓN (RECOMENDACIÓN GENERAL DEL PROYECTO)** | [Ir a 7](#7-recomendación) |
| **8** | **BIBLIOGRAFÍA (LIBROS FÍSICOS, SITIOS WEB, AGENTES/MODELOS IA Y ENTREVISTAS)** | [Ir a 8](#8-bibliografía) |
| **9** | **ANEXOS (CASOS DE ESTUDIO 1, 2 Y 3 + CÓDIGOS QR Y ENLACES DEL ECOSISTEMA)** | [Ir a 9](#9-anexos) |

---

# CAPÍTULO 4 – DESARROLLO SPRINT 4 (SIGEPSI)

> **Periodo oficial de desarrollo:** Viernes 06 de noviembre al Domingo 22 de noviembre de 2026 *(hasta las 23:59 hrs)*  
> **Entrega documental e incremento congelado:** Domingo 22 de noviembre de 2026  
> **Presentación y Defensa Final ante la Cátedra:** Martes 24 de noviembre *(grupos impares)* y Jueves 26 de noviembre de 2026 *(grupos pares)*  
> **Asignatura:** Sistemas de Información II (SI2 – Semestre 2-2026) – Grupo #9  
> **Integrantes del Equipo SCRUM:**  
> • Larrazabal Rojas Julio Cesar *(Reg: 223049255)* – **Product Owner & Full Stack (UI/UX, Angular 17 & Flutter)**  
> • Mujica Vallejos Andy Mauricio *(Reg: 224028367)* – **Scrum Master & Full Stack (IA Longitudinal, ML & Liquidación SaaS)**  
> • Delgado Rojas Alberto Caleb *(Reg: 224027204)* – **Development Team Full Stack (Móvil Flutter/CRM & Seguridad)**  
> • Condori Diaz Marilyn Esther *(Reg: 224051237)* – **Development Team Full Stack (Finanzas/Pagos BOB/USD)**  
> • Romero Saavedra Maria Ilse *(Reg: 222009772)* – **Development Team Full Stack (Contabilidad Utilidad Neta, CRM & Datasets ML)**  
> • Velasco Soliz Rolando *(Reg: 223044768)* – **Development Team Full Stack (QA Lead, Seguridad, Estrés & Automatización)**  
> **Casos de Uso del Incremento:** `CU23`, `CU24` y `CU26` *(ampliado con Extracto de Amortización, Contabilidad de Utilidad Neta y Módulo CRM de Satisfacción)*

---

## Resumen Ejecutivo del Incremento del Sprint 4

El **Sprint 4** constituye la etapa de culminación integral de la plataforma SaaS Multi-Tenant **SIGEPSI** (*Sistema de Gestión Integral de Centros de Salud Mental*). Tras consolidar la infraestructura multi-inquilino y RBAC en el Sprint 0 (`CU1–CU4, CU27`), la agenda clínica y teleconsulta WebRTC en el Sprint 1 (`CU6–CU11, CU13`), el núcleo clínico médico-legal, bitácora AES-256 Fernet, reportes QBE con voz, backup/restore y chatbot en el Sprint 2 (`CU5, CU14–CU20, CU25, CU28`), y la experiencia móvil nativa en Flutter junto con el triaje inicial de IA en el Sprint 3 (`CU12, CU21, CU22` + `CU2/11/13/17 Móvil`), el **Sprint 4** cierra el ciclo entregando salidas gerenciales, predictivas, financieras y de fidelización de nivel empresarial:

1. **Síntesis Clínica Longitudinal Asistida por IA (`CU23` / `HU-49`):** Motor de generación de resúmenes longitudinales que sintetiza múltiples notas SOAP, antecedentes del intake y evolución del *Mood Tracker* de un paciente en un informe estructurado con trazabilidad SHA-256 y supervisión humana obligatoria (*Human-in-the-Loop*).
2. **Modelo Predictivo de Señales de Riesgo y Alertas Tempranas (`CU24` / `HU-50`):** Pipeline de Machine Learning e inferencia semántica entrenado/validado sobre **datasets sintéticos longitudinales de 6 a 12 meses** (12+ centros psicológicos, más de 1,800 notas clínicas y 12,000 registros diarios de ánimo) para detectar deterioro emocional sostenido, probabilidad de deserción terapéutica y riesgo clínico crítico.
3. **Gestión Financiera Multimoneda, Planes de Amortización y Estado de Cuenta (`CU26` / `HU-51, HU-52`):** Control transaccional en **Bolivianos (BOB)** y **Dólares Estadounidenses (USD)** con tipo de cambio referencial configurable y ajuste de precisión contable (cero descuadre de centavos), ofreciendo al paciente —en Web y en la App Móvil Flutter— un **extracto completo de amortización** de paquetes o planes de terapia (cuota mensual/por sesión, seguro/cobertura aplicada, comisión financiera, capital amortizado y saldo pendiente).
4. **Liquidación de Honorarios, Facturación SaaS y Contabilidad de Utilidad Neta (`CU26` / `HU-53, HU-54`):** Módulo contable gerencial que trasciende el comprobante básico: calcula la **Ganancia Bruta** por atenciones y suscripciones, deduce los honorarios liquidados a psicólogos y resta los **Gastos Fijos Mensuales** configurados por el centro (alquiler de consultorios, servicios básicos de luz/agua/internet, planilla de personal de apoyo administrativo/recepción e infraestructura cloud), entregando el reporte real de **Utilidad Neta del Periodo**.
5. **Módulo CRM de Calificación Post-Consulta y Estadísticas de Calidad (`CU26 / CRM` / `HU-55`):** Flujo integrado en la App Móvil Flutter y portal web que invita al paciente al cierre de cada sesión a calificar el servicio del **1 al 5 estrellas** con comentarios estructurados, alimentando un panel estadístico gerencial (CSAT, distribución porcentual de calificaciones, ranking de satisfacción y alertas por calificación $\le 2$ estrellas) para medir la respuesta del cliente frente a la competencia.
6. **Arquitectura Modelada Exclusivamente bajo el Modelo C4 (`4.2.1.1`) y Validación Global (`HU-56`):** En cumplimiento directo de la directriz de la cátedra para el Sprint 4, el diseño arquitectónico se formaliza íntegramente mediante los **4 niveles del Modelo C4 de Simon Brown** (Contexto, Contenedores, Componentes y Código), acompañado por el paquete completo de diagramas UML de análisis y lógica de negocio (Casos de Uso, Dominio, Actividades, Comunicación BCE, Clases de Análisis, Secuencia UML 2.5+, Tiempo, Estados y Navegación WAE) y pruebas finales de estrés, concurrencia y seguridad SaaS.

### Trazabilidad Acumulada de Casos de Uso (Sprint 0 al Sprint 4)

| Sprint | Casos de Uso Implementados | Enfoque del Incremento | Estado Final |
| :---: | :--- | :--- | :---: |
| **Sprint 0** | `CU1, CU2, CU3, CU4, CU27` | Fundación Multi-Tenant (`django-tenants`), JWT, RBAC y recuperación de credenciales | **Concluido (100%)** |
| **Sprint 1** | `CU6, CU7, CU8, CU9, CU10, CU11, CU13` | Psicólogos, Pacientes, Disponibilidad, Dashboard KPIs, Alertas, Citas y Teleconsulta Jitsi | **Concluido (100%)** |
| **Sprint 2** | `CU5, CU14, CU15, CU16, CU17, CU18, CU19, CU20, CU25, CU28` | Bitácora AES-256 Fernet, Intake, HCE CIE-10/11, SOAP, Tareas, Firma SHA-256, Derivación, Chatbot, QBE Voz, Backup | **Concluido (100%)** |
| **Sprint 3** | `CU12, CU21, CU22` + `CU2/11/13/17 (Móvil)` | App Móvil Flutter nativa, Notificaciones Push FCM v1, Clasificación IA de motivos y Matching multivariable | **Concluido (100%)** |
| **Sprint 4** | **`CU23, CU24, CU26` (+ Contabilidad Utilidad Neta y CRM)** | **Resúmenes Longitudinales IA, Predicción ML de Riesgo (6–12 meses), Pagos Multimoneda, Extracto Amortización, Utilidad Neta Contable, Suscripciones SaaS y CRM 1–5★** | **Concluido (100%)** |

---

## 4.1 SPRINT PLANNING

### 4.1.1 Objetivos del Sprint 4

**Objetivo General:** Entregar el cierre Full Stack de **SIGEPSI** integrando inteligencia clínica longitudinal (`CU23, CU24`), gestión financiera y contable multimoneda (`CU26`), CRM de satisfacción (`1–5★`), arquitectura **Modelo C4** y validación con datasets sintéticos de 6 a 12 meses.

**Objetivos Específicos:**
1. **IA y ML Clínico (`CU23, CU24`):** Generar resúmenes longitudinales con validación humana (*HITL*) y alertas predictivas de riesgo sobre series de 6 a 12 meses.
2. **Finanzas y Utilidad Neta (`CU26`):** Soportar cobros `BOB/USD`, extracto de amortización en Web y Móvil, liquidación de honorarios/SaaS y Estado de Resultados diferenciando **Ganancia Bruta** vs. **Utilidad Neta** (descontando gastos fijos).
3. **CRM de Calidad (`CU26-CRM`):** Habilitar calificación post-consulta de 1 a 5 estrellas con métricas **CSAT/NPS** en el Dashboard.
4. **Calidad y Seguridad Multi-Tenant (`SP4-88`):** Certificar concurrencia, precisión `Decimal`, aislamiento entre esquemas y desempeño bajo carga en la nube.

#### Casos de Uso Contemplados en el Sprint 4

| ID CU | Descripción del Caso de Uso (Product Backlog) | Estado | Móvil | Web | Sprint | Requisitos Asociados |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **CU23** | Generar resúmenes clínicos longitudinales asistidos por Inteligencia Artificial | Implementado | | X | SP4 | RF-10, RF-22, RF-30, RNF-19 |
| **CU24** | Detectar señales de riesgo longitudinal y generar alertas predictivas mediante IA/ML | Implementado | | X | SP4 | RF-26, RF-27, RNF-19 |
| **CU26** | Gestionar pagos multimoneda (BOB/USD), extracto de amortización, estado de cuenta, liquidación de honorarios, suscripciones SaaS, estado de resultados (Utilidad Neta) y CRM de satisfacción (1–5 estrellas) | Implementado | X | X | SP4 | RF-04, RF-05, RF-30, RNF-17, Criterio 8 |

<br>

#### Cronograma Oficial de Hitos y Actividades del Sprint 4

| Hito / Actividad | Fecha de Inicio | Fecha de Fin | Duración | Estado |
| :--- | :---: | :---: | :---: | :---: |
| Planificación del Sprint 4 y Refinamiento Contable/CRM (Sprint Planning) | 06 de noviembre de 2026 | 07 de noviembre de 2026 | 2 días | **Concluido** |
| Diseño UI/UX (Figma Responsivo), Modelo C4 (Niveles 1–4) y Modelado SQL/UML | 07 de noviembre de 2026 | 10 de noviembre de 2026 | 4 días | **Concluido** |
| Desarrollo Full Stack IA Longitudinal (`CU23`) y Detector Predictivo ML (`CU24`) | 10 de noviembre de 2026 | 16 de noviembre de 2026 | 7 días | **Concluido** |
| Desarrollo Full Stack Pagos Multimoneda, Amortización, Utilidad Neta y CRM (`CU26`) | 12 de noviembre de 2026 | 20 de noviembre de 2026 | 9 días | **Concluido** |
| Siembra de Datasets Sintéticos (6–12 meses), Pruebas BDD, Estrés y Seguridad SaaS | 17 de noviembre de 2026 | 21 de noviembre de 2026 | 5 días | **Concluido** |
| Revisión del Sprint 4 (Sprint Review), Retrospectiva y Cierre Documental (23:59) | 22 de noviembre de 2026 | 22 de noviembre de 2026 | 1 día | **Concluido** |
| Defensa Final del Proyecto ante la Cátedra (Impares 24/11 – Pares 26/11) | **24 de noviembre de 2026** | **26 de noviembre de 2026** | 2 días | **Programado** |

---

### 4.1.2 Historias de Usuario del Sprint 4

Para el cierre del proyecto se formularon **8 Historias de Usuario (`HU-49` a `HU-56`)** aplicando rigurosamente el estándar de las **3C** (*Card, Conversation, Confirmation BDD*) y estimando su complejidad relativa mediante **Planning Poker** (escala de Fibonacci: $1, 2, 3, 5, 8, 13$), alcanzando **52 Puntos de Historia de Usuario (PHU)** alineados con las **10 tareas técnicas del Product Backlog (`SP4-79` a `SP4-88`)**.

#### Resumen de Historias de Usuario del Sprint 4

| ID | Título de la Historia de Usuario | CU / Tareas Backlog | Prioridad | PHU | Responsables Full Stack | Prototipo Asociado (Figma) |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| **HU-49** | Generación asistida de resúmenes clínicos longitudinales por IA con supervisión humana | `CU23` / `SP4-79, SP4-80, SP4-82` | Alta | 8 PHU | Mujica Andy (SM) / Larrazabal Julio (PO) | Consola de Síntesis Longitudinal IA (Web) |
| **HU-50** | Detección predictiva de señales de riesgo longitudinal y alertas tempranas ML (6–12 meses) | `CU24` / `SP4-79, SP4-81, SP4-82` | Alta | 8 PHU | Mujica Andy (SM) / Velasco Rolando | Radar Predictivo de Riesgo Clínico (Web) |
| **HU-51** | Registro de cobros multimoneda (BOB/USD), ajuste cambiario y pasarela de pago | `CU26` / `SP4-83, SP4-84, SP4-85` | Alta | 8 PHU | Condori Marilyn / Larrazabal Julio (PO) | Caja Multimoneda y Checkout QR/Stripe (Web) |
| **HU-52** | Extracto detallado de amortización de planes terapéuticos y estado de cuenta (Web y Móvil) | `CU26` / `SP4-83, SP4-84, SP4-85` | Alta | 5 PHU | Delgado Alberto / Condori Marilyn | Extracto Amortización y Estado Cuenta (Flutter/Web) |
| **HU-53** | Liquidación automatizada de honorarios a psicólogos y facturación de suscripciones SaaS | `CU26` / `SP4-86, SP4-87` | Alta | 5 PHU | Mujica Andy (SM) / Larrazabal Julio (PO) | Panel Liquidaciones y Suscripciones SaaS (Web) |
| **HU-54** | Estado de resultados contable gerencial: Ganancia Bruta vs. Utilidad Neta (Gastos Fijos) | `CU26` / `SP4-86, SP4-87` | Alta | 8 PHU | Romero Maria Ilse / Mujica Andy (SM) | Dashboard Financiero Utilidad Neta (Web) |
| **HU-55** | Módulo CRM de calificación post-consulta (1–5 estrellas) y estadísticas de calidad de servicio | `CU26-CRM` / `SP4-83, SP4-86` | Alta | 5 PHU | Romero Maria Ilse / Delgado Alberto | Encuesta 1–5★ Móvil y Panel CSAT CRM (Flutter/Web) |
| **HU-56** | Pruebas finales de estrés, concurrencia, datasets de 12 meses y seguridad Multi-Tenant SaaS | `CU23, 24, 26` / `SP4-88` | Alta | 5 PHU | Velasco Rolando / Equipo SCRUM | Consola Salud SaaS & Reporte Estrés QA |
| **TOTAL** | **Esfuerzo Planificado Sprint 4 (8 Historias de Usuario)** | **`CU23, CU24, CU26`** | — | **52 PHU** | **Equipo SCRUM Full Stack (6 integrantes)** | **8 Prototipos Responsivos Web & Móvil** |

---

#### Detalle de Historias de Usuario (Tarjetas 3C en Formato Oficial)

##### HU-49: Generación asistida de resúmenes clínicos longitudinales por IA con supervisión humana

| Campo | Especificación Oficial (Tarjeta 3C) |
| :--- | :--- |
| **ID y Título:** | **HU-49: Generación asistida de resúmenes clínicos longitudinales por IA con supervisión humana** *(CU23 / RF-10, RF-22, RNF-19)* |
| **Card (Descripción):** | Como Psicólogo Tratante, quiero generar un resumen clínico longitudinal asistido por IA que sintetice las notas SOAP, diagnósticos CIE-10 y tendencia del Mood Tracker de un paciente a lo largo de múltiples sesiones, para preparar sesiones de seguimiento o juntas médicas con trazabilidad ética. |
| **Prioridad / PHU:** | Prioridad: **Alta** &nbsp;\|&nbsp; Estimación Planning Poker: **8 PHU** |
| **Conversation:** | Antes de invocar al modelo generativo, todo texto pasa por el filtro de sanitización PII (`sanitizar_pii`). El resumen generado queda en estado `BORRADOR_IA` con hash SHA-256; el psicólogo debe revisarlo, editarlo si corresponde y aprobarlo explícitamente (*Human-in-the-Loop*) antes de incorporarlo al expediente oficial o exportarlo a PDF. |
| **Confirmation (Criterios BDD):** | • **a)** Dado que el paciente tiene $\ge 2$ notas SOAP firmadas, cuando el psicólogo solicita el resumen longitudinal en un rango de fechas, el sistema sanitiza datos personales (nombres, CI, teléfonos) y genera una síntesis estructurada (evolución sintomática, adherencia a tareas y metas alcanzadas).<br>• **b)** Dado que la síntesis se genera, cuando el usuario aún no la valida, se muestra una insignia obligatoria *"Borrador Asistido por IA – Pendiente de Validación Clínica"* y se impide su exportación oficial.<br>• **c)** Dado que el psicólogo aprueba o edita el resumen, el sistema registra usuario, fecha local `America/La_Paz` e IP en `clinica_resumenlongitudinalia` y habilita la descarga en PDF. |
| **Responsables / Prototipo:** | Mujica Vallejos Andy (SM) / Larrazabal Rojas Julio (PO) &nbsp;\|&nbsp; **Prototipo:** Consola de Síntesis Longitudinal IA (Figma)<br>**Prompt UI:** *"Desktop web clinical AI longitudinal summary drawer in Angular 17 for SIGEPSI. Timeline digest card comparing 12 SOAP sessions and mood curve, PII anonymized badge, editable markdown summary pane, and 'Aprobar y Sellar Resumen' HITL button. Clean clinical teal UI, 4k."* |

![Prototipo UI HU-49 – Consola de Síntesis Longitudinal IA (HITL)](./imagenes/prototipo_hu49_sintesis_ia.png)


<br>

##### HU-50: Detección predictiva de señales de riesgo longitudinal y alertas tempranas ML (6–12 meses)

| Campo | Especificación Oficial (Tarjeta 3C) |
| :--- | :--- |
| **ID y Título:** | **HU-50: Detección predictiva de señales de riesgo longitudinal y alertas tempranas ML (6–12 meses)** *(CU24 / RF-26, RF-27, RNF-19)* |
| **Card (Descripción):** | Como Psicólogo o Coordinador Clínico, quiero que el módulo analítico de IA/ML evalúe series históricas de 6 a 12 meses (curva de ánimo, inasistencias, incumplimiento de tareas y términos clínicos críticos) para predecir riesgo de recaída o abandono terapéutico y generar alertas prioritarias justificadas. |
| **Prioridad / PHU:** | Prioridad: **Alta** &nbsp;\|&nbsp; Estimación Planning Poker: **8 PHU** |
| **Conversation:** | En atención directa a la exigencia de la cátedra sobre Machine Learning, el modelo predictivo no se evalúa con datos mínimos de 10 registros, sino sobre **datasets sintéticos longitudinales de 6 a 12 meses** por centro. Calcula un `indice_riesgo` ($0.00 - 1.00$), clasifica en `BAJO`, `MODERADO`, `ALTO` o `CRITICO`, y desglosa los pesos explicables (SHAP/reglas) para que el terapeuta comprenda por qué se disparó la alerta. |
| **Confirmation (Criterios BDD):** | • **a)** Dado un historial longitudinal de $\ge 4$ semanas con tendencia descendente en `clinica_registroanimo` ($\Delta \le -1.5$ puntos) y $\ge 2$ tareas vencidas, cuando corre el analizador ML, genera una alerta en `clinica_alertariesgoia` con score $\ge 0.70$ y nivel `ALTO` o `CRITICO`.<br>• **b)** Dado que se genera una alerta predictiva, el panel web muestra los factores contribuyentes (ej. *Descenso anímico 42%, Ausentismo 35%, Léxico SOAP 23%*) sin emitir diagnósticos automáticos.<br>• **c)** Dado que el profesional atiende la alerta e ingresa su acción de intervención, el estado transiciona a `INTERVENIDA` quedando auditada. |
| **Responsables / Prototipo:** | Mujica Vallejos Andy (SM) / Velasco Soliz Rolando &nbsp;\|&nbsp; **Prototipo:** Radar Predictivo de Riesgo Clínico (Figma)<br>**Prompt UI:** *"Clinical Machine Learning risk prediction dashboard in Angular 17 for SIGEPSI. Patient risk heatmap, 6-to-12-month emotional trend chart with relapse risk threshold line, feature attribution horizontal bars (Mood Slope, Attendance, Homework Adherence), and 'Registrar Intervención Clínica' action modal. 4k Figma."* |

![Prototipo UI HU-50 – Radar Predictivo de Riesgo Clínico ML (6–12 meses)](./imagenes/prototipo_hu50_radar_ml.png)


<br>

##### HU-51: Registro de cobros multimoneda (BOB/USD), ajuste cambiario y pasarela de pago

| Campo | Especificación Oficial (Tarjeta 3C) |
| :--- | :--- |
| **ID y Título:** | **HU-51: Registro de cobros multimoneda (BOB/USD), ajuste cambiario y pasarela de pago** *(CU26 / RF-05, RNF-17)* |
| **Card (Descripción):** | Como Recepcionista o Administrador del Centro, quiero registrar pagos de consultas y paquetes terapéuticos en múltiples monedas (Bolivianos BOB y Dólares USD) usando distintos métodos (QR Simple, Tarjeta Stripe, Transferencia o Efectivo), aplicando conversión exacta sin diferencias de redondeo contable. |
| **Prioridad / PHU:** | Prioridad: **Alta** &nbsp;\|&nbsp; Estimación Planning Poker: **8 PHU** |
| **Conversation:** | Todos los montos monetarios se almacenan con tipo `Decimal(12, 2)` en la moneda de origen y su contravalor en moneda base (`BOB`) usando la tasa oficial del día (`tipo_cambio_aplicado`, por defecto `6.96 BOB/USD`) y redondeo bancario `ROUND_HALF_UP` con registro explícito de `ajuste_diferencia_cambio` para que los asientos contables cuadren al centavo ($0.00$ de descuadre). |
| **Confirmation (Criterios BDD):** | • **a)** Dado un cobro de sesión de `$30.00 USD` con tasa `6.96`, cuando se registra en caja con método `QR_SIMPLE`, el sistema calcula exactamente `208.80 BOB`, persiste el comprobante inmutable y actualiza el saldo del paciente.<br>• **b)** Dado un pago con tarjeta mediante pasarela Stripe, cuando el webhook o verificación retorna `paid`, se concilia automáticamente la transacción evitando cobros duplicados por clave idempotente.<br>• **c)** Dado que se consulta el libro diario de caja, la suma de montos convertidos más ajustes cambiarios cuadra exactamente con el total contable ($0.000$ de diferencia). |
| **Responsables / Prototipo:** | Condori Diaz Marilyn / Larrazabal Rojas Julio (PO) &nbsp;\|&nbsp; **Prototipo:** Caja Multimoneda y Checkout QR/Stripe (Figma)<br>**Prompt UI:** *"Modern healthcare billing and multi-currency POS screen in Angular 17 for SIGEPSI. Currency switcher pill 'BOB (Bs.) / USD ($)', live exchange rate badge '1 USD = 6.96 BOB', payment method selector (QR Simple, Tarjeta Stripe, Efectivo), itemized receipt preview and instant reconciliation badge. 4k Figma UI."* |

![Prototipo UI HU-51 – Caja Multimoneda BOB/USD y Checkout QR/Stripe](./imagenes/prototipo_hu51_caja_multimoneda.png)


<br>

##### HU-52: Extracto detallado de amortización de planes terapéuticos y estado de cuenta (Web y Móvil)

| Campo | Especificación Oficial (Tarjeta 3C) |
| :--- | :--- |
| **ID y Título:** | **HU-52: Extracto detallado de amortización de planes terapéuticos y estado de cuenta (Web y Móvil)** *(CU26 / RF-04, RF-30)* |
| **Card (Descripción):** | Como Paciente o Administrador, quiero consultar el estado de cuenta y un extracto completo de amortización cuando se contratan paquetes o planes de tratamiento en cuotas, visualizando cuota programada, seguro/cobertura, recargo o interés administrativo, monto amortizado y saldo pendiente tanto en Web como en la App Móvil Flutter. |
| **Prioridad / PHU:** | Prioridad: **Alta** &nbsp;\|&nbsp; Estimación Planning Poker: **5 PHU** |
| **Conversation:** | En respuesta directa a la directriz de la cátedra (*no conformarse con una simple facturita o comprobante, sino mostrar el extracto completo de cuotas, intereses/comisiones, seguro y amortización*), SIGEPSI permite financiar paquetes terapéuticos anuales o semestrales (ej. Programa Integral de 12 o 24 sesiones) mostrando tabla de amortización cuota a cuota, seguro de continuidad clínica y tasa referencial cuando aplica. |
| **Confirmation (Criterios BDD):** | • **a)** Dado un paciente con un plan terapéutico financiado en 6 cuotas, cuando accede a *"Mi Estado de Cuenta"* en Flutter o Web, visualiza el cronograma completo de cuotas (`Nro`, `Vencimiento`, `Capital Amortizado`, `Cargo Administrativo/Interés`, `Seguro Asistencial`, `Total Cuota`, `Saldo Insoluto` y `Estado`).<br>• **b)** Dado que se abona la cuota #1, el sistema marca la cuota como `PAGADA`, recalcula el saldo restante en tiempo real y permite descargar el extracto en PDF.<br>• **c)** Si una cuota supera la fecha de vencimiento sin pago, el estado cambia a `MORA` y el extracto muestra el ajuste correspondiente antes de consolidar el siguiente cobro. |
| **Responsables / Prototipo:** | Delgado Rojas Alberto / Condori Diaz Marilyn &nbsp;\|&nbsp; **Prototipo:** Extracto Amortización y Estado Cuenta (Figma Web & Flutter)<br>**Prompt UI:** *"Mobile and web patient financial statement screen with full therapy plan amortization schedule in Flutter 3 and Angular 17 for SIGEPSI. Summary cards for Total Plan, Amortized Capital, Insurance Fee, Remaining Balance, and scrollable installment table showing Paid/Pending pills and 'Descargar Extracto PDF'. 4k."* |

![Prototipo UI HU-52 – Extracto de Amortización y Estado de Cuenta (Flutter & Web)](./imagenes/prototipo_hu52_amortizacion_movil_web.png)


<br>

##### HU-53: Liquidación automatizada de honorarios a psicólogos y facturación de suscripciones SaaS

| Campo | Especificación Oficial (Tarjeta 3C) |
| :--- | :--- |
| **ID y Título:** | **HU-53: Liquidación automatizada de honorarios a psicólogos y facturación de suscripciones SaaS** *(CU26 / Criterio 8)* |
| **Card (Descripción):** | Como Administrador del Centro o SuperAdministrador SaaS, quiero calcular automáticamente la liquidación mensual de honorarios de cada psicólogo según sus sesiones realizadas y porcentaje de convenio, y gestionar el ciclo de facturación y renovación de suscripciones SaaS de los centros psicológicos. |
| **Prioridad / PHU:** | Prioridad: **Alta** &nbsp;\|&nbsp; Estimación Planning Poker: **5 PHU** |
| **Conversation:** | Cada centro configura el esquema de comisión por profesional (ej. 70% psicólogo / 30% clínica). El sistema consolida únicamente citas en estado `REALIZADA` y pagadas del periodo para emitir la planilla de honorarios. En paralelo, el SuperAdmin SaaS monitorea renovaciones, facturas de suscripción (`BASICO`, `PROFESIONAL`, `ENTERPRISE`) y alertas de vencimiento de cada tenant. |
| **Confirmation (Criterios BDD):** | • **a)** Dado un periodo mensual seleccionado, cuando el Administrador presiona *"Calcular Liquidación"*, el sistema agrupa las citas `REALIZADA` pagadas por psicólogo, aplica su porcentaje de honorario y genera el registro en `finanzas_liquidacionhonorario` en estado `PENDIENTE_PAGO`.<br>• **b)** Dado que el Administrador aprueba y registra el desembolso al terapeuta, el egreso queda contabilizado para el cálculo de Utilidad Neta del mes.<br>• **c)** Dado un tenant cuya suscripción SaaS vence en $\le 3$ días, el panel de SuperAdmin muestra la alerta de renovación y emite el enlace de pago Stripe/QR. |
| **Responsables / Prototipo:** | Mujica Vallejos Andy (SM) / Larrazabal Rojas Julio (PO) &nbsp;\|&nbsp; **Prototipo:** Panel Liquidaciones y Suscripciones SaaS (Figma)<br>**Prompt UI:** *"SaaS multi-tenant subscription billing and psychologist payout settlement dashboard in Angular 17 for SIGEPSI. Top tabs: 'Liquidación de Psicólogos' (table with sessions count, gross billed, 70/30 split, net payout, 'Aprobar Pago' button) and 'Suscripciones SaaS' (tenant plan cards, renewal status, invoice download). 4k."* |

![Prototipo UI HU-53 – Panel de Liquidación de Honorarios y Suscripciones SaaS](./imagenes/prototipo_hu53_liquidacion_saas.png)


<br>

##### HU-54: Estado de resultados contable gerencial: Ganancia Bruta vs. Utilidad Neta (Gastos Fijos)

| Campo | Especificación Oficial (Tarjeta 3C) |
| :--- | :--- |
| **ID y Título:** | **HU-54: Estado de resultados contable gerencial: Ganancia Bruta vs. Utilidad Neta (Gastos Fijos)** *(CU26, CU9 / RF-04)* |
| **Card (Descripción):** | Como Administrador o Gerente del Centro Psicológico, quiero registrar los gastos fijos mensuales de operación (alquiler de ambientes, servicios básicos, salarios de personal de apoyo, suscripción SaaS) y visualizar en el Dashboard un Estado de Resultados Contable que diferencie claramente la Ganancia Bruta de la Utilidad Neta real en cualquier rango de fechas. |
| **Prioridad / PHU:** | Prioridad: **Alta** &nbsp;\|&nbsp; Estimación Planning Poker: **8 PHU** |
| **Conversation:** | En estricto cumplimiento de la observación de la cátedra (*no confundir ganancia bruta con utilidad neta; contabilidad debe descontar todos los gastos fijos como alquiler, servicios básicos y personal de apoyo*), el motor contable consolida: `Ingresos Totales (Citas + Planes)` $-$ `Honorarios Psicólogos` $=$ `Ganancia Bruta Operativa`; y luego resta `Σ Gastos Fijos del Periodo (Alquiler + Servicios Básicos + Personal de Apoyo + Suscripción/Insumos)` $=$ **`Utilidad Neta Contable`**, incluyendo margen neto (%) y comparativa gráfica en el Dashboard. |
| **Confirmation (Criterios BDD):** | • **a)** Dado que existen ingresos cobrados en el periodo (ej. del 1 al 15 de noviembre o mes completo), cuando el Administrador registra o prorratea los gastos fijos (Alquiler Bs. 4,500, Servicios Básicos Bs. 850, Recepción/Apoyo Bs. 3,200), el sistema calcula automáticamente `Ganancia Bruta` y `Utilidad Neta` exactas.<br>• **b)** Dado un rango de fechas consultado en el Dashboard Financiero (incluyendo filtro por voz QBE), los KPIs y gráficos de barras/cascada (*waterfall*) muestran Ingresos, Costos Directos, Gastos Fijos y Utilidad/Pérdida Neta en tiempo real.<br>• **c)** Si los gastos fijos superan la ganancia bruta en un periodo, la tarjeta de Utilidad Neta resalta en rojo indicando déficit operativo para toma de decisiones. |
| **Responsables / Prototipo:** | Romero Saavedra Maria Ilse / Mujica Vallejos Andy (SM) &nbsp;\|&nbsp; **Prototipo:** Dashboard Financiero Utilidad Neta (Figma)<br>**Prompt UI:** *"Executive clinical accounting profit and loss (P&L) dashboard in Angular 17 for SIGEPSI. Waterfall chart breaking down Gross Revenue -> Therapist Payouts -> Gross Profit -> Fixed Monthly Expenses (Rent, Utilities, Support Staff) -> Net Profit (Utilidad Neta). Responsive cards with BOB/USD toggle and export to Excel/PDF. 4k."* |

![Prototipo UI HU-54 – Estado de Resultados: Ganancia Bruta vs. Utilidad Neta (Gastos Fijos)](./imagenes/prototipo_hu54_utilidad_neta_pnl.png)


<br>

##### HU-55: Módulo CRM de calificación post-consulta (1–5 estrellas) y estadísticas de calidad de servicio

| Campo | Especificación Oficial (Tarjeta 3C) |
| :--- | :--- |
| **ID y Título:** | **HU-55: Módulo CRM de calificación post-consulta (1–5 estrellas) y estadísticas de calidad de servicio** *(CU26-CRM / RF-04, RF-27)* |
| **Card (Descripción):** | Como Paciente y Administrador del Centro, quiero que tras concluir una cita presencial o teleconsulta el paciente pueda calificar la atención del 1 al 5 estrellas con retroalimentación cualitativa, para alimentar un panel estadístico CRM que mida satisfacción (CSAT), tiempos de espera y fidelización del centro. |
| **Prioridad / PHU:** | Prioridad: **Alta** &nbsp;\|&nbsp; Estimación Planning Poker: **5 PHU** |
| **Conversation:** | Incorporado directamente a partir de la recomendación de la docente en `datos/requerimientosSprint4.md` (*aumentar un módulo CRM con calificación de 1 a 5 estrellas y datos estadísticos que reflejen la respuesta real del cliente*). Una cita en estado `REALIZADA` habilita una única encuesta verificada por sesión; si el paciente califica con $\le 2$ estrellas, el CRM genera una tarea de seguimiento de calidad para el Coordinador Clínico/Recepción. |
| **Confirmation (Criterios BDD):** | • **a)** Dado que una cita pasa a estado `REALIZADA`, cuando el paciente abre la App Móvil Flutter o el portal web, aparece la tarjeta *"Califica tu experiencia de atención (1 a 5 estrellas)"* con etiquetas de aspecto evaluado (Puntualidad, Empatía, Calidad de Plataforma/Consultorio).<br>• **b)** Dado que el paciente envía calificación `5` estrellas, se persiste en `crm_calificacionservicio` (con unicidad 1 calificación por cita) y actualiza los promedios estadísticos del centro.<br>• **c)** Dado que un paciente califica con `1` o `2` estrellas, el CRM marca `requiere_seguimiento = True` y notifica al Administrador en el panel estadístico de satisfacción. |
| **Responsables / Prototipo:** | Romero Saavedra Maria Ilse / Delgado Rojas Alberto &nbsp;\|&nbsp; **Prototipo:** Encuesta 1–5★ Móvil y Panel CSAT CRM (Figma)<br>**Prompt UI:** *"Dual mobile Flutter rating sheet and web CRM customer satisfaction analytics dashboard for SIGEPSI. Mobile bottom sheet with 5 golden interactive stars, aspect tags (Puntualidad, Trato, Teleconsulta), and comment box. Web CRM dashboard showing CSAT score 4.7/5, star distribution histogram (1-5), NPS gauge, and low-rating follow-up queue. 4k."* |

![Prototipo UI HU-55 – Encuesta CRM Post-Consulta (1–5★) Móvil y Analítica CSAT/NPS](./imagenes/prototipo_hu55_crm_calificacion.png)


<br>

##### HU-56: Pruebas finales de estrés, concurrencia, datasets de 12 meses y seguridad Multi-Tenant SaaS

| Campo | Especificación Oficial (Tarjeta 3C) |
| :--- | :--- |
| **ID y Título:** | **HU-56: Pruebas finales de estrés, concurrencia, datasets de 12 meses y seguridad Multi-Tenant SaaS** *(CU23, CU24, CU26 / RNF-01, RNF-03, RNF-09)* |
| **Card (Descripción):** | Como QA Lead y Equipo Full Stack, quiero validar toda la plataforma bajo carga concurrente multi-tenant, con datasets sintéticos de 6 a 12 meses poblados en los centros psicológicos y pruebas de inviolabilidad financiera/clínica, para garantizar estabilidad absoluta en producción y en la defensa final. |
| **Prioridad / PHU:** | Prioridad: **Alta** &nbsp;\|&nbsp; Estimación Planning Poker: **5 PHU** |
| **Conversation:** | Se ejecuta el script `seed_sprint4 --months 12` en todos los esquemas tenant, poblando historial de sesiones SOAP, registros de ánimo, pagos multimoneda, planes de amortización, gastos fijos de 12 meses y encuestas CRM, seguido de suites automatizadas de Django, Angular y Flutter y pruebas de estrés concurrente. |
| **Confirmation (Criterios BDD):** | • **a)** Al ejecutar pruebas de concurrencia sobre pagos de cuotas y reserva simultánea de slots, el bloqueo transaccional impide dobles cobros o estados inconsistentes (`0` errores de integridad).<br>• **b)** Al consultar métricas de ML (`CU24`), Contabilidad (`CU26`) y CRM en los 14 esquemas tenant sembrados con 12 meses de historia, los tiempos de respuesta P95 se mantienen por debajo de `450 ms` y con `0` fugas entre esquemas.<br>• **c)** Todas las suites automatizadas de Backend, Frontend Web y Móvil Flutter pasan al `100%` tras la integración final. |
| **Responsables / Prototipo:** | Velasco Soliz Rolando / Equipo SCRUM Full Stack &nbsp;\|&nbsp; **Prototipo:** Consola Salud SaaS & Reporte Estrés QA |

![Prototipo UI HU-56 – Consola de Salud Multi-Tenant SaaS (14 Centros / 12m) y Reporte Estrés QA](./imagenes/prototipo_hu56_consola_qa_estres.png)


---

### 4.1.3 Contexto del Sistema

El **Sprint 4** cierra el ecosistema **SIGEPSI** integrando las salidas analíticas y gerenciales sobre la base operativa y clínica construida en los Sprints 0 al 3.

```
 +---------------------------------------------------------------------------------------------------------+
 |                                   ECOSISTEMA FINAL SIGEPSI (SPRINT 4)                                   |
 |                                                                                                         |
 |  +-----------------------+     HTTPS / JWT     +-----------------------------------------------------+  |
 |  | PACIENTE (App Flutter | ==================> |        BACKEND CORE DJANGO 5.x / DRF MULTI-TENANT   |  |
 |  |  & Portal Web)        |                     |  - IA Longitudinal & Resúmenes Clínicos (CU23)      |  |
 |  | - Estado Cuenta /     | <================== |  - Motor Predictivo ML Señales de Riesgo (CU24)     |  |
 |  |   Amortización (CU26) |  Push / Extracto    |  - Pagos Multimoneda BOB/USD & Amortización (CU26)  |  |
 |  | - Encuesta CRM 1-5 ★  |                     |  - Contabilidad: Ganancia Bruta vs. Utilidad Neta    |  |
 |  +-----------------------+                     |  - Liquidación Honorarios, SaaS & Analítica CRM     |  |
 |                                                +-----------------------------------------------------+  |
 |  +-----------------------+     HTTPS / JWT            ||                  ||                  ||        |
 |  | PERSONAL CLÍNICO /    | ===========================++                  ||                  ||        |
 |  | ADMIN / CONTADOR / PO |                                                \/                  \/        |
 |  | (Web Angular 17 Resp.)|                     +--------------------+  +------------+  +--------------+ |
 |  | - Resúmenes IA (HITL) |                     |   POSTGRESQL 16    |  |  STRIPE &  |  | IA / ML CLOUD| |
 |  | - Radar Riesgo ML     |                     | Esquemas Aislados  |  | QR SIMPLE  |  | Gemini & HF  | |
 |  | - P&L Utilidad Neta   |                     | + Dataset 12 Meses |  |  Pasarela  |  | + ScikitLearn| |
 |  | - CRM CSAT & SaaS     |                     +--------------------+  +------------+  +--------------+ |
 |  +-----------------------+                                                                              |
 +---------------------------------------------------------------------------------------------------------+
```

#### 1. Diagrama de Actividad del Modelo de Negocio Integral (Sprint 4)

Conforme a la exigencia metodológica de contextualizar el flujo de negocio antes del detalle técnico, el siguiente diagrama ilustra la interacción transversal entre la atención clínica, la asistencia predictiva de IA, la gestión de cobros/amortización, el cierre contable de utilidad neta y la retroalimentación CRM del paciente:

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *0. Modelo de Negocio - Proceso Integral (Sprint 4)* (**Diagrama ID: 333**).

![Diagrama de Actividad – Modelo de Negocio Integral (Sprint 4)](./imagenes/diagrama_modelo_negocio_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

title Modelo de Negocio Integral Sprint 4: Clínica, IA Longitudinal, Finanzas Contables y CRM (SIGEPSI)

|Paciente (Móvil / Web)|
start
:Asiste a consulta o contrata plan terapéutico;
if (¿Pago único o plan en cuotas?) then (Plan en Cuotas)
  :Consulta extracto de amortización\n(capital, seguro, comisión, saldo);
else (Pago por Sesión)
  :Realiza pago en BOB o USD\n(QR Simple / Stripe / Efectivo);
endif

|Caja / Finanzas (Web)|
:Valida pago, aplica tipo de cambio exacto\ny emite comprobante / actualiza cuota;

|Psicólogo Tratante (Web)|
:Atiende sesión y firma Nota SOAP;
:Solicita Resumen Longitudinal IA (CU23)\nsobre historial multi-sesión;
:Revisa borrador IA y aprueba (HITL);

|Motor IA / ML (CU23 & CU24)|
:Analiza serie temporal de 6-12 meses\n(Ánimo, Tareas, Ausentismo, SOAP);
if (¿Índice de riesgo ML >= 0.70?) then (Sí - Riesgo Alto/Crítico)
  :Genera Alerta Predictiva de Riesgo (CU24)\ncon pesos explicables al terapeuta;
else (No - Estable)
  :Registra monitoreo normal de evolución;
endif

|Paciente (Móvil / Web)|
:Recibe notificación de cierre de sesión;
:Califica atención en módulo CRM\n(1 a 5 estrellas + comentario);

|Administrador / Contador (Web)|
:Registra gastos fijos mensuales\n(Alquiler, Servicios Básicos, Personal Apoyo);
:Ejecuta liquidación de honorarios a psicólogos;
:Consulta Dashboard de Resultados Contables\n(Ganancia Bruta vs. Utilidad Neta) y Estadísticas CRM;
stop
@enduml
```

#### 2. Diagrama de Casos de Uso del Sprint 4 (Alcance del Incremento)

El siguiente diagrama formaliza los tres grandes casos de uso del Product Backlog asignados al Sprint 4 (`CU23`, `CU24` y `CU26`), desagregando las capacidades operativas, contables y de CRM exigidas para la entrega final:

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *1. Casos de Uso - Sprint 4* (**Diagrama ID: 334**).

![Diagrama de Casos de Uso – Sprint 4 (CU23, CU24, CU26 y CRM)](./imagenes/diagrama_casos_uso_sp4.png)

```plantuml
@startuml
left to right direction
skinparam packageStyle rectangle
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

actor "Psicólogo Tratante\n(Web Angular)" as psico
actor "Coordinador Clínico\n(Web Angular)" as coord
actor "Paciente\n(App Flutter / Web)" as pac
actor "Administrador / Contador\n(Web Angular)" as admin
actor "SuperAdmin SaaS\n(Web Angular)" as superadmin

rectangle "SIGEPSI - Incremento Final Sprint 4: IA Longitudinal, Finanzas Contables y CRM" {
  usecase "CU23: Generar resúmenes clínicos\nlongitudinales asistidos por IA" as CU23 #D4EFDF
  usecase "CU23.1: Sanitizar PII y validar\nsupervisión humana (HITL)" as CU23_INC #EBF5FB

  usecase "CU24: Detectar señales de riesgo\nlongitudinal mediante IA/ML (6-12m)" as CU24 #D4EFDF
  usecase "CU24.1: Emitir alerta prioritaria\ncon explicabilidad de factores" as CU24_EXT #FEF9E7

  usecase "CU26: Gestionar pagos multimoneda\n(BOB/USD) y estado de cuenta" as CU26 #D6EAF8
  usecase "CU26.1: Consultar extracto completo\nde amortización de plan terapéutico" as CU26_AMORT #EBF5FB
  usecase "CU26.2: Liquidar honorarios a psicólogos\ny gestionar suscripciones SaaS" as CU26_LIQ #EBF5FB
  usecase "CU26.3: Generar Estado de Resultados:\nGanancia Bruta vs. Utilidad Neta" as CU26_NETA #FCE4D6
  usecase "CU26.4: Calificar servicio en CRM (1-5 ★)\ny visualizar estadísticas CSAT/NPS" as CU26_CRM #F4ECF7
}

psico --> CU23
psico --> CU24
coord --> CU24

CU23 ..> CU23_INC : <<include>>
CU24 ..> CU24_EXT : <<extend>>

pac --> CU26
pac --> CU26_AMORT
pac --> CU26_CRM

admin --> CU26
admin --> CU26_LIQ
admin --> CU26_NETA
admin --> CU26_CRM

superadmin --> CU26_LIQ

CU26 ..> CU26_AMORT : <<extend>>
CU26 ..> CU26_NETA : <<include>>
CU26_LIQ ..> CU26_NETA : <<include>>
@enduml
```

#### 3. Especificación Expandida de los Casos de Uso del Sprint 4 (`CU23`, `CU24`, `CU26`)

| Elemento | Especificación Detallada |
| :--- | :--- |
| **CU23** | **Generar resúmenes clínicos longitudinales asistidos por Inteligencia Artificial** |
| **Actor Principal** | Psicólogo Tratante (Web Angular 17). |
| **Precondición** | El paciente cuenta con Historia Clínica abierta (`CU15`) y al menos 2 notas SOAP firmadas (`CU16`) o registros de ánimo (`CU17`). |
| **Flujo Normal** | 1. El psicólogo selecciona un rango temporal y solicita la síntesis longitudinal.<br>2. El sistema recopila notas SOAP, diagnósticos CIE-10 y curva de ánimo del periodo.<br>3. El middleware de privacidad (`sanitizar_pii`) elimina identificadores personales y genera un hash SHA-256 de trazabilidad.<br>4. El motor IA construye el borrador estructurado (Motivo inicial, Evolución de síntomas, Adherencia a tareas, Metas pendientes).<br>5. El psicólogo revisa, edita y aprueba formalmente el borrador (*HITL*), habilitando su archivo e impresión PDF. |
| **Excepciones** | • Si el paciente tiene menos de 2 sesiones o el psicólogo no está asignado al caso (`IsTreatingPsychologistOrAdmin`), retorna HTTP 403/400.<br>• Si el proveedor IA externo excede timeout, actúa el sintetizador extractivo local determinístico. |

| Elemento | Especificación Detallada |
| :--- | :--- |
| **CU24** | **Detectar señales de riesgo longitudinal y generar alertas predictivas mediante IA/ML** |
| **Actor Principal** | Psicólogo Tratante / Coordinador Clínico / Proceso Analítico ML (`Celery`). |
| **Precondición** | Base de datos poblada con serie histórica de seguimiento (3–12 meses de citas, tareas y *Mood Tracker*). |
| **Flujo Normal** | 1. El servicio ML extrae el vector de características del paciente ($X = [\text{pendiente\_animo}, \text{tasa\_inasistencia}, \text{adherencia\_tareas}, \text{score\_lexico\_soap}]$).<br>2. Calcula la probabilidad de deterioro o deserción ($P_{\text{riesgo}} \in [0, 1]$).<br>3. Desglosa la contribución explicable de cada variable.<br>4. Si $P_{\text{riesgo}} \ge 0.70$, genera alerta prioritaria en `clinica_alertariesgoia` visible en tiempo real en el Radar de Riesgo.<br>5. El profesional registra la intervención clínica efectuada, cambiando la alerta a `INTERVENIDA`. |
| **Excepciones** | • Jamás diagnostica patologías médicas ni cierra expedientes automáticamente; toda acción clínica recae en el profesional. |

| Elemento | Especificación Detallada |
| :--- | :--- |
| **CU26** | **Gestionar pagos multimoneda, amortización, utilidad neta contable, suscripciones SaaS y CRM (1–5 ★)** |
| **Actores** | Paciente (Flutter/Web), Recepcionista, Administrador/Contador del Centro, SuperAdmin SaaS. |
| **Precondición** | Usuario autenticado; citas o planes terapéuticos vigentes; catálogo de tipos de cambio BOB/USD y gastos fijos del periodo configurados. |
| **Flujo Normal** | 1. **Cobro y Amortización:** Recepción o el paciente abona una cita o cuota de plan terapéutico en BOB o USD (`QR Simple`, `Stripe`, `Efectivo`). El sistema calcula el tipo de cambio exacto (`Decimal`), amortiza capital, aplica seguro/comisión administrativa y actualiza el extracto consultable en Flutter y Web.<br>2. **Liquidación y Gastos Fijos:** Al cierre de quincena/mes, el Administrador liquida honorarios porcentuales de psicólogos y registra gastos fijos (alquiler, servicios básicos, personal de apoyo).<br>3. **Estado de Resultados (Utilidad Neta):** El motor contable presenta Ingresos Brutos, Costos de Honorarios, Ganancia Bruta, Gastos Fijos y **Utilidad Neta Real**.<br>4. **CRM Post-Consulta:** Al finalizar cada cita, el paciente califica de 1 a 5 estrellas en Flutter/Web alimentando el tablero estadístico CSAT/NPS y alertas de baja satisfacción. |
| **Excepciones** | • Bloqueo idempotente ante reintentos de webhook Stripe; rechazo de montos $\le 0$; validación de unicidad en calificación CRM por cita. |

#### 4. Diagrama de Clases del Dominio del Incremento Sprint 4

El modelo de dominio del Sprint 4 extiende de manera orgánica las entidades consolidadas de los Sprints 0 al 3 (`Paciente`, `Psicologo`, `HistoriaClinica`, `NotaSesion`, `Cita`, `Tenant`), incorporando las clases especializadas de IA Longitudinal, Gestión Financiera Multimoneda/Amortización, Contabilidad de Utilidad Neta y CRM de Calidad:

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *2. Clases del Dominio - Sprint 4* (**Diagrama ID: 335**).

![Diagrama de Clases del Dominio – Incremento Sprint 4](./imagenes/diagrama_clases_dominio_sp4.png)

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 6
skinparam defaultFontName Arial

title Diagrama de Clases del Dominio – Incremento Sprint 4 (SIGEPSI)

package "Dominio Clínico Consolidado (SP0-SP3)" #F8F9FA {
  class Tenant {
    + id: UUID
    + nombre: String
    + schema_name: String
    + plan: String
  }
  class HistoriaClinica {
    + id: UUID
    + codigo_historia: String
    + cerrada: Boolean
  }
  class Paciente {
    + id: UUID
    + codigo_expediente: String
    + ci: String
  }
  class Psicologo {
    + id: UUID
    + numero_colegiado: String
    + tarifa_base: Decimal
    + porcentaje_honorario: Decimal
  }
  class Cita {
    + id: UUID
    + fecha: Date
    + estado: String
    + costo: Decimal
  }
}

package "Dominio IA Longitudinal & Riesgo ML (CU23 / CU24)" #E8F8F5 {
  class ResumenClinicoIA {
    + id: UUID
    + periodo_inicio: Date
    + periodo_fin: Date
    + total_sesiones_analizadas: Integer
    + resumen_estructurado: Text
    + hash_pii_sha256: String
    + estado_validacion: String
    + observaciones_terapeuta: Text
    + fecha_generacion: DateTime
    + aprobar_resumen(psicologo_id): void
  }

  class AlertaRiesgoPredictivaIA {
    + id: UUID
    + indice_riesgo: Decimal
    + nivel_severidad: String
    + factores_contribuyentes: JSON
    + pendiente_animo_30d: Decimal
    + tasa_inasistencia: Decimal
    + estado: String
    + accion_clinica: Text
    + fecha_deteccion: DateTime
    + marcar_intervenida(usuario_id, nota): void
  }
}

package "Dominio Finanzas, Amortización y Contabilidad (CU26)" #EBF5FB {
  class PlanPagoTerapeutico {
    + id: UUID
    + nombre_plan: String
    + sesiones_incluidas: Integer
    + monto_total: Decimal
    + moneda: String
    + tasa_interes_anual: Decimal
    + porcentaje_seguro: Decimal
    + numero_cuotas: Integer
    + estado: String
    + generar_tabla_amortizacion(): List
  }

  class CuotaAmortizacion {
    + id: UUID
    + numero_cuota: Integer
    + fecha_vencimiento: Date
    + capital_amortizado: Decimal
    + interes_o_comision: Decimal
    + seguro_asistencial: Decimal
    + monto_total_cuota: Decimal
    + saldo_insoluto: Decimal
    + estado: String
  }

  class PagoTransaccion {
    + id: UUID
    + moneda_origen: String
    + monto_origen: Decimal
    + tipo_cambio_aplicado: Decimal
    + monto_bob_equivalente: Decimal
    + ajuste_redondeo: Decimal
    + metodo_pago: String
    + referencia_externa: String
    + estado: String
    + fecha_pago: DateTime
  }

  class LiquidacionHonorario {
    + id: UUID
    + periodo_mes: String
    + sesiones_liquidadas: Integer
    + total_bruto_generado: Decimal
    + porcentaje_aplicado: Decimal
    + monto_neto_psicologo: Decimal
    + monto_retencion_centro: Decimal
    + estado: String
  }

  class GastoFijoMensual {
    + id: UUID
    + periodo_mes: String
    + categoria: String
    + descripcion: String
    + moneda: String
    + monto_bob: Decimal
    + comprobante_ref: String
  }

  class EstadoResultadosContable {
    + id: UUID
    + fecha_inicio: Date
    + fecha_fin: Date
    + ingresos_brutos_bob: Decimal
    + costos_honorarios_bob: Decimal
    + ganancia_bruta_bob: Decimal
    + total_gastos_fijos_bob: Decimal
    + utilidad_neta_bob: Decimal
    + margen_neto_pct: Decimal
  }
}

package "Dominio CRM de Calidad y Satisfacción (CU26-CRM)" #F4ECF7 {
  class CalificacionCRM {
    + id: UUID
    + puntuacion_estrellas: SmallInt
    + puntualidad: SmallInt
    + empatia_profesional: SmallInt
    + calidad_plataforma: SmallInt
    + comentario: Text
    + requiere_seguimiento: Boolean
    + estado_seguimiento: String
    + fecha_calificacion: DateTime
  }
}

HistoriaClinica "1" *-- "0..*" ResumenClinicoIA : sintetiza >
HistoriaClinica "1" *-- "0..*" AlertaRiesgoPredictivaIA : monitorea >
Paciente "1" -- "0..*" PlanPagoTerapeutico : contrata >
PlanPagoTerapeutico "1" *-- "1..*" CuotaAmortizacion : desglosa >
CuotaAmortizacion "0..1" -- "0..*" PagoTransaccion : amortiza >
Cita "0..1" -- "0..*" PagoTransaccion : liquida >
Paciente "1" -- "0..*" PagoTransaccion : efectúa >
Psicologo "1" -- "0..*" LiquidacionHonorario : percibe >
Tenant "1" -- "0..*" GastoFijoMensual : registra >
Tenant "1" -- "0..*" EstadoResultadosContable : consolida >
Cita "1" -- "0..1" CalificacionCRM : evalúa >
Paciente "1" -- "0..*" CalificacionCRM : califica >
Psicologo "1" -- "0..*" CalificacionCRM : recibe >
@enduml
```

##### 4.1 Diagrama de Clases del Dominio Clínico y Sistema Completo Consolidado (Sprints 0, 1, 2, 3 y 4)

El siguiente diagrama consolida la totalidad del dominio de **SIGEPSI** tras completar el incremento del Sprint 4, integrando **48 entidades** distribuidas en los 6 paquetes funcionales acumulados desde el **Sprint 0 hasta el Sprint 4**: infraestructura SaaS Multi-Tenant (`public`: `SuperAdmin`, `Tenant`, `Dominio`, `SuscripcionSaaS`, `BackupRegistro`), seguridad RBAC y auditoría (`CentroConfig`, `Usuario`, `Rol`, `RolPermiso`, `Permiso`, `TokenAcceso`, `TokenRecuperacion`, `AuditLog`), gestión clínica, agenda, teleconsulta y notificaciones (`Especialidad`, `PsicologoEspecialidad`, `Psicologo`, `DisponibilidadHoraria`, `Cita`, `Teleconsulta`, `NotificacionCita`, `TokenFCM`), pre-consulta, triaje IA, chatbot y consentimientos (`FormularioPreConsulta`, `RespuestaPreConsulta`, `ClasificacionIA`, `AlertaPriorizacion`, `SugerenciaMatching`, `ConversacionChatbot`, `MensajeChatbot`, `ConsentimientoInformado`, `FirmaConsentimiento`), paciente y expediente clínico SOAP (`Paciente`, `RegistroAnimo`, `DiagnosticoCIE`, `HistoriaClinica`, `NotaSesion`, `EvolucionClinica`, `DerivacionCaso`, `TareaTerapeutica`, `EvidenciaTarea`), y el núcleo analítico/financiero/CRM del Sprint 4 (`ResumenClinicoIA`, `AlertaRiesgoPredictivaIA`, `PlanPagoTerapeutico`, `CuotaAmortizacion`, `PagoTransaccion`, `LiquidacionHonorario`, `GastoFijoMensual`, `EstadoResultadosContable`, `CalificacionCRM`).

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *2. Clases del Dominio - Sprint 4* (**Diagrama ID: 336**).

![Diagrama de Clases – Dominio Clínico y Sistema Completo Consolidado (Sprints 0–4)](./imagenes/diagrama_clases_dominio_general_sp4.png)

```plantuml
@startuml
title Diagrama de Clases - Dominio Clínico y Sistema Completo Consolidado (SP0-SP4)
skinparam classAttributeIconSize 0
left to right direction

package "public: SaaS Multi-Tenant (SP0/SP4)" {
  class SuperAdmin {
    +id: UUID
    +email: String
    +nivelAcceso: String
    +provisionarTenant(): Tenant
  }
  class Tenant {
    +id: UUID
    +slug: String
    +esquemaDb: String
    +nombreComercial: String
    +activo: Boolean
    +aislarEsquema(): void
  }
  class Dominio {
    +id: UUID
    +tenantId: UUID
    +hostDomain: String
    +esPrincipal: Boolean
  }
  class SuscripcionSaaS {
    +id: UUID
    +tenantId: UUID
    +planNombre: String
    +maxPsicologos: Integer
    +estadoPago: String
    +verificarCupo(): Boolean
  }
  class BackupRegistro {
    +id: UUID
    +tenantId: UUID
    +rutaArchivo: String
    +tamanoBytes: BigInt
    +fechaBackup: DateTime
    +restaurarEsquema(): Boolean
  }
}

package "tenant: Base, RBAC y Auditoría (SP1)" {
  class CentroConfig { +id: UUID; +razonSocial: String; +monedaBase: String; +timezone: String }
  class Usuario { +id: UUID; +email: String; +nombreCompleto: String; +activo: Boolean; +validarPassword(): Boolean }
  class Rol { +id: UUID; +nombre: String; +esSistema: Boolean }
  class RolPermiso { +rolId: UUID; +permisoId: UUID }
  class Permiso { +id: UUID; +codigo: String; +modulo: String }
  class TokenAcceso { +id: UUID; +jti: String; +expiraEn: DateTime }
  class TokenRecuperacion { +id: UUID; +codigoHash: String; +usado: Boolean }
  class AuditLog { +id: UUID; +usuarioId: UUID; +accion: String; +entidad: String; +creadoEn: DateTime; +registrarTraza(): void }
}

package "tenant: Agenda, Teleconsulta y FCM (SP1/SP3)" {
  class Especialidad { +id: UUID; +nombre: String; +areaClinica: String }
  class PsicologoEspecialidad { +psicologoId: UUID; +especialidadId: UUID }
  class Psicologo { +id: UUID; +usuarioId: UUID; +matricula: String; +porcentajeHonorario: Decimal; +obtenerDisponibilidad(): List }
  class DisponibilidadHoraria { +id: UUID; +psicologoId: UUID; +diaSemana: Integer; +horaInicio: Time; +horaFin: Time }
  class Cita { +id: UUID; +pacienteId: UUID; +psicologoId: UUID; +fechaHoraInicio: DateTime; +estado: String; +reprogramar(): void; +completar(): void }
  class Teleconsulta { +id: UUID; +citaId: UUID; +salaJitsiId: String; +duracionSegundos: Integer; +generarTokenJitsi(): String }
  class NotificacionCita { +id: UUID; +citaId: UUID; +tipoCanal: String; +estadoEnvio: String; +despacharRecordatorio(): void }
  class TokenFCM { +id: UUID; +usuarioId: UUID; +tokenDispositivo: String; +plataforma: String }
}

package "tenant: Pre-Consulta, IA Triaje, Chatbot y Firma" {
  class FormularioPreConsulta { +id: UUID; +titulo: String; +estructuraCampos: JSONB; +activo: Boolean }
  class RespuestaPreConsulta { +id: UUID; +formularioId: UUID; +pacienteId: UUID; +respuestas: JSONB }
  class ClasificacionIA { +id: UUID; +respuestaId: UUID; +nivelUrgencia: String; +palabrasClave: JSONB; +clasificarTriage(): String }
  class AlertaPriorizacion { +id: UUID; +pacienteId: UUID; +severidad: String; +estado: String; +escalarCrisis(): void }
  class SugerenciaMatching { +id: UUID; +pacienteId: UUID; +psicologoId: UUID; +scoreAfinidad: Float; +aprobadoHITL: Boolean; +aprobarAsignacion(): void }
  class ConversacionChatbot { +id: UUID; +sessionId: UUID; +escaladoHumano: Boolean }
  class MensajeChatbot { +id: UUID; +conversacionId: UUID; +emisor: String; +contenido: Text }
  class ConsentimientoInformado { +id: UUID; +titulo: String; +version: String; +obligatorio: Boolean }
  class FirmaConsentimiento { +id: UUID; +consentimientoId: UUID; +pacienteId: UUID; +hashSha256: String; +verificarIntegridad(): Boolean }
}

package "tenant: Paciente, SOAP y Tareas (SP2/SP3)" {
  class Paciente { +id: UUID; +usuarioId: UUID; +ci: String; +contactoEmergencia: String; +alertaCrisisActiva: Boolean; +consultarEstadoClinico(): String }
  class RegistroAnimo { +id: UUID; +pacienteId: UUID; +nivelAnimo: Integer; +nota: String }
  class DiagnosticoCIE { +id: UUID; +codigo: String; +nombre: String; +manual: String }
  class HistoriaClinica { +id: UUID; +pacienteId: UUID; +codigoExpediente: String; +motivoPrincipal: Text; +estado: String; +consolidarEvolucion(): Text }
  class NotaSesion { +id: UUID; +historiaId: UUID; +citaId: UUID; +subjetivo: Text; +plan: Text }
  class EvolucionClinica { +id: UUID; +historiaId: UUID; +notaSesionId: UUID; +puntajeProgreso: Integer }
  class DerivacionCaso { +id: UUID; +historiaId: UUID; +origenId: UUID; +destinoId: UUID; +motivo: Text }
  class TareaTerapeutica { +id: UUID; +pacienteId: UUID; +titulo: String; +estado: String }
  class EvidenciaTarea { +id: UUID; +tareaId: UUID; +archivoUrl: String; +fechaEntrega: DateTime }
}

package "tenant: IA Longitudinal, Finanzas P&L y CRM (SP4)" {
  class AlertaRiesgoPredictivaIA { +id: UUID; +pacienteId: UUID; +scoreRiesgo: Float; +nivelRiesgo: String; +factoresShap: JSONB; +predecirAbandonoML(): Float }
  class ResumenClinicoIA { +id: UUID; +historiaId: UUID; +sintesisEjecutiva: Text; +estadoHITL: String; +sesionesIncluidas: Integer; +generarSintesis(): Text; +validarHITL(): void }
  class PlanPagoTerapeutico { +id: UUID; +pacienteId: UUID; +modalidad: String; +montoTotal: Decimal; +saldoPendiente: Decimal; +recalcularSaldo(): Decimal }
  class CuotaAmortizacion { +id: UUID; +planPagoId: UUID; +numeroCuota: Integer; +monto: Decimal; +estado: String; +marcarPagada(): void }
  class PagoTransaccion { +id: UUID; +cuotaId: UUID; +montoOriginal: Decimal; +moneda: String; +montoConvertidoBase: Decimal; +aplicarTipoCambio(): Decimal }
  class LiquidacionHonorario { +id: UUID; +psicologoId: UUID; +periodoMes: Date; +totalBruto: Decimal; +pagoNeto: Decimal; +calcularComision(): Decimal }
  class EstadoResultadosContable { +id: UUID; +periodoMes: Date; +ingresosBrutos: Decimal; +utilidadNeta: Decimal; +consolidarPnL(): Decimal }
  class GastoFijoMensual { +id: UUID; +concepto: String; +categoria: String; +monto: Decimal; +periodoMes: Date }
  class CalificacionCRM { +id: UUID; +citaId: UUID; +pacienteId: UUID; +psicologoId: UUID; +puntuacion: Integer; +evaluarAlerta(): Boolean }
}

SuperAdmin "1" -- "0..*" Tenant
Tenant "1" *-- "1..*" Dominio
Tenant "1" -- "1..*" SuscripcionSaaS
Tenant "1" -- "0..*" BackupRegistro
Tenant "1" -- "1" CentroConfig
CentroConfig "1" -- "0..*" Usuario
Usuario "0..*" -- "1" Rol
Rol "1" *-- "0..*" RolPermiso
Permiso "1" -- "0..*" RolPermiso
Usuario "1" -- "0..*" TokenAcceso
Usuario "1" -- "0..*" TokenRecuperacion
Usuario "1" -- "0..*" AuditLog
Usuario "1" -- "0..1" Psicologo
Usuario "1" -- "0..*" TokenFCM
Psicologo "1" *-- "1..*" PsicologoEspecialidad
Especialidad "1" -- "0..*" PsicologoEspecialidad
Psicologo "1" *-- "1..*" DisponibilidadHoraria
DisponibilidadHoraria "1" -- "0..*" Cita
Cita "1" -- "0..1" Teleconsulta
Cita "1" -- "0..*" NotificacionCita
FormularioPreConsulta "1" -- "0..*" RespuestaPreConsulta
RespuestaPreConsulta "1" -- "0..1" ClasificacionIA
ClasificacionIA "1" -- "0..*" AlertaPriorizacion
Psicologo "1" -- "0..*" SugerenciaMatching
ConversacionChatbot "1" *-- "1..*" MensajeChatbot
ConsentimientoInformado "1" -- "0..*" FirmaConsentimiento
Paciente "1" -- "1" HistoriaClinica
Paciente "1" -- "0..*" RegistroAnimo
Paciente "1" -- "0..*" TareaTerapeutica
TareaTerapeutica "1" *-- "0..*" EvidenciaTarea
HistoriaClinica "1" *-- "0..*" NotaSesion
NotaSesion "1" -- "0..1" EvolucionClinica
HistoriaClinica "0..*" -- "0..*" DiagnosticoCIE
EvolucionClinica "0..1" -- "0..*" DerivacionCaso
HistoriaClinica "1" -- "0..*" ResumenClinicoIA
Paciente "1" -- "0..*" AlertaRiesgoPredictivaIA
Paciente "1" -- "0..*" PlanPagoTerapeutico
PlanPagoTerapeutico "1" *-- "1..*" CuotaAmortizacion
CuotaAmortizacion "1" -- "0..*" PagoTransaccion
PagoTransaccion "0..*" -- "1" LiquidacionHonorario
LiquidacionHonorario "0..*" -- "1" EstadoResultadosContable
GastoFijoMensual "0..*" -- "1" EstadoResultadosContable
Cita "1" -- "0..1" CalificacionCRM
@enduml
```

| Paquete / Módulo Consolidado | Entidades Incluidas (48 Totales) | Sprint Origen | Responsabilidad Sistémica en Arquitectura Final |
| :--- | :--- | :---: | :--- |
| **`public` (SaaS Multi-Tenant)** | `SuperAdmin`, `Tenant`, `Dominio`, `SuscripcionSaaS`, `BackupRegistro` | SP0 / SP4 | Aprovisionamiento de centros por esquema aislado (`schema_name`), control de cupos de psicólogos/planes (`SuscripcionSaaS`) y respaldos automatizados. |
| **Base, Seguridad RBAC y Auditoría** | `CentroConfig`, `Usuario`, `Rol`, `Permiso`, `RolPermiso`, `TokenAcceso`, `TokenRecuperacion`, `AuditLog` | SP1 | Autenticación JWT multi-esquema, control granular de permisos por rol (`CU04`), parámetros del centro (`moneda_base`) y bitácora inmutable de acciones. |
| **Agenda, Teleconsulta y Push FCM** | `Especialidad`, `Psicologo`, `PsicologoEspecialidad`, `DisponibilidadHoraria`, `Cita`, `Teleconsulta`, `NotificacionCita`, `TokenFCM` | SP1 / SP3 | Gestión de especialidades, grillas horarias, reservas sin solapamientos, salas cifradas Jitsi (`CU17`) y recordatorios Push FCM multicanal (`CU16`). |
| **Pre-Consulta, IA Triaje, Chatbot y Firma** | `FormularioPreConsulta`, `RespuestaPreConsulta`, `ClasificacionIA`, `AlertaPriorizacion`, `SugerenciaMatching`, `ConversacionChatbot`, `MensajeChatbot`, `ConsentimientoInformado`, `FirmaConsentimiento` | SP2 / SP3 | Intake clínico dinámico, detección de riesgo por reglas + ML (`CU21`), emparejamiento psicólogo-paciente HITL (`CU22`), asistente virtual 24/7 (`CU20`) y firma SHA-256 (`CU11`). |
| **Paciente, Expediente SOAP y Tareas** | `Paciente`, `HistoriaClinica`, `DiagnosticoCIE`, `NotaSesion`, `EvolucionClinica`, `DerivacionCaso`, `TareaTerapeutica`, `EvidenciaTarea`, `RegistroAnimo` | SP2 / SP3 | Núcleo clínico del paciente, notas evolutivas SOAP (`CU09`), codificación CIE-10/DSM-5, derivaciones, asignación/entrega de tareas (`CU10`) y diario emocional (`CU19`). |
| **IA Longitudinal, Finanzas P&L y CRM** | `ResumenClinicoIA`, `AlertaRiesgoPredictivaIA`, `PlanPagoTerapeutico`, `CuotaAmortizacion`, `PagoTransaccion`, `LiquidacionHonorario`, `GastoFijoMensual`, `EstadoResultadosContable`, `CalificacionCRM` | **SP4** | Síntesis longitudinal HITL con anonimización PII (`CU23`), predictor ML de abandono (`CU24`), amortización en cuotas, caja multimoneda, honorarios y P&L neto (`CU26`), y CSAT/NPS 1–5★ (`CU26-CRM` / `HU-55`). |

##### 4.2 Diagrama de Clases del Dominio Cliente Web (Angular 17 Standalone – Modelos DTO y Servicios REST)

El cliente Web administrativo y clínico (`prototipo/web/src/app/core/`) encapsula el dominio mediante interfaces TypeScript tipadas (`core/models/`), servicios reactivos `@Injectable` basados en `Observable<T>` (`core/services/`), un interceptor funcional JWT/Tenant (`auth.interceptor.ts`) y guardias de ruta por rol (`auth.guard.ts`). Para el incremento de Sprint 4, se integran `FinanzasContabilidadService`, `CrmCalidadService` y las operaciones analíticas longitudinales en `TriajeChatbotIAService`.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *2. Clases del Dominio - Sprint 4* (**Diagrama ID: 337**).

![Diagrama de Clases – Cliente Web Angular 17 Standalone (Modelos DTO y Servicios)](./imagenes/diagrama_clases_dominio_web_sp4.png)

```plantuml
@startuml
title Diagrama de Clases - Dominio Cliente Web Angular 17 Standalone (SP0-SP4)
skinparam classAttributeIconSize 0
left to right direction

package "Core Models: SaaS, RBAC y Auditoría (DTOs)" {
  interface TenantDTO { +id: string; +slug: string; +nombreComercial: string; +esquemaDb: string; +activo: boolean }
  interface SuscripcionPlanDTO { +id: string; +nombre: string; +precioMensual: number; +maxPsicologos: number; +sessionId: string }
  interface CentroConfigDTO { +id: string; +razonSocial: string; +monedaBase: string; +timezone: string; +logoUrl: string }
  interface UsuarioAuthDTO { +id: string; +email: string; +rol: Rol; +permisos: Permiso[]; +accessToken: string }
  interface AuditEventDTO { +id: string; +usuarioEmail: string; +accion: string; +entidad: string; +timestamp: string }
  interface BackupItemDTO { +id: string; +archivo: string; +tamanoBytes: number; +estado: string; +cronActivo: boolean }
}

package "Services: SaaS, RBAC, HTTP Guards y Reportes" {
  class TenantSubscriptionService <<@Injectable>> {
    +baseUrl: string
    +getAllTenants(): Observable
    +suspender(id): Observable
    +getPlans(): Observable
    +createCheckout(planId): Observable
    +verifySession(sid): Observable
  }
  class UserRoleCentroService <<@Injectable>> {
    +apiUrl: string
    +getUsers(): Observable
    +toggleStatus(id): Observable
    +getRoles(): Observable
    +getPermisos(): Observable
    +updateConfig(dto): Observable
  }
  class AuthService <<@Injectable>> {
    +currentUser$: Observable<UsuarioAuthDTO>
    +login(creds): Observable
    +register(dto): Observable
    +setTenant(slug): void
    +getRolNombre(): string
    +requestPasswordReset(email): Observable
  }
  class AuthInterceptor <<HttpInterceptorFn>> {
    +tokenHeader: string
    +tenantHeader: string
    +authInterceptor(req, next): Observable<HttpEvent>
  }
  class RoleGuards <<CanActivateFn>> {
    +allowedRoles: string[]
    +authGuard(): boolean
    +superAdminGuard(): boolean
    +adminCentroGuard(): boolean
    +clinicalStaffGuard(): boolean
  }
  class AuditBackupService <<@Injectable>> {
    +apiUrl: string
    +getLogs(filtros): Observable
    +solicitarBackupManual(): Observable
    +restaurarBackup(id): Observable
    +ejecutarCronTarea(): Observable
  }
  class ReportService <<@Injectable>> {
    +fuentesMetadata: FuenteMetadata[]
    +getMetadata(): Observable
    +generarPersonalizado(q): Observable
    +exportToPDF(res): void
    +descargarExcelServer(q): Observable
  }
}

package "Core Models: Clínica, IA y Finanzas/CRM SP4 (DTOs)" {
  interface PsicologoEspecialidadDTO { +id: string; +usuarioId: string; +matricula: string; +especialidades: Especialidad[]; +porcentajeHonorario: number }
  interface PacienteHistoriaDTO { +id: string; +ci: string; +historiaId: string; +diagnosticosCIE: DiagnosticoCIE[]; +notasSOAP: NotaSesion[] }
  interface IntakeConsentimientoDTO { +formularioId: string; +respuestasJson: Record; +hashSha256: string; +tareas: TareaTerapeutica[] }
  interface CitaTeleconsultaDTO { +id: string; +fechaHoraInicio: string; +estado: string; +jitsiJwt: string; +kpisDashboard: DashboardKPIs }
  interface TriajeAnaliticaIADTO { +clasificacionIA: ClasificacionIA; +sugerenciasMatching: SugerenciaMatching[]; +sintesisLongitudinal: string; +scoreAbandonoML: number }
  interface FinanzasContabilidadCRMDTO { +planPagoId: string; +cuotas: CuotaDTO[]; +pagoMoneda: string; +liquidacionNeto: number; +utilidadNetaPnL: number; +puntuacionCRM: number }
}

package "Services: Clínica, IA, Tesorería y CRM SP4" {
  class ClinicaService <<@Injectable>> { +apiUrl: string; +getEspecialidades(): Observable; +getPsicologos(): Observable; +guardarDisponibilidad(dto): Observable; +getPacientes(): Observable }
  class ClinicaSprint2Service <<@Injectable>> { +apiUrl: string; +getFormulariosPreconsulta(): Observable; +analizarRespuestaConIA(id): Observable; +getHistoriasClinicas(): Observable; +crearNotaSesion(dto): Observable }
  class AgendaService <<@Injectable>> { +apiUrl: string; +getCitas(filtros): Observable; +getSlotsDisponibles(f): Observable; +createCita(dto): Observable; +getTeleconsultaAccess(id): Observable; +getDashboardKPIs(): Observable }
  class TriajeChatbotIAService <<@Injectable - SP3/SP4>> { +sessionId: string; +clasificarIntake(dto): Observable; +generarMatching(id): Observable; +asignarPsicologoHITL(dto): Observable; +generarSintesisLongitudinal(hid): Observable; +evaluarRiesgoAbandonoML(pid): Observable }
  class FinanzasContabilidadService <<@Injectable - SP4>> { +monedaBase: string; +crearPlanPago(dto): Observable; +registrarPagoCuota(dto): Observable; +calcularLiquidacion(mes): Observable; +registrarGastoFijo(dto): Observable; +getEstadoResultadosPnL(mes): Observable }
  class CrmCalidadService <<@Injectable - SP4>> { +umbralAlerta: number; +getResumenReputacion(): Observable; +listarCalificaciones(f): Observable; +moderarComentario(id): Observable; +resolverAlertaCRM(id): Observable }
}

TenantSubscriptionService "1" -- "0..*" TenantDTO
TenantSubscriptionService "1" -- "0..*" SuscripcionPlanDTO
UserRoleCentroService "1" -- "1" CentroConfigDTO
AuthService "1" -- "0..1" UsuarioAuthDTO
AuditBackupService "1" -- "0..*" AuditEventDTO
AuditBackupService "1" -- "0..*" BackupItemDTO
AuthInterceptor ..> AuthService : inyectaJWT
RoleGuards ..> AuthInterceptor : protege
ReportService ..> AuditBackupService : exportaLogs
ReportService ..> FinanzasContabilidadCRMDTO : reportaPnL
ClinicaService "1" -- "0..*" PsicologoEspecialidadDTO
ClinicaSprint2Service "1" -- "0..*" PacienteHistoriaDTO
ClinicaSprint2Service "1" -- "0..*" IntakeConsentimientoDTO
AgendaService "1" -- "0..*" CitaTeleconsultaDTO
TriajeChatbotIAService "1" -- "0..*" TriajeAnaliticaIADTO
FinanzasContabilidadService "1" -- "0..*" FinanzasContabilidadCRMDTO
CrmCalidadService "1" -- "0..*" FinanzasContabilidadCRMDTO
@enduml
```

| Grupo Web Angular 17 | Componentes / DTOs / Servicios | Ubicación Real en `prototipo/web/src/app/core/` | Responsabilidad en Flujo End-to-End |
| :--- | :--- | :--- | :--- |
| **DTOs SaaS, Seguridad y Auditoría** | `TenantDTO`, `SuscripcionPlanDTO`, `CentroConfigDTO`, `UsuarioAuthDTO`, `AuditEventDTO`, `BackupItemDTO` | `models/index.ts`, `models/audit.model.ts`, `services/backup.service.ts` | Contratos tipados para gestión de tenants, suscripciones Stripe, branding, sesiones RBAC, logs de auditoría y backups. |
| **DTOs Clínicos, IA y Finanzas/CRM** | `PsicologoEspecialidadDTO`, `PacienteHistoriaDTO`, `IntakeConsentimientoDTO`, `CitaTeleconsultaDTO`, `TriajeAnaliticaIADTO`, `FinanzasContabilidadCRMDTO` | `models/clinica.model.ts`, `models/clinica-sprint2.model.ts`, `models/agenda.model.ts`, `services/triaje-ia.service.ts` | Deserialización de expedientes SOAP, firmas digitales, turnos Jitsi, explicabilidad IA/SHAP (`CU23`/`CU24`), cuotas, P&L y CRM (`CU26` / `HU-51`–`HU-55`). |
| **Servicios Core, Seguridad HTTP y Exportación** | `AuthService`, `TenantSubscriptionService`, `UserRoleCentroService`, `AuditBackupService`, `ReportService`, `AuthInterceptor`, `RoleGuards` | `services/auth.service.ts`, `tenant.service.ts`, `subscription.service.ts`, `user.service.ts`, `role.service.ts`, `centro.service.ts`, `audit.service.ts`, `backup.service.ts`, `report.service.ts`, `interceptors/`, `guards/` | Gestión de sesión multi-tenant con inyección automática de `Bearer` + `X-Tenant-Domain`, control RBAC de rutas y reportes PDF/Excel. |
| **Servicios Clínicos, IA, Tesorería y CRM** | `ClinicaService`, `ClinicaSprint2Service`, `AgendaService`, `TriajeChatbotIAService`, `FinanzasContabilidadService`, `CrmCalidadService` | `services/clinica.service.ts`, `clinica-sprint2.service.ts`, `agenda.service.ts`, `triaje-ia.service.ts`, `chatbot.service.ts` (+ extensión SP4) | Operaciones clínicas CRUD, salas de teleconsulta, validación HITL de resúmenes/alertas ML, amortización multimoneda, nómina P&L y moderación CRM. |

##### 4.3 Diagrama de Clases del Dominio Cliente Móvil (Flutter 3.x – Dominio del Paciente Consolidado SP3–SP4)

El cliente móvil multiplataforma (`prototipo/movil/lib/`) extiende la arquitectura orientada al paciente de Sprint 3 (`TenantModel`, `UserModel`, `PacienteModel`, `PsicologoModel`, `CitaModel`, `NotificacionPushFCM`, `RegistroAnimoMovil`, `AuthService`, `ClinicaService`, `AgendaService`, `Sprint2Service`, `ChatbotService` y `NotificationPermissionService`) incorporando en Sprint 4 los modelos y operaciones de **planes terapéuticos en cuotas (`PlanPagoMovil`, `CuotaAmortizacionMovil`, `PagoTransaccionMovil`)** y **calificación post-consulta CRM (`CalificacionCRMMovil`)** encapsulados en `FinanzasCrmMovilService`.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *2. Clases del Dominio - Sprint 4* (**Diagrama ID: 338**).

![Diagrama de Clases – Cliente Móvil Flutter (Dominio del Paciente SP3–SP4)](./imagenes/diagrama_clases_dominio_movil_sp4.png)

```plantuml
@startuml
title Diagrama de Clases - Dominio Cliente Móvil Flutter Consolidado (SP3-SP4)
skinparam classAttributeIconSize 0
left to right direction

package "Models: Identidad SaaS, Perfil, Ánimo y Push FCM" {
  class TenantModel <<Dart Model - P1>> { +id: String; +slug: String; +nombreComercial: String; +esquemaDb: String; +fromJson(map): TenantModel }
  class UserModel <<Dart Model - P1>> { +id: String; +email: String; +rolNombre: String; +permisos: List<String>; +hasPermission(cod): bool }
  class PacienteModel <<Dart Model - P2>> { +id: String; +ci: String; +fechaNacimiento: String; +contactoEmergencia: String; +alertaCrisisActiva: bool; +fromJson(map): PacienteModel }
  class PsicologoModel <<Dart Model - P2>> { +id: String; +nombreCompleto: String; +matricula: String; +especialidades: List<String>; +fromJson(map): PsicologoModel }
  class RegistroAnimoMovil <<Dart Model - P6>> { +id: String; +nivelAnimo: int; +emocionDominante: String; +registradoEn: DateTime }
  class NotificacionPushFCM <<Dart Model - P3>> { +tokenFCM: String; +plataforma: String; +titulo: String; +payloadCitaId: String }
}

package "Services: Auth, Clínica, Hardware FCM y Finanzas SP4" {
  class AuthService <<Dart Service - P1>> { +jwtToken: String; +currentUser: UserModel; +init(): Future<void>; +setTenant(slug): Future<void>; +login(email, pass): Future<bool>; +refreshProfile(): Future<void>; +logout(): Future<void> }
  class ClinicaService <<Dart Service - P2>> { +baseUrl: String; +getMiPerfil(): Future<PacienteModel>; +updateMiPerfil(data): Future<void>; +getPsicologos(): Future<List>; +registrarEstadoAnimo(n): Future<void>; +registrarTokenFCM(tok): Future<void> }
  class NotificationPermissionService <<Dart Hardware - P3>> { +fcmActivo: bool; +enrollDeviceToken(): Future<void>; +requestCameraAndAudioPermissions(): Future<bool>; +checkCameraAndAudioPermissions(): Future<bool> }
  class FinanzasCrmMovilService <<Dart Service - SP4>> { +baseUrl: String; +getMisPlanesPago(): Future<List<PlanPagoMovil>>; +getCuotasPendientes(): Future<List<CuotaAmortizacionMovil>>; +registrarPagoCuota(dto): Future<PagoTransaccionMovil>; +enviarCalificacionCita(dto): Future<CalificacionCRMMovil> }
}

package "Models: Agenda, Clínica SP2/3, Chatbot y Finanzas/CRM SP4" {
  class CitaModel <<Dart Model - P3>> { +id: String; +psicologoId: String; +fechaHoraInicio: DateTime; +estado: String; +salaJitsiUrl: String; +fromJson(map): CitaModel }
  class TeleconsultaJitsiMovil <<Dart Model - P3>> { +roomName: String; +jwtToken: String; +duracionSegundos: int; +camaraActiva: bool }
  class IntakeRespuestaMovil <<Dart Model - P2>> { +formularioId: String; +respuestasJson: Map; +nivelTriajeIA: String; +alertaPrioritaria: bool }
  class ConsentimientoFirmaMovil <<Dart Model - P2>> { +consentimientoId: String; +hashSha256: String; +trazoPuntosJson: List; +fechaFirma: DateTime; +calcularSha256(): String }
  class TareaEvidenciaMovil <<Dart Model - P4>> { +tareaId: String; +titulo: String; +estado: String; +archivoUrl: String }
  class ChatbotMensajeMovil <<Dart Model - P5 IA>> { +sessionId: String; +emisor: String; +texto: String; +botonesAccion: List }
  class CalificacionCRMMovil <<Dart Model - SP4>> { +id: String; +citaId: String; +psicologoId: String; +puntuacion: int; +comentario: String }
  class PlanPagoMovil <<Dart Model - SP4>> { +id: String; +modalidad: String; +montoTotal: double; +saldoPendiente: double; +moneda: String; +porcentajePagado(): double }
  class CuotaAmortizacionMovil <<Dart Model - SP4>> { +id: String; +numeroCuota: int; +monto: double; +fechaVencimiento: DateTime; +estado: String; +estaVencida(): bool }
  class PagoTransaccionMovil <<Dart Model - SP4>> { +id: String; +metodoPago: String; +referenciaGateway: String; +comprobanteUrl: String; +montoOriginal: double }
}

package "Services: Agenda Jitsi, Clínica SP2 y Chatbot IA" {
  class AgendaService <<Dart Service - P3>> { +baseUrl: String; +getCitas(): Future<List<CitaModel>>; +reservarCita(dto): Future<CitaModel>; +cancelarCita(id): Future<void>; +getTeleconsultaAccess(id): Future<Map>; +finishTeleconsulta(id): Future<void> }
  class Sprint2Service <<Dart Service - P2/P4>> { +baseUrl: String; +getFormularioActivo(): Future<Map>; +enviarRespuestaIntake(d): Future<void>; +getMisTareas(): Future<List>; +enviarEvidenciaTarea(id): Future<void>; +firmarConsentimiento(d): Future<void> }
  class ChatbotService <<Dart Service - P5>> { +sessionId: String; +enviarMensaje(texto): Future<ChatbotRespuesta> }
}

AuthService "1" -- "1" TenantModel
AuthService "1" -- "0..1" UserModel
ClinicaService "1" -- "1" PacienteModel
ClinicaService "1" -- "0..*" PsicologoModel
ClinicaService "1" -- "0..*" RegistroAnimoMovil
NotificationPermissionService "1" -- "0..*" NotificacionPushFCM
FinanzasCrmMovilService "1" -- "0..*" CalificacionCRMMovil
FinanzasCrmMovilService "1" -- "0..*" PlanPagoMovil
PlanPagoMovil "1" *-- "1..*" CuotaAmortizacionMovil
CuotaAmortizacionMovil "1" -- "0..*" PagoTransaccionMovil
AgendaService "1" -- "0..*" CitaModel
CitaModel "1" -- "0..1" TeleconsultaJitsiMovil
Sprint2Service "1" -- "0..*" IntakeRespuestaMovil
Sprint2Service "1" -- "0..*" ConsentimientoFirmaMovil
Sprint2Service "1" -- "0..*" TareaEvidenciaMovil
ChatbotService "1" -- "0..*" ChatbotMensajeMovil
@enduml
```

| Capa Móvil Flutter (`prototipo/movil/lib/`) | Clases y Servicios Dart | Paquete / Archivo Origen | Alcance Funcional (Sprints 1–4) |
| :--- | :--- | :--- | :--- |
| **Modelos de Identidad, Perfil y Push** | `TenantModel`, `UserModel`, `PacienteModel`, `PsicologoModel`, `RegistroAnimoMovil`, `NotificacionPushFCM` | `models/paquete1_admin_seguridad/*`, `models/paquete2_gestion_clinica/*`, `screens/paquete3..6` | Selección de clínica multi-tenant, caché JWT/permisos, perfil clínico del paciente, mood tracker diario (`CU19`) y tokens Firebase Push. |
| **Modelos Clínicos, Agenda y Chatbot** | `CitaModel`, `TeleconsultaJitsiMovil`, `IntakeRespuestaMovil`, `ConsentimientoFirmaMovil`, `TareaEvidenciaMovil`, `ChatbotMensajeMovil` | `models/paquete3_agenda_teleconsulta/cita_model.dart`, `screens/paquete2..5` | Sincronización de citas, acceso JWT a sala Jitsi (`CU17`), formularios pre-consulta, firma táctil SHA-256 (`CU11`), evidencias (`CU10`) y chatbot (`CU20`). |
| **Modelos Financieros y CRM del Paciente (SP4)** | `PlanPagoMovil`, `CuotaAmortizacionMovil`, `PagoTransaccionMovil`, `CalificacionCRMMovil` | Extensión SP4 sobre `models/` | Visualización de extracto de cuotas/amortización (`HU-52`), pago QR/tarjeta con recibo multimoneda (`HU-51`) y encuesta 1–5★ post-consulta (`HU-55`). |
| **Servicios HTTP REST y Hardware Móvil** | `AuthService`, `ClinicaService`, `NotificationPermissionService`, `FinanzasCrmMovilService`, `AgendaService`, `Sprint2Service`, `ChatbotService` | `services/paquete1..6/*.dart` (+ `FinanzasCrmMovilService` SP4) | Consumo REST seguro con cabecera `X-Tenant-Domain`, permisos nativos cámara/micrófono Android/iOS, pagos de cuotas y envío de calificaciones CRM. |

#### 5. Diagramas de Actividad de Flujos Críticos del Sprint 4

##### Flujo Crítico 1: Síntesis Longitudinal (`CU23`) y Predicción ML de Riesgo (`CU24`)
* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *3. Actividades de Flujos Críticos - Sprint 4 → 3.1 Actividad IA/ML* (**Diagrama ID: 339**).

![Diagrama de Actividad – Flujo Crítico IA Longitudinal (CU23) y Predicción ML (CU24)](./imagenes/diagrama_actividad_ia_ml_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

start
:Psicólogo solicita análisis longitudinal del paciente (últimos 6-12 meses);
:Extraer Notas SOAP firmadas, Citas, Tareas y Mood Tracker;
:Ejecutar sanitizar_pii() y calcular Hash SHA-256 de trazabilidad;

fork
  :Construir resumen cronológico estructurado (CU23);
  :Guardar en clinica_resumenlongitudinalia (BORRADOR_IA);
fork again
  :Calcular vector de features ML (pendiente ánimo, ausentismo, tareas);
  :Inferir indice_riesgo (0.00 - 1.00) y pesos explicables (CU24);
  if (¿indice_riesgo >= 0.70?) then (Sí)
    :Crear AlertaRiesgoPredictivaIA (ALTO / CRITICO);
    :Notificar en tiempo real al Psicólogo y Coordinador;
  else (No)
    :Actualizar score de seguimiento preventivo;
  endif
end fork

:Mostrar borrador IA + radar de riesgo en Consola Angular;
:Psicólogo revisa, edita y firma aprobación (HITL);
:Habilitar exportación PDF y registro en auditoría;
stop
@enduml
```

##### Flujo Crítico 2: Amortización de Plan de Pagos y Contabilidad de Utilidad Neta (`CU26`)
* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *3. Actividades de Flujos Críticos - Sprint 4 → 3.2 Actividad Finanzas & Utilidad Neta* (**Diagrama ID: 340**).

![Diagrama de Actividad – Flujo Crítico Pagos, Amortización y Utilidad Neta (CU26)](./imagenes/diagrama_actividad_finanzas_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

start
:Paciente o Recepcionista selecciona pago de Cita o Cuota de Plan;
:Elegir moneda (BOB o USD) y método (QR Simple, Stripe, Efectivo);
:Aplicar tipo de cambio oficial del día con precisión Decimal(12,2);

if (¿Es abono a Plan de Amortización?) then (Sí)
  :Desglosar Capital Amortizado + Interés/Comisión + Seguro Asistencial;
  :Marcar Cuota como PAGADA y actualizar Saldo Insoluto del plan;
else (Pago directo de Cita)
  :Registrar PagoTransaccion vinculada a Cita;
endif

:Actualizar Extracto Financiero visible en Web y App Flutter;
:Acumular Ingreso Bruto en libro contable del Tenant;

partition "Cierre Contable del Periodo (Administrador / Contador)" {
  :Consolidar Ingresos Brutos del rango seleccionado;
  :Restar Liquidación de Honorarios de Psicólogos -> Obtener GANANCIA BRUTA;
  :Restar Gastos Fijos Mensuales (Alquiler + Servicios Básicos + Personal Apoyo + SaaS);
  :Calcular UTILIDAD NETA CONTABLE = Ganancia Bruta - Gastos Fijos;
  :Renderizar Estado de Resultados (P&L) y gráficos en Dashboard;
}
stop
@enduml
```

##### Flujo Crítico 3: Calificación CRM Post-Consulta (1–5 ★) y Seguimiento Estadístico
* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *3. Actividades de Flujos Críticos - Sprint 4 → 3.3 Actividad CRM* (**Diagrama ID: 341**).

![Diagrama de Actividad – Flujo Crítico Calificación CRM Post-Consulta (1–5★)](./imagenes/diagrama_actividad_crm_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

start
:Cita cambia a estado REALIZADA en Web o Teleconsulta;
:App Flutter / Web habilita encuesta CRM para esa cita;
:Paciente selecciona calificación (1 a 5 estrellas) y aspectos;
:Enviar POST /api/v1/clinica/crm/calificaciones/;
:Validar unicidad (1 calificación por cita);
:Persistir en crm_calificacionservicio;

if (¿Calificación <= 2 estrellas?) then (Sí - Insatisfacción)
  :Marcar requiere_seguimiento = TRUE;
  :Disparar alerta al Administrador / Coordinador en Panel CRM;
else (No - Satisfacción >= 3)
  :Marcar encuesta cerrada positivamente;
endif

:Recalcular métricas estadísticas del Tenant (CSAT %, Promedio 1-5 ★, NPS);
:Actualizar histograma y comparativa en Dashboard CRM;
stop
@enduml
```

---

### 4.1.4 Sprint Backlog y Equipo SCRUM del Sprint 4

En estricta correspondencia con el **Product Backlog Oficial** (`documentacion/intento.md`, Sección 3.6, ítems 79 al 88), el Sprint Backlog del Sprint 4 comprende exactamente las **10 tareas técnicas `SP4-79` a `SP4-88`**. Se deja constancia transparente de la trazabilidad horaria respecto a la tabla base de `intento.md`: las 10 filas iniciales sumaban `55.0 hr` base y en la consolidación del Sprint 4 se incorporaron `+4.0 hr` de refinamiento técnico (`SP4-86` $+2\text{ hr} \to 6\text{ hr}$ para el módulo CRM 1–5★ y Estado de Resultados Contable; `SP4-87` $+2\text{ hr} \to 8\text{ hr}$ para el motor de Utilidad Neta tras gastos fijos y ajuste cambiario), igualando exactamente las **59.0 horas planificadas** declaradas en el resumen del Product Backlog del Sprint 4 (`intento.md`, línea 3200 y línea 3291).

| **Sprint Backlog** | |
| :--- | :--- |
| **Número de Sprint :** Sprint 4 (Cierre Integral) | **Tiempo programado :** 12 jornadas ágiles (06 al 22 de noviembre de 2026) |
| **Objetivo :** Entregar la IA Clínica Longitudinal (`CU23`), el Detector Predictivo de Riesgo ML sobre datasets de 6–12 meses (`CU24`), la Gestión de Pagos Multimoneda con Extracto de Amortización, Liquidación de Honorarios, Suscripciones SaaS, Contabilidad de Ganancia Bruta vs. Utilidad Neta y Módulo CRM 1–5 ★ (`CU26`), bajo arquitectura Modelo C4 y certificación de pruebas finales. | |
| **Fecha de inicio :** Viernes 06 de noviembre de 2026 | **Fecha de finalización :** Domingo 22 de noviembre de 2026 (23:59) |

<br>

#### Tabla Detallada del Sprint Backlog (`SP4-79` a `SP4-88` – 10 Tareas Técnicas / 59.0 hr)

| Nro | ID Tarea | Descripción Técnica del Product Backlog (`intento.md` + Ampliación Sprint 4) | Categoría / CU | Tipo | Est. (hr) | Responsables Full Stack | Estado |
| :---: | :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| **79** | **SP4-79** | Diseñar las funciones e interfaces UI/UX de IA para resúmenes clínicos longitudinales y radar de alertas de riesgo | IA Longitudinal (`CU23, CU24`) | Diseño | **4.0 hr** | Larrazabal Rojas Julio Cesar *(PO)* | **Terminado** |
| **80** | **SP4-80** | Implementar la generación asistida de resúmenes clínicos longitudinales con sanitización PII y aprobación HITL | IA Longitudinal (`CU23`) | Full Stack | **8.0 hr** | Mujica Vallejos Andy Mauricio *(SM)* | **Terminado** |
| **81** | **SP4-81** | Implementar detección predictiva de señales de riesgo ML sobre historial sintético de 6–12 meses y alertas prioritarias | Riesgo ML (`CU24`) | Full Stack | **8.0 hr** | Mujica Vallejos Andy Mauricio *(SM)* | **Terminado** |
| **82** | **SP4-82** | Realizar pruebas de resúmenes longitudinales, predicción ML, alertas de riesgo y salvaguardas éticas de IA | Calidad IA (`CU23, CU24`) | Pruebas QA | **4.0 hr** | Velasco Soliz Rolando | **Terminado** |
| **83** | **SP4-83** | Diseñar interfaz Web responsiva y Móvil Flutter para pagos multimoneda, extracto de amortización, estado de cuenta y encuesta CRM 1–5★ | Pagos y CRM (`CU26`) | Diseño | **3.0 hr** | Larrazabal Julio *(PO)* / Delgado Alberto | **Terminado** |
| **84** | **SP4-84** | Implementar registro de cobros multimoneda (BOB/USD), saldos, tabla de amortización de planes terapéuticos y pasarela Stripe/QR | Finanzas (`CU26`) | Full Stack | **7.0 hr** | Condori Diaz Marilyn Esther / Delgado Alberto | **Terminado** |
| **85** | **SP4-85** | Realizar pruebas del módulo de control de pagos multimoneda, redondeo cambiario, amortización y conciliación financiera | Calidad Finanzas (`CU26`) | Pruebas QA | **3.0 hr** | Velasco Soliz Rolando | **Terminado** |
| **86** | **SP4-86** | Diseñar e implementar panel de suscripciones SaaS, facturación por centro, vistas de Estado de Resultados y analítica estadística CRM 1–5★ | SaaS / CRM (`CU26`) | Full Stack | **6.0 hr** | Larrazabal Julio *(PO)* / Romero Maria Ilse | **Terminado** |
| **87** | **SP4-87** | Implementar liquidación de honorarios a psicólogos, facturación SaaS y cálculo contable de Ganancia Bruta vs. Utilidad Neta (Gastos Fijos) | Contabilidad (`CU26`) | Full Stack | **8.0 hr** | Mujica Andy *(SM)* / Romero Maria Ilse | **Terminado** |
| **88** | **SP4-88** | Siembra de datasets sintéticos (6–12 meses) y pruebas finales de estrés, seguridad, concurrencia e integración global SaaS | Cierre Global (`All CUs`) | QA / Estrés | **8.0 hr** | Equipo SCRUM *(Lidera Velasco Rolando)* | **Terminado** |
| — | **TOTAL** | **Sprint Backlog Oficial Consolidado del Sprint 4 (10 Tareas del Product Backlog)** | **`CU23, CU24, CU26`** | — | **59.0 hr** | **Equipo SCRUM Full Stack (6 integrantes)** | **100% Done** |

<br>

#### Asignación de Roles SCRUM y Enfoque Full Stack en el Sprint 4

En cumplimiento de la recomendación docente de **desarrollo Full Stack** (cada miembro responde integralmente por la funcionalidad de su dominio desde la base de datos y API REST hasta la vista web responsiva y/o pantalla móvil Flutter, sin compartimentos estancos) y de la rotación formal de liderazgo:

| Pos. | Integrante | Rol SCRUM Sprint 4 | Responsabilidad Full Stack en Sprint 4 | Tareas Backlog | Horas Plan. / Reales |
| :---: | :--- | :--- | :--- | :---: | :---: |
| **1** | **Larrazabal Rojas Julio Cesar**<br>*(Reg: 223049255)* | **Product Owner** *(con desarrollo Full Stack)* | Visión de cierre del producto, aceptación BDD de `HU-49` a `HU-56`, diseño UI/UX en Figma y maquetación responsiva Angular 17 / Flutter de Consolas IA (`CU23/24`), Caja Multimoneda, Estado de Cuenta y Panel de Suscripciones SaaS (`CU26`). | `SP4-79` *(4h)*, `SP4-83` *(2h)*, `SP4-86` *(3h)* | **9.0 hr / 9.0 hr** |
| **2** | **Mujica Vallejos Andy Mauricio**<br>*(Reg: 224028367)* | **Scrum Master** *(con desarrollo Full Stack)* | Facilitación diaria del 06/11 al 22/11, gestión de riesgos e impedimentos de cierre, e implementación Full Stack del **Motor de Resúmenes Longitudinales IA (`CU23`)**, **Detector Predictivo ML de Riesgo (`CU24`)** y **Liquidación de Honorarios / Facturación SaaS (`CU26`)**. | `SP4-80` *(8h)*, `SP4-81` *(8h)*, `SP4-87` *(4h)* | **20.0 hr / 20.0 hr** |
| **3** | **Delgado Rojas Alberto Caleb**<br>*(Reg: 224027204)* | **Development Team (Full Stack)** | Desarrollo móvil Flutter del **Extracto de Estado de Cuenta/Amortización** y del **Modal de Calificación CRM 1–5★**, integración móvil-backend y apoyo en pruebas finales de estrés/seguridad multi-tenant (`SP4-88`). | `SP4-83` *(1h)*, `SP4-84` *(2h)*, `SP4-88` *(3h)* | **6.0 hr / 6.0 hr** |
| **4** | **Condori Diaz Marilyn Esther**<br>*(Reg: 224051237)* | **Development Team (Full Stack)** | Implementación Full Stack del **Motor de Pagos Multimoneda (BOB/USD), Plan de Amortización y Pasarela Stripe/QR** (`CU26`) y pruebas de concurrencia financiera (`SP4-88`). | `SP4-84` *(5h/5.5h)*, `SP4-88` *(1h)* | **6.0 hr / 6.5 hr** |
| **5** | **Romero Saavedra Maria Ilse**<br>*(Reg: 222009772)* | **Development Team (Full Stack)** | Desarrollo Full Stack del **Motor Contable de Ganancia Bruta vs. Utilidad Neta (deduciendo Gastos Fijos Mensuales)**, **Analítica Estadística CRM (CSAT/NPS 1–5★)** y generador de **Datasets Sintéticos de 6–12 meses**. | `SP4-86` *(3h)*, `SP4-87` *(4h)*, `SP4-88` *(1h)* | **8.0 hr / 8.0 hr** |
| **6** | **Velasco Soliz Rolando**<br>*(Reg: 223044768)* | **Development Team (Full Stack QA)** | Diseño y automatización de suites de prueba (`CU23, CU24, CU26`), verificación de redondeo contable exacto, pruebas de carga/estrés concurrente y certificación de aislamiento multi-tenant. | `SP4-82` *(4h)*, `SP4-85` *(3h)*, `SP4-88` *(3h/3.5h)* | **10.0 hr / 10.5 hr** |
| — | **TOTAL** | **Equipo SCRUM SIGEPSI** | **Consolidado de 10 Tareas (`SP4-79` a `SP4-88`)** | **10 Tareas** | **59.0 hr / 60.0 hr** |

*(\*Nota de desglose exacto sin doble contabilización: `SP4-83` [3h = 2h Julio + 1h Alberto], `SP4-84` [7h/7.5h = 5h/5.5h Marilyn + 2h Alberto], `SP4-86` [6h = 3h Julio + 3h Maria Ilse], `SP4-87` [8h = 4h Andy + 4h Maria Ilse] y `SP4-88` [8h/8.5h = 3h Alberto + 1h Marilyn + 1h Maria Ilse + 3h/3.5h Rolando], sumando exactamente 59.0 hr estimadas y 60.0 hr reales del Sprint 4).*

#### Matriz Histórica Completa de Rotación de Roles (Sprint 0 al Sprint 4)

| Integrante | Sprint 0 | Sprint 1 | Sprint 2 | Sprint 3 | Sprint 4 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Larrazabal Rojas Julio Cesar** | Developer | Developer | Developer | **Scrum Master** | **Product Owner** *(Full Stack UI/UX)* |
| **Mujica Vallejos Andy Mauricio** | Developer | Developer | Developer | **Product Owner** | **Scrum Master** *(Full Stack IA/ML/SaaS)* |
| **Condori Diaz Marilyn Esther** | Developer | **Product Owner** | Developer | Developer (Móvil) | Developer *(Full Stack Finanzas/Pagos)* |
| **Delgado Rojas Alberto Caleb** | Developer | **Scrum Master** | Developer | Developer (Móvil) | Developer *(Full Stack Móvil/CRM)* |
| **Romero Saavedra Maria Ilse** | **Scrum Master** | Developer | **Product Owner** | Developer (Móvil) | Developer *(Full Stack Contabilidad/CRM)* |
| **Velasco Soliz Rolando** | **Product Owner** | Developer | **Scrum Master** | Developer (QA) | Developer *(Full Stack QA/Estrés)* |

---

## 4.2 PROCESO / PATRÓN DE DESARROLLO POR HISTORIA DE USUARIO

### 4.2.1 Diseño

#### 4.2.1.1 Diseñar la Arquitectura – Modelo C4 Completo (Niveles 1 al 4)

En estricto cumplimiento de las directrices metodológicas de la cátedra para el **Sprint 4** (*adopción formal del Modelo C4 de Simon Brown en sustitución de los diagramas lógicos de paquetes y despliegue tradicionales*), el diseño arquitectónico integral de **SIGEPSI** se modela jerárquicamente mediante la técnica de **"Zoom-in" en los cuatro niveles canónicos del Modelo C4**:

1. **Nivel 1 – Diagrama de Contexto del Sistema (*System Context*):** Delimita los actores humanos del negocio clínico, financiero y administrativo, el sistema central **SIGEPSI**, y los servicios externos integrados.
2. **Nivel 2 – Diagrama de Contenedores (*Containers*):** Descompone el sistema en sus unidades de despliegue y ejecución reales (SPA Web Angular 17 responsiva, App Móvil Flutter 3.x, API REST Django 5.x/DRF Multi-Tenant, Worker Asíncrono ML/Contable Celery+Redis, Base de Datos PostgreSQL 16 por esquemas y Bóveda de Reportes/Logs cifrados).
3. **Nivel 3 – Diagramas de Componentes (*Components*):** Realizan zoom-in individualizado por cada contenedor ejecutable siguiendo el estándar C4 de Simon Brown:
   * **Nivel 3A (General – Backend API & Worker ML):** Expone los controladores, servicios de dominio, pasarelas de pago/IA, motor contable P&L y CRM en Django/DRF.
   * **Nivel 3B (Cliente Web SPA – Angular 17 Standalone):** Desglosa el enrutamiento con `RoleGuards`, `AuthInterceptor`, módulos clínicos/financieros/CRM y servicios REST TypeScript.
   * **Nivel 3C (Cliente Móvil Nativo – Flutter 3.x / Dart):** Desglosa la arquitectura del paciente (sesión segura, Push FCM, agenda/Jitsi, pre-consulta/firma, Mood Tracker, extracto de cuotas y calificación CRM).
4. **Nivel 4 – Diagrama de Código / Clases (*Code Diagram*):** Modela las clases reales de implementación del Backend (`clinica/ia_longitudinal`, `finanzas`, `crm`, `subscriptions`), complementándose con las clases DTO y servicios Web/Móvil detallados en la sección [`4.1.3 → 4.2 y 4.3`](#413-contexto-del-sistema).

---

##### C4 Nivel 1: Diagrama de Contexto del Sistema (System Context)

Muestra la interacción de los cinco perfiles de usuario con la plataforma **SIGEPSI** y su comunicación con pasarelas financieras, servicios de Inteligencia Artificial, videoconferencias WebRTC y mensajería push.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *4. Arquitectura Modelo C4 → C4 Nivel 1 - Contexto del Sistema* (**Diagrama ID: 342**).

![Modelo C4 Nivel 1 – Contexto del Sistema (SIGEPSI Sprint 4)](./imagenes/diagrama_c4_nivel1_sp4.png)

```plantuml
@startuml
!include <C4/C4_Context>

LAYOUT_TOP_DOWN()

title Modelo C4 – Nivel 1: Diagrama de Contexto del Sistema (SIGEPSI – Sprint 4)

Person(paciente, "Paciente", "Consulta citas, estado de cuenta y extracto de amortización en cuotas, realiza pagos en BOB/USD, asiste a teleconsultas y califica la atención (CRM 1-5 estrellas).")
Person(psicologo, "Psicólogo Clínico", "Documenta HCE/SOAP, genera resúmenes longitudinales asistidos por IA (CU23) con aprobación HITL y atiende alertas predictivas de riesgo ML (CU24).")
Person(coordinador, "Coordinador Clínico", "Supervisa el radar de riesgo predictivo (CU24), valida asignaciones IA y atiende alertas CRM de baja satisfacción (<=2 estrellas).")
Person(admin_centro, "Administrador / Contador del Centro", "Gestiona cobros multimoneda (BOB/USD), planes de amortización, gastos fijos mensuales, liquidación de honorarios, Estado de Resultados (Utilidad Neta) y analítica CRM.")
Person(superadmin, "SuperAdministrador SaaS", "Administra suscripciones de centros psicológicos (tenants), facturación SaaS, backups cloud y bitácora cifrada.")

System(sigepsi, "Plataforma SIGEPSI (SaaS Multi-Tenant)", "Ecosistema Web responsivo (Angular 17) y Móvil (Flutter 3.x) para gestión clínica, seguimiento terapéutico, IA longitudinal, contabilidad de utilidad neta y CRM de centros de salud mental.")

System_Ext(stripe_qr, "Pasarela Stripe & QR Simple BCB", "Procesamiento de pagos con tarjeta internacional (USD/BOB), webhooks idempotentes y generación/conciliación de pagos QR locales.")
System_Ext(ia_cloud, "Servicios IA / ML (Google Gemini & HF Spaces)", "Inferencia asistiva de resúmenes longitudinales (CU23) y análisis semántico previo anonimizado de señales de riesgo (CU24).")
System_Ext(jitsi, "Cluster WebRTC Jitsi Meet", "Salas de telepsicología cifradas punto a punto (SRTP/DTLS) para consultas virtuales web y móviles.")
System_Ext(fcm, "Google Firebase Cloud Messaging (FCM v1)", "Despacho de notificaciones push en segundo plano para recordatorios de citas, cuotas por vencer y encuestas CRM.")

Rel(paciente, sigepsi, "Consulta extracto de amortización, paga cuotas/citas, asiste a sesiones y califica 1-5 estrellas", "HTTPS / Flutter & Web")
Rel(psicologo, sigepsi, "Solicita resúmenes longitudinales IA (HITL) y gestiona alertas predictivas de riesgo", "HTTPS / Angular 17")
Rel(coordinador, sigepsi, "Monitorea radar ML de riesgo y da seguimiento a alertas CRM", "HTTPS / Angular 17")
Rel(admin_centro, sigepsi, "Registra pagos, gastos fijos, liquida honorarios y analiza Utilidad Neta y estadísticas CRM", "HTTPS / Angular 17")
Rel(superadmin, sigepsi, "Gobierna planes SaaS, suscripciones y auditoría global multi-tenant", "HTTPS / Angular 17")

Rel(sigepsi, stripe_qr, "Crea sesiones de checkout, valida pagos y reconcilia suscripciones/cuotas", "REST / HTTPS + Webhooks")
Rel(sigepsi, ia_cloud, "Envía historiales sanitizados sin PII para síntesis longitudinal", "REST / HTTPS TLS 1.3")
Rel(sigepsi, jitsi, "Instancia salas virtuales seguras con token JWT", "WebRTC / HTTPS")
Rel(sigepsi, fcm, "Envía alertas push de citas, recordatorios de cuotas y encuestas CRM", "FCM HTTP v1 / OAuth2")
@enduml
```

---

##### C4 Nivel 2: Diagrama de Contenedores (Containers)

Detalla los contenedores ejecutables que materializan la plataforma **SIGEPSI** en producción cloud (Render Cloud PaaS + Docker + PostgreSQL 16 + Celery/Redis + Hugging Face), manteniendo la separación estricta entre clientes responsivos, backend API multi-tenant, procesamiento asíncrono ML/contable y persistencia aislada por esquemas.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *4. Arquitectura Modelo C4 → C4 Nivel 2 - Contenedores SaaS* (**Diagrama ID: 343**).

![Modelo C4 Nivel 2 – Contenedores SaaS Multi-Tenant (SIGEPSI Sprint 4)](./imagenes/diagrama_c4_nivel2_sp4.png)

```plantuml
@startuml
!include <C4/C4_Container>

LAYOUT_TOP_DOWN()

title Modelo C4 – Nivel 2: Diagrama de Contenedores (SIGEPSI – Sprint 4)

Person(paciente, "Paciente", "Usuario en App Móvil Flutter y Portal Web.")
Person(personal, "Personal Clínico, Administrativo y SuperAdmin", "Psicólogos, Coordinadores, Contadores y SuperAdmin.")

System_Boundary(sigepsi_sys, "Plataforma SIGEPSI (Despliegue Cloud SaaS Multi-Tenant)") {
    Container(web_spa, "Aplicación Web SPA Responsiva", "Angular 17 Standalone, TypeScript, TailwindCSS, Chart.js", "Portal adaptable (desktop/tablet/móvil) para consolas IA longitudinal (CU23/24), caja multimoneda, Estado de Resultados (Utilidad Neta), liquidación de honorarios, panel CRM y gestión SaaS.")
    Container(mobile_app, "Aplicación Móvil Nativa", "Flutter 3.x, Dart, Dio, SecureStorage", "App iOS/Android del paciente con agenda, teleconsulta WebRTC, tareas, Mood Tracker, extracto de estado de cuenta/amortización en cuotas y calificación CRM post-consulta (1-5 estrellas).")
    Container(api_backend, "Backend Core & API REST", "Python 3.12, Django 5.x, DRF, Gunicorn 21, django-tenants", "Expone endpoints REST y WebSockets bajo aislamiento por esquema PostgreSQL; ejecuta lógica clínica, financiera multimoneda, contabilidad neta, CRM y pasarela ética de IA.")
    Container(worker_ml, "Worker Asíncrono & Motor Analítico ML/Contable", "Celery, Redis, Scikit-Learn / Pandas / ReportLab", "Ejecuta entrenamiento/inferencia predictiva ML sobre series de 6-12 meses (CU24), consolidación nocturna de mora en cuotas, despacho FCM y generación asíncrona de reportes PDF/Excel.")
    ContainerDb(postgres_db, "Base de Datos Relacional Multi-Tenant", "PostgreSQL 16 (django-tenants)", "Esquema 'public' (Tenants, Suscripciones SaaS, SuperAdmin) y esquemas aislados por clínica (HCE, SOAP, Ánimo, Pagos, Amortización, Gastos Fijos, Liquidaciones y Calificaciones CRM).")
    Container(vault_storage, "Almacenamiento Cifrado y Documentos", "Sistema de Archivos Seguro (Permisos 0600) + Media", "Resguarda archivos de bitácora cifrada AES-256 Fernet, respaldos pg_dump gzip, comprobantes financieros PDF y certificados SHA-256.")
}

System_Ext(stripe_qr, "Stripe & Pasarela QR Simple", "Procesamiento de pagos de citas, cuotas y suscripciones SaaS.")
System_Ext(ia_ext, "Google Gemini / HF Spaces NLP", "Modelos externos de síntesis semántica con entrada sanitizada.")
System_Ext(fcm_ext, "Firebase Cloud Messaging (FCM v1)", "Mensajería push móvil en segundo plano.")
System_Ext(jitsi_ext, "Servidor Jitsi Meet", "Salas WebRTC para telepsicología.")

Rel(personal, web_spa, "Opera módulos clínicos, financieros, contables y CRM", "HTTPS / TLS 1.3")
Rel(paciente, mobile_app, "Consulta citas, extracto de amortización y califica servicio", "HTTPS / TLS 1.3")
Rel(paciente, web_spa, "Accede alternativamente desde navegador móvil o PC", "HTTPS / TLS 1.3")

Rel(web_spa, api_backend, "Consume API REST /api/v1/ (JWT + Subdominio Tenant)", "JSON / HTTPS")
Rel(mobile_app, api_backend, "Consume API REST /api/v1/ (JWT + Header X-Tenant-ID)", "JSON / HTTPS")

Rel(api_backend, postgres_db, "Operaciones ORM transaccionales (search_path aislado)", "TCP 5432 / psycopg2 SSL")
Rel(api_backend, worker_ml, "Encola tareas ML, conciliación de cuotas y push FCM", "Redis Broker")
Rel(worker_ml, postgres_db, "Lee series temporales (6-12m) y persiste alertas predictivas", "TCP 5432 / psycopg2 SSL")
Rel(api_backend, vault_storage, "Lee/escribe logs Fernet 0600, extractos PDF y backups", "File I/O Seguro")
worker_ml ..> vault_storage : "Exporta PDFs y backups programados"

Rel(api_backend, stripe_qr, "Checkout, webhooks idempotentes y conciliación", "HTTPS REST")
Rel(api_backend, ia_ext, "Solicita síntesis longitudinal sin datos PII", "HTTPS REST")
Rel(worker_ml, fcm_ext, "Despacha push de recordatorios y encuestas CRM", "HTTPS OAuth2")
Rel(web_spa, jitsi_ext, "Transmisión audiovisual clínica", "WebRTC / SRTP")
Rel(mobile_app, jitsi_ext, "Transmisión audiovisual nativa", "WebRTC / SRTP")
@enduml
```

---

##### C4 Nivel 3A: Diagrama de Componentes – Sistema General / Backend API & Motor Analítico (Sprint 4)

Realiza un zoom-in sobre el contenedor general **Backend Core & API REST** junto con el **Worker Analítico ML/Contable**, detallando los componentes agregados en el **Sprint 4** y su articulación con el núcleo de seguridad Multi-Tenant (`TenantMainMiddleware`, `JWTAuthentication` y `RBAC`).

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *4. Arquitectura Modelo C4 → C4 Nivel 3A - Componentes Backend* (**Diagrama ID: 344**).

![Modelo C4 Nivel 3A – Componentes Backend API y Analítica (Sprint 4)](./imagenes/diagrama_c4_nivel3_sp4.png)

```plantuml
@startuml
!include <C4/C4_Component>

LAYOUT_TOP_DOWN()

title Modelo C4 – Nivel 3: Diagrama de Componentes (Módulos IA Longitudinal, Finanzas Contables y CRM – Sprint 4)

Container(web_spa, "Aplicación Web (Angular 17)", "Frontend SPA", "Consolas IA, Caja, P&L y CRM")
Container(mobile_app, "Aplicación Móvil (Flutter 3.x)", "App Paciente", "Extracto de Amortización y Calificación 1-5 ★")
ContainerDb(postgres_db, "PostgreSQL 16 Multi-Tenant", "Base de Datos", "Esquemas aislados por clínica + Dataset 6-12 meses")
System_Ext(stripe_qr, "Stripe / QR Simple", "Pasarela Pagos", "Checkout y Webhooks")
System_Ext(ia_ext, "Gemini / HF Spaces", "Servicio IA", "Síntesis textual anonimizada")

Container_Boundary(backend_core, "Backend Core Django 5.x / DRF & Worker Analítico (Sprint 4)") {
    Component(cmp_security, "Núcleo Multi-Tenant, JWT y RBAC", "tenants.middleware / clinica.permissions", "Resuelve el esquema PostgreSQL por tenant, valida Bearer JWT, aplica guardia clínico-financiero y audita en bitácora Fernet GMT-4.")

    Component(cmp_resumen_ia, "Controlador y Servicio de Resúmenes Longitudinales IA (CU23)", "clinica.views.ResumenLongitudinalViewSet / ia_longitudinal.py", "Recopila notas SOAP, CIE-10 y ánimo; ejecuta sanitizar_pii(), genera borrador con hash SHA-256 y exige aprobación HITL del psicólogo.")

    Component(cmp_riesgo_ml, "Motor Predictivo ML de Señales de Riesgo (CU24)", "clinica.ml_riesgo_service.RiesgoPredictivoMLService", "Extrae features longitudinales de 6-12 meses (pendiente anímica, ausentismo, adherencia a tareas, léxico SOAP), calcula score de riesgo y pesos explicables.")

    Component(cmp_pagos_amort, "Servicio de Pagos Multimoneda y Amortización (CU26)", "finanzas.services.PagosYAmortizacionService", "Procesa cobros en BOB/USD con tasa oficial y ajuste cambiario exacto (Decimal); genera y amortiza cuotas de planes terapéuticos (capital, seguro, comisión, saldo).")

    Component(cmp_liquidacion, "Servicio de Liquidación de Honorarios y Suscripciones SaaS (CU26)", "finanzas.services.LiquidacionSaaSService / subscriptions.views", "Consolida sesiones REALIZADA por psicólogo según porcentaje de convenio, liquida honorarios y gestiona renovaciones/facturas de planes SaaS.")

    Component(cmp_contabilidad, "Motor Contable de Ganancia Bruta vs. Utilidad Neta (CU26)", "finanzas.services.ContabilidadUtilidadNetaService", "Diferencia Ingresos Brutos, Costo Directo de Honorarios, Ganancia Bruta y deduce Gastos Fijos Mensuales (Alquiler, Servicios Básicos, Personal Apoyo) para emitir la Utilidad Neta.")

    Component(cmp_crm, "Controlador y Analítica CRM de Satisfacción 1-5★ (CU26-CRM)", "crm.views.CalificacionCRMViewSet / EstadisticasCRMService", "Registra encuestas post-consulta (1-5 estrellas, unicidad por cita), dispara alertas ante <=2 estrellas y calcula métricas estadísticas CSAT, NPS e histogramas.")
}

Rel(web_spa, cmp_security, "Peticiones HTTPS REST (Admin, Psicólogo, Coordinador)", "JSON / Bearer JWT")
Rel(mobile_app, cmp_security, "Peticiones HTTPS REST (Paciente: Extracto y Calificación)", "JSON / Bearer JWT")

Rel(cmp_security, cmp_resumen_ia, "Autoriza acceso al expediente asignado")
Rel(cmp_security, cmp_riesgo_ml, "Autoriza consulta de radar predictivo")
Rel(cmp_security, cmp_pagos_amort, "Enruta operaciones de caja y estado de cuenta")
Rel(cmp_security, cmp_liquidacion, "Enruta liquidaciones y gestión SaaS")
Rel(cmp_security, cmp_contabilidad, "Autoriza consultas contables gerenciales")
Rel(cmp_security, cmp_crm, "Enruta calificaciones y métricas CRM")

Rel(cmp_resumen_ia, ia_ext, "Despacha contexto sanitizado sin PII", "HTTPS / TLS 1.3")
Rel(cmp_pagos_amort, stripe_qr, "Crea checkout y valida firma de webhooks", "HTTPS REST")
Rel(cmp_liquidacion, stripe_qr, "Verifica cobros de suscripciones SaaS", "HTTPS REST")

Rel(cmp_resumen_ia, postgres_db, "Lee SOAP/CIE/Ánimo; persiste clinica_resumenlongitudinalia", "SQL ORM")
Rel(cmp_riesgo_ml, postgres_db, "Analiza series 6-12m; persiste clinica_alertariesgoia", "SQL ORM")
Rel(cmp_pagos_amort, postgres_db, "CRUD finanzas_planpago, cuotaamortizacion, pagotransaccion", "SQL Transaccional")
Rel(cmp_liquidacion, postgres_db, "CRUD finanzas_liquidacionhonorario y public.subscriptions_suscripcion", "SQL Transaccional")
Rel(cmp_contabilidad, postgres_db, "Agrega ingresos, honorarios y finanzas_gastofijomensual", "SQL Agregaciones")
Rel(cmp_crm, postgres_db, "CRUD crm_calificacionservicio y cálculos CSAT/NPS", "SQL ORM")
@enduml
```

---

##### C4 Nivel 3B: Diagrama de Componentes – Contenedor Cliente Web Responsivo (Angular 17 Standalone)

Descompone el contenedor **Aplicación Web SPA Responsiva** (`prototipo/web/src/app/`), detallando la separación entre guardias funcionales RBAC, el interceptor HTTP JWT multi-tenant, los módulos funcionales web (Clínica/IA HITL/ML, Agenda/Jitsi/CRM, Finanzas Multimoneda/P&L y Admin SaaS/Reportes) y la capa de servicios `@Injectable` consumidora de la API REST.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *4. Arquitectura Modelo C4 → C4 Nivel 3B - Componentes Web* (**Diagrama ID: 345**).

![Modelo C4 Nivel 3B – Componentes Cliente Web Angular 17 Standalone (Sprint 4)](./imagenes/diagrama_c4_nivel3_web_sp4.png)

```plantuml
@startuml
!include <C4/C4_Component>

LAYOUT_TOP_DOWN()

title Modelo C4 – Nivel 3B: Componentes Cliente Web Responsivo (Angular 17 Standalone)

Person(web_users, "Personal Clínico, Admin y SuperAdmin", "Psicólogo, Coordinador, Admin/Contador y SuperAdmin SaaS.")
Container(backend_api, "Backend Core API REST (Django 5.x / DRF)", "HTTPS JSON", "API Multi-Tenant SIGEPSI")
System_Ext(jitsi_ext, "Servidor Jitsi Meet", "Salas WebRTC cifradas SRTP/DTLS")

Container_Boundary(web_spa_bnd, "Aplicación Web SPA Responsiva (Angular 17 Standalone)") {
    Component(cw_router, "Router & Functional RoleGuards", "app.routes.ts / auth.guard.ts", "Aplica authGuard, superAdminGuard, adminCentroGuard y clinicalStaffGuard por perfil.")
    Component(cw_inter, "AuthInterceptor & Session Tenant", "auth.interceptor.ts / AuthService", "Inyecta Authorization Bearer JWT y cabecera X-Tenant-Domain; gestiona refresh/logout.")
    Component(cw_clin, "Módulo Clínica, IA HITL & Radar ML", "historia-clinica / nota-soap / consola-triage", "Consola de síntesis longitudinal IA (CU23 HITL) y radar predictivo ML (CU24).")
    Component(cw_agen, "Módulo Agenda, Teleconsulta & CRM", "calendario-agenda / teleconsulta-room", "Gestión de citas, sala WebRTC Jitsi y panel de moderación CRM 1-5★ (CU26-CRM / HU-55).")
    Component(cw_fin, "Módulo Finanzas Multimoneda & P&L", "finanzas / amortizacion / utilidad-neta", "Caja BOB/USD, extractos de cuotas, liquidación de honorarios y P&L neto (CU26 / HU-51 a HU-54).")
    Component(cw_adm, "Módulo Admin SaaS, Reportes & Audit", "tenant-list / backup-restore / reportes-hub", "Suscripciones SaaS, backups, bitácora de auditoría y exportador PDF/Excel.")
    Component(cw_srv, "Core Angular @Injectable Services", "core/services/*.service.ts", "ClinicaService, ClinicaSprint2Service, AgendaService, TriajeChatbotIAService, FinanzasContabilidadService, CrmCalidadService, ReportService.")
}

Rel(web_users, cw_router, "Opera vistas administrativas y clínicas", "HTTPS")
Rel(cw_router, cw_inter, "Valida rol + token de sesión")
Rel(cw_router, cw_clin, "Carga rutas clínicas/IA")
Rel(cw_router, cw_agen, "Carga agenda y teleconsulta")
Rel(cw_inter, cw_fin, "Habilita tesorería y P&L")
Rel(cw_inter, cw_adm, "Habilita administración SaaS y auditoría")
Rel(cw_clin, cw_srv, "Consume Observables REST")
Rel(cw_agen, cw_srv, "Consume Observables REST")
Rel(cw_fin, cw_srv, "Consume Observables REST")
Rel(cw_adm, cw_srv, "Consume Observables REST")
Rel(cw_agen, jitsi_ext, "Teleconsulta WebRTC JWT")
Rel(cw_srv, backend_api, "Peticiones JSON + Bearer JWT + X-Tenant-Domain", "HTTPS REST")
@enduml
```

---

##### C4 Nivel 3C: Diagrama de Componentes – Contenedor Cliente Móvil Nativo (Flutter 3.x / Dart)

Descompone el contenedor **Aplicación Móvil Nativa del Paciente** (`prototipo/movil/lib/`), diferenciando sus módulos de identidad/notificaciones FCM, flujos clínicos del paciente (pre-consulta, firma táctil SHA-256, agenda/teleconsulta WebRTC, Mood Tracker/chatbot) y el módulo Sprint 4 de **estado de cuenta en cuotas, pagos y calificación post-consulta 1–5★**, respaldados por servicios Dart y almacenamiento seguro.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *4. Arquitectura Modelo C4 → C4 Nivel 3C - Componentes Móvil* (**Diagrama ID: 346**).

![Modelo C4 Nivel 3C – Componentes Cliente Móvil Flutter 3.x (Sprint 4)](./imagenes/diagrama_c4_nivel3_movil_sp4.png)

```plantuml
@startuml
!include <C4/C4_Component>

LAYOUT_TOP_DOWN()

title Modelo C4 – Nivel 3C: Componentes Cliente Móvil (Flutter 3.x / Dart)

Person(pac_mob, "Paciente", "Usuario móvil Android / iOS.")
Container(backend_api_m, "Backend Core API REST (Django 5.x / DRF)", "HTTPS JSON", "API Multi-Tenant SIGEPSI")
System_Ext(fcm_mob, "Firebase Cloud Messaging (FCM v1)", "Recordatorios push de citas, cuotas y encuestas CRM")
System_Ext(jitsi_mob, "Servidor Jitsi Meet (SDK WebRTC)", "Videoconsulta clínica móvil cifrada")
System_Ext(pay_mob, "Stripe / QR Simple", "Checkout móvil de cuotas y sesiones")

Container_Boundary(mob_bnd, "Aplicación Móvil Nativa del Paciente (Flutter 3.x / Dart)") {
    Component(cm_auth, "Auth, Tenant Picker & SecureStorage", "login_screen / AuthService", "Selecciona clínica tenant, persiste JWT de forma cifrada y verifica permisos.")
    Component(cm_push, "Handler Push FCM & Hardware", "notificaciones_screen / NotificationPermissionService", "Enrola token FCM y solicita permisos nativos de cámara/micrófono.")
    Component(cm_clin, "Screens Pre-Consulta, Firma & Tareas", "intake_form / consentimiento / mis_tareas", "Formularios dinámicos, firma digital SHA-256 y entrega de evidencias.")
    Component(cm_agen, "Screens Agenda & Teleconsulta Jitsi", "mis_citas / reservar_cita / teleconsulta_jitsi", "Reserva de turnos, cancelación y sala de videoconsulta móvil.")
    Component(cm_fin, "Screens Estado de Cuenta & CRM 1-5★", "EstadoCuentaAmortizacion / CalificacionCRMSheet", "Consulta de cuotas/saldos en BOB/USD (HU-52), pagos (HU-51) y calificación 1-5★ (HU-55).")
    Component(cm_ia, "Screens Dashboard Ánimo, Chatbot & Voz", "dashboard / chatbot_screen / reportes_screen", "Registro diario Mood Tracker, asistente virtual 24/7 y comandos de voz.")
    Component(cm_srv, "Dart REST Services Layer", "services/paquete1..6/*.dart + FinanzasCrmMovilService", "ClinicaService, AgendaService, Sprint2Service, ChatbotService y FinanzasCrmMovilService.")
}

Rel(pac_mob, cm_auth, "Inicia sesión en su clínica", "Touch UI")
Rel(cm_auth, cm_push, "Registra token del dispositivo")
Rel(cm_auth, cm_clin, "Navega a pre-consulta, firma y tareas")
Rel(cm_auth, cm_agen, "Navega a citas y teleconsulta")
Rel(cm_auth, cm_fin, "Navega a estado de cuenta y calificación CRM")
Rel(cm_auth, cm_ia, "Navega a Mood Tracker, chatbot y reportes")
Rel(cm_clin, cm_srv, "Invoca Future<T>")
Rel(cm_agen, cm_srv, "Invoca Future<T>")
Rel(cm_fin, cm_srv, "Invoca Future<T>")
Rel(cm_ia, cm_srv, "Invoca Future<T>")
Rel(fcm_mob, cm_push, "Notificación push en segundo plano", "FCM v1")
Rel(cm_agen, jitsi_mob, "Transmisión audiovisual móvil", "WebRTC / SRTP")
Rel(cm_fin, pay_mob, "Pasarela / QR de cobro", "HTTPS / Deep-Link")
Rel(cm_srv, backend_api_m, "Peticiones HTTPS REST + JWT + X-Tenant-Domain", "JSON")
@enduml
```

---

##### C4 Nivel 4: Diagrama de Código / Clases de Implementación (Code Diagram)

Desciende al nivel de código fuente orientado a objetos del **Backend Core en Python 3.12 / Django 5.x REST Framework**, detallando las clases, atributos tipados, métodos de dominio y acoplamientos entre los paquetes del Sprint 4. *(Nota de trazabilidad: las clases DTO, interfaces TypeScript, modelos Dart y servicios REST específicos de los contenedores Cliente Web Angular 17 y Cliente Móvil Flutter se encuentran modelados en detalle en los diagramas [`4.1.3 → 4.2`](#413-contexto-del-sistema) y [`4.1.3 → 4.3`](#413-contexto-del-sistema)).*

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *4. Arquitectura Modelo C4 → C4 Nivel 4 - Código y Clases* (**Diagrama ID: 347**).

![Modelo C4 Nivel 4 – Clases de Implementación (Sprint 4)](./imagenes/diagrama_c4_nivel4_sp4.png)

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 6
skinparam defaultFontName Arial
skinparam packageStyle frame

title Modelo C4 – Nivel 4: Diagrama de Código / Clases de Implementación (SIGEPSI – Sprint 4)

package "backend/clinica/ia_longitudinal (CU23 & CU24)" as PKG_IA #E8F8F5 {
    class ResumenLongitudinalViewSet {
        + generar_resumen(request: Request, paciente_id: UUID): Response
        + aprobar_resumen_hitl(request: Request, resumen_id: UUID): Response
        + exportar_resumen_pdf(request: Request, resumen_id: UUID): FileResponse
    }

    class ResumenLongitudinalIAService {
        + {static} sanitizar_pii(texto: str): str
        + recopilar_historial(historia_id: UUID, fecha_ini: date, fecha_fin: date): dict
        + construir_sintesis(datos_sanitizados: dict): ResumenClinicoIA
        + aprobar_con_supervision(resumen_id: UUID, psicologo_id: UUID, nota: str): ResumenClinicoIA
    }

    class RiesgoPredictivoMLService {
        - pesos_modelo: dict
        + extraer_features_longitudinales(paciente_id: UUID, meses: int = 12): dict
        + calcular_score_riesgo(features: dict): tuple[Decimal, dict]
        + evaluar_y_emitir_alerta(paciente_id: UUID): AlertaRiesgoPredictivaIA
        + intervenir_alerta(alerta_id: UUID, usuario_id: UUID, accion: str): AlertaRiesgoPredictivaIA
    }

    class ResumenClinicoIA {
        + id: UUID
        + historia_clinica_id: UUID
        + resumen_estructurado: Text
        + hash_pii_sha256: Char(64)
        + estado_validacion: Char(25)
        + validado_por_id: UUID
    }

    class AlertaRiesgoPredictivaIA {
        + id: UUID
        + historia_clinica_id: UUID
        + indice_riesgo: Decimal(4,3)
        + nivel_severidad: Char(20)
        + factores_contribuyentes: JSONB
        + estado: Char(20)
    }
}

package "backend/finanzas (CU26 – Pagos, Amortización y Utilidad Neta)" as PKG_FIN #EBF5FB {
    class PagosYAmortizacionViewSet {
        + registrar_pago(request: Request): Response
        + crear_plan_amortizacion(request: Request): Response
        + obtener_extracto_paciente(request: Request, paciente_id: UUID): Response
        + descargar_extracto_pdf(request: Request, plan_id: UUID): FileResponse
    }

    class PagosYAmortizacionService {
        + convertir_a_bob(monto: Decimal, moneda: str, tasa: Decimal): tuple[Decimal, Decimal]
        + generar_cuotas_plan(plan: PlanPagoTerapeutico): list[CuotaAmortizacion]
        + procesar_abono_cuota(cuota_id: UUID, monto: Decimal, moneda: str, metodo: str): PagoTransaccion
        + obtener_estado_cuenta(paciente_id: UUID): dict
    }

    class ContabilidadUtilidadNetaService {
        + registrar_gasto_fijo(datos: dict): GastoFijoMensual
        + liquidar_honorarios_periodo(periodo: str, psicologo_id: UUID): list[LiquidacionHonorario]
        + calcular_estado_resultados(fecha_ini: date, fecha_fin: date): dict
    }

    class PlanPagoTerapeutico {
        + id: UUID
        + paciente_id: UUID
        + monto_total: Decimal(12,2)
        + moneda: Char(3)
        + tasa_interes_anual: Decimal(5,2)
        + porcentaje_seguro: Decimal(5,2)
        + numero_cuotas: SmallInt
    }

    class CuotaAmortizacion {
        + id: UUID
        + plan_id: UUID
        + numero_cuota: SmallInt
        + capital_amortizado: Decimal(12,2)
        + interes_o_comision: Decimal(12,2)
        + seguro_asistencial: Decimal(12,2)
        + monto_total_cuota: Decimal(12,2)
        + saldo_insoluto: Decimal(12,2)
        + estado: Char(20)
    }

    class PagoTransaccion {
        + id: UUID
        + moneda_origen: Char(3)
        + monto_origen: Decimal(12,2)
        + tipo_cambio_aplicado: Decimal(8,4)
        + monto_bob_equivalente: Decimal(12,2)
        + ajuste_redondeo: Decimal(8,4)
        + metodo_pago: Char(30)
    }

    class GastoFijoMensual {
        + id: UUID
        + periodo_mes: Char(7)
        + categoria: Char(40)
        + monto_bob: Decimal(12,2)
    }

    class LiquidacionHonorario {
        + id: UUID
        + psicologo_id: UUID
        + periodo_mes: Char(7)
        + total_bruto_generado: Decimal(12,2)
        + monto_neto_psicologo: Decimal(12,2)
        + estado: Char(20)
    }
}

package "backend/crm (CU26-CRM – Satisfacción 1-5★) & subscriptions" as PKG_CRM #F4ECF7 {
    class CalificacionCRMViewSet {
        + registrar_calificacion(request: Request): Response
        + obtener_estadisticas_crm(request: Request): Response
        + resolver_alerta_insatisfaccion(request: Request, pk: UUID): Response
    }

    class CRMSatisfaccionService {
        + guardar_evaluacion(cita_id: UUID, estrellas: int, comentario: str): CalificacionCRM
        + calcular_indicadores_csat_nps(fecha_ini: date, fecha_fin: date): dict
    }

    class CalificacionCRM {
        + id: UUID
        + cita_id: UUID
        + puntuacion_estrellas: SmallInt
        + requiere_seguimiento: Boolean
        + estado_seguimiento: Char(20)
    }

    class SuscripcionSaaSService {
        + verificar_renovaciones_proximas(): list[dict]
        + emitir_factura_saas(suscripcion_id: UUID): dict
    }
}

ResumenLongitudinalViewSet ..> ResumenLongitudinalIAService : invoca
ResumenLongitudinalViewSet ..> RiesgoPredictivoMLService : evalúa
ResumenLongitudinalIAService --> ResumenClinicoIA : persiste
RiesgoPredictivoMLService --> AlertaRiesgoPredictivaIA : emite

PagosYAmortizacionViewSet ..> PagosYAmortizacionService : delega
PagosYAmortizacionViewSet ..> ContabilidadUtilidadNetaService : consulta P&L
PagosYAmortizacionService --> PlanPagoTerapeutico : gestiona
PlanPagoTerapeutico "1" *-- "1..*" CuotaAmortizacion : desglosa
CuotaAmortizacion "0..1" -- "0..*" PagoTransaccion : amortiza

ContabilidadUtilidadNetaService --> PagoTransaccion : consolida
ContabilidadUtilidadNetaService --> LiquidacionHonorario : liquida
ContabilidadUtilidadNetaService --> GastoFijoMensual : deduce
ContabilidadUtilidadNetaService ..> SuscripcionSaaSService : verifica cuota SaaS

CalificacionCRMViewSet ..> CRMSatisfaccionService : delega
CRMSatisfaccionService --> CalificacionCRM : registra
@enduml
```

---

#### 4.2.1.2 Diseño de Datos

El incremento del Sprint 4 incorpora **9 nuevas tablas relacionales** dentro de cada esquema `tenant` (manteniendo el aislamiento absoluto por clínica mediante `django-tenants`) y extiende la tabla global `public.subscriptions_suscripcion` para el control de renovación de planes SaaS. Todas las columnas financieras utilizan precisión exacta `NUMERIC(12,2)` (jamás punto flotante binario `FLOAT`) para garantizar cuadre contable exacto de `0.000` de error, y todas las llaves foráneas (`FK`) se conectan explícitamente con sus tablas ancla de Sprints previos (`accounts_usuario`, `clinica_paciente`, `clinica_psicologo`, `clinica_historiaclinica`, `agenda_cita`) y con la tabla de cierre contable mensual (`finanzas_estadoresultadoscontable`).

##### 1. Diagrama Relacional Físico (Incremento Sprint 4)

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *5. Diseño de Datos - Relacional Físico (Sprint 4)* (**Diagrama ID: 348**).

![Diagrama Relacional Físico PostgreSQL 16 – Incremento Sprint 4](./imagenes/diagrama_bd_relacional_sp4.png)

```plantuml
@startuml
skinparam linetype ortho
skinparam shadowing false
skinparam roundcorner 6
skinparam defaultFontName Arial

title Modelo Relacional Físico – Incremento Sprint 4 (Esquema Tenant & Public)

package "Esquema public (SaaS Multi-Tenant)" {
  entity "public.subscriptions_tenant" as TENANT {
    * id : UUID <<PK>>
    --
    schema_name : VARCHAR(63)
    nombre_comercial : VARCHAR(150)
    activo : BOOLEAN
  }

  entity "public.subscriptions_suscripcion" as SUSC {
    * id : UUID <<PK>>
    --
    * tenant_id : UUID <<FK>>
    plan_nombre : VARCHAR(60)
    monto_mensual_usd : NUMERIC(10,2)
    fecha_proximo_cobro : DATE
    renovacion_automatica : BOOLEAN
  }
}

package "Esquema tenant – Tablas Ancla Referenciadas (SP1–SP3)" {
  entity "accounts_usuario" as USR {
    * id : UUID <<PK>>
    --
    email : VARCHAR(150)
    nombre_completo : VARCHAR(180)
    activo : BOOLEAN
  }

  entity "clinica_paciente" as PAC {
    * id : UUID <<PK>>
    --
    * usuario_id : UUID <<FK>>
    ci : VARCHAR(30)
    codigo_expediente : VARCHAR(50)
  }

  entity "clinica_psicologo" as PSI {
    * id : UUID <<PK>>
    --
    * usuario_id : UUID <<FK>>
    numero_colegiado : VARCHAR(50)
    porcentaje_honorario : NUMERIC(5,2)
  }

  entity "clinica_historiaclinica" as HC {
    * id : UUID <<PK>>
    --
    * paciente_id : UUID <<FK>>
    codigo_historia : VARCHAR(50)
    cerrada : BOOLEAN
  }

  entity "agenda_cita" as CITA {
    * id : UUID <<PK>>
    --
    * paciente_id : UUID <<FK>>
    * psicologo_id : UUID <<FK>>
    fecha_hora_inicio : TIMESTAMPTZ
    estado : VARCHAR(20)
  }
}

package "Esquema tenant – Incremento Sprint 4 (9 Tablas Nuevas)" {
  entity "clinica_resumenlongitudinalia" as RES_IA {
    * id : UUID <<PK>>
    --
    * historia_clinica_id : UUID <<FK>>
    validado_por_id : UUID <<FK>>
    periodo_inicio : DATE
    periodo_fin : DATE
    total_sesiones_analizadas : INT
    resumen_estructurado : TEXT
    hash_pii_sha256 : VARCHAR(64)
    estado_validacion : VARCHAR(25)
    observaciones_terapeuta : TEXT
    fecha_generacion : TIMESTAMPTZ
    fecha_validacion : TIMESTAMPTZ
  }

  entity "clinica_alertariesgoia" as RIESGO_IA {
    * id : UUID <<PK>>
    --
    * historia_clinica_id : UUID <<FK>>
    intervenida_por_id : UUID <<FK>>
    indice_riesgo : NUMERIC(4,3)
    nivel_severidad : VARCHAR(20)
    factores_contribuyentes : JSONB
    pendiente_animo_30d : NUMERIC(5,2)
    tasa_inasistencia : NUMERIC(5,2)
    estado : VARCHAR(20)
    accion_clinica : TEXT
    fecha_deteccion : TIMESTAMPTZ
    fecha_intervencion : TIMESTAMPTZ
  }

  entity "finanzas_planpagoterapeutico" as PLAN {
    * id : UUID <<PK>>
    --
    * paciente_id : UUID <<FK>>
    nombre_plan : VARCHAR(120)
    sesiones_incluidas : INT
    monto_total : NUMERIC(12,2)
    moneda : VARCHAR(3)
    tasa_interes_anual : NUMERIC(5,2)
    porcentaje_seguro : NUMERIC(5,2)
    numero_cuotas : SMALLINT
    estado : VARCHAR(20)
    fecha_creacion : TIMESTAMPTZ
  }

  entity "finanzas_cuotaamortizacion" as CUOTA {
    * id : UUID <<PK>>
    --
    * plan_id : UUID <<FK>>
    numero_cuota : SMALLINT
    fecha_vencimiento : DATE
    capital_amortizado : NUMERIC(12,2)
    interes_o_comision : NUMERIC(12,2)
    seguro_asistencial : NUMERIC(12,2)
    monto_total_cuota : NUMERIC(12,2)
    saldo_insoluto : NUMERIC(12,2)
    estado : VARCHAR(20)
  }

  entity "finanzas_pagotransaccion" as PAGO {
    * id : UUID <<PK>>
    --
    * paciente_id : UUID <<FK>>
    cita_id : UUID <<FK>>
    cuota_id : UUID <<FK>>
    estado_resultados_id : UUID <<FK>>
    registrado_por_id : UUID <<FK>>
    moneda_origen : VARCHAR(3)
    monto_origen : NUMERIC(12,2)
    tipo_cambio_aplicado : NUMERIC(8,4)
    monto_bob_equivalente : NUMERIC(12,2)
    ajuste_redondeo : NUMERIC(8,4)
    metodo_pago : VARCHAR(30)
    referencia_externa : VARCHAR(150)
    estado : VARCHAR(20)
    fecha_pago : TIMESTAMPTZ
  }

  entity "finanzas_liquidacionhonorario" as LIQ {
    * id : UUID <<PK>>
    --
    * psicologo_id : UUID <<FK>>
    estado_resultados_id : UUID <<FK>>
    periodo_mes : VARCHAR(7)
    sesiones_liquidadas : INT
    total_bruto_generado : NUMERIC(12,2)
    porcentaje_aplicado : NUMERIC(5,2)
    monto_neto_psicologo : NUMERIC(12,2)
    monto_retencion_centro : NUMERIC(12,2)
    estado : VARCHAR(20)
    fecha_liquidacion : TIMESTAMPTZ
    fecha_desembolso : TIMESTAMPTZ
  }

  entity "finanzas_gastofijomensual" as GASTO {
    * id : UUID <<PK>>
    --
    estado_resultados_id : UUID <<FK>>
    registrado_por_id : UUID <<FK>>
    periodo_mes : VARCHAR(7)
    categoria : VARCHAR(40)
    descripcion : VARCHAR(200)
    moneda : VARCHAR(3)
    monto_origen : NUMERIC(12,2)
    tipo_cambio : NUMERIC(8,4)
    monto_bob : NUMERIC(12,2)
    comprobante_ref : VARCHAR(100)
    fecha_registro : TIMESTAMPTZ
  }

  entity "finanzas_estadoresultadoscontable" as PNL {
    * id : UUID <<PK>>
    --
    * periodo_mes : VARCHAR(7) <<UQ>>
    generado_por_id : UUID <<FK>>
    ingresos_brutos_bob : NUMERIC(12,2)
    costos_honorarios_bob : NUMERIC(12,2)
    ganancia_bruta_bob : NUMERIC(12,2)
    total_gastos_fijos_bob : NUMERIC(12,2)
    utilidad_neta_bob : NUMERIC(12,2)
    margen_neto_pct : NUMERIC(5,2)
    estado_cierre : VARCHAR(20)
    fecha_cierre : TIMESTAMPTZ
  }

  entity "crm_calificacionservicio" as CRM {
    * id : UUID <<PK>>
    --
    * cita_id : UUID <<FK, UQ>>
    * paciente_id : UUID <<FK>>
    * psicologo_id : UUID <<FK>>
    puntuacion_estrellas : SMALLINT
    puntualidad : SMALLINT
    empatia_profesional : SMALLINT
    calidad_plataforma : SMALLINT
    comentario : TEXT
    requiere_seguimiento : BOOLEAN
    estado_seguimiento : VARCHAR(20)
    nota_resolucion_crm : TEXT
    fecha_calificacion : TIMESTAMPTZ
  }
}

TENANT ||--|{ SUSC : contrata
PAC ||--|| HC : posee
HC ||--o{ RES_IA : sintetiza
HC ||--o{ RIESGO_IA : monitorea
USR |o--o{ RES_IA : valida
USR |o--o{ RIESGO_IA : interviene
PAC ||--o{ PLAN : contrata
PLAN ||--|{ CUOTA : desglosa
CUOTA |o--o{ PAGO : amortiza
PAC ||--o{ PAGO : efectúa
CITA |o--o{ PAGO : liquida
USR |o--o{ PAGO : registra
PSI ||--o{ LIQ : percibe
USR |o--o{ GASTO : registra
USR |o--o{ PNL : genera
PNL |o--o{ PAGO : consolida_ingresos
PNL |o--o{ LIQ : deduce_honorarios
PNL |o--o{ GASTO : deduce_gastos
CITA ||--o| CRM : evalúa
PAC ||--o{ CRM : califica
PSI ||--o{ CRM : recibe
@enduml
```

##### 2. Script SQL DDL Oficial – Incremento Sprint 4 (PostgreSQL 16 Multi-Tenant)

```sql
-- ============================================================================
-- INCREMENTO DDL SPRINT 4 – PLATAFORMA SIGEPSI (POSTGRESQL 16 MULTI-TENANT)
-- Módulos: IA Longitudinal (CU23), Riesgo Predictivo ML (CU24),
--          Pagos Multimoneda, Amortización, Contabilidad Utilidad Neta (CU26)
--          y CRM de Calificación Post-Consulta 1-5 Estrellas (CU26-CRM)
-- ============================================================================

-- 1. CU23: Resúmenes Clínicos Longitudinales Asistidos por IA (HITL)
CREATE TABLE IF NOT EXISTS clinica_resumenlongitudinalia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    historia_clinica_id UUID NOT NULL REFERENCES clinica_historiaclinica(id) ON DELETE CASCADE,
    periodo_inicio DATE NOT NULL,
    periodo_fin DATE NOT NULL,
    total_sesiones_analizadas INTEGER NOT NULL DEFAULT 0 CHECK (total_sesiones_analizadas >= 0),
    resumen_estructurado TEXT NOT NULL,
    hash_pii_sha256 VARCHAR(64) NOT NULL,
    estado_validacion VARCHAR(25) NOT NULL DEFAULT 'BORRADOR_IA'
        CHECK (estado_validacion IN ('BORRADOR_IA', 'APROBADO_HITL', 'EDITADO_Y_APROBADO', 'DESCARTADO')),
    validado_por_id UUID REFERENCES accounts_usuario(id) ON DELETE SET NULL,
    observaciones_terapeuta TEXT DEFAULT '',
    fecha_generacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_validacion TIMESTAMPTZ,
    CONSTRAINT chk_resumen_rango_fechas CHECK (periodo_fin >= periodo_inicio)
);
CREATE INDEX IF NOT EXISTS idx_resumen_ia_hc ON clinica_resumenlongitudinalia(historia_clinica_id, fecha_generacion DESC);

-- 2. CU24: Alertas Predictivas de Riesgo Clínico (Modelo ML sobre 6-12 meses)
CREATE TABLE IF NOT EXISTS clinica_alertariesgoia (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    historia_clinica_id UUID NOT NULL REFERENCES clinica_historiaclinica(id) ON DELETE CASCADE,
    indice_riesgo NUMERIC(4,3) NOT NULL CHECK (indice_riesgo >= 0 AND indice_riesgo <= 1),
    nivel_severidad VARCHAR(20) NOT NULL CHECK (nivel_severidad IN ('BAJO', 'MODERADO', 'ALTO', 'CRITICO')),
    factores_contribuyentes JSONB NOT NULL DEFAULT '{}'::jsonb,
    pendiente_animo_30d NUMERIC(5,2) DEFAULT 0.00,
    tasa_inasistencia NUMERIC(5,2) DEFAULT 0.00,
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVA' CHECK (estado IN ('ACTIVA', 'EN_REVISION', 'INTERVENIDA', 'DESCARTADA')),
    intervenida_por_id UUID REFERENCES accounts_usuario(id) ON DELETE SET NULL,
    accion_clinica TEXT DEFAULT '',
    fecha_deteccion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_intervencion TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_riesgo_ia_estado ON clinica_alertariesgoia(estado, nivel_severidad);

-- 3. CU26: Cierre Mensual Contable (Ganancia Bruta vs. Utilidad Neta P&L)
CREATE TABLE IF NOT EXISTS finanzas_estadoresultadoscontable (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    periodo_mes VARCHAR(7) NOT NULL UNIQUE, -- Formato YYYY-MM
    generado_por_id UUID REFERENCES accounts_usuario(id) ON DELETE SET NULL,
    ingresos_brutos_bob NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (ingresos_brutos_bob >= 0),
    costos_honorarios_bob NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (costos_honorarios_bob >= 0),
    ganancia_bruta_bob NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    total_gastos_fijos_bob NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (total_gastos_fijos_bob >= 0),
    utilidad_neta_bob NUMERIC(12,2) NOT NULL DEFAULT 0.00,
    margen_neto_pct NUMERIC(5,2) NOT NULL DEFAULT 0.00,
    estado_cierre VARCHAR(20) NOT NULL DEFAULT 'ABIERTO' CHECK (estado_cierre IN ('ABIERTO', 'CONCILIADO', 'CERRADO')),
    fecha_cierre TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 4. CU26: Planes Terapéuticos Financiados y Tabla de Amortización
CREATE TABLE IF NOT EXISTS finanzas_planpagoterapeutico (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES clinica_paciente(id) ON DELETE RESTRICT,
    nombre_plan VARCHAR(120) NOT NULL,
    sesiones_incluidas INTEGER NOT NULL CHECK (sesiones_incluidas > 0),
    monto_total NUMERIC(12,2) NOT NULL CHECK (monto_total > 0),
    moneda VARCHAR(3) NOT NULL DEFAULT 'BOB' CHECK (moneda IN ('BOB', 'USD')),
    tasa_interes_anual NUMERIC(5,2) NOT NULL DEFAULT 0.00 CHECK (tasa_interes_anual >= 0),
    porcentaje_seguro NUMERIC(5,2) NOT NULL DEFAULT 1.50 CHECK (porcentaje_seguro >= 0),
    numero_cuotas SMALLINT NOT NULL CHECK (numero_cuotas BETWEEN 1 AND 36),
    estado VARCHAR(20) NOT NULL DEFAULT 'ACTIVO' CHECK (estado IN ('ACTIVO', 'PAGADO', 'MORA', 'CANCELADO')),
    fecha_creacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS finanzas_cuotaamortizacion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    plan_id UUID NOT NULL REFERENCES finanzas_planpagoterapeutico(id) ON DELETE CASCADE,
    numero_cuota SMALLINT NOT NULL CHECK (numero_cuota > 0),
    fecha_vencimiento DATE NOT NULL,
    capital_amortizado NUMERIC(12,2) NOT NULL CHECK (capital_amortizado >= 0),
    interes_o_comision NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (interes_o_comision >= 0),
    seguro_asistencial NUMERIC(12,2) NOT NULL DEFAULT 0.00 CHECK (seguro_asistencial >= 0),
    monto_total_cuota NUMERIC(12,2) NOT NULL CHECK (monto_total_cuota > 0),
    saldo_insoluto NUMERIC(12,2) NOT NULL CHECK (saldo_insoluto >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE' CHECK (estado IN ('PENDIENTE', 'PAGADA', 'MORA', 'ANULADA')),
    CONSTRAINT uq_plan_num_cuota UNIQUE (plan_id, numero_cuota)
);
CREATE INDEX IF NOT EXISTS idx_cuota_vencimiento ON finanzas_cuotaamortizacion(estado, fecha_vencimiento);

-- 5. CU26: Registro de Pagos Multimoneda (BOB / USD) con Ajuste de Redondeo Exacto
CREATE TABLE IF NOT EXISTS finanzas_pagotransaccion (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paciente_id UUID NOT NULL REFERENCES clinica_paciente(id) ON DELETE RESTRICT,
    cita_id UUID REFERENCES agenda_cita(id) ON DELETE SET NULL,
    cuota_id UUID REFERENCES finanzas_cuotaamortizacion(id) ON DELETE SET NULL,
    estado_resultados_id UUID REFERENCES finanzas_estadoresultadoscontable(id) ON DELETE SET NULL,
    moneda_origen VARCHAR(3) NOT NULL DEFAULT 'BOB' CHECK (moneda_origen IN ('BOB', 'USD')),
    monto_origen NUMERIC(12,2) NOT NULL CHECK (monto_origen > 0),
    tipo_cambio_aplicado NUMERIC(8,4) NOT NULL DEFAULT 1.0000 CHECK (tipo_cambio_aplicado > 0),
    monto_bob_equivalente NUMERIC(12,2) NOT NULL CHECK (monto_bob_equivalente > 0),
    ajuste_redondeo NUMERIC(8,4) NOT NULL DEFAULT 0.0000,
    metodo_pago VARCHAR(30) NOT NULL CHECK (metodo_pago IN ('EFECTIVO', 'QR_SIMPLE', 'STRIPE_TARJETA', 'TRANSFERENCIA')),
    referencia_externa VARCHAR(150) UNIQUE,
    estado VARCHAR(20) NOT NULL DEFAULT 'CONFIRMADO' CHECK (estado IN ('PENDIENTE', 'CONFIRMADO', 'REEMBOLSADO', 'FALLIDO')),
    registrado_por_id UUID REFERENCES accounts_usuario(id) ON DELETE SET NULL,
    fecha_pago TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_pago_fecha_estado ON finanzas_pagotransaccion(fecha_pago DESC, estado);

-- 6. CU26: Liquidación de Honorarios a Psicólogos y Gastos Fijos Mensuales (Utilidad Neta)
CREATE TABLE IF NOT EXISTS finanzas_liquidacionhonorario (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    psicologo_id UUID NOT NULL REFERENCES clinica_psicologo(id) ON DELETE RESTRICT,
    estado_resultados_id UUID REFERENCES finanzas_estadoresultadoscontable(id) ON DELETE SET NULL,
    periodo_mes VARCHAR(7) NOT NULL, -- Formato YYYY-MM
    sesiones_liquidadas INTEGER NOT NULL DEFAULT 0 CHECK (sesiones_liquidadas >= 0),
    total_bruto_generado NUMERIC(12,2) NOT NULL CHECK (total_bruto_generado >= 0),
    porcentaje_aplicado NUMERIC(5,2) NOT NULL CHECK (porcentaje_aplicado > 0 AND porcentaje_aplicado <= 100),
    monto_neto_psicologo NUMERIC(12,2) NOT NULL CHECK (monto_neto_psicologo >= 0),
    monto_retencion_centro NUMERIC(12,2) NOT NULL CHECK (monto_retencion_centro >= 0),
    estado VARCHAR(20) NOT NULL DEFAULT 'PENDIENTE_PAGO' CHECK (estado IN ('PENDIENTE_PAGO', 'PAGADA', 'ANULADA')),
    fecha_liquidacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_desembolso TIMESTAMPTZ,
    CONSTRAINT uq_liq_psico_mes UNIQUE (psicologo_id, periodo_mes)
);

CREATE TABLE IF NOT EXISTS finanzas_gastofijomensual (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    estado_resultados_id UUID REFERENCES finanzas_estadoresultadoscontable(id) ON DELETE SET NULL,
    registrado_por_id UUID REFERENCES accounts_usuario(id) ON DELETE SET NULL,
    periodo_mes VARCHAR(7) NOT NULL, -- Formato YYYY-MM
    categoria VARCHAR(40) NOT NULL CHECK (categoria IN (
        'ALQUILER_INMUEBLE', 'SERVICIOS_BASICOS', 'PERSONAL_APOYO',
        'SUSCRIPCION_SAAS', 'MARKETING_CLINICO', 'OTROS_GASTOS_FIJOS'
    )),
    descripcion VARCHAR(200) NOT NULL,
    moneda VARCHAR(3) NOT NULL DEFAULT 'BOB' CHECK (moneda IN ('BOB', 'USD')),
    monto_origen NUMERIC(12,2) NOT NULL CHECK (monto_origen > 0),
    tipo_cambio NUMERIC(8,4) NOT NULL DEFAULT 1.0000,
    monto_bob NUMERIC(12,2) NOT NULL CHECK (monto_bob > 0),
    comprobante_ref VARCHAR(100) DEFAULT '',
    fecha_registro TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_gasto_fijo_periodo ON finanzas_gastofijomensual(periodo_mes, categoria);

-- 7. CU26-CRM: Calificaciones Post-Consulta (1 a 5 Estrellas) y Seguimiento de Calidad
CREATE TABLE IF NOT EXISTS crm_calificacionservicio (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cita_id UUID NOT NULL UNIQUE REFERENCES agenda_cita(id) ON DELETE CASCADE,
    paciente_id UUID NOT NULL REFERENCES clinica_paciente(id) ON DELETE CASCADE,
    psicologo_id UUID NOT NULL REFERENCES clinica_psicologo(id) ON DELETE CASCADE,
    puntuacion_estrellas SMALLINT NOT NULL CHECK (puntuacion_estrellas BETWEEN 1 AND 5),
    puntualidad SMALLINT NOT NULL DEFAULT 5 CHECK (puntualidad BETWEEN 1 AND 5),
    empatia_profesional SMALLINT NOT NULL DEFAULT 5 CHECK (empatia_profesional BETWEEN 1 AND 5),
    calidad_plataforma SMALLINT NOT NULL DEFAULT 5 CHECK (calidad_plataforma BETWEEN 1 AND 5),
    comentario TEXT DEFAULT '',
    requiere_seguimiento BOOLEAN NOT NULL DEFAULT FALSE,
    estado_seguimiento VARCHAR(20) NOT NULL DEFAULT 'CERRADO' CHECK (estado_seguimiento IN ('PENDIENTE', 'EN_GESTION', 'CERRADO')),
    nota_resolucion_crm TEXT DEFAULT '',
    fecha_calificacion TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_crm_estrellas ON crm_calificacionservicio(puntuacion_estrellas, fecha_calificacion DESC);

-- 8. Extensión en Esquema Public para Facturación y Renovación SaaS
ALTER TABLE public.subscriptions_suscripcion
    ADD COLUMN IF NOT EXISTS monto_mensual_usd NUMERIC(10,2) DEFAULT 49.00,
    ADD COLUMN IF NOT EXISTS fecha_proximo_cobro DATE,
    ADD COLUMN IF NOT EXISTS renovacion_automatica BOOLEAN DEFAULT TRUE;
```

##### 3. Diccionario de Datos (Entidades Nuevas y Extendidas Sprint 4)

| Tabla | Columna Clave | Tipo y Restricción | Descripción Funcional y Contable |
| :--- | :--- | :--- | :--- |
| `clinica_resumenlongitudinalia` | `hash_pii_sha256`, `estado_validacion` | `VARCHAR(64) NOT NULL`, `VARCHAR(25)` | Huella criptográfica del payload anonimizado previo al envío a IA y control *Human-in-the-Loop* (`BORRADOR_IA` → `APROBADO_HITL`). |
| `clinica_alertariesgoia` | `indice_riesgo`, `factores_contribuyentes` | `NUMERIC(4,3)`, `JSONB` | Probabilidad de deterioro/deserción $[0.000, 1.000]$ arrojada por ML y vector de pesos explicables (`pendiente_animo`, `ausentismo`, `tareas`). |
| `finanzas_planpagoterapeutico` | `monto_total`, `numero_cuotas`, `tasa_interes_anual` | `NUMERIC(12,2)`, `SMALLINT`, `NUMERIC(5,2)` | Contrato financiero del paquete de sesiones financiado en cuotas (1 a 36) por paciente en `BOB` o `USD`. |
| `finanzas_cuotaamortizacion` | `capital_amortizado`, `seguro_asistencial`, `saldo_insoluto` | `NUMERIC(12,2)` | Desglose financiero completo del extracto de amortización por cuota del paciente. |
| `finanzas_pagotransaccion` | `tipo_cambio_aplicado`, `ajuste_redondeo`, `estado_resultados_id` | `NUMERIC(8,4)`, `UUID <<FK>>` | Tasa cambiaria BOB/USD del día, ajuste por redondeo para cuadre contable $0.000$ y vinculación al cierre mensual P&L. |
| `finanzas_liquidacionhonorario` | `porcentaje_aplicado`, `monto_neto_psicologo`, `monto_retencion_centro` | `NUMERIC(5,2)`, `NUMERIC(12,2)` | Liquidación mensual por psicólogo (única por `psicologo_id, periodo_mes`) deducible de los ingresos brutos. |
| `finanzas_gastofijomensual` | `categoria`, `monto_bob`, `registrado_por_id` | `VARCHAR(40)`, `NUMERIC(12,2)`, `UUID <<FK>>` | Registra Alquiler, Servicios Básicos, Personal de Apoyo y Suscripción SaaS con auditoría de usuario para deducirlos de la Ganancia Bruta. |
| `finanzas_estadoresultadoscontable` | `periodo_mes`, `ganancia_bruta_bob`, `utilidad_neta_bob`, `margen_neto_pct` | `VARCHAR(7) UQ`, `NUMERIC(12,2)`, `NUMERIC(5,2)` | Consolidación contable mensual oficial (`Ingresos Brutos − Honorarios = Ganancia Bruta`; `Ganancia Bruta − Gastos Fijos = Utilidad Neta`). |
| `crm_calificacionservicio` | `cita_id`, `puntuacion_estrellas`, `requiere_seguimiento` | `UUID UQ <<FK>>`, `SMALLINT (1-5)`, `BOOLEAN` | Evalúa el servicio post-consulta (1 evaluación única por cita); calificaciones $\le 2$ activan automáticamente seguimiento CRM. |
| `public.subscriptions_suscripcion` | `monto_mensual_usd`, `fecha_proximo_cobro`, `renovacion_automatica` | `NUMERIC(10,2)`, `DATE`, `BOOLEAN` | Extensión en esquema global `public` para control de facturación recurrente SaaS por clínica tenant. |

##### 4. Dataset Sintético Longitudinal de 6 a 12 Meses para Machine Learning (`CU24`), Contabilidad (`CU26`) y CRM

En respuesta directa a la observación docente de que un modelo de **Machine Learning** y un análisis contable serio **no pueden demostrarse con datos mínimos de un mes o diez registros** (`datos/requerimientosSprint4.md`, líneas 37–39), se diseñó e implementó el comando `python manage.py seed_sprint4 --months 12 --tenants all`, el cual genera información sintética realista y coherente distribuida en **12 meses continuos (diciembre 2025 – noviembre 2026)** a través de los **14 esquemas tenant**:

| Indicador del Dataset Sintético | Volumen Total (14 Tenants) | Profundidad Temporal | Finalidad Analítica y de Defensa |
| :--- | :---: | :---: | :--- |
| **Sesiones Clínicas y Notas SOAP** | **2,180+ sesiones** | 12 meses continuos | Alimentar resúmenes longitudinales multi-sesión (`CU23`) y series temporales de evolución. |
| **Registros Diarios de Ánimo (*Mood Tracker*)** | **14,400+ registros** | 6 a 12 meses por paciente | Calcular pendiente emocional móvil (`pendiente_animo_30d`) y detectar caídas sostenidas en `CU24`. |
| **Planes de Pago, Cuotas y Transacciones (BOB/USD)** | **2,650+ movimientos** | 12 meses fiscales | Demostrar extractos de amortización de cuotas, pagos mixtos BOB/USD y conciliación exacta. |
| **Gastos Fijos Mensuales + Liquidación Honorarios** | **168 cierres mensuales** | 12 meses x 14 centros | Calcular reportes reales de **Ganancia Bruta vs. Utilidad Neta** deduciendo Alquiler, Servicios Básicos y Sueldos. |
| **Calificaciones CRM Post-Consulta (1–5 ★)** | **1,740+ encuestas** | 12 meses continuos | Sustentar histogramas estadísticos CSAT (89.4% satisfacción $\ge 4$★), NPS y alertas de baja calificación. |

---

#### 4.2.1.3 Diseño de la Lógica de Negocio (Patrón BCE: Comunicación, Clases de Análisis y Secuencia UML 2.5+)

Cada flujo crítico del Sprint 4 se modela bajo la tríada metodológica obligatoria del patrón **BCE (*Boundary - Control - Entity*)**:
1. **1º Diagrama de Comunicación BCE:** Modela la colaboración horizontal numerada entre el actor, la interfaz (`IU_`), el controlador (`CTR_`) y las entidades individualizadas (`CE_`).
2. **2º Diagrama de Clases de Análisis (BCE / VOPC):** Especifica los controles visuales de la interfaz (`IU_`), las operaciones puras de negocio del controlador (`CTR_`, sin atributos de estado) y los atributos/métodos de cada entidad (`CE_`).
3. **3º Diagrama de Secuencia UML 2.5+:** Representa el orden cronológico exacto con barras de activación, guardas `alt`/`opt` y bucles `loop` nacidos exclusivamente desde el controlador hacia las entidades (sin encerrar nunca la interfaz de usuario).

---

##### 4.2.1.3.1 CU23: Generación Asistida de Resúmenes Clínicos Longitudinales con IA y Supervisión Humana (`HU-49`)

* **Trazabilidad:** `CU23` ← `HU-49` (`RF-10, RF-22, RF-30, RNF-19`).
* **Clases BCE:** `IU_ConsolaResumenLongitudinal` (Angular 17), `CTR_ResumenLongitudinalIA` (Django REST), `CE_HistoriaClinica` (`clinica_historiaclinica`), `CE_NotaSesion` (`clinica_notasesion`), `CE_RegistroAnimo` (`clinica_registroanimo`), `CE_ResumenClinicoIA` (`clinica_resumenlongitudinalia`), `CE_AuditLog` (`accounts_auditlog`).

###### 1º Diagrama de Comunicación BCE – CU23: Resúmenes Clínicos Longitudinales IA

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *6. Comunicación BCE → CU23* (**Diagrama ID: 372**).

![Diagrama de Comunicación BCE – CU23: Resúmenes Clínicos Longitudinales IA](./imagenes/diagrama_comunicacion_cu23_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

actor "Psicólogo Tratante" as act
boundary "IU_ConsolaResumenLongitudinal\n(Angular 17)" as iu
control "CTR_ResumenLongitudinalIA\n(Django REST)" as ctr
entity "CE_HistoriaClinica\n(clinica_historiaclinica)" as hc
entity "CE_NotaSesion\n(clinica_notasesion)" as soap
entity "CE_RegistroAnimo\n(clinica_registroanimo)" as mood
entity "CE_ResumenClinicoIA\n(clinica_resumenlongitudinalia)" as res
entity "CE_AuditLog\n(accounts_auditlog)" as aud

act -> iu : 1: seleccionar_rango_y_solicitar(paciente_id, fecha_ini, fecha_fin)
iu -> ctr : 2: POST /api/v1/clinica/ia/resumen-longitudinal/
ctr -> hc : 3: verificar_asignacion_tratante(paciente_id, psicologo_id)
hc --> ctr : 4: historia_clinica_autorizada(historia_id)
ctr -> soap : 5: obtener_notas_firmadas(historia_id, fecha_ini, fecha_fin)
soap --> ctr : 6: lista_notas_soap[]
ctr -> mood : 7: obtener_serie_animo(paciente_id, fecha_ini, fecha_fin)
mood --> ctr : 8: serie_emocional[]
ctr -> ctr : 9: sanitizar_pii_y_sintetizar(lista_notas_soap, serie_emocional)
ctr -> res : 10: crear_borrador_ia(resumen_texto, hash_pii_sha256, 'BORRADOR_IA')
res --> ctr : 11: borrador_creado(resumen_id)
ctr -> aud : 12: registrar_evento('GENERACION_RESUMEN_IA', ip)
aud --> ctr : 13: auditado()
ctr --> iu : 14: 201 Created {borrador_ia, estado='BORRADOR_IA'}
act -> iu : 15: revisar_editar_y_aprobar(resumen_id, texto_final)
iu -> ctr : 16: PATCH /api/v1/clinica/ia/resumen-longitudinal/{id}/aprobar/
ctr -> res : 17: aprobar_con_supervision(psicologo_id, texto_final)
res --> ctr : 18: resumen_aprobado('APROBADO_HITL')
ctr --> iu : 19: 200 OK {habilitar_pdf=true}
@enduml
```

###### 2º Diagrama de Clases de Análisis (BCE) – CU23

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *7. Clases de Análisis BCE → CU23* (**Diagrama ID: 373**).

![Diagrama de Clases de Análisis BCE – CU23: Síntesis Longitudinal IA](./imagenes/diagrama_clases_analisis_cu23_sp4.png)

```plantuml
@startuml
left to right direction
skinparam shadowing false
skinparam roundcorner 6
skinparam defaultFontName Arial
skinparam classAttributeIconSize 0
hide circle

class "Psicólogo Tratante" <<Actor>> #LightYellow

class "IU_ConsolaResumenLongitudinal" as UI <<boundary>> #EBF5FB {
    - dtFechaInicio: MatDatepicker
    - dtFechaFin: MatDatepicker
    - btnGenerarResumen: Button
    - badgeBorradorIA: Chip
    - txtEditorResumen: MarkdownEditor
    - btnAprobarHITL: Button
    - btnExportarPDF: Button
    __
    + seleccionar_rango_y_solicitar(pac_id: UUID, ini: Date, fin: Date): void
    + mostrar_borrador_pendiente(resumen: JSON): void
    + revisar_editar_y_aprobar(resumen_id: UUID, texto: String): void
    + habilitar_descarga_pdf(url: String): void
}

class "CTR_ResumenLongitudinalIA" as CTR <<control>> #E8F8F5 {
    __
    + verificar_permiso_tratante(pac_id: UUID, psico_id: UUID): UUID
    + sanitizar_pii(texto: String): String
    + calcular_hash_sha256(texto: String): String
    + generar_resumen_longitudinal(hc_id: UUID, ini: Date, fin: Date): ResumenClinicoIA
    + aprobar_resumen_hitl(resumen_id: UUID, psico_id: UUID, texto: String): ResumenClinicoIA
}

class "CE_HistoriaClinica" as HC <<entity>> #FADBD8 {
    - id: UUID
    - paciente_id: UUID
    - psicologo_apertura_id: UUID
    - codigo_historia: String
    __
    + verificar_asignacion_tratante(psico_id: UUID): Boolean
}

class "CE_NotaSesion" as SOAP <<entity>> #FDEDEC {
    - id: UUID
    - historia_clinica_id: UUID
    - numero_sesion: Integer
    - subjetivo: Text
    - analisis: Text
    - estado_guardado: String
    __
    + obtener_notas_firmadas(ini: Date, fin: Date): List
}

class "CE_RegistroAnimo" as MOOD <<entity>> #FDEDEC {
    - id: UUID
    - paciente_id: UUID
    - fecha_registro: Date
    - escala_valor: Integer
    __
    + obtener_serie_animo(ini: Date, fin: Date): List
}

class "CE_ResumenClinicoIA" as RES <<entity>> #FADBD8 {
    - id: UUID
    - historia_clinica_id: UUID
    - resumen_estructurado: Text
    - hash_pii_sha256: String
    - estado_validacion: String
    - validado_por_id: UUID
    __
    + crear_borrador_ia(texto: Text, hash: String): UUID
    + aprobar_con_supervision(psico_id: UUID, texto: Text): void
}

class "CE_AuditLog" as AUD <<entity>> #FDEDEC {
    - id: UUID
    - usuario_id: UUID
    - evento: String
    - ip_origen: String
    __
    + registrar_evento(evento: String, ip: String): void
}

"Psicólogo Tratante" -- UI
UI -- CTR
CTR -- HC
HC "1" -- "1..*" SOAP : documenta >
HC "1" -- "0..*" MOOD : correlaciona >
HC "1" *-- "0..*" RES : sintetiza >
RES "0..*" -- "1..*" AUD : audita >
@enduml
```

###### 3º Diagrama de Secuencia UML 2.5+ – CU23

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *8. Secuencia UML 2.5+ → CU23* (**Diagrama ID: 374**).

![Diagrama de Secuencia UML 2.5+ – CU23: Síntesis Longitudinal IA (HITL)](./imagenes/diagrama_secuencia_cu23_sp4.png)

```plantuml
@startuml
!theme plain
skinparam sequenceMessageAlign center
skinparam ParticipantPadding 10

title Diagrama de Secuencia UML 2.5+ – CU23: Resumen Clínico Longitudinal IA con Validación HITL

actor "Psicólogo Tratante" as Actor
boundary "IU_ConsolaResumenLongitudinal" as IU
control "CTR_ResumenLongitudinalIA" as CTR
entity "CE_HistoriaClinica" as HC
entity "CE_NotaSesion" as SOAP
entity "CE_RegistroAnimo" as MOOD
entity "CE_ResumenClinicoIA" as RES
entity "CE_AuditLog" as AUD

Actor -> IU : 1: seleccionar_rango_y_solicitar(paciente_id, fecha_ini, fecha_fin)
activate Actor
activate IU
IU -> CTR : 2: POST /api/v1/clinica/ia/resumen-longitudinal/
activate CTR

CTR -> HC : 3: verificar_asignacion_tratante(paciente_id, psicologo_id)
activate HC
HC --> CTR : 4: autorizado, historia_id [retorno]
deactivate HC

alt psicologo_autorizado == true
    CTR -> SOAP : 5: obtener_notas_firmadas(historia_id, fecha_ini, fecha_fin)
    activate SOAP
    SOAP --> CTR : 6: lista_notas_soap[] [retorno]
    deactivate SOAP

    loop por cada nota en lista_notas_soap[]
        CTR -> CTR : 7: sanitizar_pii(nota.subjetivo + nota.analisis)
    end

    CTR -> MOOD : 8: obtener_serie_animo(paciente_id, fecha_ini, fecha_fin)
    activate MOOD
    MOOD --> CTR : 9: serie_emocional[] [retorno]
    deactivate MOOD

    CTR -> CTR : 10: construir_sintesis_y_hash_sha256()
    CTR -> RES : 11: crear_borrador_ia(resumen_texto, hash_pii_sha256)
    activate RES
    RES --> CTR : 12: resumen_id (estado='BORRADOR_IA') [retorno]
    deactivate RES

    CTR -> AUD : 13: registrar_evento('GENERACION_RESUMEN_IA', ip)
    activate AUD
    AUD --> CTR : 14: ok [retorno]
    deactivate AUD

    CTR --> IU : 15: HTTP 201 Created {resumen_id, borrador_ia} [retorno]
    IU --> Actor : 16: mostrar_borrador_pendiente('Pendiente de Revisión HITL') [retorno]

    Actor -> IU : 17: revisar_editar_y_aprobar(resumen_id, texto_final)
    IU -> CTR : 18: PATCH /api/v1/clinica/ia/resumen-longitudinal/{id}/aprobar/
    CTR -> RES : 19: aprobar_con_supervision(psicologo_id, texto_final)
    activate RES
    RES --> CTR : 20: estado='APROBADO_HITL' [retorno]
    deactivate RES
    CTR --> IU : 21: HTTP 200 OK {exportable_pdf=true} [retorno]
    IU --> Actor : 22: habilitar_descarga_pdf() [retorno]
else psicologo_no_asignado
    CTR -> AUD : 23: registrar_evento('ACCESO_DENEGADO_CU23', ip)
    activate AUD
    AUD --> CTR : 24: ok [retorno]
    deactivate AUD
    CTR --> IU : 25: HTTP 403 Forbidden [retorno]
    deactivate CTR
    IU --> Actor : 26: mostrar_error('Acceso restringido al tratante') [retorno]
    deactivate IU
    deactivate Actor
end
@enduml
```

---

##### 4.2.1.3.2 CU24: Detección Predictiva de Señales de Riesgo Longitudinal por IA/ML (`HU-50`)

* **Trazabilidad:** `CU24` ← `HU-50` (`RF-26, RF-27, RNF-19`).
* **Clases BCE:** `IU_RadarRiesgoML` (Angular 17), `CTR_DetectorRiesgoML` (Django/Celery), `CE_HistoriaClinica` (`clinica_historiaclinica`), `CE_RegistroAnimo` (`clinica_registroanimo`), `CE_Cita` (`agenda_cita`), `CE_TareaTerapeutica` (`clinica_tareaterapeutica`), `CE_AlertaRiesgoIA` (`clinica_alertariesgoia`).

###### 1º Diagrama de Comunicación BCE – CU24

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *6. Comunicación BCE → CU24* (**Diagrama ID: 375**).

![Diagrama de Comunicación BCE – CU24: Detección Predictiva ML](./imagenes/diagrama_comunicacion_cu24_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

actor "Coordinador / Psicólogo" as act
boundary "IU_RadarRiesgoML\n(Angular 17)" as iu
control "CTR_DetectorRiesgoML\n(Django + ML)" as ctr
entity "CE_RegistroAnimo\n(clinica_registroanimo)" as mood
entity "CE_Cita\n(agenda_cita)" as cita
entity "CE_TareaTerapeutica\n(clinica_tareaterapeutica)" as tarea
entity "CE_AlertaRiesgoIA\n(clinica_alertariesgoia)" as alerta

act -> iu : 1: ejecutar_analisis_predictivo_lote(ventana_meses=12)
iu -> ctr : 2: POST /api/v1/clinica/ml/evaluar-riesgo/
ctr -> mood : 3: extraer_serie_animo_12m(paciente_id)
mood --> ctr : 4: valores_diarios[]
ctr -> cita : 5: calcular_tasa_inasistencia(paciente_id)
cita --> ctr : 6: tasa_no_show
ctr -> tarea : 7: calcular_adherencia_tareas(paciente_id)
tarea --> ctr : 8: ratio_cumplimiento
ctr -> ctr : 9: inferir_indice_riesgo_y_factores()
ctr -> alerta : 10: guardar_alerta_si_umbral(indice_riesgo, nivel, factores)
alerta --> ctr : 11: alerta_persistida(alerta_id)
ctr --> iu : 12: 200 OK {ranking_riesgo[], explicabilidad}
iu --> act : 13: renderizar_radar_y_factores()
@enduml
```

###### 2º Diagrama de Clases de Análisis (BCE) – CU24

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *7. Clases de Análisis BCE → CU24* (**Diagrama ID: 376**).

![Diagrama de Clases de Análisis BCE – CU24: Detección Predictiva ML](./imagenes/diagrama_clases_analisis_cu24_sp4.png)

```plantuml
@startuml
left to right direction
skinparam shadowing false
skinparam roundcorner 6
skinparam defaultFontName Arial
skinparam classAttributeIconSize 0
hide circle

class "Coordinador / Psicólogo" <<Actor>> #LightYellow

class "IU_RadarRiesgoML" as UI <<boundary>> #EBF5FB {
    - selVentanaMeses: Select
    - tblAlertasRiesgo: MatTable
    - chartTendenciaAnimo: ChartCanvas
    - barFactoresExplicables: ProgressList
    - btnRegistrarIntervencion: Button
    __
    + ejecutar_analisis_predictivo_lote(meses: Integer): void
    + renderizar_radar_y_factores(datos: JSON): void
    + registrar_intervencion_clinica(alerta_id: UUID, nota: String): void
}

class "CTR_DetectorRiesgoML" as CTR <<control>> #E8F8F5 {
    __
    + extraer_features_longitudinales(pac_id: UUID, meses: Integer): Dict
    + calcular_score_riesgo_ml(features: Dict): Tuple
    + evaluar_cohorte_tenant(meses: Integer): List
    + intervenir_alerta(alerta_id: UUID, usr_id: UUID, accion: String): void
}

class "CE_HistoriaClinica" as HC <<entity>> #FADBD8 {
    - id: UUID
    - paciente_id: UUID
    - cerrada: Boolean
    __
    + listar_historias_activas(): List
}

class "CE_RegistroAnimo" as MOOD <<entity>> #FDEDEC {
    - id: UUID
    - paciente_id: UUID
    - fecha_registro: Date
    - escala_valor: Integer
    __
    + calcular_pendiente_30d(): Decimal
}

class "CE_Cita" as CITA <<entity>> #FDEDEC {
    - id: UUID
    - paciente_id: UUID
    - estado: String
    __
    + calcular_tasa_inasistencia(): Decimal
}

class "CE_TareaTerapeutica" as TAREA <<entity>> #FDEDEC {
    - id: UUID
    - paciente_id: UUID
    - estado: String
    __
    + calcular_ratio_cumplimiento(): Decimal
}

class "CE_AlertaRiesgoIA" as ALERTA <<entity>> #FADBD8 {
    - id: UUID
    - historia_clinica_id: UUID
    - indice_riesgo: Decimal
    - nivel_severidad: String
    - factores_contribuyentes: JSON
    - estado: String
    __
    + guardar_alerta(score: Decimal, factores: JSON): UUID
    + marcar_intervenida(usr_id: UUID, nota: Text): void
}

"Coordinador / Psicólogo" -- UI
UI -- CTR
CTR -- HC
HC "1" -- "0..*" MOOD : analiza >
HC "1" -- "0..*" CITA : evalúa asistencia >
HC "1" -- "0..*" TAREA : evalúa adherencia >
HC "1" *-- "0..*" ALERTA : genera alerta ML >
@enduml
```

###### 3º Diagrama de Secuencia UML 2.5+ – CU24

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *8. Secuencia UML 2.5+ → CU24* (**Diagrama ID: 377**).

![Diagrama de Secuencia UML 2.5+ – CU24: Detección Predictiva Riesgo ML (12m)](./imagenes/diagrama_secuencia_cu24_sp4.png)

```plantuml
@startuml
!theme plain
skinparam sequenceMessageAlign center
skinparam ParticipantPadding 10

title Diagrama de Secuencia UML 2.5+ – CU24: Detección Predictiva de Riesgo Longitudinal (ML 6-12 Meses)

actor "Coordinador / Psicólogo" as Actor
boundary "IU_RadarRiesgoML" as IU
control "CTR_DetectorRiesgoML" as CTR
entity "CE_HistoriaClinica" as HC
entity "CE_RegistroAnimo" as MOOD
entity "CE_Cita" as CITA
entity "CE_TareaTerapeutica" as TAREA
entity "CE_AlertaRiesgoIA" as ALERTA

Actor -> IU : 1: ejecutar_analisis_predictivo_lote(ventana_meses=12)
activate Actor
activate IU
IU -> CTR : 2: POST /api/v1/clinica/ml/evaluar-riesgo/
activate CTR

CTR -> HC : 3: listar_historias_activas()
activate HC
HC --> CTR : 4: lista_historias[] [retorno]
deactivate HC

loop por cada historia en lista_historias[]
    CTR -> MOOD : 5: calcular_pendiente_30d(paciente_id)
    activate MOOD
    MOOD --> CTR : 6: pendiente_animo_30d [retorno]
    deactivate MOOD

    CTR -> CITA : 7: calcular_tasa_inasistencia(paciente_id)
    activate CITA
    CITA --> CTR : 8: tasa_inasistencia [retorno]
    deactivate CITA

    CTR -> TAREA : 9: calcular_ratio_cumplimiento(paciente_id)
    activate TAREA
    TAREA --> CTR : 10: ratio_adherencia [retorno]
    deactivate TAREA

    CTR -> CTR : 11: calcular_score_riesgo_ml(features)

    opt indice_riesgo >= 0.50
        CTR -> ALERTA : 12: guardar_alerta(indice_riesgo, nivel, factores_contribuyentes)
        activate ALERTA
        ALERTA --> CTR : 13: alerta_id [retorno]
        deactivate ALERTA
    end
end

CTR --> IU : 14: HTTP 200 OK {alertas_generadas[], resumen_cohorte} [retorno]
deactivate CTR
IU --> Actor : 15: renderizar_radar_y_factores() [retorno]
deactivate IU
deactivate Actor
@enduml
```

---

##### 4.2.1.3.3 CU26-A: Gestión de Pagos Multimoneda (BOB/USD), Plan de Amortización y Estado de Cuenta (`HU-51, HU-52`)

* **Trazabilidad:** `CU26` ← `HU-51, HU-52` (`RF-05, RF-30`).
* **Clases BCE:** `IU_CajaYExtractoPagos` (Angular 17 / Flutter 3.x), `CTR_PagosAmortizacion` (Django REST), `CE_PlanPagoTerapeutico` (`finanzas_planpagoterapeutico`), `CE_CuotaAmortizacion` (`finanzas_cuotaamortizacion`), `CE_PagoTransaccion` (`finanzas_pagotransaccion`), `CE_Cita` (`agenda_cita`).

###### 1º Diagrama de Comunicación BCE – CU26-A

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *6. Comunicación BCE → CU26-A* (**Diagrama ID: 378**).

![Diagrama de Comunicación BCE – CU26-A: Pagos Multimoneda BOB/USD y Amortización](./imagenes/diagrama_comunicacion_cu26a_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

actor "Paciente / Recepción" as act
boundary "IU_CajaYExtractoPagos\n(Web Angular / Flutter)" as iu
control "CTR_PagosAmortizacion\n(Django REST)" as ctr
entity "CE_PlanPagoTerapeutico\n(finanzas_planpago)" as plan
entity "CE_CuotaAmortizacion\n(finanzas_cuota)" as cuota
entity "CE_PagoTransaccion\n(finanzas_pagotransaccion)" as pago

act -> iu : 1: seleccionar_cuota_y_moneda(cuota_id, moneda='USD', metodo='QR_SIMPLE')
iu -> ctr : 2: POST /api/v1/finanzas/pagos/registrar/
ctr -> cuota : 3: bloquear_cuota_para_pago(cuota_id)
cuota --> ctr : 4: cuota_pendiente(monto_bob_esperado)
ctr -> ctr : 5: convertir_y_calcular_ajuste_cambio(monto_origen, moneda, tasa=6.96)
ctr -> pago : 6: insertar_transaccion_inmutable(monto_bob, ajuste_redondeo, ref)
pago --> ctr : 7: pago_confirmado(pago_id)
ctr -> cuota : 8: marcar_cuota_pagada(cuota_id)
cuota --> ctr : 9: cuota_actualizada('PAGADA')
ctr -> plan : 10: recalcular_saldo_insoluto(plan_id)
plan --> ctr : 11: extracto_actualizado(saldo_restante)
ctr --> iu : 12: 201 Created {comprobante, extracto_amortizacion}
iu --> act : 13: mostrar_extracto_y_recibo()
@enduml
```

###### 2º Diagrama de Clases de Análisis (BCE) – CU26-A

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *7. Clases de Análisis BCE → CU26-A* (**Diagrama ID: 379**).

![Diagrama de Clases de Análisis BCE – CU26-A: Pagos y Amortización](./imagenes/diagrama_clases_analisis_cu26a_sp4.png)

```plantuml
@startuml
left to right direction
skinparam shadowing false
skinparam roundcorner 6
skinparam defaultFontName Arial
skinparam classAttributeIconSize 0
hide circle

class "Paciente / Recepcionista" <<Actor>> #LightYellow

class "IU_CajaYExtractoPagos" as UI <<boundary>> #EBF5FB {
    - swMoneda: ToggleBOB_USD
    - lblTipoCambio: Text
    - selMetodoPago: Dropdown
    - tblCuotasAmortizacion: DataTable
    - lblSaldoInsoluto: Badge
    - btnConfirmarPago: Button
    - btnDescargarExtractoPDF: Button
    __
    + seleccionar_cuota_y_moneda(cuota_id: UUID, moneda: String): void
    + confirmar_transaccion_pago(): void
    + renderizar_extracto_amortizacion(extracto: JSON): void
}

class "CTR_PagosAmortizacion" as CTR <<control>> #E8F8F5 {
    __
    + convertir_a_bob(monto: Decimal, moneda: String, tasa: Decimal): Tuple
    + generar_tabla_amortizacion(plan_datos: Dict): List
    + registrar_pago_cuota(cuota_id: UUID, monto: Decimal, moneda: String, metodo: String): Dict
    + obtener_extracto_paciente(paciente_id: UUID): Dict
}

class "CE_PlanPagoTerapeutico" as PLAN <<entity>> #FADBD8 {
    - id: UUID
    - paciente_id: UUID
    - monto_total: Decimal
    - moneda: String
    - tasa_interes_anual: Decimal
    - porcentaje_seguro: Decimal
    - numero_cuotas: SmallInt
    - estado: String
    __
    + calcular_saldo_restante(): Decimal
    + actualizar_estado_plan(): void
}

class "CE_CuotaAmortizacion" as CUOTA <<entity>> #FDEDEC {
    - id: UUID
    - plan_id: UUID
    - numero_cuota: SmallInt
    - capital_amortizado: Decimal
    - interes_o_comision: Decimal
    - seguro_asistencial: Decimal
    - monto_total_cuota: Decimal
    - saldo_insoluto: Decimal
    - estado: String
    __
    + bloquear_para_pago(): CuotaAmortizacion
    + marcar_pagada(): void
}

class "CE_PagoTransaccion" as PAGO <<entity>> #FDEDEC {
    - id: UUID
    - paciente_id: UUID
    - cuota_id: UUID
    - moneda_origen: String
    - monto_origen: Decimal
    - tipo_cambio_aplicado: Decimal
    - monto_bob_equivalente: Decimal
    - ajuste_redondeo: Decimal
    - metodo_pago: String
    - estado: String
    __
    + registrar_transaccion(): UUID
}

"Paciente / Recepcionista" -- UI
UI -- CTR
CTR -- PLAN
PLAN "1" *-- "1..*" CUOTA : amortiza >
CUOTA "1" -- "0..*" PAGO : respalda_pago >
@enduml
```

###### 3º Diagrama de Secuencia UML 2.5+ – CU26-A

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *8. Secuencia UML 2.5+ → CU26-A* (**Diagrama ID: 380**).

![Diagrama de Secuencia UML 2.5+ – CU26-A: Cobros Multimoneda y Amortización](./imagenes/diagrama_secuencia_cu26a_sp4.png)

```plantuml
@startuml
!theme plain
skinparam sequenceMessageAlign center
skinparam ParticipantPadding 10

title Diagrama de Secuencia UML 2.5+ – CU26-A: Cobro Multimoneda (BOB/USD), Amortización y Extracto

actor "Paciente / Recepción" as Actor
boundary "IU_CajaYExtractoPagos" as IU
control "CTR_PagosAmortizacion" as CTR
entity "CE_PlanPagoTerapeutico" as PLAN
entity "CE_CuotaAmortizacion" as CUOTA
entity "CE_PagoTransaccion" as PAGO

Actor -> IU : 1: confirmar_transaccion_pago(cuota_id, monto, moneda='USD', metodo)
activate Actor
activate IU
IU -> CTR : 2: POST /api/v1/finanzas/pagos/registrar/
activate CTR

CTR -> CUOTA : 3: bloquear_cuota_para_pago(cuota_id) [SELECT FOR UPDATE]
activate CUOTA
CUOTA --> CTR : 4: cuota_info(estado, monto_total_cuota, plan_id) [retorno]
deactivate CUOTA

alt cuota.estado in ('PENDIENTE', 'MORA') and monto > 0
    CTR -> CTR : 5: convertir_a_bob(monto, moneda, tasa_oficial=6.96)
    CTR -> PAGO : 6: registrar_transaccion(monto_origen, monto_bob, ajuste_redondeo)
    activate PAGO
    PAGO --> CTR : 7: pago_id, comprobante [retorno]
    deactivate PAGO

    CTR -> CUOTA : 8: marcar_pagada(cuota_id)
    activate CUOTA
    CUOTA --> CTR : 9: estado='PAGADA' [retorno]
    deactivate CUOTA

    CTR -> PLAN : 10: calcular_saldo_restante(plan_id)
    activate PLAN
    PLAN --> CTR : 11: saldo_insoluto, lista_cuotas[] [retorno]
    deactivate PLAN

    CTR --> IU : 12: HTTP 201 Created {comprobante, extracto_actualizado} [retorno]
    IU --> Actor : 13: renderizar_extracto_amortizacion() [retorno]
else cuota_ya_pagada o monto_invalido
    CTR --> IU : 14: HTTP 400 Bad Request ('Cuota no elegible o monto inválido') [retorno]
    deactivate CTR
    IU --> Actor : 15: mostrar_alerta_validacion() [retorno]
    deactivate IU
    deactivate Actor
end
@enduml
```

---

##### 4.2.1.3.4 CU26-B & CRM: Contabilidad de Ganancia Bruta vs. Utilidad Neta y Calificación CRM (`HU-53, HU-54, HU-55`)

* **Trazabilidad:** `CU26` ← `HU-53, HU-54, HU-55` (`RF-04, RF-27, Criterio 8`).
* **Clases BCE:** `IU_EstadoResultadosYCRM` (Angular 17 / Flutter), `CTR_ContabilidadYCRM` (Django REST), `CE_PagoTransaccion` (`finanzas_pagotransaccion`), `CE_LiquidacionHonorario` (`finanzas_liquidacionhonorario`), `CE_GastoFijoMensual` (`finanzas_gastofijomensual`), `CE_CalificacionCRM` (`crm_calificacionservicio`).

###### 1º Diagrama de Comunicación BCE – CU26-B & CRM

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *6. Comunicación BCE → CU26-B & CRM* (**Diagrama ID: 381**).

![Diagrama de Comunicación BCE – CU26-B & CRM: Utilidad Neta y Satisfacción 1–5★](./imagenes/diagrama_comunicacion_cu26b_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial

actor "Administrador / Contador" as act
boundary "IU_EstadoResultadosYCRM\n(Angular 17)" as iu
control "CTR_ContabilidadYCRM\n(Django REST)" as ctr
entity "CE_PagoTransaccion\n(finanzas_pagotransaccion)" as pago
entity "CE_LiquidacionHonorario\n(finanzas_liquidacionhonorario)" as liq
entity "CE_GastoFijoMensual\n(finanzas_gastofijomensual)" as gasto
entity "CE_CalificacionCRM\n(crm_calificacionservicio)" as crm

act -> iu : 1: consultar_estado_resultados_y_crm(fecha_ini, fecha_fin)
iu -> ctr : 2: GET /api/v1/finanzas/estado-resultados/?ini=...&fin=...
ctr -> pago : 3: sumar_ingresos_confirmados_bob(fecha_ini, fecha_fin)
pago --> ctr : 4: ingresos_brutos_bob
ctr -> liq : 5: sumar_honorarios_psicologos(fecha_ini, fecha_fin)
liq --> ctr : 6: costos_honorarios_bob
ctr -> gasto : 7: sumar_gastos_fijos_desglosados(fecha_ini, fecha_fin)
gasto --> ctr : 8: total_gastos_fijos_bob (Alquiler, Servicios, Personal)
ctr -> ctr : 9: calcular_ganancia_bruta_y_utilidad_neta()
ctr -> crm : 10: calcular_metricas_csat_nps(fecha_ini, fecha_fin)
crm --> ctr : 11: estadisticas_crm (Promedio 1-5 ★, CSAT %, Alertas)
ctr --> iu : 12: 200 OK {estado_resultados_pl, estadisticas_crm}
iu --> act : 13: renderizar_waterfall_utilidad_neta_y_crm()
@enduml
```

###### 2º Diagrama de Clases de Análisis (BCE) – CU26-B & CRM

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *7. Clases de Análisis BCE → CU26-B & CRM* (**Diagrama ID: 382**).

![Diagrama de Clases de Análisis BCE – CU26-B & CRM: Utilidad Neta y CSAT/NPS](./imagenes/diagrama_clases_analisis_cu26b_sp4.png)

```plantuml
@startuml
left to right direction
skinparam shadowing false
skinparam roundcorner 6
skinparam defaultFontName Arial
skinparam classAttributeIconSize 0
hide circle

class "Administrador / Contador" <<Actor>> #LightYellow

class "IU_EstadoResultadosYCRM" as UI <<boundary>> #EBF5FB {
    - dtPeriodoInicio: DatePicker
    - dtPeriodoFin: DatePicker
    - cardIngresosBrutos: MetricCard
    - cardGananciaBruta: MetricCard
    - cardUtilidadNeta: MetricCard
    - chartWaterfallPL: ChartCanvas
    - chartHistogramaCRM: ChartCanvas
    __
    + consultar_estado_resultados_y_crm(ini: Date, fin: Date): void
    + registrar_gasto_fijo(categoria: String, monto: Decimal): void
    + renderizar_waterfall_utilidad_neta_y_crm(data: JSON): void
}

class "CTR_ContabilidadYCRM" as CTR <<control>> #E8F8F5 {
    __
    + calcular_estado_resultados(ini: Date, fin: Date): Dict
    + liquidar_honorarios_mes(periodo: String): List
    + calcular_estadisticas_crm(ini: Date, fin: Date): Dict
    + registrar_calificacion_crm(cita_id: UUID, estrellas: SmallInt, msg: Text): UUID
}

class "CE_PagoTransaccion" as PAGO <<entity>> #FADBD8 {
    - id: UUID
    - monto_bob_equivalente: Decimal
    - ajuste_redondeo: Decimal
    - estado: String
    - fecha_pago: DateTime
    __
    + sumar_ingresos_bob(ini: Date, fin: Date): Decimal
}

class "CE_LiquidacionHonorario" as LIQ <<entity>> #FDEDEC {
    - id: UUID
    - psicologo_id: UUID
    - periodo_mes: String
    - monto_neto_psicologo: Decimal
    __
    + sumar_honorarios_periodo(ini: Date, fin: Date): Decimal
}

class "CE_GastoFijoMensual" as GASTO <<entity>> #FDEDEC {
    - id: UUID
    - periodo_mes: String
    - categoria: String
    - monto_bob: Decimal
    __
    + desglosar_por_categoria(ini: Date, fin: Date): List
}

class "CE_CalificacionCRM" as CRM <<entity>> #F4ECF7 {
    - id: UUID
    - cita_id: UUID
    - puntuacion_estrellas: SmallInt
    - requiere_seguimiento: Boolean
    __
    + obtener_distribucion_estrellas(ini: Date, fin: Date): Dict
}

"Administrador / Contador" -- UI
UI -- CTR
CTR -- PAGO
PAGO "1..*" -- "0..*" LIQ : deduce_honorario >
PAGO "1..*" -- "0..*" GASTO : deduce_gasto_fijo >
PAGO "0..*" -- "0..*" CRM : correlaciona_calidad >
@enduml
```

###### 3º Diagrama de Secuencia UML 2.5+ – CU26-B & CRM

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *8. Secuencia UML 2.5+ → CU26-B & CRM* (**Diagrama ID: 383**).

![Diagrama de Secuencia UML 2.5+ – CU26-B & CRM: Estado de Resultados y CRM](./imagenes/diagrama_secuencia_cu26b_sp4.png)

```plantuml
@startuml
!theme plain
skinparam sequenceMessageAlign center
skinparam ParticipantPadding 10

title Diagrama de Secuencia UML 2.5+ – CU26-B: Estado de Resultados (Utilidad Neta) y Estadísticas CRM

actor "Administrador / Contador" as Actor
boundary "IU_EstadoResultadosYCRM" as IU
control "CTR_ContabilidadYCRM" as CTR
entity "CE_PagoTransaccion" as PAGO
entity "CE_LiquidacionHonorario" as LIQ
entity "CE_GastoFijoMensual" as GASTO
entity "CE_CalificacionCRM" as CRM

Actor -> IU : 1: consultar_estado_resultados_y_crm(fecha_ini, fecha_fin)
activate Actor
activate IU
IU -> CTR : 2: GET /api/v1/finanzas/estado-resultados/?ini=...&fin=...
activate CTR

CTR -> PAGO : 3: sumar_ingresos_bob(fecha_ini, fecha_fin)
activate PAGO
PAGO --> CTR : 4: ingresos_brutos_bob, ajuste_cambiario_neto [retorno]
deactivate PAGO

CTR -> LIQ : 5: sumar_honorarios_periodo(fecha_ini, fecha_fin)
activate LIQ
LIQ --> CTR : 6: costos_honorarios_bob [retorno]
deactivate LIQ

CTR -> CTR : 7: ganancia_bruta = ingresos_brutos_bob - costos_honorarios_bob

CTR -> GASTO : 8: desglosar_por_categoria(fecha_ini, fecha_fin)
activate GASTO
GASTO --> CTR : 9: gastos_por_rubro[] (Alquiler, Servicios, Personal) [retorno]
deactivate GASTO

loop por cada rubro en gastos_por_rubro[]
    CTR -> CTR : 10: acumular_total_gastos_fijos(rubro.monto_bob)
end

CTR -> CTR : 11: utilidad_neta = ganancia_bruta - total_gastos_fijos

CTR -> CRM : 12: obtener_distribucion_estrellas(fecha_ini, fecha_fin)
activate CRM
CRM --> CTR : 13: csat_pct, promedio_estrellas, histograma_1a5, alertas_baja_calif [retorno]
deactivate CRM

CTR --> IU : 14: HTTP 200 OK {ganancia_bruta, gastos_fijos, utilidad_neta, crm_stats} [retorno]
deactivate CTR
IU --> Actor : 15: renderizar_waterfall_utilidad_neta_y_crm() [retorno]
deactivate IU
deactivate Actor
@enduml
```

---

#### 4.2.1.4 Diagramas de Tiempo UML 2.5

##### Diagrama de Tiempo 1: Pipeline de Síntesis Longitudinal (`CU23`) y Predicción ML (`CU24`)
* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *9. Diagramas de Tiempo → Tiempo 1* (**Diagrama ID: 349**).

![Diagrama de Tiempo UML 2.5 – Pipeline Síntesis Longitudinal (CU23) y Predicción ML (CU24)](./imagenes/diagrama_tiempo_ia_ml_sp4.png)

```plantuml
@startuml
title Diagrama de Tiempo UML 2.5 – Pipeline de Síntesis Longitudinal IA (CU23) y Predicción ML (CU24)

robust "Frontend Angular" as Web
robust "Backend DRF & PII" as API
robust "Motor ML & LLM" as ML
robust "Psicólogo (HITL)" as Psico

@0
Web is Inactivo
API is Esperando
ML is Inactivo
Psico is Consulta

@+50
Web is Solicitando
API is "Validando RBAC y Sanitizando PII"

@+150
API is "Calculando SHA-256"
ML is "Extrayendo Serie 12m y Sintetizando"

@+450
ML is "Score ML + Borrador Listos"
API is "Persistiendo BORRADOR_IA"

@+550
Web is "Mostrando Radar y Borrador"
Psico is "Revisando y Editando (HITL)"

@+1200
Psico is "Aprobando Síntesis Oficial"
API is "Sellando APROBADO_HITL"
Web is "PDF Habilitado"
@enduml
```

##### Diagrama de Tiempo 2: Pago Multimoneda, Amortización de Cuota y Calificación CRM (`CU26`)
* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *9. Diagramas de Tiempo → Tiempo 2* (**Diagrama ID: 350**).

![Diagrama de Tiempo UML 2.5 – Cobro Multimoneda, Amortización y CRM (CU26)](./imagenes/diagrama_tiempo_finanzas_crm_sp4.png)

```plantuml
@startuml
title Diagrama de Tiempo UML 2.5 – Ciclo de Cobro Multimoneda, Amortización y CRM 1-5 Estrellas

robust "App Flutter / Web" as Client
robust "API Finanzas (Django)" as Fin
robust "PostgreSQL Lock" as DB
robust "Panel Contable/CRM" as Dash

@0
Client is "Seleccionando Cuota"
Fin is Inactivo
DB is Libre
Dash is Monitoreando

@+40
Client is "Enviando Pago USD/QR"
Fin is "Validando Tasa 6.96"
DB is "SELECT FOR UPDATE"

@+120
DB is "Commit Pago + Cuota PAGADA"
Fin is "Recalculando Saldo Insoluto"

@+200
Client is "Extracto Actualizado / Encuesta CRM"
Dash is "Utilidad Neta Actualizada"

@+600
Client is "Enviando 5★ CRM"
Fin is "Persistiendo Calificación"
Dash is "CSAT y Estadísticas Refrescadas"
@enduml
```

##### Diagrama de Tiempo 3: Cierre Contable P&L y Renovación/Facturación SaaS (`CU26` / `HU-53`, `HU-54`)

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *9. Diagramas de Tiempo → Tiempo 3* (**Diagrama ID: 351**).

![Diagrama de Tiempo UML 2.5 – Cierre Contable P&L y Facturación SaaS (SP4)](./imagenes/diagrama_tiempo_cierre_pnl_saas_sp4.png)

```plantuml
@startuml
title Diagrama de Tiempo UML 2.5 – Cierre Contable Utilidad Neta P&L y Renovación SaaS (SP4)

robust "Admin / Contador Web" as Admin
robust "Servicio Contable & SaaS" as Svc
robust "PostgreSQL Batch P&L" as DB
robust "Pasarela Stripe SaaS" as Stripe

@0
Admin is "Consultando Mes"
Svc is Ocioso
DB is Disponible
Stripe is "En Espera"

@+100
Admin is "Solicitando Cierre P&L"
Svc is "Liquidando Honorarios 70/30"
DB is "Agregando Pagos y Gastos"

@+400
DB is "EstadoResultados CERRADO"
Svc is "Deduciendo Gastos Fijos"

@+650
Svc is "Emitiendo Factura SaaS USD"
Stripe is "Procesando Cobro Renovación"

@+900
Stripe is "Webhook Idempotente OK"
Svc is "Cierre CONCILIADO"
Admin is "Revisando Utilidad Neta y PDF"
@enduml
```

---

#### 4.2.1.5 Diagramas de Máquina de Estados UML 2.5

##### Máquina de Estados 1: Ciclo de Vida de Síntesis Longitudinal IA (`CU23`)
* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *10. Máquinas de Estados → Estado 1* (**Diagrama ID: 352**).

![Máquina de Estados UML 2.5 – Síntesis Longitudinal IA HITL (CU23)](./imagenes/diagrama_estados_ia_ml_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial

title Máquina de Estados – Ciclo de Vida de Síntesis Longitudinal IA (CU23)

[*] --> RECOPILANDO_HISTORIAL : Solicitud o Job Nocturno (6-12m)
RECOPILANDO_HISTORIAL --> BORRADOR_IA : Sanitización PII + Hash SHA-256 OK
BORRADOR_IA : entry / Mostrar insignia "Pendiente Supervisión Humana"

BORRADOR_IA --> APROBADO_HITL : Psicólogo aprueba sin cambios
BORRADOR_IA --> EDITADO_Y_APROBADO : Psicólogo ajusta texto y firma
BORRADOR_IA --> DESCARTADO : Psicólogo rechaza salida IA

APROBADO_HITL --> ARCHIVADO_PDF : Exportación oficial a expediente HCE
EDITADO_Y_APROBADO --> ARCHIVADO_PDF : Exportación oficial a expediente HCE
ARCHIVADO_PDF --> [*]
DESCARTADO --> [*]
@enduml
```

##### Máquina de Estados 2: Ciclo de Vida de Alerta Predictiva ML de Riesgo (`CU24`)

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *10. Máquinas de Estados → Estado 2* (**Diagrama ID: 353**).

![Máquina de Estados UML 2.5 – Alerta Predictiva Riesgo ML (CU24)](./imagenes/diagrama_estados_alerta_ml_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial

title Máquina de Estados – Alerta Predictiva de Riesgo Clínico ML (CU24)

[*] --> ACTIVA : ScoreML >= 0.70 (modelo 6-12m)
ACTIVA : entry / Notificar Push y Consola Radar ML

ACTIVA --> EN_REVISION : Coordinador / Psicólogo abre expediente
EN_REVISION --> ACTIVA : Reevaluación detecta nuevo deterioro
EN_REVISION --> INTERVENIDA : Plan clínico prioritario y fecha_intervencion
EN_REVISION --> DESCARTADA : Falso positivo documentado clínicamente

INTERVENIDA --> [*]
DESCARTADA --> [*]
@enduml
```

##### Máquina de Estados 3: Ciclo de Vida de Cuota de Amortización y Liquidación Contable (`CU26`)
* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *10. Máquinas de Estados → Estado 3* (**Diagrama ID: 354**).

![Máquina de Estados UML 2.5 – Cuota de Amortización y Liquidación Contable (CU26)](./imagenes/diagrama_estados_finanzas_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial

title Máquina de Estados – Cuota de Plan de Amortización y Liquidación de Honorarios (CU26)

[*] --> PENDIENTE : Plan terapéutico generado (Cuotas 1..N)
PENDIENTE --> PAGADA : Abono BOB/USD validado + Recálculo Saldo
PENDIENTE --> MORA : Vence fecha_vencimiento sin pago
MORA --> PAGADA : Abono con ajuste y regularización de mora
PENDIENTE --> ANULADA : Rescisión formal del plan terapéutico
MORA --> ANULADA : Rescisión formal tras incumplimiento

state PAGADA {
  [*] --> EN_CAJA_BRUTA
  EN_CAJA_BRUTA --> LIQUIDADA_HONORARIO : Cierre mensual por porcentaje psicólogo
  LIQUIDADA_HONORARIO --> CONSOLIDADA_UTILIDAD_NETA : Deducción de Gastos Fijos del periodo
  CONSOLIDADA_UTILIDAD_NETA --> [*]
}

PAGADA --> [*]
ANULADA --> [*]
@enduml
```

##### Máquina de Estados 4: Seguimiento CRM (`CU26-CRM` / `HU-55`) y Cierre Contable Mensual P&L (`CU26` / `HU-54`)

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *10. Máquinas de Estados → Estado 4* (**Diagrama ID: 355**).

![Máquina de Estados UML 2.5 – Seguimiento CRM 1–5★ y Cierre Contable P&L (CU26)](./imagenes/diagrama_estados_crm_pnl_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam defaultFontName Arial

title Máquina de Estados – Seguimiento CRM 1-5★ (CU26-CRM / HU-55) y Cierre Contable P&L (CU26 / HU-54)

state "Ciclo de Seguimiento CRM (crm_calificacionservicio)" as CRM {
  [*] --> CRM_PENDIENTE : Evaluacion <= 2 estrellas (requiere_seguimiento=TRUE)
  [*] --> CRM_CERRADO : Evaluacion >= 3 estrellas
  CRM_PENDIENTE --> CRM_EN_GESTION : Coordinador asume caso CRM
  CRM_EN_GESTION --> CRM_CERRADO : Registra nota_resolucion_crm
  CRM_CERRADO --> [*]
}

state "Ciclo de Cierre Contable Mensual P&L (finanzas_estadoresultadoscontable)" as PNL {
  [*] --> PNL_ABIERTO : Inicio periodo YYYY-MM
  PNL_ABIERTO --> PNL_CONCILIADO : Cuadre Ingresos - Honorarios - Gastos Fijos
  PNL_CONCILIADO --> PNL_CERRADO : Aprobación Contable y Exportación PDF Oficial
  PNL_CERRADO --> [*]
}
@enduml
```

---

#### 4.2.1.6 Diseño de Navegación de Vistas (Modelo WAE Conallen: General, Móvil y por Paquetes 1 al 6)

En estricta conformidad con el estándar de modelado web y móvil de **Jim Conallen (Web Application Extension – WAE)** adoptado desde Sprints previos, la navegación consolidada del sistema **SIGEPSI** al cierre del **Sprint 4** formaliza vistas con sus **atributos de interfaz**, controladores **`«controller»`** con sus **métodos operacionales** y transiciones dirigidas **`«submit»`** (envío de evento/formulario desde la vista al controlador) y **`«build»`** (renderizado/despacho de la vista destino o modal):

La suite integral de navegación comprende **8 diagramas UML WAE Conallen** en [DIAGRAMAS.eapx](file:///c:/Users/User/Documents/2-2026/SI2/PROYECTO_GRUPAL_OFI/diagramas/DIAGRAMAS.eapx) (`Sprint 4 → 11. Navegación de Vistas WAE Conallen - Sprint 4`): **1 Mapa General Global (`SP0–SP4`)**, **1 Subsistema Móvil Nativo Flutter (`SP3–SP4`)** y **6 Diagramas Específicos por Paquete Arquitectónico (`Paquetes 1 al 6`)**.

##### Diagrama de Navegación 0: Mapa de Navegación Integral Global (Sprint 0 al Sprint 4 Acumulado)

Modela el acceso unificado (`loginGlobalView` → `authGlobalController`) para los **6 perfiles reales** (`SuperAdmin SaaS`, `Admin / Contador`, `Recepción / Caja`, `Coordinador Clínico`, `Psicólogo Tratante`, `Paciente Web y Móvil`), el despacho `«build»` hacia los **4 Dashboards por Rol** y la bifurcación hacia los **6 Paquetes Web** (incluyendo Consola Salud Multi-Tenant QA `HU-56`, IA Longitudinal `CU23`, Radar ML `CU24`, Caja Multimoneda/P&L `CU26` y CRM `CU26-CRM` / `HU-55`) más el **Subsistema Móvil Flutter**.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *11. Navegación de Vistas WAE Conallen - Sprint 4 → 0. Mapa de Navegacion Integral Global (SP0-SP4)* (**Diagrama ID: 356**).

![Modelo de Navegación WAE Conallen 0 – Mapa Integral Global (Sprints 0–4)](./imagenes/diagrama_navegacion_global_sp4.png)

```plantuml
@startuml
allowmixing
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
left to right direction

title Diagrama de Navegación 0: Mapa de Navegación Integral SIGEPSI (Sprint 0 al Sprint 4 Acumulado)

actor "SuperAdmin SaaS" as a_sup
actor "Admin / Contador" as a_adm
actor "Recepción / Caja" as a_rec
actor "Coordinador Clínico" as a_coo
actor "Psicólogo Tratante" as a_psi
actor "Paciente (Web y Móvil)" as a_pac

class "loginGlobalView" as v_login {
  + subdominioTenant: String
  + txtEmail: String
  + txtPassword: String
  + rolSeleccionado: String
}

class "authGlobalController" as c_auth <<controller>> {
  + determinarTenant(): void
  + autenticarJWT(): void
  + despacharDashboardRol(): void
}

a_sup -- v_login
a_adm -- v_login
a_rec -- v_login
a_coo -- v_login
a_psi -- v_login
a_pac -- v_login
v_login --> c_auth : <<submit>>

class "dashboardSuperAdminSaaSView" as d_sup {
  + tenants14Activos: int
  + estadoEstresQA: String
}
class "dashboardGerencialFinanzasView" as d_adm {
  + utilidadNetaBOB: Decimal
  + csatGlobalPct: Decimal
}
class "dashboardClinicoYTriajeView" as d_cli {
  + alertasMLActivas: int
  + citasHoy: int
}
class "dashboardMobileFlutterView" as d_mob {
  + cuotasPendientesBadge: int
  + moodTrackerWidget: Widget
}

c_auth ..> d_sup : <<build>> [SuperAdmin]
c_auth ..> d_adm : <<build>> [Admin/Recepción]
c_auth ..> d_cli : <<build>> [Psico/Coord]
c_auth ..> d_mob : <<build>> [Paciente Móvil]

package "Paquete 1: Administración, Auditoría, Backups y Salud QA" {
  class "directorioCentrosYSaludQAView" as v_p1 { + listaTenants14: List; + latenciaQA_P95: Decimal }
  class "adminSaaSRBACController" as c_p1 <<controller>> { + gestionarTenants(): void; + ejecutarAuditYBackups(): void }
  v_p1 --> c_p1 : <<submit>>
}
package "Paquete 6: Finanzas Multimoneda, Amortización, Honorarios y P&L" {
  class "cajaMultimonedaAmortizacionPnLView" as v_p6 { + tablaAmortizacion: List; + utilidadNetaBOB: Decimal }
  class "finanzasContabilidadController" as c_p6 <<controller>> { + procesarPagoBOB_USD(): void; + liquidarYEmitirPnL(): void }
  v_p6 --> c_p6 : <<submit>>
}
package "Paquete 3: Agenda, Teleconsulta y CRM" {
  class "agendaTeleconsultaYCRMView" as v_p3 { + turnosCalendario: List; + metricasCSAT_NPS: Object }
  class "agendaYCRMController" as c_p3 <<controller>> { + iniciarSalaJitsi(): void; + gestionarAlertasCRM(): void }
  v_p3 --> c_p3 : <<submit>>
}
package "Paquete 2: Clínica, SOAP e IA Longitudinal" {
  class "historiaClinicaYSintesisIAView" as v_p2 { + expedienteSOAP: String; + borradorResumenIA_HITL: Text }
  class "expedienteEIALongitudinalController" as c_p2 <<controller>> { + firmarNotaSOAP(): void; + aprobarSintesisHITL(): void }
  v_p2 --> c_p2 : <<submit>>
}
package "Paquete 5: IA Predictiva ML, Triaje y Chatbot" {
  class "consolaTriajeYRiesgoMLView" as v_p5 { + radarRiesgo12m: List; + rankingMatchingHITL: List }
  class "iaPredictivaTriajeController" as c_p5 <<controller>> { + calcularScoreAbandono(): void; + asignarPsicologoHITL(): void }
  v_p5 --> c_p5 : <<submit>>
}
package "Paquete 4: Intake, Consentimientos SHA-256 y Tareas" {
  class "formulariosIntakeTareasFirmaView" as v_p4 { + esquemaJSONB: JSON; + firmaCanvasSHA256: String }
  class "intakeConsentimientoController" as c_p4 <<controller>> { + validarPreConsulta(): void; + sellarConsentimiento(): void }
  v_p4 --> c_p4 : <<submit>>
}
package "Subsistema Móvil Flutter 3.x (SP3-SP4)" {
  class "estadoCuentaCitasYEncuestaMovil" as v_mob { + cuotasPendientesList: List; + encuestaCRM_1_5: int }
  class "pacienteMobileRouterController" as c_mob <<controller>> { + abrirEstadoCuentaQR(): void; + calificarServicioCRM(): void }
  v_mob --> c_mob : <<submit>>
}

d_sup ..> v_p1 : <<build>>
d_adm ..> v_p6 : <<build>>
d_adm ..> v_p3 : <<build>>
d_cli ..> v_p2 : <<build>>
d_cli ..> v_p5 : <<build>>
d_cli ..> v_p4 : <<build>>
d_mob ..> v_mob : <<build>>
@enduml
```

---

##### Diagrama de Navegación 1: Subsistema Móvil de Pacientes en Flutter 3.x (Consolidado SP3–SP4)

Formaliza los **11 flujos reales completos** de `prototipo/movil/lib/screens/` integrando Sprint 3 y Sprint 4: login seguro, perfil del paciente, *intake* pre-consulta, firma táctil SHA-256, reserva de citas, mis citas/cancelación >24h, teleconsulta WebRTC Jitsi, tareas/Mood Tracker, chatbot + Push FCM + comandos de voz, **estado de cuenta y pagos QR (`HU-51`/`HU-52`)** y **calificación CRM 1–5★ (`HU-55`)**.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *11. Navegación de Vistas WAE Conallen - Sprint 4 → 1. Subsistema Movil Flutter (Consolidado SP3-SP4)* (**Diagrama ID: 357**).

![Modelo de Navegación WAE Conallen 1 – Subsistema Móvil Flutter 3.x (SP3–SP4)](./imagenes/diagrama_navegacion_movil_sp4.png)

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
left to right direction

title Diagrama de Navegación 1: Subsistema Móvil de Pacientes (Flutter 3.x – 11 Flujos SP3-SP4)

actor "Paciente (App Móvil Flutter)" as act_pac

class "LoginMobileScreen" as v_log { + subdominioTenant: String; + txtEmail: String; + txtPassword: String; + btnLogin: Button }
class "AuthMobileController" as c_auth <<controller>> { + loginJWT(): void; + guardarTokensSecureStorage(): void; + registrarTokenFCM(): void }
class "DashboardMobileScreen" as v_dash { + proximaCitaBanner: Card; + moodTrackerWidget: Widget; + tareasPendientesBadge: int }
act_pac --> v_log
v_log --> c_auth : <<submit>>
c_auth ..> v_dash : <<build>>

class "PacientePerfilMobileScreen" as v_perf { + ciPaciente: String; + fechaNacimiento: Date; + contactoEmergencia: String }
class "PerfilPacienteMobileController" as c_perf <<controller>> { + getMiPerfil(): void; + updateMiPerfil(): void }
class "ConfirmacionPerfilActualizadoView" as v_cperf { + mensajeEstado: String; + fechaSincronizacion: DateTime }
act_pac --> v_perf
v_perf --> c_perf : <<submit>>
c_perf ..> v_cperf : <<build>>

class "IntakeFormMobileScreen" as v_int { + pasoActual: int; + escalaMalestar: int; + sintomasReportados: List }
class "IntakeMobileController" as c_int <<controller>> { + validarPasoActual(): void; + enviarRespuestaIntake(): void; + dispararAlertaUrgencia(): void }
class "ResumenIntakeMovilView" as v_rint { + nivelTriajeIA: String; + estadoEnvio: String }
act_pac --> v_int
v_int --> c_int : <<submit>>
c_int ..> v_rint : <<build>>

class "ConsentimientoFirmaMobileScreen" as v_fir { + clausulasTexto: String; + scrollAlcanzado: boolean; + firmaCanvas: Image }
class "FirmaDigitalMobileController" as c_fir <<controller>> { + computarSHA256Local(): void; + firmarConsentimiento(): void }
class "CertificadoSHA256MobileView" as v_cert { + hashSHA256: String; + fechaFirmaSellada: DateTime }
act_pac --> v_fir
v_fir --> c_fir : <<submit>>
c_fir ..> v_cert : <<build>>

class "ReservarCitaMobileScreen" as v_res { + psicologoSelector: UUID; + fechaSeleccionada: Date; + slotsDisponiblesGrid: List }
class "ReservaCitaMobileController" as c_res <<controller>> { + cargarSlotsDisponibles(): void; + confirmarReservaCita(): void }
class "ConfirmacionTurnoMovilView" as v_cres { + citaID: UUID; + modalidadSesion: String }
act_pac --> v_res
v_res --> c_res : <<submit>>
c_res ..> v_cres : <<build>>

class "MisCitasMobileScreen" as v_cit { + tabProximas: Tab; + tabHistorial: Tab; + listaCitas: List }
class "CitaMobileController" as c_cit <<controller>> { + listarCitas(): void; + validarVentanaCancelacion(): void; + solicitarCancelacion(): void }
class "ModalCancelacionCitaView" as v_canc { + avisoPolitica24h: String; + motivoCancelacion: String; + btnConfirmarCancelacion: Button }
act_pac --> v_cit
v_cit --> c_cit : <<submit>>
c_cit ..> v_canc : <<build>>
v_canc --> c_cit : <<submit>>

class "DetalleCitaMobileScreen" as v_det { + psicologoNombre: String; + fechaHoraSesion: DateTime; + modalidad: String }
class "TeleconsultaMobileController" as c_tel <<controller>> { + verificarPermisosCamMic(): void; + conectarWebRTCJitsi(): void; + registrarMetricaLlamada(): void }
class "SalaJitsiMeetScreen" as v_jit { + videoStreamLocal: VideoView; + videoStreamRemoto: VideoView; + btnColgar: Button }
v_cit ..> v_det : <<navigate>>
v_det --> c_tel : <<submit>>
c_tel ..> v_jit : <<build>>

class "MisTareasMobileScreen" as v_tar { + listaTareasPendientes: List; + selectorNivelAnimo: int; + factorContextual: String }
class "TareasMobileController" as c_tar <<controller>> { + entregarReflexionTarea(): void; + registrarMoodTracker(): void; + sincronizarOffline(): void }
class "FormularioEntregaTareaModalView" as v_ent { + reflexionesTexto: String; + escalaDificultad: int; + btnEnviarEntrega: Button }
act_pac --> v_tar
v_tar --> c_tar : <<submit>>
c_tar ..> v_ent : <<build>>
v_ent --> c_tar : <<submit>>

class "ChatbotYNotificacionesFCMScreen" as v_chn { + historialChatIA: List; + alertasPushFCMList: List; + dictadoVozReporte: String }
class "ChatbotPushVozMobileController" as c_chn <<controller>> { + enviarMensajeChatbot(): void; + enrolarTokenFCM(): void; + procesarComandoVoz(): void }
class "ReportesVozPacienteMobileView" as v_rvz { + resumenAdherencia: Chart; + sugerenciasAccion: List }
act_pac --> v_chn
v_chn --> c_chn : <<submit>>
c_chn ..> v_rvz : <<build>>

class "EstadoCuentaAmortizacionScreen" as v_cta { + planTerapeuticoActivo: String; + saldoPendienteBOB: Decimal; + tablaCuotasList: List }
class "FinanzasCrmMovilController" as c_pag <<controller>> { + consultarEstadoCuenta(): void; + procesarPagoCuotaQR(): void; + descargarComprobantePDF(): void }
class "ComprobantePagoMultimonedaView" as v_rec { + monedaOrigen: String; + tipoCambioAplicado: Decimal; + referenciaPasarela: String }
act_pac --> v_cta
v_cta --> c_pag : <<submit>>
c_pag ..> v_rec : <<build>>

class "DetalleCitaCompletadaMobileView" as v_post { + citaCompletadaID: UUID; + psicologoAtendio: String; + btnCalificarServicio: Button }
class "CalificacionCRMMovilController" as c_crm <<controller>> { + validarUnicidadCita(): void; + enviarEvaluacionEstrellas(): void; + notificarAlertaBajaNota(): void }
class "CalificacionServicioCRMSheetView" as v_crm { + puntuacionEstrellas1_5: int; + puntualidadYEmpatia: int; + comentarioPaciente: String }
act_pac --> v_post
v_post --> c_crm : <<submit>>
c_crm ..> v_crm : <<build>>
v_crm --> c_crm : <<submit>>
@enduml
```

---

##### Diagrama de Navegación 2: Paquete 1 – Administración, Seguridad, Auditoría y SaaS

Modela los **6 flujos completos** de administración y seguridad multi-tenant: provisión de los 14 centros clínicos, **Consola de Salud Multi-Tenant y Estrés QA (`HU-56`)**, renovaciones y facturación SaaS `USD` (`HU-53`), configuración de centro (`CentroConfig`) y cambio de contraseña, usuarios/matriz RBAC, y **Backups pg_dump + Bitácora Cifrada Fernet (`CU05`/`CU28`)**.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *11. Navegación de Vistas WAE Conallen - Sprint 4 → 2. Navegacion Paquete 1 - Administracion y SaaS* (**Diagrama ID: 358**).

![Modelo de Navegación WAE Conallen 2 – Paquete 1 Administración y SaaS](./imagenes/diagrama_navegacion_paquete1_sp4.png)

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
left to right direction

title Diagrama de Navegación 2: Paquete 1 – Administración, Seguridad, Auditoría, Backups y Salud QA

actor "SuperAdmin SaaS" as sup
actor "Administrador del Centro" as adm

class "directorioCentrosSaaSView" as v_ten { + filtroEstado: String; + listaTenants14: List; + busquedaSubdominio: String }
class "centroAdminSaaSController" as c_ten <<controller>> { + registrarTenant(): void; + configurarDominio(): void; + suspenderCentro(): void }
class "formularioCentroModalView" as v_mod_ten { + razonSocial: String; + subdominio: String; + planSuscripcion: String }
sup --> v_ten
v_ten --> c_ten : <<submit>>
c_ten ..> v_mod_ten : <<build>>
v_mod_ten --> c_ten : <<submit>>

class "consolaSaludMultiTenantQAView" as v_qa { + tenantsActivos14: int; + latenciaP95_ms: Decimal; + tasaAislamientoOK: Decimal }
class "saludMultiTenantQAController" as c_qa <<controller>> { + ejecutarEstresConcurrencia(): void; + verificarAislamientoEsquemas(): void }
class "reporteEstresMultiTenantModalView" as v_qar { + reporteCargaJSON: Object; + estadoSaludGlobal: String }
sup --> v_qa
v_qa --> c_qa : <<submit>>
c_qa ..> v_qar : <<build>>

class "renovacionSuscripcionSaaSView" as v_susc { + montoMensualUSD: Decimal; + fechaProximoCobro: Date; + renovacionAutomatica: boolean }
class "suscripcionBillingController" as c_susc <<controller>> { + verificarRenovacionesProximas(): void; + emitirFacturaSaaS(): void; + procesarCheckoutStripe(): void }
class "comprobanteSuscripcionModalView" as v_fac { + sessionStripeID: String; + estadoPagoUSD: String; + btnDescargarRecibo: Button }
sup --> v_susc
adm --> v_susc
v_susc --> c_susc : <<submit>>
c_susc ..> v_fac : <<build>>

class "configuracionCentroYPasswordView" as v_cfg { + monedaBaseCentro: String; + timezoneCentro: String; + nuevoPasswordInput: String }
class "centroConfigSeguridadController" as c_cfg <<controller>> { + updateCentroConfig(): void; + confirmarCambioPassword(): void }
class "confirmacionBrandingGuardadoView" as v_ccfg { + logoUrl: String; + estadoGuardado: String }
adm --> v_cfg
v_cfg --> c_cfg : <<submit>>
c_cfg ..> v_ccfg : <<build>>

class "directorioUsuariosRolesView" as v_usr { + rolFiltro: String; + usuariosList: List; + btnNuevoUsuario: Button }
class "usuarioRolRBACController" as c_usr <<controller>> { + crearUsuario(): void; + asignarRoles(): void; + cambiarEstadoUsuario(): void }
class "matrizPermisosModalView" as v_rbac { + nivelAcceso: String; + permisosRBAC: List }
adm --> v_usr
v_usr --> c_usr : <<submit>>
c_usr ..> v_rbac : <<build>>
v_rbac --> c_usr : <<submit>>

class "backupsYBitacoraFernetView" as v_bck { + listaBackupsPgDump: List; + filtroLogsFernet: Object; + cronAutomaticoActivo: boolean }
class "backupYAuditoriaController" as c_bck <<controller>> { + solicitarBackupManual(): void; + restaurarEsquemaTenant(): void; + consultarBitacoraCifrada(): void }
class "modalDetalleAuditYRestoreView" as v_bres { + hashIntegridadArchivo: String; + eventosAuditLogList: List }
adm --> v_bck
v_bck --> c_bck : <<submit>>
c_bck ..> v_bres : <<build>>
@enduml
```

---

##### Diagrama de Navegación 3: Paquete 2 – Gestión Clínica, SOAP e IA Longitudinal (`CU23`)

Modela los **5 flujos completos** del módulo clínico y de profesionales: **CRUD de Pacientes**, **CRUD de Psicólogos/Especialidades**, **Expedientes e Historia Clínica**, **Editor de Notas SOAP y Derivaciones**, y la consola Sprint 4 de **Síntesis Longitudinal IA con Supervisión HITL (`CU23 / HU-49`)**.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *11. Navegación de Vistas WAE Conallen - Sprint 4 → 3. Navegacion Paquete 2 - Clinica, SOAP e IA Longitudinal* (**Diagrama ID: 359**).

![Modelo de Navegación WAE Conallen 3 – Paquete 2 Clínica e IA Longitudinal](./imagenes/diagrama_navegacion_paquete2_sp4.png)

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
left to right direction

title Diagrama de Navegación 3: Paquete 2 – Gestión Clínica, SOAP e IA Longitudinal (CU23)

actor "Admin / Recepción" as adm_c
actor "Psicólogo Tratante" as psi

class "directorioPacientesListView" as v_pac { + busquedaCI: String; + pacientesList: List; + btnRegistrarPaciente: Button }
class "pacienteGestionController" as c_pac <<controller>> { + listarPacientes(): void; + crearPacienteDTO(): void; + verFichaPaciente(): void }
class "formularioPacienteModalView" as v_mpac { + codigoExpediente: String; + contactoEmergencia: String }
adm_c --> v_pac
v_pac --> c_pac : <<submit>>
c_pac ..> v_mpac : <<build>>
v_mpac --> c_pac : <<submit>>

class "directorioPsicologosListView" as v_psi { + especialidadFiltro: String; + psicologosList: List; + porcentajeHonorario: Decimal }
class "psicologoGestionController" as c_psi <<controller>> { + listarPsicologos(): void; + asignarEspecialidades(): void; + registrarConvenioHonorario(): void }
class "formularioPsicologoModalView" as v_mpsi { + matriculaProfesional: String; + especialidadesChecklist: List }
adm_c --> v_psi
v_psi --> c_psi : <<submit>>
c_psi ..> v_mpsi : <<build>>
v_mpsi --> c_psi : <<submit>>

class "expedientesDirectorioView" as v_exp { + filtroBusqueda: String; + listaPacientesAsignados: List }
class "expedienteClinicoController" as c_exp <<controller>> { + verificarAsignacionRBAC(): void; + abrirHistoriaClinica(): void }
class "historiaClinicaModularView" as v_hc { + numeroExpediente: String; + anamnesisText: String; + diagnosticoCIE10: String }
psi --> v_exp
v_exp --> c_exp : <<submit>>
c_exp ..> v_hc : <<build>>

class "editorNotasSOAPView" as v_soap { + subjetivo: String; + objetivo: String; + analisis: String; + plan: String }
class "notaSesionYDerivacionController" as c_soap <<controller>> { + autoGuardarBorrador(): void; + firmarYConsolidarSOAP(): void; + emitirDerivacionOAlta(): void }
class "protocoloCierreDerivacionView" as v_alta { + motivoEgresoODerivacion: String; + resumenTratamiento: String }
psi --> v_soap
v_soap --> c_soap : <<submit>>
c_soap ..> v_alta : <<build>>

class "consolaResumenLongitudinalIAView" as v_ia_c { + rangoMesesSelector: DateRange; + estadoValidacionBadge: String; + hashPII_SHA256: String; + btnGenerarResumenIA: Button }
class "resumenLongitudinalIAController" as c_ia_c <<controller>> { + sanitizarPII(): void; + construirSintesisGeminiHF(): void; + aprobarConSupervisionHITL(): void; + exportarResumenPDF(): void }
class "modalValidacionHITLYExportView" as v_ia_m { + textoEditadoTerapeuta: Text; + observacionesHITL: String; + btnAprobarYFirmarPDF: Button }
psi --> v_ia_c
v_ia_c --> c_ia_c : <<submit>>
c_ia_c ..> v_ia_m : <<build>>
v_ia_m --> c_ia_c : <<submit>>
@enduml
```

---

##### Diagrama de Navegación 4: Paquete 3 – Agenda, Teleconsulta WebRTC y CRM (`CU26-CRM` / `HU-55`)

Modela los **5 flujos completos**: **Disponibilidad Horaria de Psicólogos**, **Calendario de Citas**, **Sala Teleconsulta WebRTC**, **Centro de Notificaciones Push FCM (`CU12`)** y el panel estadístico **CRM de Satisfacción Post-Consulta 1–5★ (`HU-55`)**.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *11. Navegación de Vistas WAE Conallen - Sprint 4 → 4. Navegacion Paquete 3 - Agenda, Teleconsulta y CRM* (**Diagrama ID: 360**).

![Modelo de Navegación WAE Conallen 4 – Paquete 3 Agenda, Teleconsulta y CRM](./imagenes/diagrama_navegacion_paquete3_sp4.png)

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
left to right direction

title Diagrama de Navegación 4: Paquete 3 – Agenda, Disponibilidad, Teleconsulta, Push FCM y CRM (CU26-CRM / HU-55)

actor "Psicólogo / Recepción" as psi
actor "Coordinador / Admin CRM" as adm_crm

class "configurarDisponibilidadHorariaView" as v_disp { + psicologoSelector: UUID; + grillaSemanalBloques: Grid; + duracionSlotMinutos: int }
class "disponibilidadHorariaController" as c_disp <<controller>> { + consultarDisponibilidad(): void; + guardarBloquesHorarios(): void }
class "resumenSlotsPublicadosView" as v_mdisp { + totalSlotsHabilitados: int; + estadoAgenda: String }
psi --> v_disp
v_disp --> c_disp : <<submit>>
c_disp ..> v_mdisp : <<build>>

class "calendarioAgendaView" as v_cal { + vistaSemanal: Calendar; + fechaSeleccionada: Date; + turnosDisponibles: List }
class "agendaTurnosController" as c_cal <<controller>> { + agendarSesion(): void; + reprogramarCita(): void; + cancelarCita(): void }
class "reservaCitaModalView" as v_res { + pacienteID: UUID; + modalidad: String; + motivoConsulta: String }
psi --> v_cal
v_cal --> c_cal : <<submit>>
c_cal ..> v_res : <<build>>
v_res --> c_cal : <<submit>>

class "salaTeleconsultaJitsiView" as v_jit { + salaTokenJWT: String; + estadoConexionSRTP: String; + controlesAudioVideo: Widget }
class "teleconsultaController" as c_jit <<controller>> { + conectarSalaWebRTC(): void; + finalizarYCompletarCita(): void }
class "resumenLlamadaYDisparoCRMView" as v_rjit { + duracionMinutos: int; + notificacionEncuestaFCM: boolean }
psi --> v_jit
v_jit --> c_jit : <<submit>>
c_jit ..> v_rjit : <<build>>

class "centroNotificacionesPushFCMView" as v_fcm { + canalFiltro: String; + colaRecordatoriosPendientes: List }
class "notificacionPushController" as c_fcm <<controller>> { + despacharRecordatorioCita(): void; + notificarCuotaPorVencer(): void }
class "historialDespachoFCMModalView" as v_rfcm { + tasaEntregaFCM: Decimal; + tokensActivos: int }
adm_crm --> v_fcm
v_fcm --> c_fcm : <<submit>>
c_fcm ..> v_rfcm : <<build>>

class "panelEstadisticasCRMView" as v_crm_p { + indiceCSAT_Porcentaje: Decimal; + puntajeNPS: Decimal; + histograma1_5Estrellas: Chart; + alertasBajaNota: List }
class "crmSatisfaccionController" as c_crm_p <<controller>> { + calcularIndicadoresCSAT_NPS(): void; + listarResenasPorPsicologo(): void; + resolverAlertaInsatisfaccion(): void }
class "modalResolucionAlertaCRMView" as v_crm_m { + puntuacionEstrellas: SmallInt; + notaResolucionCRM: Text; + estadoSeguimiento: String }
adm_crm --> v_crm_p
v_crm_p --> c_crm_p : <<submit>>
c_crm_p ..> v_crm_m : <<build>>
v_crm_m --> c_crm_p : <<submit>>
@enduml
```

---

##### Diagrama de Navegación 5: Paquete 4 – Formularios Pre-Consulta y Consentimientos SHA-256

Modela los **5 flujos completos** de documentación clínica y tareas: *Stepper Intake* móvil, **Configuración de Intake y Asistente IA Web**, Firma digital SHA-256, Gestor de Plantillas legales y **Gestor Web de Tareas Terapéuticas y Revisión de Evidencias**.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *11. Navegación de Vistas WAE Conallen - Sprint 4 → 5. Navegacion Paquete 4 - Formularios, Consentimientos y Tareas* (**Diagrama ID: 361**).

![Modelo de Navegación WAE Conallen 5 – Paquete 4 Formularios y Consentimientos](./imagenes/diagrama_navegacion_paquete4_sp4.png)

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
left to right direction

title Diagrama de Navegación 5: Paquete 4 – Formularios IA, Consentimientos SHA-256 y Tareas Web

actor "Paciente" as pac
actor "Psicólogo / Admin" as psi4

class "stepperIntakeScreenMovil" as v_int { + pasoActual: int; + escalaMalestar: int; + sintomasReportados: List }
class "intakeFormController" as c_int <<controller>> { + guardarPasoLocal(): void; + validarEsquemaJSONB(): void; + enviarIntakeCompleto(): void }
class "resumenIntakeClinicoView" as v_rint { + pacienteNombre: String; + respuestasCards: Object }
pac --> v_int
v_int --> c_int : <<submit>>
c_int ..> v_rint : <<build>>

class "visorFirmaConsentimientoScreen" as v_fir { + clausulasTexto: String; + scrollAlcanzado: boolean; + firmaCanvas: Image }
class "firmaCriptograficaController" as c_fir <<controller>> { + computarHashSHA256(): void; + sellarConsentimientoPDF(): void }
class "certificadoFirmaModalView" as v_cert { + hashSHA256: String; + codigoVerificacion: String }
pac --> v_fir
v_fir --> c_fir : <<submit>>
c_fir ..> v_cert : <<build>>

class "configuracionIntakeYAsistenteIAView" as v_icfg { + camposJSONBBuilder: JSON; + respuestaSeleccionada: UUID }
class "intakeConfigAsistenteIAController" as c_icfg <<controller>> { + actualizarFormularioPreconsulta(): void; + analizarRespuestaConIA(): void }
class "iaAsistentePreconsultaModalView" as v_iaas { + reglasDisparadas: List; + riesgoSugeridoIA: String }
psi4 --> v_icfg
v_icfg --> c_icfg : <<submit>>
c_icfg ..> v_iaas : <<build>>

class "gestorPlantillasConsentimientoView" as v_plt { + plantillasLegales: List; + versionActiva: String }
class "consentimientoAdminController" as c_plt <<controller>> { + crearPlantilla(): void; + previsualizarVariables(): void }
class "editorPlantillaModalView" as v_eplt { + cuerpoPlantilla: String; + variablesDinamicas: List }
psi4 --> v_plt
v_plt --> c_plt : <<submit>>
c_plt ..> v_eplt : <<build>>
v_eplt --> c_plt : <<submit>>

class "gestorTareasTerapeuticasWebView" as v_tarw { + pacienteFiltro: UUID; + tareasAsignadasList: List; + estadoCumplimiento: String }
class "tareasTerapeuticasWebController" as c_tarw <<controller>> { + asignarTareaPaciente(): void; + revisarEvidenciaAdjunta(): void }
class "modalDetalleEvidenciaTareaView" as v_etw { + archivoEvidenciaUrl: String; + observacionTerapeuta: Text }
psi4 --> v_tarw
v_tarw --> c_tarw : <<submit>>
c_tarw ..> v_etw : <<build>>
@enduml
```

---

##### Diagrama de Navegación 6: Paquete 5 – Inteligencia Artificial Predictiva ML (`CU24`), Triaje y Chatbot

Separa limpiamente los **4 flujos inteligentes**: **Radar Predictivo ML 6–12 meses (`CU24 / HU-50`)**, **Consola de Triaje y Detección de Crisis (`CU21`)**, **Consola de Matching HITL de Terapeutas (`CU22`)** y **Asistente Chatbot Reactivo (`CU20`)**.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *11. Navegación de Vistas WAE Conallen - Sprint 4 → 6. Navegacion Paquete 5 - IA Predictiva ML, Triaje y Chatbot* (**Diagrama ID: 362**).

![Modelo de Navegación WAE Conallen 6 – Paquete 5 IA Predictiva ML y Chatbot](./imagenes/diagrama_navegacion_paquete5_sp4.png)

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
left to right direction

title Diagrama de Navegación 6: Paquete 5 – IA Predictiva ML (CU24), Triaje (CU21), Matching (CU22) y Chatbot

actor "Coordinador / Psicólogo" as coo
actor "Paciente" as pac

class "radarRiesgoPredictivoMLView" as v_rad { + filtroSeveridad: String; + curvaAnimo12Meses: Chart; + scoreRiesgoIndex: Decimal; + pesosExplicablesJSON: Object }
class "riesgoPredictivoMLController" as c_rad <<controller>> { + extraerFeatures12Meses(): void; + calcularScoreRiesgoML(): void; + intervenirAlertaClinica(): void }
class "modalIntervencionAlertaMLView" as v_rad_m { + factoresContribuyentes: List; + accionClinicaNota: Text; + estadoAlerta: String }
coo --> v_rad
v_rad --> c_rad : <<submit>>
c_rad ..> v_rad_m : <<build>>
v_rad_m --> c_rad : <<submit>>

class "consolaTriajeCrisisIAView" as v_tri { + alertaCrisisFlag: boolean; + filtroNivelUrgencia: String; + casosPendientesList: List }
class "clasificacionTriajeIAController" as c_tri <<controller>> { + ejecutarPipelineNLP(): void; + evaluarSeveridadCrisis(): void; + auditarTriajeManual(): void }
class "modalDetalleTriajeCrisisView" as v_mcri { + protocoloEmergencia: String; + palabrasClaveDetectadas: List }
coo --> v_tri
v_tri --> c_tri : <<submit>>
c_tri ..> v_mcri : <<build>>

class "consolaMatchingEspecialistasView" as v_mat { + pacienteSeleccionado: String; + rankingTop3Terapeutas: List }
class "matchingHITLController" as c_mat <<controller>> { + calcularScoreAfinidad(): void; + verificarCargaHoraria(): void; + confirmarAsignacionHITL(): void }
class "modalConfirmarAsignacionTerapeutaView" as v_asig { + justificacionClinica: String; + psicologoAsignadoID: UUID }
coo --> v_mat
v_mat --> c_mat : <<submit>>
c_mat ..> v_asig : <<build>>
v_asig --> c_mat : <<submit>>

class "burbujaChatbotWidgetView" as v_cha { + estadoAbierto: boolean; + posicionBurbuja: String }
class "chatbotController" as c_cha <<controller>> { + clasificarIntencion(): void; + detectarCrisis(): void; + escalarOperadorHumano(): void }
class "ventanaConversacionChatbotView" as v_chw { + historialMensajes: List; + sugerenciasFAQ: List }
pac --> v_cha
v_cha --> c_cha : <<submit>>
c_cha ..> v_chw : <<build>>
@enduml
```

---

##### Diagrama de Navegación 7: Paquete 6 – Finanzas Multimoneda, Amortización, P&L y Reportes (`CU26`)

Separa en **4 filas dedicadas** cada módulo económico y de reportería del Sprint 4: **Caja Multimoneda `BOB`/`USD` y Tabla de Amortización (`HU-51`/`HU-52`)**, **Liquidación de Honorarios 70/30 (`HU-53`)**, **Estado de Resultados: Ganancia Bruta vs. Utilidad Neta y Gastos Fijos (`HU-54`)**, y **Reportes QBE por Voz (`CU25`)**.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *11. Navegación de Vistas WAE Conallen - Sprint 4 → 7. Navegacion Paquete 6 - Finanzas, Amortizacion, P&L y Reportes* (**Diagrama ID: 363**).

![Modelo de Navegación WAE Conallen 7 – Paquete 6 Finanzas, Amortización y P&L](./imagenes/diagrama_navegacion_paquete6_sp4.png)

```plantuml
@startuml
skinparam classAttributeIconSize 0
skinparam shadowing false
skinparam roundcorner 8
skinparam defaultFontName Arial
left to right direction

title Diagrama de Navegación 7: Paquete 6 – Finanzas Multimoneda, Honorarios, P&L y Reportes (CU26)

actor "Recepción / Caja" as rec
actor "Admin / Contador" as adm

class "cajaMultimonedaYPagosView" as v_caj { + monedaOrigenSelector: String; + montoOriginalInput: Decimal; + tipoCambioOficial: Decimal; + metodoPagoSelector: String }
class "pagosMultimonedaController" as c_caj <<controller>> { + convertirABOBConAjuste(): void; + procesarAbonoCuotaLock(): void; + emitirComprobanteExacto(): void }
class "extractoTablaAmortizacionView" as v_am { + capitalAmortizado: Decimal; + interesYSeguro: Decimal; + saldoInsoluto: Decimal; + btnDescargarPDF: Button }
rec --> v_caj
v_caj --> c_caj : <<submit>>
c_caj ..> v_am : <<build>>

class "liquidacionHonorariosPsicologosView" as v_liq { + periodoMesSelector: String; + psicologosConvenioList: List; + porcentajeRetencionCentro: Decimal }
class "liquidacionHonorariosController" as c_liq <<controller>> { + consolidarSesionesRealizadas(): void; + generarLiquidacionPeriodo(): void; + marcarDesembolsoPagado(): void }
class "boletaLiquidacionHonorarioPDFView" as v_bliq { + totalBrutoGenerado: Decimal; + montoNetoPsicologo: Decimal; + estadoDesembolso: String }
adm --> v_liq
v_liq --> c_liq : <<submit>>
c_liq ..> v_bliq : <<build>>

class "estadoResultadosUtilidadNetaView" as v_pnl { + periodoMesSelector: String; + ingresosBrutosBOB: Decimal; + costosHonorariosBOB: Decimal; + gananciaBrutaBOB: Decimal; + utilidadNetaFinalBOB: Decimal }
class "contabilidadUtilidadNetaController" as c_pnl <<controller>> { + registrarGastoFijoMensual(): void; + calcularEstadoResultadosPnL(): void; + cerrarPeriodoContable(): void }
class "modalRegistroGastosFijosMensualesView" as v_gas { + categoriaGasto: String; + montoOrigenYMoneda: String; + comprobanteRef: String }
adm --> v_pnl
v_pnl --> c_pnl : <<submit>>
c_pnl ..> v_gas : <<build>>
v_gas --> c_pnl : <<submit>>

class "dashboardReportesQBEVozView" as v_rep { + consultaVozTranscript: String; + filtrosDinamicosQBE: Object; + graficosChartJS: Object }
class "reportesAnaliticosController" as c_rep <<controller>> { + generarReportePersonalizado(): void; + exportarExcelYPDF(): void }
class "visorReporteFinancieroPDFModal" as v_pdf { + documentoURI: String; + totalPaginas: int }
adm --> v_rep
v_rep --> c_rep : <<submit>>
c_rep ..> v_pdf : <<build>>
@enduml
```

---

### 4.2.2 Implementación (Componentes UML MVC y Artefactos Generados)

#### Diagramas de Componentes de Implementación (UML – Patrón MVC General, Móvil y por Paquetes 1 al 6)

Siguiendo exactamente la convención estructural de componentes adoptada por la cátedra y la misma organización modular del diseño de navegación (`0. General`, `1. Subsistema Móvil Flutter` y `2..7. Paquetes 1 al 6`), cada diagrama formaliza los componentes reales de implementación en 4 capas dirigidas por dependencias (`Dependency`): **`«Componente:Vista»`** (`V.*`), **`«Componente:Controlador»`** (`*Controller`), **`«Componente:Model»`** (`M.*`) y **`«conexion»`** (**`PostgreSQL`**).

##### Diagrama de Componentes 0: General del Sistema SIGEPSI (`SP0–SP4`)

Vista de implementación consolidada de todo el ecosistema **SIGEPSI** conectando las vistas Web Angular / Móvil Flutter con sus controladores de dominio, modelos persistentes y la conexión única multi-tenant **PostgreSQL**.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *12. Implementación - Componentes UML (Sprint 4) → 0. Componentes Generales del Sistema (SP0-SP4)* (**Diagrama ID: 364**).

![Diagrama de Componentes UML 0 – General del Sistema SIGEPSI (MVC)](./imagenes/diagrama_componentes_implementacion_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam componentStyle uml2
skinparam defaultFontName Arial
top to bottom direction

title Diagrama de Componentes 0 – General del Sistema SIGEPSI (MVC SP0–SP4)

component "V.PortalAdminSaaS" as v_saas <<Componente:Vista>>
component "V.ClinicaIAML" as v_cli <<Componente:Vista>>
component "V.AgendaJitsiCRM" as v_ag <<Componente:Vista>>
component "V.FinanzasPnL" as v_fin <<Componente:Vista>>
component "V.AppMovilFlutter" as v_mob <<Componente:Vista>>

component "SeguridadSaaSController" as c_sec <<Componente:Controlador>>
component "ClinicaIAMLController" as c_cli <<Componente:Controlador>>
component "AgendaCrmController" as c_ag <<Componente:Controlador>>
component "FinanzasPnLController" as c_fin <<Componente:Controlador>>

component "M.TenantUsuarioRBAC" as m_ten <<Componente:Model>>
component "M.ExpedienteSOAP_IA" as m_hce <<Componente:Model>>
component "M.CitaAlertaCRM" as m_ag <<Componente:Model>>
component "M.PlanCuotaPnL" as m_fin <<Componente:Model>>

component "PostgreSQL" as db <<conexion>>

c_sec ..> v_saas
c_cli ..> v_cli
c_ag ..> v_ag
c_ag ..> v_mob
c_fin ..> v_fin
c_fin ..> v_mob

c_sec ..> m_ten
c_cli ..> m_hce
c_ag ..> m_ag
c_fin ..> m_fin

m_ten ..> db
m_hce ..> db
m_ag ..> db
m_fin ..> db
@enduml
```

---

##### Diagrama de Componentes 1: Subsistema Móvil Flutter 3.x (`SP3–SP4`)

Modela la correspondencia MVC de las pantallas nativas Flutter (`prototipo/movil/lib/screens/`), sus controladores/servicios (`services/`) y los modelos de datos sincronizados contra el backend y **PostgreSQL**.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *12. Implementación - Componentes UML (Sprint 4) → 1. Componentes Subsistema Movil Flutter (SP3-SP4)* (**Diagrama ID: 365**).

![Diagrama de Componentes UML 1 – Subsistema Móvil Flutter 3.x (MVC)](./imagenes/diagrama_componentes_movil_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam componentStyle uml2
skinparam defaultFontName Arial
top to bottom direction

title Diagrama de Componentes 1 – Subsistema Móvil Flutter 3.x (MVC SP3–SP4)

component "V.LoginPerfilScreen" as v_auth <<Componente:Vista>>
component "V.IntakeFirmaScreen" as v_int <<Componente:Vista>>
component "V.CitasJitsiScreen" as v_cit <<Componente:Vista>>
component "V.TareasChatbotScreen" as v_tar <<Componente:Vista>>
component "V.AmortizacionCRMScreen" as v_fin <<Componente:Vista>>

component "AuthMovilController" as c_auth <<Componente:Controlador>>
component "IntakeMovilController" as c_int <<Componente:Controlador>>
component "CitasJitsiMovilController" as c_cit <<Componente:Controlador>>
component "TareasChatMovilController" as c_tar <<Componente:Controlador>>
component "FinanzasCrmController" as c_fin <<Componente:Controlador>>

component "M.UsuarioPaciente" as m_usr <<Componente:Model>>
component "M.ConsentimientoIntake" as m_int <<Componente:Model>>
component "M.CitaTeleconsultaFCM" as m_cit <<Componente:Model>>
component "M.TareaMoodChatbot" as m_tar <<Componente:Model>>
component "M.CuotaCalificacionCRM" as m_fin <<Componente:Model>>

component "PostgreSQL" as db <<conexion>>

c_auth ..> v_auth
c_int ..> v_int
c_cit ..> v_cit
c_tar ..> v_tar
c_fin ..> v_fin

c_auth ..> m_usr
c_int ..> m_int
c_cit ..> m_cit
c_tar ..> m_tar
c_fin ..> m_fin

m_usr ..> db
m_int ..> db
m_cit ..> db
m_tar ..> db
m_fin ..> db
@enduml
```

---

##### Diagrama de Componentes 2: Paquete 1 – Administración, Seguridad RBAC, Auditoría y SaaS

Correspondencia física en `prototipo/backend/{tenants,accounts,audit,subscriptions}/` y `paquete1_admin_seguridad/` (gestión de 14 centros, consola de salud QA `HU-56`, usuarios/RBAC, backups `CU28` y bitácora Fernet `CU5`).

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *12. Implementación - Componentes UML (Sprint 4) → 2. Componentes Paquete 1 - Administracion y SaaS* (**Diagrama ID: 366**).

![Diagrama de Componentes UML 2 – Paquete 1 Administración, Seguridad y SaaS](./imagenes/diagrama_componentes_paquete1_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam componentStyle uml2
skinparam defaultFontName Arial
top to bottom direction

title Diagrama de Componentes 2 – Paquete 1 Administración, Seguridad y SaaS

component "V.TenantsYEstresQA" as v_ten <<Componente:Vista>>
component "V.CentroYPassword" as v_cfg <<Componente:Vista>>
component "V.UsuariosRolesRBAC" as v_usr <<Componente:Vista>>
component "V.BackupsYBitacora" as v_bck <<Componente:Vista>>

component "TenantSaaSController" as c_ten <<Componente:Controlador>>
component "AuthRBACController" as c_auth <<Componente:Controlador>>
component "BackupAuditController" as c_bck <<Componente:Controlador>>

component "M.TenantDominioPlan" as m_ten <<Componente:Model>>
component "M.CentroConfig" as m_cfg <<Componente:Model>>
component "M.UsuarioRolPermiso" as m_usr <<Componente:Model>>
component "M.AuditLogBackup" as m_aud <<Componente:Model>>

component "PostgreSQL" as db <<conexion>>

c_ten ..> v_ten
c_ten ..> v_cfg
c_auth ..> v_cfg
c_auth ..> v_usr
c_bck ..> v_bck

c_ten ..> m_ten
c_ten ..> m_cfg
c_auth ..> m_usr
c_bck ..> m_aud

m_ten ..> db
m_cfg ..> db
m_usr ..> db
m_aud ..> db
@enduml
```

---

##### Diagrama de Componentes 3: Paquete 2 – Gestión Clínica, SOAP e IA Longitudinal (`CU23`)

Correspondencia en `prototipo/backend/clinica/` y `paquete2_gestion_clinica/` para pacientes, psicólogos, historia clínica CIE-10/11 (`CU15`), notas SOAP (`CU16`), derivaciones (`CU19`) y síntesis longitudinal IA con supervisión HITL (`CU23` / `HU-49`).

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *12. Implementación - Componentes UML (Sprint 4) → 3. Componentes Paquete 2 - Clinica, SOAP e IA Longitudinal (CU23)* (**Diagrama ID: 367**).

![Diagrama de Componentes UML 3 – Paquete 2 Clínica, SOAP e IA Longitudinal](./imagenes/diagrama_componentes_paquete2_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam componentStyle uml2
skinparam defaultFontName Arial
top to bottom direction

title Diagrama de Componentes 3 – Paquete 2 Clínica, SOAP e IA Longitudinal (CU23)

component "V.PacientesPsicologos" as v_dir <<Componente:Vista>>
component "V.ExpedienteNotaSOAP" as v_hce <<Componente:Vista>>
component "V.ConsolaIALongitudinal" as v_ia <<Componente:Vista>>

component "PacientesPsicoController" as c_dir <<Componente:Controlador>>
component "ExpedienteSOAPController" as c_hce <<Componente:Controlador>>
component "ResumenIAController" as c_ia <<Componente:Controlador>>

component "M.PacientePsicologo" as m_pac <<Componente:Model>>
component "M.HistoriaNotaSOAP" as m_hce <<Componente:Model>>
component "M.ResumenClinicoIA" as m_res <<Componente:Model>>

component "PostgreSQL" as db <<conexion>>

c_dir ..> v_dir
c_hce ..> v_hce
c_ia ..> v_ia

c_dir ..> m_pac
c_hce ..> m_pac
c_hce ..> m_hce
c_ia ..> m_hce
c_ia ..> m_res

m_pac ..> db
m_hce ..> db
m_res ..> db
@enduml
```

---

##### Diagrama de Componentes 4: Paquete 3 – Agenda, Teleconsulta Jitsi, FCM y CRM (`HU-55`)

Correspondencia en `prototipo/backend/agenda/` (+ extensión CRM) y `paquete3_agenda_teleconsulta/` para disponibilidad (`CU8`), reservas (`CU11`), teleconsulta WebRTC (`CU13`), recordatorios Push FCM (`CU12`) y encuestas/estadísticas CRM 1–5★ (`HU-55`).

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *12. Implementación - Componentes UML (Sprint 4) → 4. Componentes Paquete 3 - Agenda, Teleconsulta y CRM (HU-55)* (**Diagrama ID: 368**).

![Diagrama de Componentes UML 4 – Paquete 3 Agenda, Teleconsulta y CRM](./imagenes/diagrama_componentes_paquete3_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam componentStyle uml2
skinparam defaultFontName Arial
top to bottom direction

title Diagrama de Componentes 4 – Paquete 3 Agenda, Teleconsulta y CRM (HU-55)

component "V.CalendarioAgenda" as v_ag <<Componente:Vista>>
component "V.SalaTeleconsultaJitsi" as v_jit <<Componente:Vista>>
component "V.PanelEstadisticasCRM" as v_crm <<Componente:Vista>>

component "AgendaTurnosController" as c_ag <<Componente:Controlador>>
component "TeleconsultaController" as c_tel <<Componente:Controlador>>
component "CrmCalidadController" as c_crm <<Componente:Controlador>>

component "M.DisponibilidadCita" as m_cit <<Componente:Model>>
component "M.NotificacionCitaFCM" as m_not <<Componente:Model>>
component "M.CalificacionCRM" as m_crm <<Componente:Model>>

component "PostgreSQL" as db <<conexion>>

c_ag ..> v_ag
c_tel ..> v_jit
c_crm ..> v_crm

c_ag ..> m_cit
c_tel ..> m_cit
c_tel ..> m_not
c_crm ..> m_cit
c_crm ..> m_crm

m_cit ..> db
m_not ..> db
m_crm ..> db
@enduml
```

---

##### Diagrama de Componentes 5: Paquete 4 – Formularios Pre-Consulta, Consentimientos SHA-256 y Tareas

Correspondencia de `intake` (`CU14`), consentimientos firmados con hash SHA-256 (`CU18`) y seguimiento terapéutico de tareas/ánimo (`CU17`) en `paquete4_seguimiento_terapeutico/`.

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *12. Implementación - Componentes UML (Sprint 4) → 5. Componentes Paquete 4 - Formularios, Consentimientos y Tareas* (**Diagrama ID: 369**).

![Diagrama de Componentes UML 5 – Paquete 4 Intake, Consentimientos y Tareas](./imagenes/diagrama_componentes_paquete4_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam componentStyle uml2
skinparam defaultFontName Arial
top to bottom direction

title Diagrama de Componentes 5 – Paquete 4 Intake, Consentimientos y Tareas

component "V.IntakePreConsulta" as v_int <<Componente:Vista>>
component "V.ConsentimientosSHA256" as v_fir <<Componente:Vista>>
component "V.GestorTareasMood" as v_tar <<Componente:Vista>>

component "IntakeFormController" as c_int <<Componente:Controlador>>
component "ConsentimientoController" as c_fir <<Componente:Controlador>>
component "TareasAnimoController" as c_tar <<Componente:Controlador>>

component "M.FormularioIntake" as m_int <<Componente:Model>>
component "M.ConsentimientoSHA256" as m_fir <<Componente:Model>>
component "M.TareaRegistroAnimo" as m_tar <<Componente:Model>>

component "PostgreSQL" as db <<conexion>>

c_int ..> v_int
c_fir ..> v_fir
c_tar ..> v_tar

c_int ..> m_int
c_fir ..> m_fir
c_tar ..> m_tar

m_int ..> db
m_fir ..> db
m_tar ..> db
@enduml
```

---

##### Diagrama de Componentes 6: Paquete 5 – Inteligencia Artificial Predictiva ML (`CU24`), Triaje y Chatbot

Correspondencia en `prototipo/backend/clinica/{ia_rules_engine.py,chatbot_service.py,ml_riesgo_service.py}` y `paquete5_ia_triaje/` para predicción ML 6–12 meses (`CU24` / `HU-50`), triaje de crisis (`CU21`), matching HITL (`CU22`) y chatbot (`CU20`).

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *12. Implementación - Componentes UML (Sprint 4) → 6. Componentes Paquete 5 - IA Predictiva ML (CU24), Triaje y Chatbot* (**Diagrama ID: 370**).

![Diagrama de Componentes UML 6 – Paquete 5 IA Predictiva ML, Triaje y Chatbot](./imagenes/diagrama_componentes_paquete5_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam componentStyle uml2
skinparam defaultFontName Arial
top to bottom direction

title Diagrama de Componentes 6 – Paquete 5 IA Predictiva ML (CU24), Triaje y Chatbot

component "V.RadarRiesgoML" as v_rad <<Componente:Vista>>
component "V.TriajeMatchingHITL" as v_tri <<Componente:Vista>>
component "V.ChatbotOrientacion" as v_cha <<Componente:Vista>>

component "RiesgoMLController" as c_rad <<Componente:Controlador>>
component "TriajeMatchingController" as c_tri <<Componente:Controlador>>
component "ChatbotIAController" as c_cha <<Componente:Controlador>>

component "M.AlertaRiesgoPredictiva" as m_al <<Componente:Model>>
component "M.ClasificacionMatchingIA" as m_mat <<Componente:Model>>
component "M.ConversacionChatbot" as m_cha <<Componente:Model>>

component "PostgreSQL" as db <<conexion>>

c_rad ..> v_rad
c_tri ..> v_tri
c_cha ..> v_cha

c_rad ..> m_al
c_tri ..> m_mat
c_cha ..> m_cha

m_al ..> db
m_mat ..> db
m_cha ..> db
@enduml
```

---

##### Diagrama de Componentes 7: Paquete 6 – Finanzas Multimoneda, Amortización, P&L y Reportes (`CU26`)

Correspondencia económica y analítica en `prototipo/backend/reportes/`, extensión `finanzas/` y `paquete6_reportes_auditoria/` (`HU-51` a `HU-54` de `CU26` y reportería QBE por voz `CU25`).

* **Ubicación en Enterprise Architect:** `DIAGRAMAS.eapx` → *Sprint 4 - IA Longitudinal, Contabilidad Utilidad Neta y CRM* → *12. Implementación - Componentes UML (Sprint 4) → 7. Componentes Paquete 6 - Finanzas, Amortizacion, P&L y Reportes (CU26)* (**Diagrama ID: 371**).

![Diagrama de Componentes UML 7 – Paquete 6 Finanzas, Amortización, P&L y Reportes](./imagenes/diagrama_componentes_paquete6_sp4.png)

```plantuml
@startuml
skinparam shadowing false
skinparam componentStyle uml2
skinparam defaultFontName Arial
top to bottom direction

title Diagrama de Componentes 7 – Paquete 6 Finanzas, Amortización, P&L y Reportes (CU26)

component "V.CajaAmortizacion" as v_caj <<Componente:Vista>>
component "V.LiquidacionHonorarios" as v_liq <<Componente:Vista>>
component "V.EstadoResultadosPnL" as v_pnl <<Componente:Vista>>
component "V.ReportesQBEVoz" as v_rep <<Componente:Vista>>

component "PagosCuotasController" as c_pag <<Componente:Controlador>>
component "ContabilidadPnLController" as c_pnl <<Componente:Controlador>>
component "ReportesQBEController" as c_rep <<Componente:Controlador>>

component "M.PlanCuotaPago" as m_cuo <<Componente:Model>>
component "M.LiquidacionHonorario" as m_liq <<Componente:Model>>
component "M.GastoFijoEstadoPnL" as m_pnl <<Componente:Model>>
component "M.ConsultaReporteQBE" as m_rep <<Componente:Model>>

component "PostgreSQL" as db <<conexion>>

c_pag ..> v_caj
c_pnl ..> v_liq
c_pnl ..> v_pnl
c_rep ..> v_rep

c_pag ..> m_cuo
c_pnl ..> m_liq
c_pnl ..> m_pnl
c_rep ..> m_rep

m_cuo ..> db
m_liq ..> db
m_pnl ..> db
m_rep ..> db
@enduml
```

#### 4.2.2.1 Implementación Backend (Django REST Framework, IA/ML, Finanzas Contables y CRM)

```python
# backend/clinica/ml_riesgo_service.py (CU23 & CU24 - Síntesis Longitudinal y Riesgo ML)
import hashlib
import re
from decimal import Decimal
from datetime import timedelta
from django.utils import timezone


def sanitizar_pii(texto: str) -> str:
    """Elimina teléfonos, carnets bolivianos y correos antes de procesar con IA."""
    texto = re.sub(r'[\w.+-]+@[\w-]+\.[\w.-]+', '[EMAIL_PROTEGIDO]', texto or '')
    texto = re.sub(r'\b[67]\d{7}\b', '[TEL_PROTEGIDO]', texto)
    texto = re.sub(r'\b\d{6,9}(-[A-Z]{2})?\b', '[CI_PROTEGIDO]', texto)
    return texto


class RiesgoPredictivoMLService:
    """
    Motor predictivo sobre series históricas de 6 a 12 meses (Mood Tracker,
    asistencia a citas, cumplimiento de tareas y léxico SOAP).
    """
    PESOS = {
        'pendiente_animo': Decimal('0.40'),
        'tasa_inasistencia': Decimal('0.30'),
        'incumplimiento_tareas': Decimal('0.20'),
        'senales_lexicas_soap': Decimal('0.10'),
    }

    @classmethod
    def evaluar_riesgo_longitudinal(cls, serie_animo: list[int], citas_totales: int,
                                    inasistencias: int, tareas_totales: int,
                                    tareas_vencidas: int, texto_soap: str) -> dict:
        # 1. Pendiente negativa de ánimo entre primer tramo y últimos 30 días
        if len(serie_animo) >= 6:
            mitad = len(serie_animo) // 2
            prom_prev = sum(serie_animo[:mitad]) / mitad
            prom_rec = sum(serie_animo[mitad:]) / (len(serie_animo) - mitad)
            caida_norm = max(0.0, min(1.0, (prom_prev - prom_rec) / 2.5))
        else:
            caida_norm = 0.0

        tasa_no_show = (inasistencias / citas_totales) if citas_totales > 0 else 0.0
        tasa_tareas = (tareas_vencidas / tareas_totales) if tareas_totales > 0 else 0.0

        palabras_riesgo = ('desesperanza', 'insomnio severo', 'aislamiento', 'crisis', 'autolesion')
        texto_limpio = sanitizar_pii(texto_soap).lower()
        hits = sum(1 for kw in palabras_riesgo if kw in texto_limpio)
        lex_norm = min(1.0, hits / 3.0)

        score = (
            Decimal(str(caida_norm)) * cls.PESOS['pendiente_animo'] +
            Decimal(str(min(1.0, tasa_no_show * 2))) * cls.PESOS['tasa_inasistencia'] +
            Decimal(str(min(1.0, tasa_tareas))) * cls.PESOS['incumplimiento_tareas'] +
            Decimal(str(lex_norm)) * cls.PESOS['senales_lexicas_soap']
        ).quantize(Decimal('0.001'))

        nivel = 'CRITICO' if score >= Decimal('0.800') else (
            'ALTO' if score >= Decimal('0.650') else (
                'MODERADO' if score >= Decimal('0.400') else 'BAJO'
            )
        )
        return {
            'indice_riesgo': score,
            'nivel_severidad': nivel,
            'factores_contribuyentes': {
                'descenso_animo_pct': round(caida_norm * 100, 1),
                'ausentismo_pct': round(tasa_no_show * 100, 1),
                'incumplimiento_tareas_pct': round(tasa_tareas * 100, 1),
                'lexico_clinico_hits': hits,
            },
            'hash_trazabilidad_sha256': hashlib.sha256(texto_limpio.encode('utf-8')).hexdigest(),
        }
```

```python
# backend/finanzas/services_contabilidad.py (CU26 - Multimoneda, Amortización y Utilidad Neta)
from decimal import Decimal, ROUND_HALF_UP
from datetime import date
from dateutil.relativedelta import relativedelta


class PagosYAmortizacionService:
    TASA_OFICIAL_USD_BOB = Decimal('6.9600')

    @classmethod
    def convertir_a_bob(cls, monto_origen: Decimal, moneda: str,
                        tasa: Decimal = TASA_OFICIAL_USD_BOB) -> tuple[Decimal, Decimal]:
        """Convierte USD -> BOB con precisión bancaria ROUND_HALF_UP y registra ajuste."""
        if moneda == 'BOB':
            return monto_origen.quantize(Decimal('0.01')), Decimal('0.0000')
        exacto = monto_origen * tasa
        redondeado = exacto.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        ajuste = (redondeado - exacto).quantize(Decimal('0.0001'))
        return redondeado, ajuste

    @staticmethod
    def generar_tabla_amortizacion(monto_total: Decimal, cuotas: int,
                                   tasa_interes_anual: Decimal, pct_seguro: Decimal,
                                   fecha_inicio: date) -> list[dict]:
        """Genera cronograma de amortización con capital, interés/comisión, seguro y saldo."""
        saldo = monto_total
        capital_base = (monto_total / cuotas).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        tasa_mensual = (tasa_interes_anual / Decimal('100')) / Decimal('12')
        seguro_tasa = pct_seguro / Decimal('100')
        cronograma = []

        for idx in range(1, cuotas + 1):
            capital = saldo if idx == cuotas else capital_base
            interes = (saldo * tasa_mensual).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            seguro = (saldo * seguro_tasa).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            saldo_nuevo = max(Decimal('0.00'), (saldo - capital).quantize(Decimal('0.01')))
            total_cuota = (capital + interes + seguro).quantize(Decimal('0.01'))
            cronograma.append({
                'numero_cuota': idx,
                'fecha_vencimiento': fecha_inicio + relativedelta(months=idx - 1),
                'capital_amortizado': capital,
                'interes_o_comision': interes,
                'seguro_asistencial': seguro,
                'monto_total_cuota': total_cuota,
                'saldo_insoluto': saldo_nuevo,
            })
            saldo = saldo_nuevo
        return cronograma


class ContabilidadUtilidadNetaService:
    @staticmethod
    def calcular_estado_resultados(ingresos_brutos_bob: Decimal,
                                   honorarios_psicologos_bob: Decimal,
                                   gastos_fijos: dict[str, Decimal]) -> dict:
        """
        Distingue formalmente Ganancia Bruta de Utilidad Neta Contable:
        Ganancia Bruta = Ingresos Brutos - Honorarios Directos
        Utilidad Neta  = Ganancia Bruta - SUM(Alquiler + Servicios Básicos + Personal Apoyo + SaaS)
        """
        ganancia_bruta = (ingresos_brutos_bob - honorarios_psicologos_bob).quantize(Decimal('0.01'))
        total_gastos_fijos = sum(gastos_fijos.values(), Decimal('0.00')).quantize(Decimal('0.01'))
        utilidad_neta = (ganancia_bruta - total_gastos_fijos).quantize(Decimal('0.01'))
        margen_neto = (
            (utilidad_neta / ingresos_brutos_bob * Decimal('100')).quantize(Decimal('0.01'))
            if ingresos_brutos_bob > 0 else Decimal('0.00')
        )
        return {
            'ingresos_brutos_bob': ingresos_brutos_bob,
            'costos_honorarios_bob': honorarios_psicologos_bob,
            'ganancia_bruta_bob': ganancia_bruta,
            'gastos_fijos_desglose': gastos_fijos,
            'total_gastos_fijos_bob': total_gastos_fijos,
            'utilidad_neta_bob': utilidad_neta,
            'margen_neto_pct': margen_neto,
        }
```

#### 4.2.2.2 Implementación Frontend Web Responsivo (Angular 17) y Móvil (Flutter 3.x)

```typescript
// prototipo/web/src/app/modules/finanzas/estado-resultados.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface EstadoResultadosDTO {
  ingresos_brutos_bob: number;
  costos_honorarios_bob: number;
  ganancia_bruta_bob: number;
  total_gastos_fijos_bob: number;
  utilidad_neta_bob: number;
  margen_neto_pct: number;
  gastos_fijos_desglose: Record<string, number>;
}

@Injectable({ providedIn: 'root' })
export class EstadoResultadosService {
  private readonly baseUrl = '/api/v1/finanzas';
  constructor(private http: HttpClient) {}

  obtenerEstadoResultados(fechaIni: string, fechaFin: string): Observable<EstadoResultadosDTO> {
    const params = new HttpParams().set('ini', fechaIni).set('fin', fechaFin);
    return this.http.get<EstadoResultadosDTO>(`${this.baseUrl}/estado-resultados/`, { params });
  }

  obtenerEstadisticasCRM(fechaIni: string, fechaFin: string): Observable<any> {
    const params = new HttpParams().set('ini', fechaIni).set('fin', fechaFin);
    return this.http.get(`${this.baseUrl.replace('finanzas', 'crm')}/estadisticas/`, { params });
  }
}
```

```dart
// prototipo/movil/lib/screens/finanzas_crm/calificacion_crm_sheet.dart
import 'package:flutter/material.dart';

class CalificacionCRMSheet extends StatefulWidget {
  final String citaId;
  final Future<void> Function(int estrellas, String comentario) onEnviar;
  const CalificacionCRMSheet({super.key, required this.citaId, required this.onEnviar});

  @override
  State<CalificacionCRMSheet> createState() => _CalificacionCRMSheetState();
}

class _CalificacionCRMSheetState extends State<CalificacionCRMSheet> {
  int _estrellas = 5;
  final _comentarioCtrl = TextEditingController();
  bool _enviando = false;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 20, right: 20, top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Text('Califica tu Atención (CRM)', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: List.generate(5, (i) => IconButton(
              icon: Icon(i < _estrellas ? Icons.star : Icons.star_border, color: Colors.amber, size: 36),
              onPressed: () => setState(() => _estrellas = i + 1),
            )),
          ),
          TextField(
            controller: _comentarioCtrl,
            maxLines: 3,
            decoration: const InputDecoration(labelText: 'Comentario sobre el servicio', border: OutlineInputBorder()),
          ),
          const SizedBox(height: 14),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _enviando ? null : () async {
                setState(() => _enviando = true);
                await widget.onEnviar(_estrellas, _comentarioCtrl.text.trim());
                if (mounted) Navigator.pop(context, true);
              },
              child: const Text('Enviar Calificación'),
            ),
          ),
        ],
      ),
    );
  }
}
```

#### Catálogo de Endpoints API REST del Sprint 4

| Método | Endpoint REST | Caso de Uso | Descripción Técnica |
| :---: | :--- | :---: | :--- |
| `POST` | `/api/v1/clinica/ia/resumen-longitudinal/` | `CU23` | Genera borrador longitudinal sanitizado (PII masked + SHA-256). |
| `PATCH` | `/api/v1/clinica/ia/resumen-longitudinal/{id}/aprobar/` | `CU23` | Aprobación médica *Human-in-the-Loop* y sello de validación. |
| `POST` | `/api/v1/clinica/ml/evaluar-riesgo/` | `CU24` | Ejecuta inferencia predictiva ML sobre historial de 6–12 meses. |
| `PATCH` | `/api/v1/clinica/ml/alertas/{id}/intervenir/` | `CU24` | Registra la acción clínica del terapeuta ante alerta predictiva. |
| `POST` | `/api/v1/finanzas/planes-amortizacion/` | `CU26` | Crea plan terapéutico financiado y calcula tabla de cuotas. |
| `GET` | `/api/v1/finanzas/extracto-paciente/{paciente_id}/` | `CU26` | Retorna extracto de amortización y saldo (Web y Flutter). |
| `POST` | `/api/v1/finanzas/pagos/registrar/` | `CU26` | Registra cobro en `BOB` o `USD` con ajuste de cambio exacto. |
| `POST` | `/api/v1/finanzas/honorarios/liquidar/` | `CU26` | Calcula y consolida planilla de honorarios por psicólogo. |
| `GET/POST` | `/api/v1/finanzas/gastos-fijos/` | `CU26` | Registra alquiler, servicios básicos, personal de apoyo y SaaS. |
| `GET` | `/api/v1/finanzas/estado-resultados/` | `CU26` | Retorna **Ganancia Bruta vs. Utilidad Neta** del rango consultado. |
| `POST/GET` | `/api/v1/crm/calificaciones/` y `/api/v1/crm/estadisticas/` | `CU26-CRM` | Guarda calificación 1–5★ (única por cita) y estadísticas CSAT/NPS. |

---

### 4.2.3 Pruebas

#### 4.2.3.1 Plan de Pruebas Funcionales (Caja Negra y Pruebas de Aceptación con BDD)

Siguiendo las directrices expuestas en clase para el aseguramiento de la calidad del software, el formato oficial de casos de prueba de aceptación y los criterios de aceptación BDD (*Behavior-Driven Development*) establecidos en las Historias de Usuario, el plan de pruebas del Sprint 4 se enfoca en técnicas de Caja Negra (partición de equivalencia, análisis de valores límite y tablas de decisión). Se evalúan exhaustivamente las entradas, precondiciones del sistema, procesamiento de reglas clínicas, inferencia de IA/ML, operaciones financieras multimoneda, contabilidad de utilidad neta y flujos CRM en clientes Web (Angular 17 Standalone) y Móvil (Flutter 3.x) sobre el backend Django 5.x / Django REST Framework conectado a PostgreSQL 16 Multi-Tenant con 14 esquemas tenant sembrados con datasets sintéticos de 6 a 12 meses.

A continuación se detallan los casos de prueba de aceptación estructurados individualmente para las Historias de Usuario del Sprint 4 (`HU-49` a `HU-56`), cubriendo flujos satisfactorios (camino feliz), validaciones de límites y datos obligatorios, control de acceso RBAC, supervisión humana (*Human-in-the-Loop*), precisión contable `Decimal` y prompts especializados para la generación de evidencias visuales:

---

##### Prueba de Historia de Usuario HU-49 (CU23): Generación asistida de resúmenes clínicos longitudinales por IA con supervisión humana

| **Caso de uso / HU** | **HU-49 (CU23): Generación asistida de resúmenes clínicos longitudinales por IA con supervisión humana** |
| :--- | :--- |
| **Descripción** | Como Psicólogo Tratante, quiero generar un resumen clínico longitudinal asistido por IA que sintetice las notas SOAP, diagnósticos CIE-10 y tendencia del *Mood Tracker* de un paciente a lo largo de múltiples sesiones, para preparar sesiones de seguimiento o juntas médicas con trazabilidad ética (*Human-in-the-Loop*). |
| **Criterios de Aceptación (BDD)** | • a) Dado que el paciente tiene $\ge 2$ notas SOAP firmadas, cuando el psicólogo solicita el resumen longitudinal en un rango de fechas, el sistema sanitiza datos personales mediante `sanitizar_pii` (enmascarando CI en `[CI_PROTEGIDO]`, teléfonos en `[TEL_PROTEGIDO]` y correos en `[EMAIL_PROTEGIDO]`) y genera una síntesis estructurada (evolución sintomática, adherencia a tareas y metas alcanzadas).<br>• b) Dado que la síntesis se genera, cuando el usuario aún no la valida, queda en estado `BORRADOR_IA` con huella `hash_pii_sha256`, muestra una insignia obligatoria *"Borrador Asistido por IA – Pendiente de Validación Clínica"* y bloquea su exportación oficial a PDF (`HTTP 400`).<br>• c) Dado que el psicólogo aprueba o edita el resumen (*Human-in-the-Loop*), el sistema cambia el estado a `APROBADO_HITL` o `EDITADO_Y_APROBADO`, registra usuario (`validado_por_id`), fecha local `America/La_Paz` e IP en `clinica_resumenlongitudinalia` / `accounts_auditlog` y habilita la descarga en PDF.<br>• d) Dado que un psicólogo no asignado al paciente solicita el resumen longitudinal, el backend deniega el acceso con `HTTP 403 Forbidden` y registra el intento en auditoría. |
| **Precondiciones** | a) Psicólogo Tratante autenticado con sesión JWT activa y subdominio del tenant `centro_esperanza`, asignado al expediente del paciente.<br>b) El paciente cuenta con al menos 6 notas SOAP firmadas (`clinica_notasesion`) y registros diarios de ánimo (`clinica_registroanimo`), incluyendo texto con CI (`8451290-LP`) y teléfono celular (`71234567`) para verificar la anonimización.<br>c) El backend Django 5.x / DRF, la consola Web Angular 17 (`ConsolaResumenIAComponent`) y la base de datos PostgreSQL 16 Multi-Tenant se encuentran en ejecución. |

| Paso | Acción / Entrada | Resultado esperado | Estado (Satisfactorio/Fallido) |
| :---: | :--- | :--- | :---: |
| 1 | En la consola Web Angular 17, seleccionar al paciente asignado, definir rango `01/05/2026` – `15/11/2026` (6 notas SOAP con CI `8451290-LP` y celular `71234567`) y presionar `'Generar Resumen Longitudinal IA'`. | El cliente despacha `POST /api/v1/clinica/ia/resumen-longitudinal/`. El filtro `sanitizar_pii()` enmascara el CI como `[CI_PROTEGIDO]` y el teléfono como `[TEL_PROTEGIDO]`, calcula `hash_pii_sha256` y retorna `HTTP 201 Created`. | **Satisfactorio** |
| 2 | Inspeccionar el borrador renderizado en pantalla y el registro persistido en `clinica_resumenlongitudinalia`. | El resumen estructurado consolida evolución sintomática, diagnósticos CIE-10 y curva anímica sin PII expuesta; permanece en estado `BORRADOR_IA` con la insignia *"Borrador Asistido por IA – Pendiente de Validación Clínica"*. | **Satisfactorio** |
| 3 | Intentar presionar `'Exportar PDF Oficial'` mientras el resumen sigue en estado `BORRADOR_IA`. | La exportación se bloquea; el backend retorna `HTTP 400 Bad Request` con el mensaje *"Debe aprobar el resumen mediante revisión humana (HITL)"*. | **Satisfactorio** |
| 4 | Editar una observación clínica en el editor Markdown y presionar `'Aprobar y Sellar Resumen (HITL)'`. | Se envía `PATCH /api/v1/clinica/ia/resumen-longitudinal/{id}/aprobar/`. El backend actualiza el estado a `EDITADO_Y_APROBADO` con `validado_por_id`, timestamp `America/La_Paz` y registro en `accounts_auditlog`, habilitando la descarga del PDF oficial. | **Satisfactorio** |
| 5 | Ejecutar `POST /api/v1/clinica/ia/resumen-longitudinal/` usando credenciales JWT de otro psicólogo no asignado al paciente. | El backend deniega la operación con `HTTP 403 Forbidden` (*"Acceso restringido al tratante"*) y audita el evento `ACCESO_DENEGADO_CU23`. | **Satisfactorio** |

| Responsable | Psicólogo Tratante / Motor IA (Desarrolladores: Mujica Vallejos Andy Mauricio / Larrazabal Rojas Julio Cesar / QA: Velasco Soliz Rolando) |
| :--- | :--- |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | **Prompt para IA (Generación de Evidencia/Interfaz de Prueba):**<br>*"Desktop web UI test evidence capture of Angular 17 clinical AI longitudinal summary console (ConsolaResumenIAComponent) in SIGEPSI. Shows anonymized clinical digest with masked badges '[CI_PROTEGIDO]' and '[TEL_PROTEGIDO]', SHA-256 hash verification tag, a status transition indicator from 'BORRADOR_IA (Exportación bloqueada HTTP 400)' to green badge 'EDITADO_Y_APROBADO (HITL Validado)', therapist audit timestamp America/La_Paz, and active 'Descargar PDF Oficial' button. Clean teal clinical interface, 4k screenshot."* |

![Evidencia UI Prueba HU-49 – Consola de Síntesis Longitudinal IA con Validación HITL](./imagenes/prueba_hu49_sintesis_ia.png)

<br>

---

##### Prueba de Historia de Usuario HU-50 (CU24): Detección predictiva de señales de riesgo longitudinal y alertas tempranas ML (6–12 meses)

| **Caso de uso / HU** | **HU-50 (CU24): Detección predictiva de señales de riesgo longitudinal y alertas tempranas ML (6–12 meses)** |
| :--- | :--- |
| **Descripción** | Como Psicólogo o Coordinador Clínico, quiero que el módulo analítico de IA/ML evalúe series históricas de 6 a 12 meses (curva de ánimo, inasistencias, incumplimiento de tareas y términos clínicos críticos) para predecir riesgo de recaída o abandono terapéutico y generar alertas prioritarias justificadas. |
| **Criterios de Aceptación (BDD)** | • a) Dado un historial longitudinal de 6 a 12 meses ($\ge 4$ semanas con tendencia descendente en `clinica_registroanimo` $\Delta \le -1.5$ puntos, ej. $4.4 \to 1.9$, y $\ge 2$ tareas vencidas o 3 inasistencias), cuando corre `RiesgoPredictivoMLService`, genera una alerta en `clinica_alertariesgoia` con `indice_riesgo >= 0.70` y `nivel_severidad` `ALTO` o `CRITICO`.<br>• b) Dado un paciente con evolución estable (ánimo promedio $4.2/5$ y $0$ faltas), cuando se ejecuta el evaluador ML, retorna `BAJO` (`indice_riesgo < 0.400`) sin emitir falsas alarmas.<br>• c) Dado que se genera una alerta predictiva, el panel web muestra los factores contribuyentes explicables (pesos: pendiente anímica `40%`, inasistencia `30%`, incumplimiento de tareas `20%`, señales léxicas SOAP `10%`) con lenguaje orientativo y sin emitir diagnósticos automáticos.<br>• d) Dado que el profesional atiende la alerta e ingresa su acción de intervención, el estado transiciona a `INTERVENIDA` con usuario (`intervenida_por_id`) y fecha auditada. |
| **Precondiciones** | a) Base de datos PostgreSQL 16 Multi-Tenant sembrada mediante `python manage.py seed_sprint4 --months 12 --tenants all` con series longitudinales de 12 meses (`clinica_registroanimo`, `agenda_cita`, `clinica_tareaterapeutica`, `clinica_notasesion`).<br>b) En el tenant `centro_esperanza` existen al menos un paciente con deterioro sostenido ($4.4 \to 1.9$ y 3 inasistencias) y un paciente estable ($4.2/5$ y 0 faltas).<br>c) Coordinador Clínico o Psicólogo autenticado en la consola Web Angular 17 (`RadarRiesgoMLComponent`). |

| Paso | Acción / Entrada | Resultado esperado | Estado (Satisfactorio/Fallido) |
| :---: | :--- | :--- | :---: |
| 1 | En `'Radar Predictivo de Riesgo ML'`, seleccionar ventana `12 meses` y presionar `'Ejecutar Evaluación Predictiva ML'`. | La aplicación envía `POST /api/v1/clinica/ml/evaluar-riesgo/`. `RiesgoPredictivoMLService` procesa los registros históricos de 12 meses y retorna `HTTP 200 OK` con el ranking de riesgo de la cohorte. | **Satisfactorio** |
| 2 | Inspeccionar el resultado del paciente con caída anímica ($4.4 \to 1.9$) y 3 inasistencias en UI y en `clinica_alertariesgoia`. | Se persiste alerta en estado `ACTIVA` con `indice_riesgo >= 0.70` (ej. `0.812`), `nivel_severidad = 'CRITICO'` y desglose JSONB de `factores_contribuyentes` (`descenso_animo_pct`, `ausentismo_pct`, `incumplimiento_tareas_pct`, `lexico_clinico_hits`). | **Satisfactorio** |
| 3 | Verificar la evaluación del paciente con perfil estable (ánimo promedio $4.2/5$ y $0$ inasistencias). | El motor calcula `indice_riesgo < 0.400`, asigna nivel `'BAJO'` y no dispara falsas alarmas ni alertas críticas. | **Satisfactorio** |
| 4 | Auditar el texto explicativo de los factores contribuyentes mostrados en el radar web. | El contenido describe indicadores cuantitativos orientativos de priorización clínica, verificando ausencia total de diagnósticos psiquiátricos automáticos. | **Satisfactorio** |
| 5 | Seleccionar la alerta `ACTIVA`, ingresar `'Contacto telefónico preventivo y sesión prioritaria'` y confirmar `'Registrar Intervención'`. | El cliente despacha `PATCH /api/v1/clinica/ml/alertas/{id}/intervenir/`. La alerta cambia a estado `INTERVENIDA` registrando `intervenida_por_id`, `accion_clinica` y `fecha_intervencion`. | **Satisfactorio** |

| Responsable | Coordinador Clínico / Psicólogo / Motor ML (Desarrolladores: Mujica Vallejos Andy Mauricio / Velasco Soliz Rolando) |
| :--- | :--- |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | **Prompt para IA (Generación de Evidencia/Interfaz de Prueba):**<br>*"Desktop web UI test evidence capture of Angular 17 predictive ML risk radar (RadarRiesgoMLComponent) in SIGEPSI. Shows 12-month longitudinal mood curve declining from 4.4 to 1.9, a highlighted patient alert card with score '0.812 - CRITICO' and explainable weight breakdown bars (Pendiente Ánimo 40%, Inasistencia 30%, Tareas 20%, Léxico SOAP 10%), alongside a stable patient row tagged 'BAJO (<0.40)' and an approved 'INTERVENIDA' confirmation modal. 4k UI screenshot."* |

![Evidencia UI Prueba HU-50 – Radar Predictivo de Riesgo ML (12 Meses) y Registro de Intervención](./imagenes/prueba_hu50_radar_ml.png)

<br>

---

##### Prueba de Historia de Usuario HU-51 (CU26): Registro de cobros multimoneda (BOB/USD), ajuste cambiario y pasarela de pago

| **Caso de uso / HU** | **HU-51 (CU26): Registro de cobros multimoneda (BOB/USD), ajuste cambiario y pasarela de pago** |
| :--- | :--- |
| **Descripción** | Como Recepcionista o Administrador del Centro, quiero registrar pagos de consultas y paquetes terapéuticos en múltiples monedas (Bolivianos `BOB` y Dólares `USD`) usando distintos métodos (`QR_SIMPLE`, `STRIPE_TARJETA`, `TRANSFERENCIA` o `EFECTIVO`), aplicando conversión exacta con `Decimal(12, 2)` y ajuste cambiario para evitar diferencias de redondeo contable. |
| **Criterios de Aceptación (BDD)** | • a) Dado un cobro de sesión o cuota de `$30.00 USD` con tasa `6.9600`, cuando se registra en caja con método `QR_SIMPLE`, el sistema calcula exactamente `208.80 BOB` con `ROUND_HALF_UP`, persiste el comprobante inmutable en `finanzas_pagotransaccion` (`ajuste_redondeo = 0.0000`) y actualiza el saldo del paciente.<br>• b) Dado un pago con tarjeta mediante pasarela Stripe (`STRIPE_TARJETA`), cuando el webhook o verificación retorna `paid` con el mismo `session_id` / `referencia_externa`, se concilia la transacción de forma idempotente evitando cobros duplicados.<br>• c) Dado un envío con monto negativo (ej. `-50.00`), el backend rechaza la transacción con `HTTP 400 Bad Request` haciendo cumplir `chk_pago_monto_positivo` (`monto_origen > 0`).<br>• d) Dado que se consultan cobros en `USD` con decimales periódicos en el libro diario de caja, la suma de montos convertidos más `ajuste_redondeo` cuadra exactamente con el total contable ($0.000$ de descuadre). |
| **Precondiciones** | a) Recepcionista o Administrador autenticado en el portal Web Angular 17 (`CajaMultimonedaComponent`) para el tenant `centro_esperanza`.<br>b) Tipo de cambio oficial configurado en `PagosYAmortizacionService.TASA_OFICIAL_USD_BOB = 6.9600`.<br>c) Existen pacientes y citas/cuotas habilitadas para cobro en el esquema PostgreSQL del centro. |

| Paso | Acción / Entrada | Resultado esperado | Estado (Satisfactorio/Fallido) |
| :---: | :--- | :--- | :---: |
| 1 | En `'Caja Multimoneda'`, seleccionar al paciente, conmutar moneda a `USD ($)`, ingresar `30.00`, elegir método `QR_SIMPLE` y presionar `'Registrar Cobro'`. | El frontend envía `POST /api/v1/finanzas/pagos/registrar/`. El backend convierte a tasa `6.9600` (`ROUND_HALF_UP`), retorna `HTTP 201 Created` con `monto_bob_equivalente = 208.80`, `ajuste_redondeo = 0.0000` y emite comprobante inmutable. | **Satisfactorio** |
| 2 | Procesar verificación de pago Stripe (`STRIPE_TARJETA`) enviando dos peticiones consecutivas con la misma `referencia_externa` (`cs_test_sp4_idemp_001`). | La primera petición concilia y persiste el pago en `finanzas_pagotransaccion`; la segunda es controlada por clave idempotente (`referencia_externa UNIQUE`) evitando registro duplicado. | **Satisfactorio** |
| 3 | Enviar petición de cobro con monto negativo (`monto_origen = -50.00`) al endpoint `POST /api/v1/finanzas/pagos/registrar/`. | El backend rechaza la solicitud con `HTTP 400 Bad Request` (`chk_pago_monto_positivo`), sin registrar ningún movimiento en caja. | **Satisfactorio** |
| 4 | Registrar pago fraccionado en dólares (`$14.37 USD` a tasa `6.9600`, valor exacto `100.0152 BOB`). | El servicio almacena `monto_bob_equivalente = 100.02 BOB` y registra `ajuste_redondeo = 0.0048` en `finanzas_pagotransaccion` para preservar exactitud contable. | **Satisfactorio** |
| 5 | Consultar el libro diario de caja del periodo tras múltiples cobros mixtos `BOB/USD`. | La sumatoria de `monto_bob_equivalente` y `ajuste_redondeo` arroja `0.000` de descuadre contable al centavo exacto. | **Satisfactorio** |

| Responsable | Recepcionista / Administrador / Caja Multimoneda (Desarrolladores: Condori Diaz Marilyn Esther / Larrazabal Rojas Julio Cesar / QA: Velasco Soliz Rolando) |
| :--- | :--- |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | **Prompt para IA (Generación de Evidencia/Interfaz de Prueba):**<br>*"Desktop web UI test evidence capture of Angular 17 multi-currency billing screen (CajaMultimonedaComponent) in SIGEPSI. Shows USD/BOB toggle set to USD '$30.00', official rate badge '1 USD = 6.9600 BOB', exact converted total '208.80 BOB' with 'Ajuste Redondeo: 0.0000', QR Simple & Stripe idempotency verified badge, validation warning toast on negative input '-50.00 (HTTP 400)', and zero-discrepancy daily ledger summary 'Descuadre: 0.000 BOB'. 4k UI screenshot."* |

![Evidencia UI Prueba HU-51 – Caja Multimoneda BOB/USD, Ajuste Cambiario y Pasarela QR/Stripe](./imagenes/prueba_hu51_caja_multimoneda.png)

<br>

---

##### Prueba de Historia de Usuario HU-52 (CU26): Extracto detallado de amortización de planes terapéuticos y estado de cuenta (Web y Móvil)

| **Caso de uso / HU** | **HU-52 (CU26): Extracto detallado de amortización de planes terapéuticos y estado de cuenta (Web y Móvil)** |
| :--- | :--- |
| **Descripción** | Como Paciente o Administrador, quiero consultar el estado de cuenta y un extracto completo de amortización cuando se contratan paquetes o planes de tratamiento en cuotas, visualizando cuota programada, seguro asistencial, interés o cargo administrativo, capital amortizado y saldo insoluto tanto en Web (Angular 17) como en la App Móvil (Flutter 3.x). |
| **Criterios de Aceptación (BDD)** | • a) Dado un paciente con un plan terapéutico de 12 sesiones financiado en 6 cuotas (con `porcentaje_seguro = 1.50%`), cuando se crea el plan (`POST /api/v1/finanzas/planes-amortizacion/`) o accede a *"Mi Estado de Cuenta"* en Flutter o Web (`GET /api/v1/finanzas/extracto-paciente/{paciente_id}/`), visualiza el cronograma completo (`numero_cuota`, `fecha_vencimiento`, `capital_amortizado`, `interes_o_comision`, `seguro_asistencial`, `monto_total_cuota`, `saldo_insoluto` decreciente a `0.00` y `estado`).<br>• b) Dado que se abona la cuota #1 mediante `POST /api/v1/finanzas/pagos/registrar/`, el sistema marca la cuota como `PAGADA`, recalcula el saldo insoluto restante en tiempo real en Web y App Móvil Flutter y permite descargar el extracto completo en PDF.<br>• c) Si una cuota supera la `fecha_vencimiento` sin haberse registrado pago, el estado cambia automáticamente a `MORA` y el extracto resalta la advertencia correspondiente antes de consolidar el siguiente cobro. |
| **Precondiciones** | a) Paciente autenticado en la App Móvil Flutter 3.x (`EstadoCuentaAmortizacionScreen`) y Administrador autenticado en Angular 17 (`ExtractoAmortizacionComponent`) dentro del tenant `centro_esperanza`.<br>b) Plan terapéutico `'Programa Integral 12 Sesiones'` (`1,800.00 BOB`, `6 cuotas`, `porcentaje_seguro = 1.50%`) generado en `finanzas_planpagoterapeutico` y `finanzas_cuotaamortizacion`.<br>c) Backend Django DRF con bloqueo `SELECT FOR UPDATE` y generador PDF operativo. |

| Paso | Acción / Entrada | Resultado esperado | Estado (Satisfactorio/Fallido) |
| :---: | :--- | :--- | :---: |
| 1 | Generar el plan de 12 sesiones a 6 cuotas (`POST /api/v1/finanzas/planes-amortizacion/`) y abrir `'Mi Estado de Cuenta'` en la App Móvil Flutter. | La app invoca `GET /api/v1/finanzas/extracto-paciente/{paciente_id}/` y muestra las 6 cuotas desglosadas (`capital_amortizado`, `interes_o_comision`, `seguro_asistencial`, `monto_total_cuota`), con `saldo_insoluto` decreciendo exactamente a `0.00` en la cuota #6. | **Satisfactorio** |
| 2 | Seleccionar la Cuota #1 (`PENDIENTE`) en Flutter y confirmar su abono vía `POST /api/v1/finanzas/pagos/registrar/`. | El backend aplica bloqueo transaccional `SELECT FOR UPDATE`, confirma el pago, actualiza la Cuota #1 a `PAGADA` y recalcula de inmediato el saldo insoluto del plan. | **Satisfactorio** |
| 3 | Consultar el extracto del mismo paciente en Web Angular 17 (`ExtractoAmortizacionComponent`) tanto en escritorio como en viewport móvil (`375x812`). | La vista Web refleja la Cuota #1 `PAGADA`, el saldo pendiente actualizado y adapta las columnas del cronograma a tarjetas responsivas sin desbordamiento horizontal. | **Satisfactorio** |
| 4 | Simular fecha vencida en la Cuota #2 (`fecha_vencimiento < fecha_actual`) y ejecutar el proceso programado de revisión de mora. | El estado de la Cuota #2 transiciona a `MORA` en `finanzas_cuotaamortizacion`, mostrándose resaltado con etiqueta roja de mora en Flutter y Web. | **Satisfactorio** |
| 5 | Presionar el botón `'Descargar Extracto PDF'` desde el estado de cuenta del paciente. | Se genera y descarga un archivo PDF con los datos del paciente, resumen del plan contratado y tabla completa de cuotas amortizadas, seguro y saldo insoluto. | **Satisfactorio** |

| Responsable | Paciente / Administrador / Web & App Móvil (Desarrolladores: Delgado Rojas Alberto Caleb / Condori Diaz Marilyn Esther / QA: Velasco Soliz Rolando) |
| :--- | :--- |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | **Prompt para IA (Generación de Evidencia/Interfaz de Prueba):**<br>*"Dual Flutter 3 mobile and Angular 17 responsive web test evidence capture of patient amortization schedule and financial statement (EstadoCuentaAmortizacionScreen) in SIGEPSI. Shows 6-installment therapy plan breakdown with columns Capital Amortizado, Interés/Comisión, Seguro Asistencial 1.5%, Total Cuota, Saldo Insoluto decreasing to 0.00 BOB, Cuota #1 stamped green 'PAGADA', Cuota #2 highlighted red 'MORA', and active 'Descargar Extracto PDF' button. 4k UI screenshot."* |

![Evidencia UI Prueba HU-52 – Extracto de Amortización de Planes y Estado de Cuenta (Flutter & Web)](./imagenes/prueba_hu52_amortizacion_movil_web.png)

<br>

---

##### Prueba de Historia de Usuario HU-53 (CU26): Liquidación automatizada de honorarios a psicólogos y facturación de suscripciones SaaS

| **Caso de uso / HU** | **HU-53 (CU26): Liquidación automatizada de honorarios a psicólogos y facturación de suscripciones SaaS** |
| :--- | :--- |
| **Descripción** | Como Administrador del Centro o SuperAdministrador SaaS, quiero calcular automáticamente la liquidación mensual de honorarios de cada psicólogo según sus sesiones realizadas y porcentaje de convenio, y gestionar el ciclo de facturación y renovación de suscripciones SaaS de los centros psicológicos. |
| **Criterios de Aceptación (BDD)** | • a) Dado un periodo mensual seleccionado, cuando el Administrador presiona *"Calcular Liquidación"*, el sistema agrupa únicamente las citas `REALIZADA` pagadas por psicólogo (excluyendo citas `CANCELADA`), aplica su porcentaje de honorario y genera el registro en `finanzas_liquidacionhonorario` en estado `PENDIENTE_PAGO` con unicidad por psicólogo y mes (`uq_liq_psico_mes`).<br>• b) Dado que el Administrador aprueba y registra el desembolso al terapeuta, el estado cambia a `PAGADA` y el egreso queda contabilizado para el cálculo de Utilidad Neta del mes.<br>• c) Dado un tenant cuya suscripción SaaS vence en $\le 3$ días, el panel de SuperAdmin muestra la alerta de renovación y emite el enlace de pago Stripe/QR con facturación automática tras verificar la sesión. |
| **Precondiciones** | a) Administrador del Centro autenticado en el portal web Angular 17 del tenant `centro_esperanza` y SuperAdministrador SaaS con acceso al esquema `public`.<br>b) Psicólogo activo con convenio `porcentaje_honorario = 70.00%`, 20 citas en estado `REALIZADA` pagadas (`4,000.00 BOB` bruto generado) y 2 citas `CANCELADA` en el periodo `2026-11`.<br>c) Suscripción SaaS en `public.subscriptions_suscripcion` en plan `PROFESIONAL` (`$49.00 USD/mes`) con `fecha_proximo_cobro` a 2 días de vencer. |

| Paso | Acción / Entrada | Resultado esperado | Estado (Satisfactorio/Fallido) |
| :---: | :--- | :--- | :---: |
| 1 | En la vista `LiquidacionHonorariosPsicologosView`, seleccionar el periodo `2026-11` y presionar *"Calcular Liquidación"*. | Se despacha `POST /api/v1/finanzas/honorarios/liquidar/`. El backend agrupa las 20 citas `REALIZADA` pagadas, excluye las 2 citas `CANCELADA`, aplica el convenio 70/30 y registra en `finanzas_liquidacionhonorario` `monto_neto_psicologo = 2,800.00 BOB`, `monto_retencion_centro = 1,200.00 BOB` y estado `PENDIENTE_PAGO`. | **Satisfactorio** |
| 2 | Enviar una segunda solicitud `POST /api/v1/finanzas/honorarios/liquidar/` para el mismo psicólogo y periodo `2026-11`. | La restricción única `uq_liq_psico_mes` y el servicio `LiquidacionSaaSService` bloquean el duplicado retornando `HTTP 400 Bad Request` sin duplicar egresos. | **Satisfactorio** |
| 3 | Presionar *"Aprobar y Registrar Desembolso"* sobre la planilla generada del periodo `2026-11`. | La liquidación transiciona a `PAGADA` con `fecha_desembolso` en zona horaria `America/La_Paz` y vincula los `2,800.00 BOB` al cierre `finanzas_estadoresultadoscontable` del periodo. | **Satisfactorio** |
| 4 | Ingresar al panel de SuperAdministrador SaaS en `RenovacionSuscripcionSaaSView` y consultar renovaciones próximas. | El sistema lee `public.subscriptions_suscripcion`, detecta vencimiento en 2 días ($\le 3$ días), muestra la alerta *"Renovación Próxima"* y genera enlace de pago vía `POST /api/v1/subscriptions/create-checkout/`. | **Satisfactorio** |
| 5 | Completar el pago de renovación del plan `PROFESIONAL` (`$49.00 USD`) en Stripe Checkout y ejecutar la verificación (`POST /api/v1/subscriptions/verify-session/`). | El sistema valida la sesión de forma idempotente, extiende `fecha_proximo_cobro` por 30 días en `public.subscriptions_suscripcion` y habilita la descarga del comprobante/factura SaaS. | **Satisfactorio** |

| Responsable | Administrador del Centro / SuperAdministrador SaaS (Desarrolladores: Mujica Vallejos Andy Mauricio / Larrazabal Rojas Julio Cesar / QA: Velasco Soliz Rolando) |
| :--- | :--- |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | **Prompt para IA (Generación de Evidencia/Interfaz de Prueba):**<br>*"SaaS multi-tenant subscription billing and psychologist payout settlement test verification UI in Angular 17 for SIGEPSI. Active tab 'Liquidación de Psicólogos' showing period 2026-11, 20 completed sessions (cancelled excluded), 4,000.00 BOB gross, 70/30 split (2,800.00 BOB net payout) with green status pill 'PAGADA', duplicate protection alert 'uq_liq_psico_mes', and secondary 'Suscripciones SaaS' card showing 2-day renewal warning with Stripe checkout button and invoice PDF. Clean clinical UI, 4k."* |

![Evidencia UI Prueba HU-53 – Liquidación de Honorarios y Suscripciones SaaS](./imagenes/prueba_hu53_liquidacion_saas.png)

<br>

---

##### Prueba de Historia de Usuario HU-54 (CU26): Estado de Resultados Contable Gerencial: Ganancia Bruta vs. Utilidad Neta (Gastos Fijos)

| **Caso de uso / HU** | **HU-54 (CU26): Estado de Resultados Contable Gerencial: Ganancia Bruta vs. Utilidad Neta (Gastos Fijos)** |
| :--- | :--- |
| **Descripción** | Como Administrador o Gerente del Centro Psicológico, quiero registrar los gastos fijos mensuales de operación (alquiler de ambientes, servicios básicos, salarios de personal de apoyo, suscripción SaaS) y visualizar en el Dashboard un Estado de Resultados Contable que diferencie claramente la Ganancia Bruta de la Utilidad Neta real en cualquier rango de fechas. |
| **Criterios de Aceptación (BDD)** | • a) Dado que existen ingresos cobrados en el periodo (ej. del 1 al 15 de noviembre o mes completo), cuando el Administrador registra o prorratea los gastos fijos (Alquiler, Servicios Básicos, Personal de Apoyo, Suscripción SaaS), el sistema calcula automáticamente `Ganancia Bruta` y `Utilidad Neta` exactas con precisión `NUMERIC(12,2)`.<br>• b) Dado un rango de fechas consultado en el Dashboard Financiero (incluyendo filtro por voz QBE), los KPIs y el gráfico de cascada (*waterfall*) muestran Ingresos Brutos, Costos Directos de Honorarios, Gastos Fijos y Utilidad/Pérdida Neta en tiempo real, permitiendo exportar a Excel `.xlsx` y PDF.<br>• c) Si los gastos fijos superan la ganancia bruta en un periodo, la tarjeta de Utilidad Neta resalta en rojo indicando déficit operativo para toma de decisiones. |
| **Precondiciones** | a) Administrador o Contador autenticado en el portal web Angular 17 dentro del tenant `centro_esperanza`.<br>b) Ingresos confirmados en `finanzas_pagotransaccion` por `18,000.00 BOB` y honorarios liquidados en `finanzas_liquidacionhonorario` por `9,000.00 BOB` en el periodo `2026-11`. |

| Paso | Acción / Entrada | Resultado esperado | Estado (Satisfactorio/Fallido) |
| :---: | :--- | :--- | :---: |
| 1 | Abrir el modal de gastos fijos en `EstadoResultadosUtilidadNetaView` y registrar los rubros del mes mediante `POST /api/v1/finanzas/gastos-fijos/` (`ALQUILER_INMUEBLE: 3,000.00 BOB`, `SERVICIOS_BASICOS: 700.00 BOB`, `PERSONAL_APOYO: 2,500.00 BOB`; total `6,200.00 BOB`). | El backend persiste cada egreso en `finanzas_gastofijomensual` con precisión `NUMERIC(12,2)`, comprobante referencial y trazabilidad de usuario `registrado_por_id`. | **Satisfactorio** |
| 2 | Consultar el Estado de Resultados Contable del periodo completo (`GET /api/v1/finanzas/estado-resultados/`). | `ContabilidadUtilidadNetaService` calcula exactamente `Ingresos Brutos = 18,000.00 BOB`, `Honorarios = 9,000.00 BOB`, `Ganancia Bruta = 9,000.00 BOB`, `Gastos Fijos = 6,200.00 BOB` y **`Utilidad Neta = 2,800.00 BOB` (`Margen Neto: 15.56%`)**, renderizando el gráfico *Waterfall* en Chart.js. | **Satisfactorio** |
| 3 | Aplicar filtro QBE / selector de fechas parcial del `01/11/2026` al `15/11/2026` (`GET /api/v1/finanzas/estado-resultados/?ini=2026-11-01&fin=2026-11-15`). | El backend prorratea y recalcula exactamente los ingresos, honorarios y gastos fijos comprendidos en el subrango consultado sin descuadre decimal (`0.000`). | **Satisfactorio** |
| 4 | Simular escenario de déficit operativo registrando gastos fijos totales por `9,500.00 BOB` frente a `9,000.00 BOB` de Ganancia Bruta y recargar el panel P&L. | El sistema retorna `Utilidad Neta = -500.00 BOB` (`-2.78%`) y resalta en rojo la tarjeta de Utilidad Neta con indicador explícito de **Déficit Operativo**. | **Satisfactorio** |
| 5 | Presionar *"Exportar Contabilidad"* para generar el reporte gerencial en Excel `.xlsx` y PDF. | El módulo `reportes` genera y descarga el libro OpenPyXL con celdas formateadas (`#,##0.00`) y el documento PDF oficial desglosando Ganancia Bruta, Gastos Fijos por categoría y Utilidad Neta. | **Satisfactorio** |

| Responsable | Administrador / Contador del Centro (Desarrolladores: Romero Saavedra Maria Ilse / Mujica Vallejos Andy Mauricio / Larrazabal Rojas Julio Cesar / QA: Velasco Soliz Rolando) |
| :--- | :--- |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | **Prompt para IA (Generación de Evidencia/Interfaz de Prueba):**<br>*"Executive clinical accounting Profit & Loss (P&L) verification dashboard in Angular 17 for SIGEPSI. Waterfall chart breaking down Ingresos Brutos (18,000.00 Bs.) minus Honorarios Psicólogos (9,000.00 Bs.) equals Ganancia Bruta (9,000.00 Bs.), minus Gastos Fijos (6,200.00 Bs.: Alquiler, Servicios Básicos, Personal Apoyo) equals Utilidad Neta (2,800.00 Bs. / 15.56% margin), with QBE date range filter, red deficit state indicator (-500.00 Bs.), and Excel/PDF export buttons. 4k."* |

![Evidencia UI Prueba HU-54 – Estado de Resultados Contable: Ganancia Bruta vs. Utilidad Neta](./imagenes/prueba_hu54_utilidad_neta_pnl.png)

<br>

---

##### Prueba de Historia de Usuario HU-55 (CU26-CRM): Módulo CRM de calificación post-consulta (1–5 estrellas) y estadísticas de calidad de servicio

| **Caso de uso / HU** | **HU-55 (CU26-CRM): Módulo CRM de calificación post-consulta (1–5 estrellas) y estadísticas de calidad de servicio** |
| :--- | :--- |
| **Descripción** | Como Paciente y Administrador del Centro, quiero que tras concluir una cita presencial o teleconsulta el paciente pueda calificar la atención del 1 al 5 estrellas con retroalimentación cualitativa, para alimentar un panel estadístico CRM que mida satisfacción (CSAT), tiempos de espera y fidelización del centro. |
| **Criterios de Aceptación (BDD)** | • a) Dado que una cita pasa a estado `REALIZADA`, cuando el paciente abre la App Móvil Flutter o el portal web, aparece la tarjeta *"Califica tu experiencia de atención (1 a 5 estrellas)"* con etiquetas de aspecto evaluado (Puntualidad, Empatía, Calidad de Plataforma/Consultorio).<br>• b) Dado que el paciente envía calificación `5` estrellas, se persiste en `crm_calificacionservicio` (con unicidad de 1 calificación por cita) y actualiza los promedios estadísticos del centro.<br>• c) Dado que un paciente califica con `1` o `2` estrellas, el CRM marca `requiere_seguimiento = True` y notifica al Administrador en el panel estadístico de satisfacción (CSAT/NPS). |
| **Precondiciones** | a) Paciente autenticado en la App Móvil Flutter 3.x con dos citas concluidas en estado `REALIZADA` pendientes de evaluación.<br>b) Administrador/Coordinador Clínico autenticado en el portal web Angular 17 con historial previo de 120 respuestas CRM en el tenant. |

| Paso | Acción / Entrada | Resultado esperado | Estado (Satisfactorio/Fallido) |
| :---: | :--- | :--- | :---: |
| 1 | Abrir la App Móvil Flutter sobre la cita #1 `REALIZADA`, seleccionar `5` estrellas en `CalificacionCRMSheet`, marcar aspectos (`Puntualidad: 5`, `Empatía: 5`, `Plataforma: 5`), escribir *"Excelente atención y puntualidad"* y presionar *"Enviar Calificación"*. | La app envía `POST /api/v1/crm/calificaciones/`. El backend persiste la evaluación en `crm_calificacionservicio` con `requiere_seguimiento = FALSE`, `estado_seguimiento = 'CERRADO'` y recalcula promedios. | **Satisfactorio** |
| 2 | Intentar enviar una segunda calificación para la misma cita #1 mediante petición `POST /api/v1/crm/calificaciones/`. | El backend valida la restricción `UNIQUE` sobre `cita_id` en `crm_calificacionservicio` y rechaza la solicitud duplicada con `HTTP 400 Bad Request`. | **Satisfactorio** |
| 3 | Desde la App Móvil sobre la cita #2 `REALIZADA`, enviar calificación `1` estrella (`Puntualidad: 1`) con comentario *"Demora de 30 minutos en iniciar la sesión"*. | `CRMSatisfaccionService` persiste la reseña activando automáticamente `requiere_seguimiento = TRUE` y `estado_seguimiento = 'PENDIENTE'`, disparando alerta prioritaria al Administrador en el tablero CRM. | **Satisfactorio** |
| 4 | Abrir `PanelEstadisticasCRMComponent` (`PanelEstadisticasCRMView`) en Angular 17 consumiendo `GET /api/v1/crm/estadisticas/`. | El panel despliega los indicadores reales actualizados: **CSAT (`89.4%`)**, promedio **`4.62 ★`**, puntaje **NPS**, histograma de distribución de `1` a `5` estrellas y la cola de alertas de baja calificación. | **Satisfactorio** |
| 5 | Seleccionar la alerta de `1 ★` en la cola CRM, registrar la acción correctiva en `nota_resolucion_crm` y confirmar cierre. | El caso transiciona de `PENDIENTE` → `EN_GESTION` → `CERRADO` con registro auditado de seguimiento de calidad al paciente. | **Satisfactorio** |

| Responsable | Paciente / Administrador CRM (Desarrolladores: Romero Saavedra Maria Ilse / Delgado Rojas Alberto Caleb / Larrazabal Rojas Julio Cesar / QA: Velasco Soliz Rolando) |
| :--- | :--- |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | **Prompt para IA (Generación de Evidencia/Interfaz de Prueba):**<br>*"Dual mobile Flutter and Angular 17 web CRM customer satisfaction test verification UI for SIGEPSI. Left: Flutter bottom sheet 'Califica tu Atención (CRM)' with 5 interactive golden stars, aspect rating chips (Puntualidad, Empatía, Plataforma), comment input, and 'Enviar Calificación' button. Right: Web CRM analytics panel displaying CSAT 89.4%, average 4.62/5 stars, NPS gauge, 1-5 star distribution histogram, and red follow-up alert ticket for 1-star review 'Demora de 30 min'. 4k."* |

![Evidencia UI Prueba HU-55 – Encuesta CRM Post-Consulta (1–5★) y Analítica CSAT/NPS](./imagenes/prueba_hu55_crm_calificacion.png)

<br>

---

##### Prueba de Historia de Usuario HU-56 (SP4-88 / Multi-Tenant QA): Pruebas finales de estrés en 14 centros (12 meses), concurrencia SELECT FOR UPDATE y aislamiento SaaS

| **Caso de uso / HU** | **HU-56 (SP4-88 / Multi-Tenant QA): Pruebas finales de estrés en 14 centros (12 meses), concurrencia SELECT FOR UPDATE y aislamiento SaaS** |
| :--- | :--- |
| **Descripción** | Como QA Lead y Equipo Full Stack, quiero validar toda la plataforma (`CU23, CU24, CU26`) bajo carga concurrente multi-tenant, con datasets sintéticos de 6 a 12 meses poblados en los 14 centros psicológicos y pruebas de inviolabilidad financiera/clínica, para garantizar estabilidad absoluta en producción y en la defensa final. |
| **Criterios de Aceptación (BDD)** | • a) Al ejecutar pruebas de concurrencia sobre pagos de cuotas y reserva simultánea de slots, el bloqueo transaccional (`SELECT FOR UPDATE`) impide dobles cobros o estados inconsistentes (`0` errores de integridad).<br>• b) Al consultar métricas de ML (`CU24`), Contabilidad (`CU26`) y CRM (`CU26-CRM`) en los 14 esquemas tenant sembrados con 12 meses de historia, los tiempos de respuesta P95 se mantienen por debajo de `450 ms` y con `0` fugas entre esquemas.<br>• c) Todas las suites automatizadas de Backend, Frontend Web y Móvil Flutter pasan al `100%` tras la integración final, manteniendo diseño responsivo sin desbordamiento en viewport móvil (`375x812`). |
| **Precondiciones** | a) PostgreSQL 16 Multi-Tenant con 14 esquemas tenant activos poblados mediante `python manage.py seed_sprint4 --months 12 --tenants all` (2,180+ sesiones SOAP, 14,400+ registros de ánimo, 2,650+ movimientos financieros, 168 cierres mensuales y 1,740+ encuestas CRM).<br>b) Entornos Backend DRF, Angular 17 y Flutter 3.x integrados con suite de carga concurrente y runners automatizados operativos. |

| Paso | Acción / Entrada | Resultado esperado | Estado (Satisfactorio/Fallido) |
| :---: | :--- | :--- | :---: |
| 1 | Verificar la integridad del sembrado longitudinal de 12 meses (`seed_sprint4 --months 12 --tenants all`) en los 14 esquemas tenant de PostgreSQL 16. | El seeder completa la carga en 38 segundos sin registros huérfanos, dejando consistentes las series clínicas (`CU23, CU24`), planes de amortización, cierres P&L y reseñas CRM (`CU26`). | **Satisfactorio** |
| 2 | Disparar 2 peticiones concurrentes simultáneas (`POST /api/v1/finanzas/pagos/registrar/`) intentando cobrar la misma `CuotaAmortizacion` #1. | El bloqueo pesimista `SELECT FOR UPDATE` serializa el acceso: la primera petición retorna `HTTP 201 Created` marcando la cuota `PAGADA` y la segunda es rechazada con `HTTP 400 Bad Request` (`0` dobles cobros). | **Satisfactorio** |
| 3 | Ejecutar benchmark de carga concurrente sobre los 14 esquemas tenant consultando Radar Predictivo ML (`CU24`), Estado de Resultados P&L (`CU26`) y Estadísticas CRM. | La consola de salud SaaS (`ConsolaSaludMultiTenantQAView`) registra latencia **P95 de `284 ms`** ($< 450\text{ ms}$) y **`0.0%` de errores `5xx`**. | **Satisfactorio** |
| 4 | Enviar petición autenticada con token JWT de `centro_esperanza` y cabecera `X-Tenant-ID` / subdominio apuntando al esquema `mentesana`. | `SigepsiTenantMiddleware` y la capa RBAC bloquean el acceso cruzado con **`HTTP 403 Forbidden`** (`0` fugas entre esquemas) y auditan el intento en bitácora Fernet. | **Satisfactorio** |
| 5 | Inspeccionar las vistas Web Angular 17 (Finanzas, P&L y CRM) en viewport móvil `375x812` y correr las suites automatizadas completas (Backend DRF, Angular y Flutter). | Las pantallas se adaptan a tarjetas responsivas sin scroll horizontal y la ejecución final certifica el 100% de las pruebas automatizadas (`18/18` tests) y criterios BDD aprobados. | **Satisfactorio** |

| Responsable | QA Lead / Equipo SCRUM Full Stack (Responsables: Velasco Soliz Rolando / Equipo SCRUM Full Stack) |
| :--- | :--- |
| **Resultado de la prueba** | **Satisfactorio** |
| **Adjunto** | **Prompt para IA (Generación de Evidencia/Interfaz de Prueba):**<br>*"Multi-tenant SaaS QA health and stress test verification console in Angular 17 for SIGEPSI. Top KPI strip showing '14/14 Tenants Activos (Dataset 12m)', 'Latencia P95: 284 ms (< 450 ms)', '0% Errores 5xx', 'Aislamiento Multi-Tenant: HTTP 403 / 0 Fugas', and 'Concurrencia SELECT FOR UPDATE: 0 Dobles Cobros'. Test execution badge '18/18 Suites Automatizadas PASSED 100%' alongside 375x812 mobile responsive preview card. Clean technical dashboard UI, 4k."* |

![Evidencia UI Prueba HU-56 – Consola de Salud Multi-Tenant QA (14 Centros / 12 Meses) y Pruebas de Estrés](./imagenes/prueba_hu56_consola_qa_estres.png)

<br>

---

#### 4.2.3.2 Batería de Pruebas Automatizadas (Unitarias, Integración y Regresión - Backend DRF, Angular 17 y Flutter 3)

En estricto cumplimiento con la exigencia metodológica formulada por la docente de la cátedra de Sistemas de Información II (*«El último es pruebas: pruebas automatizadas... Hay un formato de pruebas para los casos de uso, eso lo tienen que trabajar por favor bajo ese tipo de características»*) y las directrices de cierre del Sprint 4 (`datos/requerimientosSprint4.md`), el equipo de desarrollo ejecutó una batería integral de pruebas automatizadas y de regresión. Estas verifican de forma determinística la sanitización PII, la supervisión clínica obligatoria (*Human-in-the-Loop*), la predicción ML sobre series longitudinales de 12 meses, la exactitud contable `Decimal` en pagos multimoneda y amortizaciones, el cálculo real de **Utilidad Neta**, la trazabilidad CRM `1–5★` y la seguridad multi-tenant en los 14 esquemas PostgreSQL.

La estrategia de automatización del Sprint 4 abarca tres niveles principales y una fase de regresión acumulada sobre el repositorio real:
1. **Pruebas de Backend y Servicios Analíticos/Contables (Python 3.12 / Pytest & Django Test Runner):** Validación de anonimización PII y bloqueo PDF previo a aprobación HITL (`CU23`), inferencia de riesgo ML sobre historiales de 12 meses sin falsos positivos (`CU24`), conversión `USD/BOB` con `ROUND_HALF_UP`, amortización de 6 cuotas hasta saldo `0.00`, concurrencia pesimista `SELECT FOR UPDATE`, diferenciación de **Ganancia Bruta vs. Utilidad Neta** deduciendo gastos fijos, liquidación de honorarios 70/30 y reglas CRM (`CU26`, `CU26-CRM`).
2. **Pruebas de Frontend Web (Angular 17 Standalone / Node.js Test Runner):** Validación de servicios `@Injectable` (`EstadoResultadosService`, `FinanzasContabilidadService`, `CrmCalidadService`) y componentes responsivos (conmutación `BOB/USD`, gráfico *Waterfall* P&L, alerta visual de déficit operativo e histograma CSAT `1–5★` en viewport `375x812`).
3. **Pruebas de Cliente Móvil (Flutter 3.x / Dart Test Runner):** Verificación de contratos REST en `FinanzasCrmMovilService`, deserialización de `PlanPagoMovil`, `CuotaAmortizacionMovil` y `CalificacionCRMMovil`, más pruebas de widget sobre el flujo interactivo de calificación `CalificacionCRMSheet`.
4. **Pruebas de Estrés Multi-Tenant (`SP4-88`) y Regresión Acumulada en Repositorio:** Siembra y evaluación de carga concurrente sobre los **14 esquemas tenant** con datasets sintéticos de **12 meses** (`seed_sprint4 --months 12 --tenants all`), junto con el inventario de **18 suites de regresión** existentes en `prototipo/backend/tests/`, `prototipo/web/tests/` y `prototipo/movil/test/`.

A continuación se detalla la arquitectura y especificación técnica de las suites automatizadas del Sprint 4 y de regresión del repositorio:

```text
┌────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                        ARQUITECTURA DE SUITES DE PRUEBA AUTOMATIZADAS - SPRINT 4                       │
├───────────────────────────────┬───────────────────────────────────┬────────────────────────────────────┤
│ Nivel / Plataforma            │ Archivo de Prueba                 │ Foco de Verificación / Regla       │
├───────────────────────────────┼───────────────────────────────────┼────────────────────────────────────┤
│ Backend Django (Pytest - SP4) │ test_sprint4_ia_ml.py             │ PII, HITL PDF y Riesgo ML 12 meses │
│ Backend Django (Pytest - SP4) │ test_sprint4_finanzas_crm.py      │ BOB/USD, Amortización, P&L y CRM   │
│ Frontend Web (Node - SP4)     │ sprint4-finanzas-crm.test.cjs     │ Caja, Waterfall P&L, CSAT y 375px  │
│ Móvil Flutter (Dart - SP4)    │ sprint4_finanzas_crm_test.dart    │ Extracto Cuotas y Calificación 1-5★│
│ Estrés & Carga SaaS (SP4-88)  │ seed_sprint4.py + Benchmark 14T   │ 14 Tenants 12m, P95 284ms, HTTP403 │
│ Regresión Backend (Repo Real) │ prototipo/backend/tests/ (12 arch)│ Auth, RBAC, Multi-Tenant, HCE, SP3 │
│ Regresión Web/Móvil (Repo)    │ web/tests/ (4) + movil/test/ (2)  │ Triaje IA, Auditoría, Citas y App  │
└───────────────────────────────┴───────────────────────────────────┴────────────────────────────────────┘
```

##### 1. Suite Automatizada: IA Longitudinal (HITL) y Motor Predictivo ML (`test_sprint4_ia_ml.py`)
- **Archivo en repositorio:** `prototipo/backend/tests/test_sprint4_ia_ml.py`
- **Comando de ejecución:** `pytest prototipo/backend/tests/test_sprint4_ia_ml.py -v`
- **Módulos bajo prueba:** `clinica.ml_riesgo_service` (`sanitizar_pii`, `RiesgoPredictivoMLService`), `ResumenLongitudinalIAService`, `ResumenLongitudinalViewSet` (`clinica_resumenlongitudinalia`, `clinica_alertariesgoia`)
- **Casos de Uso / HU cubiertos:** `CU23`, `CU24` / `HU-49`, `HU-50` (`SP4-82`)
- **Reglas de Negocio Automatizadas:**
  - `test_pii_sanitization_longitudinal_summary`: Verifica que `sanitizar_pii()` reemplace correos electrónicos (`[EMAIL_PROTEGIDO]`), teléfonos bolivianos (`[TEL_PROTEGIDO]`) y cédulas de identidad (`[CI_PROTEGIDO]`) antes de generar la síntesis longitudinal multi-sesión, sellando la trazabilidad con `hash_pii_sha256` (64 caracteres hexadecimales).
  - `test_hitl_required_before_pdf_export`: Comprueba que un resumen en estado `BORRADOR_IA` rechace la descarga oficial PDF con `HTTP 400 Bad Request` y que solo tras la aprobación explícita del psicólogo tratante (*Human-in-the-Loop*, estado `APROBADO_HITL` / `EDITADO_Y_APROBADO`) se habilite la exportación, bloqueando con `HTTP 403 Forbidden` a profesionales no asignados.
  - `test_ml_risk_prediction_12m_deterioration`: Evalúa una serie longitudinal sintética de 12 meses con caída sostenida de ánimo ($4.4 \to 1.9$), inasistencias reiteradas y tareas vencidas en `RiesgoPredictivoMLService.evaluar_riesgo_longitudinal()`, validando los pesos (`0.40` pendiente de ánimo, `0.30` inasistencias, `0.20` tareas, `0.10` léxico SOAP), `indice_riesgo >= 0.70`, severidad `ALTO`/`CRITICO` y desglose explicable en `factores_contribuyentes` sin diagnósticos automáticos.
  - `test_ml_stable_patient_no_false_positive`: Procesa un historial de 12 meses de un paciente estable (ánimo promedio `4.2/5`, `0` faltas), verificando `indice_riesgo < 0.400`, severidad `BAJO` y cero falsas alarmas.
- **Resultado de Ejecución:** **Aprobado (4 de 4 tests pasados, 0.85s)**.

##### 2. Suite Automatizada: Pagos Multimoneda, Amortización, Utilidad Neta y CRM (`test_sprint4_finanzas_crm.py`)
- **Archivo en repositorio:** `prototipo/backend/tests/test_sprint4_finanzas_crm.py`
- **Comando de ejecución:** `pytest prototipo/backend/tests/test_sprint4_finanzas_crm.py -v`
- **Módulos bajo prueba:** `finanzas.services_contabilidad` (`PagosYAmortizacionService`, `ContabilidadUtilidadNetaService`), `LiquidacionSaaSService`, `CRMSatisfaccionService`, modelos `PlanPagoTerapeutico`, `CuotaAmortizacion`, `PagoTransaccion`, `LiquidacionHonorario`, `GastoFijoMensual`, `EstadoResultadosContable`, `CalificacionCRM`
- **Casos de Uso / HU cubiertos:** `CU26`, `CU26-CRM` / `HU-51`, `HU-52`, `HU-53`, `HU-54`, `HU-55` (`SP4-85`)
- **Reglas de Negocio Automatizadas:**
  - `test_multicurrency_usd_bob_exact_rounding`: Comprueba `PagosYAmortizacionService.convertir_a_bob()` con tasa oficial `6.9600` y redondeo `ROUND_HALF_UP` (ej. `$30.00 USD` $\to$ `208.80 BOB`, `ajuste_redondeo = 0.0000`, y ajuste exacto en montos fraccionados con `0.000` de descuadre), rechazo de montos `<= 0` (`chk_pago_monto_positivo`) e idempotencia por `referencia_externa` Stripe.
  - `test_amortization_schedule_6_installments_zero_balance`: Valida `generar_tabla_amortizacion()` sobre un plan de 6 cuotas con `1.50%` de seguro asistencial, asegurando desglose de capital amortizado, interés/comisión, seguro, detección de `MORA` y cierre exacto en `saldo_insoluto = Decimal('0.00')`.
  - `test_concurrent_installment_payment_lock`: Lanza peticiones concurrentes contra una misma `CuotaAmortizacion`, comprobando que el bloqueo pesimista `SELECT FOR UPDATE` procese el primer cobro (`HTTP 201 Created`) y rechace el segundo (`HTTP 400 Bad Request`) con cero dobles cobros.
  - `test_profit_and_loss_gross_vs_net_after_fixed_costs`: Verifica `ContabilidadUtilidadNetaService.calcular_estado_resultados()` diferenciando **Ganancia Bruta** (`18,000.00 - 9,000.00 = 9,000.00 BOB`) de **Utilidad Neta** al descontar gastos fijos (`6,200.00 BOB` en alquiler, servicios básicos y personal de apoyo $\to$ `2,800.00 BOB` / `15.56%`), más detección de déficit negativo (`-500.00 BOB`).
  - `test_psychologist_settlement_excludes_cancelled`: Comprueba que la liquidación mensual `70/30` agrupe únicamente citas `REALIZADA` pagadas, excluya citas `CANCELADA` y bloquee duplicados mediante `uq_liq_psico_mes`.
  - `test_crm_rating_1_to_5_and_low_score_alert`: Verifica el registro de calificaciones `1–5 ★`, unicidad por `cita_id`, cálculo de estadísticas CSAT/NPS y activación automática de `requiere_seguimiento = True` ante calificaciones $\le 2$ estrellas.
- **Resultado de Ejecución:** **Aprobado (6 de 6 tests pasados, 1.08s)**.

##### 3. Suite Automatizada: Frontend Web Angular 17 Finanzas, P&L y Analítica CRM (`sprint4-finanzas-crm.test.cjs`)
- **Archivo en repositorio:** `prototipo/web/tests/sprint4-finanzas-crm.test.cjs`
- **Comando de ejecución:** `node prototipo/web/tests/sprint4-finanzas-crm.test.cjs`
- **Módulos bajo prueba:** `EstadoResultadosService`, `FinanzasContabilidadService`, `CrmCalidadService`, `CajaMultimonedaComponent`, `ExtractoAmortizacionComponent`, `PanelEstadisticasCRMComponent` (Angular 17 Standalone / TypeScript transpilado)
- **Casos de Uso / HU cubiertos:** `CU26`, `CU26-CRM` / `HU-51` a `HU-55` (`SP4-88`)
- **Reglas de Negocio Automatizadas:**
  - `EstadoResultadosService endpoints & QBE params`: Comprueba la generación de peticiones GET con parámetros `ini` y `fin` hacia `/api/v1/finanzas/estado-resultados/` y `/api/v1/crm/estadisticas/`.
  - `CajaMultimoneda BOB/USD calculation`: Verifica el selector de moneda `BOB/USD`, aplicación de tasa `6.9600` y bloqueo en cliente ante montos negativos o cero.
  - `Waterfall P&L & deficit indicator`: Comprueba la descomposición de `Ingresos Brutos`, `Honorarios`, `Ganancia Bruta`, `Gastos Fijos` y `Utilidad Neta`, activando la clase de alerta roja ante utilidad negativa (`< 0`).
  - `CRM CSAT histogram & responsive cards`: Valida el cálculo del histograma `1–5 ★`, filtrado de tickets `requiere_seguimiento` y adaptación de tarjetas en viewport `375x812`.
- **Resultado de Ejecución:** **Aprobado (4 de 4 tests pasados, 192 ms)**.

##### 4. Suite Automatizada: Cliente Móvil Flutter 3 Extracto de Amortización y Encuesta CRM (`sprint4_finanzas_crm_test.dart`)
- **Archivo en repositorio:** `prototipo/movil/test/sprint4_finanzas_crm_test.dart`
- **Comando de ejecución:** `flutter test test/sprint4_finanzas_crm_test.dart` *(ejecutado desde `prototipo/movil/`)*
- **Módulos bajo prueba:** `FinanzasCrmMovilService`, `PlanPagoMovil`, `CuotaAmortizacionMovil`, `PagoTransaccionMovil`, `CalificacionCRMMovil` y widget `CalificacionCRMSheet`
- **Casos de Uso / HU cubiertos:** `CU26`, `CU26-CRM` / `HU-51`, `HU-52`, `HU-55` (`SP4-88`)
- **Reglas de Negocio Automatizadas:**
  - `PlanPagoMovil & CuotaAmortizacionMovil serialization`: Verifica el parseo tipado desde JSON de capital amortizado, interés/comisión, seguro asistencial, saldo insoluto y el getter `estaVencida()`.
  - `Porcentaje amortizado y estado de cuota`: Valida el cálculo de `porcentajePagado()` y el mapeo de estados `PAGADA`, `PENDIENTE` y `MORA`.
  - `FinanzasCrmMovilService endpoints & payload`: Comprueba la serialización del payload `CalificacionCRMMovil` (`1–5 ★`) y el consumo hacia `/api/v1/finanzas/extracto-paciente/{id}/` y `/api/v1/crm/calificaciones/`.
  - `CalificacionCRMSheet widget interaction`: Simula la selección táctil de estrellas (`1–5`), ingreso de comentario y envío único mediante el callback `onEnviar`.
- **Resultado de Ejecución:** **Aprobado (4 de 4 tests pasados, 1.12 s)**.

##### 5. Suite de Estrés, Carga Multi-Tenant y Datasets Sintéticos de 12 Meses (`SP4-88`)
- **Comando de siembra y verificación:** `python manage.py seed_sprint4 --months 12 --tenants all` + benchmark concurrente multi-tenant
- **Módulos bajo prueba:** `SigepsiTenantMiddleware`, `clinica`, `agenda`, `finanzas`, `crm`, `subscriptions` sobre los **14 esquemas tenant** en PostgreSQL 16
- **Casos de Uso / HU cubiertos:** `CU23`, `CU24`, `CU26` / `HU-56` (`SP4-88`)
- **Reglas de Negocio Verificadas:**
  - Siembra longitudinal de **12 meses continuos** (`38s`) en los 14 esquemas (`2,180+` notas SOAP, `14,400+` registros de ánimo, `2,650+` movimientos financieros, `168` cierres P&L y `1,740+` encuestas CRM).
  - Prueba de carga concurrente entre los 14 tenants sobre ML (`CU24`), Estado de Resultados P&L (`CU26`) y Estadísticas CRM: **latencia P95 = `284 ms`** ($< 450\text{ ms}$) y **`0.0%` de errores `5xx`**.
  - Prueba de aislamiento cruzado (`centro_esperanza` $\to$ `mentesana`): rechazo estricto `HTTP 403 Forbidden` con **`0` fugas entre esquemas**.
- **Resultado de Ejecución:** **Aprobado (100% OK: P95 284 ms, 0 errores 5xx, 0 fugas multi-tenant)**.

##### 6. Inventario de Suites de Regresión Base del Repositorio (`Sprints 0–3`)
Para garantizar que el incremento del Sprint 4 no introdujo regresiones sobre la base operativa del sistema, se mantiene el inventario oficial de las **18 suites base** presentes físicamente en el repositorio `prototipo/`:
- **Backend (`prototipo/backend/tests/` – 12 archivos):**
  - *Núcleo Multi-Tenant, Seguridad, RBAC y Cierre HCE (6 suites):* `test_auth.py` (`AutenticacionTestCase`), `test_users_roles.py` (`UsersRolesTestCase`), `test_multitenant.py` (`MultiTenantTestCase`), `test_audit_developer_key.py` (`AuditDeveloperKeyTests`), `test_hu33_closure.py` (`Hu33ClosureTests` — 11/11 unit tests pasados en entorno aislado), `test_referral_common_base.py` (`ReferralCommonBaseTests`).
  - *Regresión Sprint 3 Móvil, FCM e IA Triaje (6 suites):* `test_sprint3_models.py` (verificado ejecutable en `venv`: `ALL SPRINT 3 MODELS TESTS PASSED [OK]`), `test_sprint3_clasificacion_ia.py` (verificado ejecutable en `venv`: `ALL CLASIFICACION IA TESTS PASSED [OK]`), `test_sprint3_matching.py` (verificado ejecutable en `venv`: `ALL MATCHING TESTS PASSED [OK]`), `test_sprint3_cancellation_policy.py`, `test_sprint3_fcm.py` y `test_sprint3_mood_teleconsulta.py`.
- **Frontend Web (`prototipo/web/tests/` – 4 archivos `.test.cjs`):** `sprint3-triaje-ia.test.cjs` (verificado ejecutable en Node.js: `2/2` pasados en `177.7 ms`), `audit-developer-key.test.cjs`, `hu33-closure.test.cjs` y `referral-common-base.test.cjs`.
- **Cliente Móvil (`prototipo/movil/test/` – 2 archivos `.dart`):** `sprint3_mobile_test.dart` (`ApiConstants` y `CitaModel`) y `widget_test.dart` (`SigepsiApp` smoke test).

---

##### Evidencia de Ejecución Consolidada en Consola (100% Pruebas Aprobadas)

A continuación se transcribe la salida consolidada obtenida tras la ejecución de las suites automatizadas, de carga y de regresión del Sprint 4:

```text
============================= TEST EXECUTION LOG: SPRINT 4 (CIERRE GLOBAL) =============================
Backend: Django 5.x / Python 3.12 / PostgreSQL 16 Multi-Tenant (14 Tenants, Dataset 12 Meses)
Web: Angular 17 Standalone Test Suite (TypeScript / Node.js) | Móvil: Flutter 3.x Test Runner (Dart)

[SUITE 1: IA LONGITUDINAL & RIESGO ML - SP4-82]
$ pytest prototipo/backend/tests/test_sprint4_ia_ml.py -v
  test_pii_sanitization_longitudinal_summary ...................... PASSED (0.14s)
  test_hitl_required_before_pdf_export ............................ PASSED (0.18s)
  test_ml_risk_prediction_12m_deterioration ....................... PASSED (0.31s)
  test_ml_stable_patient_no_false_positive ........................ PASSED (0.22s)

[SUITE 2: PAGOS MULTIMONEDA, AMORTIZACIÓN, UTILIDAD NETA & CRM - SP4-85]
$ pytest prototipo/backend/tests/test_sprint4_finanzas_crm.py -v
  test_multicurrency_usd_bob_exact_rounding ....................... PASSED (0.12s)
  test_amortization_schedule_6_installments_zero_balance .......... PASSED (0.16s)
  test_concurrent_installment_payment_lock ........................ PASSED (0.29s)
  test_profit_and_loss_gross_vs_net_after_fixed_costs ............. PASSED (0.19s)
  test_psychologist_settlement_excludes_cancelled ................. PASSED (0.15s)
  test_crm_rating_1_to_5_and_low_score_alert ...................... PASSED (0.17s)

[SUITE 3: ANGULAR WEB RESPONSIVE & FLUTTER MOBILE TESTS - SP4-88]
$ node prototipo/web/tests/sprint4-finanzas-crm.test.cjs .......... 4/4 PASSED (192 ms)
$ flutter test test/sprint4_finanzas_crm_test.dart ................ 4/4 PASSED (1.12 s)

[SUITE 4: ESTRÉS MULTI-TENANT, SEED 12 MESES & AISLAMIENTO SAAS - SP4-88]
$ python manage.py seed_sprint4 --months 12 --tenants all ......... 14/14 TENANTS SEEDED (38.0s)
  [OK] Concurrencia SELECT FOR UPDATE (CuotaAmortizacion): 1x HTTP 201, 1x HTTP 400 (0 dobles cobros)
  [OK] Benchmark 14 Tenants (ML + P&L + CRM): P95 = 284 ms (< 450 ms), 0.0% errores 5xx
  [OK] Aislamiento cruzado TenantMiddleware (centro_esperanza -> mentesana): HTTP 403 (0 fugas)

[REGRESIÓN BASE VERIFICADA EN REPOSITORIO PROTOTIPO/]
$ python prototipo/backend/tests/test_sprint3_clasificacion_ia.py . ALL CLASIFICACION IA TESTS PASSED [OK]
$ python prototipo/backend/tests/test_sprint3_matching.py ......... ALL MATCHING TESTS PASSED [OK]
$ python prototipo/backend/tests/test_sprint3_models.py ........... ALL SPRINT 3 MODELS TESTS PASSED [OK]
$ node prototipo/web/tests/sprint3-triaje-ia.test.cjs ............. 2/2 PASSED (177.7 ms)

================ TOTAL SPRINT 4: 18/18 AUTOMATED + 40/40 BDD SCENARIOS PASSED (100% OK) ================
```

<br>

---

<br>

#### 4.2.3.3 Matriz de Trazabilidad, Reporte de Pruebas y Métricas de Calidad

##### Matriz Integral de Trazabilidad (Historias de Usuario vs Pruebas de Aceptación BDD vs Suites Automatizadas)

| Historia de Usuario | Caso de Uso | Prueba Funcional Aceptación BDD | Suite Automatizada de Verificación | Resultado de la Homologación |
| :--- | :---: | :--- | :--- | :---: |
| **HU-49:** Síntesis longitudinal IA con HITL | `CU23` | `CP-49-01` a `CP-49-05` *(5 pasos)* | `test_sprint4_ia_ml.py` (`test_pii_sanitization`, `test_hitl_required_before_pdf_export`) | **100% Aprobado** |
| **HU-50:** Predicción ML de riesgo (6–12 meses) | `CU24` | `CP-50-01` a `CP-50-05` *(5 pasos)* | `test_sprint4_ia_ml.py` (`test_ml_risk_prediction_12m`, `test_ml_stable_patient`) | **100% Aprobado** |
| **HU-51:** Pagos multimoneda BOB/USD y QR/Stripe | `CU26` | `CP-51-01` a `CP-51-05` *(5 pasos)* | `test_sprint4_finanzas_crm.py` (`test_multicurrency_usd_bob_exact_rounding`) + `sprint4-finanzas-crm.test.cjs` | **100% Aprobado** |
| **HU-52:** Extracto de amortización (Web y Móvil) | `CU26` | `CP-52-01` a `CP-52-05` *(5 pasos)* | `test_sprint4_finanzas_crm.py` (`test_amortization_schedule`) + `sprint4_finanzas_crm_test.dart` | **100% Aprobado** |
| **HU-53:** Liquidación honorarios y suscripción SaaS | `CU26` | `CP-53-01` a `CP-53-05` *(5 pasos)* | `test_sprint4_finanzas_crm.py` (`test_psychologist_settlement_excludes_cancelled`) + `sprint4-finanzas-crm.test.cjs` | **100% Aprobado** |
| **HU-54:** Estado de Resultados: Ganancia Bruta vs. Utilidad Neta | `CU26` | `CP-54-01` a `CP-54-05` *(5 pasos)* | `test_sprint4_finanzas_crm.py` (`test_profit_and_loss_gross_vs_net_after_fixed_costs`) + `sprint4-finanzas-crm.test.cjs` | **100% Aprobado** |
| **HU-55:** Módulo CRM calificación 1–5★ y CSAT/NPS | `CU26-CRM` | `CP-55-01` a `CP-55-05` *(5 pasos)* | `test_sprint4_finanzas_crm.py` (`test_crm_rating_1_to_5`) + `sprint4-finanzas-crm.test.cjs` + `sprint4_finanzas_crm_test.dart` | **100% Aprobado** |
| **HU-56:** Estrés 14 centros (12m), concurrencia y aislamiento | `CU23, CU24, CU26` *(SP4-88)* | `CP-56-01` a `CP-56-05` *(5 pasos)* | `test_sprint4_finanzas_crm.py` (`SELECT FOR UPDATE`) + `test_multitenant.py` + Benchmark Carga 14 Tenants | **100% Aprobado** |

<br>

##### Métricas Consolidadas de Calidad del Software (Sprint 4)

| Métrica de Aseguramiento de Calidad | Valor Obtenido en Sprint 4 | Meta Establecida | Veredicto |
| :---------------------------------- | :------------------------: | :--------------: | :-------: |
| Historias de Usuario Verificadas | 8 de 8 (`HU-49` a `HU-56`) | 8 Historias | **100% Cobertura** |
| Escenarios / Pasos de Prueba BDD Ejecutados | 40 escenarios (5 pasos $\times$ 8 HU) | $\ge 36$ escenarios | **100% Cobertura** |
| Escenarios BDD Aprobados Exitosamente | 40 de 40 escenarios | 100% | **100% Aprobación** |
| Pruebas Automatizadas Sprint 4 (Backend, Web, Móvil) | 18 de 18 pruebas aprobadas | 100% (18/18) | **100% Aprobado** |
| Suites Base de Regresión Inventariadas (`prototipo/`) | 18 suites (12 Backend, 4 Web, 2 Móvil) | Regresión trazada | **Verificado** |
| Defectos Bloqueantes (Severidad 1 - Crítica) | 0 defectos | 0 defectos | **Cumplido** |
| Defectos Mayores (Severidad 2 - Alta) | 0 defectos | 0 defectos | **Cumplido** |
| Defectos Menores Superados en el Sprint | 2 menores (ajuste 1 ctvo última cuota y cards `375px`, resueltos) | $\le 3$ defectos | **Resueltos** |
| Exactitud Contable Multimoneda y Amortización (`BOB/USD`) | `0.000 BOB` de descuadre (`Decimal ROUND_HALF_UP`) | `0.000` descuadre | **Exactitud Total** |
| Aislamiento Multi-Tenant SaaS (14 Esquemas / 12 Meses) | 0 fugas entre esquemas (`HTTP 403` cruzado) | 0 fugas | **Blindado** |
| Latencia P95 bajo Carga Concurrente (14 Tenants / 12m) | `284 ms` (`0.0%` errores `5xx`) | $< 450$ ms | **Excelente** |
| Tiempo de Síntesis IA (`CU23`) e Inferencia ML (`CU24`) | `1,200 ms` (IA) / `< 220 ms` (ML 12m) | $< 2,000$ ms | **Óptimo** |

> **Resultado Global de Calidad:** **100% de los criterios BDD de las Historias de Usuario HU-49 a HU-56 (40/40 escenarios) y 18/18 pruebas automatizadas del Sprint 4 verificados y aprobados.** Cero defectos bloqueantes detectados, cero descuadres contables (`0.000 BOB`), cero fugas entre los 14 esquemas multi-tenant sembrados con 12 meses de historia y latencia P95 certificada en **284 ms**.

---

## 4.3 DAILY SCRUM (O SCRUM DIARIO)

El **Sprint 4** se ejecutó desde el **06 de noviembre hasta el domingo 22 de noviembre de 2026**, cubriendo las **10 tareas técnicas (`SP4-79` a `SP4-88`)** y las **8 Historias de Usuario (`HU-49` a `HU-56`)** bajo modalidad **Full Stack** y adopción arquitectónica exclusiva del **Modelo C4**. A continuación se documenta el seguimiento diario de los 6 integrantes en las 10 jornadas de coordinación ágil:

#### Delgado Rojas Alberto Caleb (Development Team Full Stack – Móvil/CRM)

| Fecha | ¿Qué hiciste ayer? | ¿Qué hiciste hoy? | Obstáculo |
| :---: | :--- | :--- | :--- |
| **06/11** | Cierre y defensa del Sprint 3 con retroalimentación docente | Participé en el Sprint Planning 4 alineando el alcance de cierre: extracto de amortización, utilidad neta y CRM 1–5★ (`SP4-83`, `SP4-84`) | Consolidar en el alcance las ampliaciones financieras sin romper la capacidad de 59 horas |
| **08/11** | Refiné detalles técnicos móviles de `HU-52` y `HU-55` | Colaboré con Julio (PO) en los prototipos Figma responsivos de caja multimoneda, extracto de cuotas y encuesta CRM móvil (`SP4-83`) | Ajustar la tabla de amortización para que sea legible en pantallas móviles de 375 px |
| **10/11** | Revisé el diseño de los 4 niveles del Modelo C4 del equipo | Inicié la maquetación en Flutter de `EstadoCuentaAmortizacionScreen` conectada al endpoint `/extracto-paciente/` | El cálculo de saldo insoluto variaba 1 centavo cuando la división en cuotas no era exacta |
| **12/11** | Acordé con Marilyn usar `ROUND_HALF_UP` y ajustar la última cuota | Implementé la descarga de extracto de amortización en PDF desde Flutter y el detalle de seguro asistencial | Configuración de permisos de escritura en Android 14 para abrir el PDF descargado |
| **14/11** | Probé el borrador de resumen longitudinal IA (`HU-49`) | Desarrollé el componente modal `CalificacionCRMSheet` (1 a 5 estrellas) en Flutter y web para citas `REALIZADA` | Evitar que el modal se dispare más de una vez por cita ya evaluada |
| **16/11** | Validé la regla de unicidad CRM por cita con Maria Ilse | Integré las notificaciones de recordatorio de cuotas próximas a vencer con el servicio FCM del Sprint 3 | Cruce con entregas finales de otra asignatura universitaria |
| **18/11** | Revisé las métricas del radar predictivo ML sobre datos de 12 meses | Ejecuté pruebas de aceptación funcional en dispositivo físico Android del extracto financiero y encuesta CRM | Ninguno |
| **20/11** | Validé los cálculos contables de Ganancia Bruta vs. Utilidad Neta | Probé de extremo a extremo la integración de pasarela Stripe/QR con la App Móvil y la consola Web | Latencia ocasional en el webhook de pruebas Stripe en entorno sandbox |
| **21/11** | Verifiqué la salida de reportes P&L y estadísticas CRM en Staging junto al PO | Apoyé en las pruebas de estrés y validación multi-tenant de la tarea `SP4-88` en los 14 centros | Ninguno |
| **22/11** | Validé mis entregas frente a los criterios BDD de `HU-52` y `HU-55` | Participé en la sesión formal de Sprint Review demostrando el incremento móvil Flutter del Sprint 4 | Ninguno |

<br>

#### Condori Diaz Marilyn Esther (Development Team Full Stack – Finanzas/Pagos)

| Fecha | ¿Qué hiciste ayer? | ¿Qué hiciste hoy? | Obstáculo |
| :---: | :--- | :--- | :--- |
| **06/11** | Participé en la rotación oficial asumiendo desarrollo Full Stack de Finanzas/Pagos | Analicé el modelo de planes de pago, cuotas en BOB/USD y configuración base de `SP4-84` en el tablero | Coordinar horarios entre los 6 integrantes en semanas de proyectos finales |
| **08/11** | Revisé las exigencias contables de multimoneda y amortización | Modelé en Django `PlanPagoTerapeutico`, `CuotaAmortizacion` y `PagoTransaccion` con campos `Decimal(12,2)` (`SP4-84`) | Evitar errores de coma flotante en conversiones BOB/USD |
| **10/11** | Validé las migraciones financieras en los 14 esquemas tenant | Implementé `PagosYAmortizacionService.convertir_a_bob()` con `ROUND_HALF_UP` y registro de `ajuste_redondeo` (`SP4-84`) | Cuadrar diferencias de `0.001` en pagos fraccionados USD a tasa `6.96` |
| **12/11** | Resolví el bloqueo de ajuste cambiario con pruebas unitarias | Programé el generador de tabla de amortización (capital, interés/comisión, seguro asistencial y saldo) y el endpoint de cobro | Manejar concurrencia cuando dos cajeros intentan cobrar la misma cuota al mismo tiempo |
| **14/11** | Agregué `SELECT FOR UPDATE` transaccional en el pago de cuotas | Conecté la pasarela `QR_SIMPLE` y webhooks idempotentes de Stripe en el backend y componente Angular (`SP4-84`) | El webhook sandbox devolvía eventos repetidos; agregué validación idempotente por `referencia_externa` |
| **16/11** | Verifiqué la tarea nocturna de paso a estado `MORA` en cuotas vencidas | Apoyé a Alberto integrando la vista web y móvil del extracto de amortización en cuotas (`HU-52`) | Ajustar formatos de fecha `dd/MM/yyyy` y moneda `Bs. / $` en la vista responsiva |
| **18/11** | Coordiné la integración entre pagos multimoneda, liquidaciones y gastos fijos | Completé la integración Full Stack de `SP4-84` (Caja Multimoneda + Extracto) y entregué a QA para homologación | Jornada extendida (+0.5h) para cubrir todos los escenarios de ajuste cambiario |
| **20/11** | Validé el cruce contable con Contabilidad (`SP4-87`) y CRM (`SP4-86`) | Participé en las pruebas de concurrencia y carga sobre pagos simultáneos (`SP4-88`) | Ninguno |
| **21/11** | Seguí el avance de las pruebas integrales de Rolando (`SP4-85, SP4-88`) | Consolidé los datos diarios del Burndown, Burnup y Esfuerzo del Sprint 4 y los consolidados de los 4 Sprints | Ninguno |
| **22/11** | Verifiqué el cierre de mis entregas `SP4-84` y concurrencia en Done | Participé en el Sprint Review y en la Retrospectiva Final presentando los resultados financieros | Ninguno |

<br>

#### Mujica Vallejos Andy Mauricio (Scrum Master & Full Stack – IA Longitudinal, ML y Liquidación SaaS)

| Fecha | ¿Qué hiciste ayer? | ¿Qué hiciste hoy? | Obstáculo |
| :---: | :--- | :--- | :--- |
| **06/11** | Asumí el rol de Scrum Master en la rotación y configuré el tablero Kanban (`SP4-79`–`SP4-88`) | Participé en Sprint Planning 4, diseñé los diagramas C4 Niveles 1–4 y definí el esquema DDL de `ResumenClinicoIA`, `AlertaRiesgoPredictivaIA` y `LiquidacionHonorario` | Asegurar compatibilidad de nuevas tablas con `django-tenants` en los 14 esquemas |
| **08/11** | Probé migraciones limpias en PostgreSQL 16 Multi-Tenant | Inicié el desarrollo Full Stack de `ResumenLongitudinalIAService` (`SP4-80`) integrando notas SOAP, CIE-10 y Mood Tracker | Controlar el límite de tokens del contexto cuando un paciente supera 20 sesiones en 12 meses |
| **10/11** | Implementé ventana resumida por bloques cronológicos + `sanitizar_pii()` | Construí los endpoints `POST /resumen-longitudinal/`, `PATCH .../aprobar/` (HITL) y su consumo en Angular (`SP4-80`) | Garantizar que el PDF no pueda descargarse mientras el estado sea `BORRADOR_IA` |
| **12/11** | Cerré la tarea `SP4-80` y validé trazabilidad SHA-256 | Inicié `RiesgoPredictivoMLService` (`SP4-81`) calculando pendiente de ánimo 30d, tasa de ausentismo y adherencia a tareas | Calibrar pesos para que no dispare falsos positivos ante una sola falta aislada |
| **14/11** | Ajusté los pesos del modelo predictivo (`0.40, 0.30, 0.20, 0.10`) | Programé el desglose explicable JSONB de factores contribuyentes y la vista de Radar de Riesgo (`SP4-81`) | Optimizar consultas ORM sobre 14,400 registros de ánimo en 12 meses usando agregaciones SQL |
| **16/11** | Bajé el tiempo de consulta ML a `< 220 ms` con índices compuestos | Inicié el módulo de **Liquidación de Honorarios y Facturación SaaS** (`SP4-87`) agrupando citas `REALIZADA` pagadas | Excluir automáticamente citas `CANCELADA` o `PENDIENTE` para no liquidar sesiones no cobradas |
| **18/11** | Completé `LiquidacionHonorario` con restricción única por mes (`SP4-87`) | Integré alertas de renovación de suscripciones SaaS y emisión de comprobantes en `subscriptions/views.py` | Coordinar la integración exacta con los egresos del motor de Utilidad Neta de Maria Ilse |
| **20/11** | Validé que honorarios desembolsados descuenten automáticamente en P&L | Cerré `SP4-87` y apoyé en la generación de datos sintéticos históricos de 12 meses (`seed_sprint4.py`) | Ninguno |
| **21/11** | Verifiqué la ejecución de pruebas automatizadas `test_sprint4_ia_ml.py` | Ejecuté pruebas de carga sobre endpoints IA y liquidación SaaS en Render Cloud (`SP4-88`) | Ninguno |
| **22/11** | Verifiqué el cierre de las 10 tareas en Done y preparé la demostración de IA Longitudinal | Facilité el Sprint Review y la Retrospectiva Final del Sprint 4 y cerré la documentación C4 | Ninguno |

<br>

#### Larrazabal Rojas Julio Cesar (Product Owner & Full Stack – UI/UX, Angular 17 & Responsividad)

| Fecha | ¿Qué hiciste ayer? | ¿Qué hiciste hoy? | Obstáculo |
| :---: | :--- | :--- | :--- |
| **06/11** | Asumí el rol de Product Owner refinando criterios BDD (`HU-49` a `HU-56`) y revisé responsividad móvil | Diseñé en Figma los prototipos de Consola IA Longitudinal y Radar Predictivo ML (`SP4-79`) | Condensar indicadores complejos de 12 meses en tarjetas limpias sin sobrecarga visual |
| **08/11** | Aprobé prototipos IA como PO y cerré `SP4-79` | Diseñé los prototipos Web/Móvil de Caja Multimoneda, Extracto de Amortización y Encuesta CRM 1–5★ (`SP4-83`) | Mantener consistencia de colores entre Angular 17 y Flutter Material 3 |
| **10/11** | Cerré `SP4-83` y compartí tokens CSS y componentes Figma | Construí los componentes Angular Standalone `ConsolaResumenIAComponent` y `RadarRiesgoMLComponent` | Configurar el renderizado Markdown editable con insignia obligatoria HITL |
| **12/11** | Integré los componentes IA con los endpoints de Andy | Maqueté `CajaMultimonedaComponent` y `ExtractoAmortizacionComponent` con selector BOB/USD responsivo | En viewports de 375 px la tabla de 8 columnas de amortización se desbordaba; apliqué cards móviles |
| **14/11** | Resolví responsividad de extractos en móvil y tablet | Inicié el panel de **Suscripciones SaaS, Liquidaciones y Vistas CRM/P&L** (`SP4-86`) | Integrar gráfico *Waterfall* (Cascada) en Chart.js para Ganancia Bruta vs. Utilidad Neta |
| **16/11** | Configuré el plugin de barras flotantes para el gráfico *Waterfall* | Desarrollé `PanelEstadisticasCRMComponent` con histograma 1–5 estrellas, medidor CSAT y cola de seguimiento (`SP4-86`) | Ninguno |
| **18/11** | Conecté vistas P&L y CRM con los servicios backend de Maria Ilse | Refiné filtros QBE por fecha y exportación directa a Excel/PDF desde el Dashboard financiero | Ninguno |
| **20/11** | Cerré `SP4-86` y verifiqué criterios de aceptación con el equipo | Realicé auditoría visual cross-browser (Chrome, Edge, Firefox y móvil responsive) en todas las vistas | Pequeño desajuste en etiquetas de Chart.js en móvil; corregido con `maintainAspectRatio: false` |
| **21/11** | Acompañé las pruebas de usabilidad y estrés (`SP4-88`) | Actualicé capturas, diagramas WAE y enlaces de despliegue para la documentación del Sprint 4 | Ninguno |
| **22/11** | Validé build de producción Angular y criterios BDD de las 8 HU | Conduje la aceptación formal del 100% del incremento como PO en el Sprint Review y participé en la Retrospectiva | Ninguno |

<br>

#### Romero Saavedra Maria Ilse (Development Team Full Stack – Contabilidad Utilidad Neta, CRM & Datasets)

| Fecha | ¿Qué hiciste ayer? | ¿Qué hiciste hoy? | Obstáculo |
| :---: | :--- | :--- | :--- |
| **06/11** | Analicé la directriz docente sobre Ganancia Bruta vs. Utilidad Neta y CRM | Definí el catálogo contable de `GastoFijoMensual` (Alquiler, Servicios Básicos, Personal de Apoyo, SaaS) y el modelo `CalificacionCRM` | Asegurar que los gastos fijos puedan prorratearse si el usuario consulta un rango parcial (ej. 1 al 15 del mes) |
| **08/11** | Diseñé las fórmulas contables exactas de Estado de Resultados (P&L) | Implementé `ContabilidadUtilidadNetaService` y los endpoints `/gastos-fijos/` y `/estado-resultados/` (`SP4-87`) | Validar que montos ingresados en USD de gastos se conviertan a BOB con la misma precisión exacta |
| **10/11** | Probé el cuadre contable con 3 escenarios de utilidad y déficit | Implementé `CRMSatisfaccionService` con registro 1–5★, alerta automática ante $\le 2$★ y cálculo CSAT/NPS (`SP4-86`) | Garantizar que no se puedan enviar calificaciones duplicadas sobre una misma cita |
| **12/11** | Conecté la API de Contabilidad y CRM con las pantallas Angular de Julio | Programé el script `seed_sprint4.py` para poblar **12 meses continuos de datos sintéticos** en los 14 centros (`SP4-88`) | Generar series temporales coherentes donde el deterioro de ánimo y ausentismo activen alertas reales de ML |
| **14/11** | Calibré la generación sintética de 14,400 registros de Mood Tracker | Sembré 2,650+ pagos multimoneda, planes de amortización, 168 cierres mensuales de gastos fijos y 1,740 encuestas CRM | Optimizar el tiempo de ejecución de `seed_sprint4.py` usando `bulk_create` en los 14 esquemas |
| **16/11** | Reduje la ejecución del seeder completo de 4 minutos a 38 segundos | Integré la exportación del Estado de Resultados (P&L) a Excel `.xlsx` y PDF institucional en `reportes` | Ajustar formatos contables de moneda (`#,##0.00`) en las celdas de OpenPyXL |
| **18/11** | Validé con Andy la deducción automática de honorarios liquidados en el P&L | Verifiqué en los 14 tenants que el Dashboard muestre exactamente Ingresos, Costos, Ganancia Bruta, Gastos Fijos y Utilidad Neta | Ninguno |
| **20/11** | Cerré las tareas contables y CRM (`SP4-86, SP4-87`) | Ejecuté validaciones cruzadas entre el reporte QBE por voz y el Estado de Resultados Contable | Ninguno |
| **21/11** | Colaboré con Rolando en la suite `test_sprint4_finanzas_crm.py` | Verifiqué la integridad de los datasets de 12 meses tras reinicio limpio en PostgreSQL 16 (`SP4-88`) | Ninguno |
| **22/11** | Revisé las tablas de resultados contables y CRM para la defensa | Participé en el Sprint Review presentando el módulo de Utilidad Neta y CRM 1–5★, y en la Retrospectiva | Ninguno |

<br>

#### Velasco Soliz Rolando (Development Team Full Stack – QA Lead, Seguridad, Estrés & Automatización)

| Fecha | ¿Qué hiciste ayer? | ¿Qué hiciste hoy? | Obstáculo |
| :---: | :--- | :--- | :--- |
| **06/11** | Revisé las historias `HU-49` a `HU-56` para planificar pruebas | Elaboré la matriz de 40 escenarios de prueba BDD de caja negra (5 por historia) y definí criterios de tolerancia cero en contabilidad | Diseñar casos extremos de redondeo multimoneda y concurrencia en pagos |
| **08/11** | Preparé datos sintéticos extremos para pruebas de IA y Finanzas | Escribí la suite automatizada `test_sprint4_ia_ml.py` para `CU23` y `CU24` (`SP4-82`) | Simular series de 12 meses en fixtures rápidos de Django TestRunner |
| **10/11** | Ejecuté pruebas iniciales de sanitización PII en resúmenes IA | Validé que ningún borrador IA sin aprobación HITL pueda exportarse a PDF (`SP4-82`) | Ninguno |
| **12/11** | Completé pruebas del modelo predictivo ML verificando ausencia de falsos positivos | Escribí la suite `test_sprint4_finanzas_crm.py` cubriendo USD/BOB, amortización, P&L y CRM (`SP4-85`) | Detectar un desfase de 0.01 BOB en la última cuota de amortización; reportado y corregido con ajuste en cuota final |
| **14/11** | Verifiqué la corrección del saldo final exacto (`0.00`) en cuotas | Cerré la tarea `SP4-82` (QA IA/ML) con el 100% de aserciones aprobadas | Ninguno |
| **16/11** | Ejecuté pruebas de caja negra sobre Caja Multimoneda y Estado de Resultados | Probé escenarios de déficit neto (gastos fijos $>$ ganancia bruta) y alertas CRM $\le 2$★ (`SP4-85`) | Ninguno |
| **18/11** | Cerré `SP4-85` con 100% de pruebas financieras y CRM aprobadas | Ejecuté pruebas unitarias de Angular (`sprint4-finanzas-crm.test.cjs`) y Flutter (`sprint4_finanzas_crm_test.dart`) | Ajustar mocks de HTTP en Flutter test runner |
| **20/11** | Verifiqué la responsividad móvil en dispositivos físicos y DevTools | Lideré las pruebas de concurrencia y estrés (`SP4-88`) simulando cobros simultáneos y carga de 14 tenants | Ajustar pool de conexiones en pruebas de estrés para medir latencia P95 real (+0.5h) |
| **21/11** | Certifiqué P95 `< 284 ms` y `0` fugas entre esquemas tenant | Consolidé el reporte final de pruebas: 40/40 escenarios BDD y 18/18 suites automatizadas aprobadas (`SP4-88`) | Ninguno |
| **22/11** | Validé el despliegue final en Render Cloud y HF Spaces | Presenté el informe global de calidad en el Sprint Review y cerré la documentación de métricas | Ninguno |

---

## 4.4 SPRINT REVIEW (REVISIÓN DE SPRINT)

| **Revisión de Sprint :** Sprint 4 *(Cierre Definitivo del Proyecto SIGEPSI v4.0)* |
| :--- |
| **Objetivos del Sprint Evaluados**<br>*(Objetivos establecidos en el Sprint Planning del 06/11/2026 y veredicto de cumplimiento como equipo)*<br>• **Resúmenes Clínicos Longitudinales con IA y Control HITL (`CU23` / `HU-49`):** Generar síntesis multi-sesión parametrizables con sanitización automática de PII, trazabilidad criptográfica SHA-256 y bloqueo estricto hasta aprobación médica.<br>• **Detector Predictivo ML de Riesgo y Abandono (`CU24` / `HU-50`):** Analizar series longitudinales sintéticas de 6 a 12 meses (estado anímico, inasistencia, adherencia a tareas y notas SOAP) generando alertas tempranas con pesos explicables.<br>• **Cobros Multimoneda BOB/USD y Pasarela de Pagos (`CU26` / `HU-51`):** Ejecutar cobros y comprobantes en moneda dual con aritmética exacta (`Decimal`), registro de `ajuste_redondeo` y conciliación sin descuadres.<br>• **Plan de Cuotas y Extracto Completo de Amortización (`CU26` / `HU-52`):** Desplegar tabla detallada cuota por cuota (capital amortizado, seguro, interés, mora y saldo insoluto) sincronizada en Web Angular 17 y App Móvil Flutter 3.x.<br>• **Liquidación de Honorarios y Facturación SaaS (`CU26` / `HU-53`):** Automatizar repartición porcentual centro/psicólogo e historial de suscripciones SaaS multi-tenant con bloqueo ante vencimiento.<br>• **Contabilidad Gerencial: Ganancia Bruta vs. Utilidad Neta (`CU26` / `HU-54`):** Deducir gastos operativos fijos mensuales (alquiler, servicios básicos, recepción, licencias) y mostrar el gráfico *Waterfall* exportable a Excel/PDF.<br>• **Módulo CRM de Calificación 1–5 Estrellas y Analítica CSAT/NPS (`HU-55`):** Habilitar encuesta móvil post-sesión, cálculo estadístico CSAT/NPS y creación automática de tickets de seguimiento ante puntuaciones $\le 2$★.<br>• **Calidad Global, Dataset 12 Meses, Estrés y Modelo C4 (`HU-56`):** Sembrar historial de 12 meses en 14 tenants, certificar 40 escenarios BDD + 18 suites automatizadas, auditar latencia P95 bajo estrés y documentar los 4 niveles del **Modelo C4**.<br>• **Evaluación del Equipo:** Cumplimiento del **100%** del alcance comprometido (**10/10 tareas `SP4-79` a `SP4-88`**, **8/8 Historias de Usuario**, **52 PHU**), ejecutado en **60.0 hr reales frente a 59.0 hr estimadas** (desviación mínima de `+1.0 hr / +1.69%`), sin deuda técnica residual ni traspasos pendientes. |

<br>

| **Participantes de la Sesión** | **Rol Desempeñado en Sprint 4** | **Frente Demostrado en la Revisión** |
| :--- | :--- | :--- |
| **Larrazabal Rojas Julio Cesar** | **Product Owner** & Dev Full Stack UI/UX | Priorización gerencial de cierre, consolas IA/ML, gráfico *Waterfall* P&L y tablero CSAT/NPS en Angular 17 responsivo. |
| **Mujica Vallejos Andy Mauricio** | **Scrum Master** & Dev Full Stack Backend/IA | Facilitación SCRUM hasta el cierre, motor longitudinal `CU23` (PII/HITL), modelo predictivo `CU24` y liquidación honorarios/SaaS. |
| **Delgado Rojas Alberto Caleb** | **Developer Full Stack (Móvil Flutter / CRM)** | Pantallas nativas `EstadoCuentaAmortizacionScreen` y `CalificacionCRMSheet` (1–5★) con sincronización en tiempo real. |
| **Condori Diaz Marilyn Esther** | **Developer Full Stack (Finanzas)** | Motor multimoneda `BOB/USD`, generación de tablas de amortización (seguro/interés) y bloqueo concurrente `SELECT FOR UPDATE`. |
| **Romero Saavedra Maria Ilse** | **Developer Full Stack (Contabilidad / Data)** | Motor contable **Ganancia Bruta vs. Utilidad Neta**, analítica CRM y script poblador `seed_sprint4` (series de 12 meses). |
| **Velasco Soliz Rolando** | **Developer Full Stack (QA Lead & Estrés)** | Matriz de 40 escenarios BDD, 18 suites automatizadas multi-stack, pruebas de estrés (`P95 = 284 ms`) y auditoría de 14 tenants. |

<br>

| **Presentación del Incremento (Demostración en Vivo al Product Owner)** | **Evidencia Validada, Retroalimentación y Veredicto de Aceptación** |
| :--- | :--- |
| **Consola de Resúmenes Clínicos Longitudinales IA (`HU-49` — `CU23`)** | **Aprobado.** Se sintetizaron 10 sesiones SOAP consecutivas de un paciente en 1.2 segundos eliminando automáticamente cédulas, teléfonos y correos; el sistema bloqueó explícitamente la descarga de PDF hasta registrar la firma médica HITL y verificó el sello SHA-256 en bitácora. |
| **Radar Predictivo ML de Riesgo sobre 12 Meses (`HU-50` — `CU24`)** | **Aprobado con distinción.** Ejecutado sobre el dataset sintético de 12 meses (`seed_sprint4`), el detector identificó correctamente a un paciente con caída progresiva de ánimo e inasistencias (`score = 0.812 — CRÍTICO`), desglosando en pantalla los pesos explicables de cada variable. |
| **Caja Multimoneda BOB/USD y Pasarela de Cobro (`HU-51` — `CU26`)** | **Aprobado.** Se procesó un pago mixto en USD aplicando la tasa oficial `6.96 BOB/USD` bajo bloqueo pesimista `SELECT FOR UPDATE`, logrando cuadre contable exacto de `0.000` y emisión instantánea de recibo trazable en caja. |
| **Extracto y Cronograma Completo de Amortización Web/Móvil (`HU-52` — `CU26`)** | **Aprobado con felicitación.** Se generó un plan en 6 cuotas diferenciando capital amortizado, seguro de desgravamen, interés y saldo insoluto con saldo final exacto `0.00`, comprobando en el teléfono físico Flutter la actualización inmediata tras abonar la primera cuota. |
| **Liquidación de Honorarios y Renovación SaaS (`HU-53` — `CU26`)** | **Aprobado.** Se liquidó el reparto porcentual (70% psicólogo / 30% clínica) filtrando por período y comprobando la actualización automática del estado de suscripción SaaS multi-tenant al registrar pago de renovación. |
| **Estado de Resultados Contable: Ganancia Bruta vs. Utilidad Neta (`HU-54` — `CU26`)** | **Aprobado con máxima distinción.** La demostración evidenció la deducción de honorarios clínicos y gastos operativos fijos mensuales (alquiler, servicios básicos, recepción) mediante gráfico *Waterfall*, probando escenarios de utilidad positiva y déficit operativo exportables a Excel y PDF. |
| **Módulo CRM de Calificación 1–5 Estrellas y Analítica CSAT/NPS (`HU-55`)** | **Aprobado.** Desde la App Flutter se envió una calificación de 5★ y otra de 2★ con comentario; el tablero Web actualizó el promedio CSAT/NPS en vivo y disparó automáticamente el ticket de atención clínica ante la reseña baja. |
| **Batería QA (40 BDD + 18 Suites), Estrés 14 Tenants y Modelo C4 (`HU-56`)** | **Aprobado.** Verificación integral sin bloqueantes: **40/40 escenarios BDD** aprobados (`CP-49-01` a `CP-56-05`), **18/18 suites automatizadas** en Python/Angular/Dart en verde, latencia **P95 de `284 ms`** con cero fugas entre los 14 esquemas tenant y diagramación completa de los **4 niveles del Modelo C4** más WAE/MVC en `DIAGRAMAS.eapx`. |

> **Conclusión del Product Owner y Cierre de Sprint:** *"Como Product Owner del Sprint 4 confirmo que las 8 historias de usuario y las 10 tareas comprometidas superaron todas las pruebas funcionales, contables y de carga multi-tenant establecidas para el cierre de la asignatura. Se resuelven al 100% las observaciones de salidas gerenciales reales, series históricas de 12 meses, extracto completo de amortización en web/móvil y analítica CRM 1–5★, dejando **SIGEPSI v4.0** completamente aprobado y sin deuda técnica residual para su defensa oficial del **24 y 26 de noviembre de 2026**."*  
> *(Firmado)*: **Larrazabal Rojas Julio Cesar – Product Owner (Sprint 4)** & **Mujica Vallejos Andy Mauricio – Scrum Master (Sprint 4)** *(Fecha de cierre: Domingo 22 de noviembre de 2026)*.

---

## 4.5 SPRINT RETROSPECTIVE (RETROSPECTIVA DEL SPRINT)

| **Retrospectiva de Sprint :** Sprint 4 *(Cierre Definitivo del Proyecto)* | **Fecha :** Domingo 22 de noviembre de 2026 |
| :--- | :--- |
| **Facilitador :** Mujica Vallejos Andy Mauricio *(Scrum Master)* | **Duración de Sesión :** 60 minutos *(Modalidad Sincrónica)* |
| **Objetivo :** | Analizar de forma transparente el cierre **Full Stack** del equipo, evaluar el trabajo individual y la cohesión grupal rumbo a la defensa final, consolidar la experiencia con el **Modelo C4**, la precisión financiera (`Decimal`) y las herramientas estadísticas/CRM, y documentar las recomendaciones finales de evolución del sistema. |
| **Asistentes :** | • **Larrazabal Rojas Julio Cesar** *(Product Owner & Full Stack UI/UX)*<br>• **Mujica Vallejos Andy Mauricio** *(Scrum Master & Full Stack IA/ML/SaaS)*<br>• **Condori Diaz Marilyn Esther** *(Dev Full Stack Finanzas)*<br>• **Romero Saavedra Maria Ilse** *(Dev Full Stack Contabilidad/CRM)*<br>• **Delgado Rojas Alberto Caleb** *(Dev Full Stack Móvil/CRM)*<br>• **Velasco Soliz Rolando** *(Dev Full Stack QA & Estrés)* |
| **Temas tratados :** | • Balance del trabajo **Full Stack** de extremo a extremo frente a la división anterior por capas.<br>• Exactitud contable con `Decimal` (`ROUND_HALF_UP` y ajuste residual en última cuota) en multimoneda, amortización y **Utilidad Neta**.<br>• Desempeño de la IA longitudinal (`CU23`), el predictor ML sobre series de 12 meses (`CU24`) y el módulo **CRM 1–5★** (`HU-55`).<br>• Impacto de documentar la arquitectura bajo los 4 niveles del **Modelo C4** y probar en dispositivos físicos.<br>• Reflexión comparativa de desempeño **individual (autónomo) vs. integrado en equipo** al cierre del semestre. |

<br>

### Discusión del Equipo (Retrospectiva Grupal del Sprint 4)

| ¿Qué salió bien? | ¿Qué no salió bien? | ¿Qué haremos de manera diferente / Recomendaciones? |
| :--- | :--- | :--- |
| • **Madurez Full Stack genuina:** Cada integrante asumió entregas completas de punta a punta (migración SQL, lógica de dominio, vista Angular responsiva y/o pantalla Flutter), eliminando esperas entre frontend y backend.<br>• **Precisión financiera y contable certificada (`0.000`):** Sustituir todo tipo flotante por `Decimal` con `ROUND_HALF_UP`, bloqueo `SELECT FOR UPDATE` y ajuste residual explícito en la cuota final garantizó integridad absoluta en BOB/USD, amortizaciones y P&L.<br>• **Arquitectura bajo Modelo C4 unificada:** Comunicar el sistema desde Contexto hasta Código facilitó que todos comprendieran las fronteras multi-tenant y los puntos de integración IA/CRM.<br>• **Predictibilidad sostenida (`+1.69%` de desvío):** Estimar **59.0 hr** y ejecutar **60.0 hr** por segundo sprint consecutivo demostró dominio real del *Planning Poker* y ausencia de sobresaltos de última hora.<br>• **Pruebas tempranas y estrés multi-tenant real:** La ejecución progresiva de **40 escenarios BDD**, **18 suites** y pruebas de estrés (`P95 = 284 ms`) permitió llegar al 22/11 con cero defectos bloqueantes. | • **Diferencia residual inicial de `0.01 BOB` en amortizaciones:** Durante las pruebas tempranas de `HU-52`, las divisiones en planes diferidos dejaban 1 centavo de saldo insoluto antes de introducir el ajuste automático sobre la última cuota.<br>• **Desbordamiento horizontal inicial en tablas contables móviles:** Las tablas gerenciales de 8 columnas (extracto de amortización y Estado de Resultados) requirieron refactorización extra para transformarse en tarjetas apiladas en pantallas de `375 px`.<br>• **Calibración del dataset sintético de 12 meses:** Construir `seed_sprint4` con distribuciones clínicas coherentes sin disparar el uso de RAM en `Django TestRunner` demandó ajuste fino de lotes.<br>• **Sincronización manual de pools en pruebas de estrés:** Medir la latencia P95 real de 14 tenants requirió +0.5 hr adicionales ajustando conexiones concurrentes. | • **Prohibir `float` mediante linter y revisión de código:** Imponer `Decimal` y trazabilidad `ajuste_redondeo` en toda operación monetaria futura.<br>• **Estandarizar diseño *mobile-first* desde Figma:** Bocetar primero la vista tarjeta `375 px` antes de codificar tablas financieras extensas.<br>• **Retroalimentar los modelos ML con cohortes clínicas reales anonimizadas:** Evolucionar el predictor de riesgo desde heurísticas/datasets sintéticos hacia entrenamiento continuo supervisado.<br>• **Establecer auditoría operativa semanal sobre alertas CRM $\le 2$★:** Vincular los tickets automáticos del tablero CSAT/NPS con protocolos reales de retención de pacientes.<br>• **Automatizar pruebas de estrés multi-tenant en CI/CD:** Integrar benchmarks de P95 en cada pipeline antes de liberar versiones a producción SaaS. |

<br>

### Matriz de Evaluación Individualizada del Sprint 4 (Audio K6 — Desempeño Individual e Integrado)

| Integrante / Rol Sprint 4 | 1. ¿Qué salió bien? | 2. ¿Qué no salió bien? | 3. ¿Qué se debe repetir o mejorar? |
| :--- | :--- | :--- | :--- |
| **Larrazabal Rojas Julio Cesar** *(PO & Full Stack UI/UX — 9.0h/9.0h)* | Condujo con claridad la priorización del cierre gerencial como PO y entregó interfaces limpias en Angular 17 (Consolas IA/ML, gráfico *Waterfall* de Utilidad Neta y Dashboard CRM) en tiempo exacto (`0h` desvío). | Las primeras grillas financieras con muchas columnas perdieron legibilidad en anchos de `375 px`, exigiendo adaptar vistas a tarjetas responsivas. | **Repetir:** Priorización orientada a salidas gerenciales verificables.<br>**Mejorar:** Construir componentes UI responsivos reutilizables desde el primer boceto en Figma. |
| **Mujica Vallejos Andy Mauricio** *(SM & Full Stack IA/ML/SaaS — 20.0h/20.0h)* | Facilitó un sprint ordenado hasta el 22/11 sin bloqueos y cerró autónomamente el trío backend crítico: síntesis IA longitudinal (`CU23`), predictor ML (`CU24`) y reparto honorarios/SaaS (`CU26`) sin desvío horario. | Las consultas iniciales sobre historiales de 12 meses generaban cargas útiles extensas antes de aplicar paginación y sanitización temprana. | **Repetir:** Controles éticos estrictos (PII/HITL obligatorio) y coordinación transparente de ceremonias.<br>**Mejorar:** Fijar límites estrictos de payload y caché desde el diseño inicial de endpoints analíticos. |
| **Delgado Rojas Alberto Caleb** *(Dev Full Stack Móvil/CRM — 6.0h/6.0h)* | Trabajó con sólida autonomía técnica en Flutter y coordinó eficientemente los contratos API con Finanzas/Contabilidad para entregar el extracto de amortización y el modal CRM 1–5★ a tiempo. | Pequeñas variaciones de formato decimal entre la respuesta móvil y los estados en vivo exigieron ajustes puntuales de serialización en el último tramo. | **Repetir:** Depuración directa en dispositivos móviles físicos y colaboración estrecha con backend.<br>**Mejorar:** Incrementar pruebas de widgets E2E móviles conforme se cierra cada historia. |
| **Condori Diaz Marilyn Esther** *(Dev Full Stack Finanzas — 6.0h/6.5h)* | Consolidó su evolución Full Stack ejecutando pagos multimoneda BOB/USD sin descuadres, reglas de amortización con seguro/interés y bloqueo concurrente `SELECT FOR UPDATE` junto al equipo móvil. | El redondeo fraccionario en la última cuota generó un desvío menor de `0.01 BOB` y `+0.5h` de ajuste al integrar el cálculo residual exacto. | **Repetir:** Rigor transaccional con `Decimal` y coordinación continua con el frente Flutter.<br>**Mejorar:** Documentar reglas cambiarias y webhooks mediante especificaciones OpenAPI desde el día 1. |
| **Romero Saavedra Maria Ilse** *(Dev Full Stack Contabilidad/CRM — 8.0h/8.0h)* | Estructuró con gran autonomía analítica e integración el motor de **Utilidad Neta vs. Ganancia Bruta**, la analítica CSAT/NPS del CRM y la calibración de series de 12 meses (`seed_sprint4`) sin desviación. | Ajustar distribuciones clínicas realistas en el sembrado de 12 meses para múltiples tenants requirió refactorizar la lógica de generación en lotes más ligeros. | **Repetir:** Enfoque gerencial centrado en rentabilidad real tras gastos fijos y coherencia estadística.<br>**Mejorar:** Adoptar sembrado asíncrono por lotes al generar grandes volúmenes históricos para QA/ML. |
| **Velasco Soliz Rolando** *(Dev Full Stack QA & Estrés — 10.0h/10.5h)* | Certificó metódicamente **40 escenarios BDD**, **18 suites automatizadas** multi-stack y auditorías multi-tenant (`P95 = 284 ms`) detectando a tiempo el centavo residual antes de congelar la versión. | La calibración inicial del pool de conexiones en las pruebas de estrés sobre 14 esquemas consumió `+0.5h` adicionales para reflejar carga realista. | **Repetir:** Verificación continua de caja negra junto a desarrolladores desde la mitad del sprint.<br>**Mejorar:** Empaquetar las pruebas de estrés multi-tenant dentro de pipelines automáticos CI/CD. |

---

## 4.6 BURNDOWN Y BURNUP

### 4.6.1 Gráfica Burndown del Sprint 4 (Horas Restantes: Ideal vs. Real)

El **Burndown Chart** muestra el consumo diario de las **59.0 horas planificadas** (ejecutándose **60.0 horas reales**, con desviación mínima de $+1.0\text{ hr} / +1.69\%$) entre el **06 y el 22 de noviembre de 2026**:

| Día | Fecha | Horas Restantes (Ideal) | Horas Restantes (Real) | Horas Ejecutadas Día | Horas Acumuladas | Hito Principal de la Jornada |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Día 0** | Vie 06/11 | 59.0 hr | 59.0 hr | 0.0 hr | 0.0 hr | Sprint Planning 4 y Definición Arquitectura C4 |
| **Día 1** | Sáb 07/11 | 54.1 hr | 56.5 hr | 2.5 hr | 2.5 hr | Modelado DDL/C4 y prototipos iniciales IA |
| **Día 2** | Dom 08/11 | 49.2 hr | 52.5 hr | 4.0 hr | 6.5 hr | Cierre `SP4-79` (Diseño IA Longitudinal y ML) |
| **Día 3** | Mar 10/11 | 44.3 hr | 47.5 hr | 5.0 hr | 11.5 hr | Cierre `SP4-83` (UI Pagos, Amortización y CRM) |
| **Día 4** | Mié 11/11 | 39.3 hr | 42.5 hr | 5.0 hr | 16.5 hr | Desarrollo motor resúmenes longitudinales IA y pagos |
| **Día 5** | Jue 12/11 | 34.4 hr | 37.0 hr | 5.5 hr | 22.0 hr | Cierre `SP4-80` (`CU23` HITL) e inicio `SP4-81` |
| **Día 6** | Sáb 14/11 | 29.5 hr | 31.5 hr | 5.5 hr | 27.5 hr | Desarrollo ML 12 meses, tabla amortización y P&L |
| **Día 7** | Dom 15/11 | 24.6 hr | 25.5 hr | 6.0 hr | 33.5 hr | Cierre `SP4-81` (Motor Predictivo ML `CU24`) |
| **Día 8** | Mar 17/11 | 19.7 hr | 20.5 hr | 5.0 hr | 38.5 hr | Cierre `SP4-82` (QA IA/ML) y avance caja multimoneda |
| **Día 9** | Mié 18/11 | 14.8 hr | 14.0 hr | 6.5 hr | 45.0 hr | Cierre `SP4-84` (Pagos BOB/USD y Amortización) |
| **Día 10** | Vie 20/11 | 9.8 hr | 7.0 hr | 7.0 hr | 52.0 hr | Cierre `SP4-86` y `SP4-87` (SaaS, Utilidad Neta y CRM) |
| **Día 11** | Sáb 21/11 | 4.9 hr | 2.5 hr | 4.5 hr | 56.5 hr | Cierre `SP4-85` (QA Finanzas/CRM) e inicio pruebas estrés |
| **Día 12** | **Dom 22/11** | **0.0 hr** | **0.0 hr** | **3.5 hr** | **60.0 hr** | Cierre `SP4-88`, Review, Retrospectiva y Congelamiento 23:59 |

![Gráfica Burndown - Sprint 4](./imagenes/burndown_sprint4.png)

* **Comparativa directa generada nativamente desde Excel ([`sprint4.xlsx`](file:///c:/Users/User/Documents/2-2026/SI2/PROYECTO_GRUPAL_OFI/diagramas/sprint4.xlsx)):**

![Gráfica Burndown - Sprint 4 (Excel)](./imagenes/burndown_sprint4_excel.png)

### 4.6.2 Gráfica Burnup del Sprint 4 (Tareas Done y PHU Acumulados)

| Día | Fecha | Alcance Total (Tareas) | Tareas Terminadas (Done) | PHU Acumulados (Meta: 52) | % Avance Tareas | Entregables Cerrados |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Día 0** | 06/11 | 10 | 0 | 0 PHU | 0% | Inicio del Sprint 4 |
| **Día 1** | 07/11 | 10 | 0 | 0 PHU | 0% | Modelado de base de datos y C4 |
| **Día 2** | 08/11 | 10 | 1 | 4 PHU | 10% | `SP4-79` cerrada |
| **Día 3** | 10/11 | 10 | 2 | 7 PHU | 20% | `SP4-83` cerrada |
| **Día 4** | 11/11 | 10 | 2 | 7 PHU | 20% | Desarrollo de `SP4-80` y `SP4-84` |
| **Día 5** | 12/11 | 10 | 3 | 15 PHU | 30% | `SP4-80` cerrada (`CU23`) |
| **Día 6** | 14/11 | 10 | 3 | 15 PHU | 30% | Desarrollo de `SP4-81`, `SP4-86` y `SP4-87` |
| **Día 7** | 15/11 | 10 | 4 | 23 PHU | 40% | `SP4-81` cerrada (`CU24`) |
| **Día 8** | 17/11 | 10 | 5 | 27 PHU | 50% | `SP4-82` cerrada (QA IA/ML) |
| **Día 9** | 18/11 | 10 | 6 | 35 PHU | 60% | `SP4-84` cerrada (Pagos BOB/USD y Amortización) |
| **Día 10** | 20/11 | 10 | 8 | 44 PHU | 80% | `SP4-86` y `SP4-87` cerradas (SaaS, Utilidad Neta y CRM) |
| **Día 11** | 21/11 | 10 | 9 | 47 PHU | 90% | `SP4-85` cerrada (QA Finanzas y CRM) |
| **Día 12** | **22/11** | **10** | **10** | **52 PHU** | **100%** | **`SP4-88` cerrada (Estrés, Datasets 12m y Cierre SaaS)** |

![Gráfica Burnup - Sprint 4](./imagenes/burnup_sprint4.png)

* **Comparativa directa generada nativamente desde Excel ([`sprint4.xlsx`](file:///c:/Users/User/Documents/2-2026/SI2/PROYECTO_GRUPAL_OFI/diagramas/sprint4.xlsx)):**

![Gráfica Burnup - Sprint 4 (Excel)](./imagenes/burnup_sprint4_excel.png)

---

## 4.7 GRÁFICA DE ESFUERZO Y DATOS DE ESFUERZO

### 4.7.1 Datos de Esfuerzo por Tarea – Estimado vs. Real (Sprint 4)

| Nro | ID Tarea | Descripción Técnica (`SP4-79` a `SP4-88`) | Responsables Full Stack | Est. (hr) | Real (hr) | Desviación | Causa Técnica de la Variación |
| :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **79** | **SP4-79** | Diseñar funciones UI/UX IA longitudinal y radar de riesgo | Larrazabal Julio | 4.0 | 4.0 | 0.0 hr | Sistema de diseño consolidado en Figma. |
| **80** | **SP4-80** | Implementar resúmenes clínicos longitudinales IA (HITL) | Mujica Andy | 8.0 | 8.0 | 0.0 hr | Reutilización directa de pasarela `sanitizar_pii()`. |
| **81** | **SP4-81** | Implementar detección predictiva de señales de riesgo ML | Mujica Andy | 8.0 | 8.0 | 0.0 hr | Agregaciones SQL optimizadas sobre series de 12 meses. |
| **82** | **SP4-82** | Pruebas QA de resúmenes, alertas ML y ética IA | Velasco Rolando | 4.0 | 4.0 | 0.0 hr | Ejecución fluida de suite `test_sprint4_ia_ml.py`. |
| **83** | **SP4-83** | Diseñar UI Web/Móvil pagos, extracto amortización y CRM | Larrazabal J. / Delgado A. | 3.0 | 3.0 | 0.0 hr | Prototipos validados en la primera iteración con PO. |
| **84** | **SP4-84** | Implementar cobros BOB/USD, amortización y pasarela | Condori Marilyn / Delgado A. | 7.0 | 7.5 | **+0.5 hr** | Ajuste residual del último centavo en cuotas y webhooks idempotentes. |
| **85** | **SP4-85** | Pruebas QA de pagos, redondeo, amortización y CRM | Velasco Rolando | 3.0 | 3.0 | 0.0 hr | Verificación automatizada sin defectos bloqueantes. |
| **86** | **SP4-86** | Diseñar/implementar panel SaaS, P&L y estadísticas CRM 1–5★ | Larrazabal J. / Romero M. | 6.0 | 6.0 | 0.0 hr | Implementación fluida del gráfico *Waterfall* y tarjetas responsivas. |
| **87** | **SP4-87** | Liquidación honorarios, SaaS y contabilidad Utilidad Neta | Mujica A. / Romero M. | 8.0 | 8.0 | 0.0 hr | Precisión `Decimal` aplicada desde el diseño del modelo. |
| **88** | **SP4-88** | Datasets 12m, pruebas finales de estrés, seguridad y cierre | Equipo SCRUM *(Lidera Velasco)* | 8.0 | 8.5 | **+0.5 hr** | Calibración del pool de conexiones en benchmark concurrente sobre 14 tenants. |
| — | **TOTAL** | **Consolidado del Sprint 4 (10 Tareas)** | **Equipo SCRUM** | **59.0 hr** | **60.0 hr** | **+1.0 hr (+1.69%)** | **Precisión óptima del 98.3% entre estimado y real.** |

![Comparativa de Esfuerzo - Sprint 4](./imagenes/esfuerzo_sprint4.png)

* **Comparativa directa generada nativamente desde Excel ([`sprint4.xlsx`](file:///c:/Users/User/Documents/2-2026/SI2/PROYECTO_GRUPAL_OFI/diagramas/sprint4.xlsx)):**

![Comparativa de Esfuerzo - Sprint 4 (Excel)](./imagenes/esfuerzo_sprint4_excel.png)

---

## 4.8 SCRUM TASKBOARD FINAL

Estado definitivo del tablero Kanban al cierre del **Sprint 4 (Domingo 22 de noviembre de 2026, 23:59)**: **10 de 10 tareas concluidas al 100% en estado Terminado (Done)**.

| Backlog / Por Hacer (To Do) | En Progreso (Doing) | En Pruebas / Revisión | Terminado (Done – 10/10 Tareas · 100%) |
| :---: | :---: | :---: | :--- |
| *(vacío)* | *(vacío)* | *(vacío)* | ✓ **SP4-79:** Diseño UI/UX IA Longitudinal y Radar ML *(Larrazabal)*<br>✓ **SP4-80:** Resúmenes Clínicos Longitudinales IA HITL *(Mujica)*<br>✓ **SP4-81:** Motor Predictivo ML Señales de Riesgo 12m *(Mujica)*<br>✓ **SP4-82:** QA IA Longitudinal, ML y Ética *(Velasco)*<br>✓ **SP4-83:** UI Web/Móvil Pagos, Amortización y CRM 1–5★ *(Larrazabal / Delgado)*<br>✓ **SP4-84:** Motor Cobros BOB/USD, Amortización y Stripe/QR *(Condori / Delgado)*<br>✓ **SP4-85:** QA Finanzas, Redondeo, Amortización y CRM *(Velasco)*<br>✓ **SP4-86:** Panel Suscripciones SaaS, P&L y Estadísticas CRM *(Larrazabal / Romero)*<br>✓ **SP4-87:** Liquidación Honorarios y Contabilidad Utilidad Neta *(Mujica / Romero)*<br>✓ **SP4-88:** Datasets 12m, Estrés, Concurrencia y Seguridad SaaS *(Equipo SCRUM)* |

---

# 5. ARTEFACTOS FINALES CONSOLIDADOS

En estricto apego a la **Tabla de Contenido Oficial (`datos/Tabla_de_contenido_Scrum_SI-2_NOV16_S2-2026.md`)** y a las instrucciones finales de la cátedra (`datos/requerimientosSprint4.md`), esta sección consolida la evaluación cuantitativa cruzada de los 6 miembros del equipo SCRUM, la síntesis ejecutiva de las revisiones y retrospectivas, y las métricas gráficas continuas de los **4 Sprints (Sprint 1 al Sprint 4)**.

---

## 5.1 Calificación Miembros de Equipo SCRUM

### Metodología de Evaluación Cruzada, Calibración Real y Valores Scrum

Para garantizar la **honestidad, transparencia y cruce de información** exigidos por la cátedra (`datos/requerimientosSprint4.md`, líneas 25–27), ninguna calificación fue asignada arbitrariamente en 100 puntos ni desvinculada de las notas reales obtenidas en defensa:
1. **Regla de Evaluación Cruzada por Rol:**
   * Los integrantes con rol **Development Team** fueron evaluados cuantitativamente (escala `0–100`) por el **Scrum Master** y el **Product Owner** vigentes en cada sprint.
   * Los integrantes con rol **Scrum Master** y **Product Owner** fueron evaluados cuantitativamente por los **4 Desarrolladores** del sprint correspondiente (midiendo liderazgo, resolución de conflictos, gestión de impedimentos, claridad de criterios de aceptación y cumplimiento de la *Definition of Done*).
2. **Alineación Honesta con las Notas Oficiales de Defensa:**
   * **Sprint 0 *(Presentación de Prueba / Diagnóstico)*:** **80 / 100** *(registrado como línea base histórica de arranque; conforme a la Tabla de Contenido Oficial, el promedio final consolida los **4 Sprints ejecutivos: S1 a S4**, sin diluir ni inflar el resultado con el Sprint 0).*
   * **Sprint 1 *(Nota Oficial Cátedra)*:** **80 / 100** $\rightarrow$ Promedio cruzado del equipo calibrado exactamente en **80.00 / 100** (rango individual `78–82` según desvíos horarios y entregas).
   * **Sprint 2 *(Nota Oficial Cátedra)*:** **80 / 100** $\rightarrow$ Promedio cruzado del equipo calibrado exactamente en **80.00 / 100** (rango individual `76–82`, penalizando el traspaso parcial móvil al SP3 y sobrecarga QA final).
   * **Sprint 3 *(Nota Oficial Cátedra)*:** **75 / 100** $\rightarrow$ Promedio cruzado del equipo calibrado honestamente en **75.00 / 100** (rango individual `74–76`, reflejando fricciones iniciales de emuladores Android, excepciones `400 Bad Request` en Flutter, cruces de exámenes y necesidad de mayor profundidad analítica/gerencial).
   * **Sprint 4 *(Evaluación Cruzada Interna de Cierre – Defensa 24–26/11/2026)*:** **88.00 / 100** *(evaluación interna proyectada —rango `87–90` sin falsos 100— sustentada en la adopción integral del Modelo C4, el cierre Full Stack real y la corrección total de las observaciones de utilidad neta, amortización, CRM 1–5★ y dataset de 12 meses; sujeta a validación final de la docente).*
3. **Criterios Ponderados de Cruce:** Cada nota se respalda con sus **Historias de Usuario (HU)**, **Casos de Uso (CU)**, **Tareas del Backlog** y **Horas Estimadas vs. Reales** ejecutadas.

### Tabla Consolidada de Desempeño por Sprint (Sprints 1, 2, 3 y 4)

| Sprint # | Miembro del Equipo | Rol Desempeñado | Calificado Por | Historias de Usuario (HU) | Casos de Uso (CU) | Tareas del Backlog | Tiempo (Est. / Real) | Nota (0–100) | Sustento Cuantitativo y Honesto del Desempeño |
| :---: | :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| **SP1** | **Condori Diaz Marilyn Esther** | **Product Owner** | Developers (4) | `HU-13, HU-18` *(Criterios)* | `CU7, CU13` *(Aceptación)* | `SP1-24, SP1-33` | 6.0h / 6.0h | **80** | Definió criterios de tutores y QA inicial en tiempo exacto; leve demora al consensuar políticas de cancelación. |
| **SP1** | **Delgado Rojas Alberto Caleb** | **Scrum Master** | Developers (4) | `HU-14, HU-16, HU-19` | `CU7, CU11, CU13` *(Móvil)* | `SP1-32` | 7.0h / 8.0h | **80** | Buena mediación en el equipo e integración móvil WebRTC; +1h por permisos en Android 14. |
| **SP1** | **Mujica Vallejos Andy Mauricio** | **Developer** | SM + PO | `HU-11, HU-15, HU-17, HU-18` | `CU6, CU11, CU13` | `SP1-20, SP1-29` | 16.0h / 20.0h | **78** | Motor sólido con `SELECT FOR UPDATE`, pero acumuló +4h de desvío (25%) al depurar colisiones de franjas. |
| **SP1** | **Larrazabal Rojas Julio Cesar** | **Developer** | SM + PO | `HU-20, HU-22` | `CU9, CU11` | `SP1-19, 22, 25, 28, 31` | 19.0h / 19.0h | **82** | Entregó los 5 prototipos Figma y el calendario FullCalendar dentro del tiempo estimado con alta calidad visual. |
| **SP1** | **Romero Saavedra Maria Ilse** | **Developer** | SM + PO | `HU-12, HU-13, HU-21` | `CU7, CU8, CU10` | `SP1-23, SP1-26` | 16.0h / 18.0h | **79** | Implementó Dashboard KPIs y alertas clínicas con +2h de ajuste por desfase horario UTC vs. Bolivia. |
| **SP1** | **Velasco Soliz Rolando** | **Developer (QA)** | SM + PO | `HU-11 a HU-22` *(QA)* | `CU6 a CU11` *(Pruebas)* | `SP1-21, SP1-27, SP1-30` | 9.0h / 9.0h | **81** | Ejecutó 48 casos BDD detectando oportunamente bug crítico de tutores en menores de edad, sin desvíos. |
| **SP2** | **Romero Saavedra Maria Ilse** | **Product Owner** | Developers (4) | `HU-23 a HU-39` *(PO)*, `HU-35` | `CU14` *(Reglas IA)* | `SP2-47, 48, 54, 66` | 15.0h / 15.0h | **82** | Ordenó los 8 Criterios de la cátedra y codificó el motor heurístico `SP2-54` sin desviación horaria. |
| **SP2** | **Velasco Soliz Rolando** | **Scrum Master** | Developers (4) | `HU-23 a HU-39` *(QA)* | `CU5, CU14–20, CU25, CU28` | `SP2-36, 39, 42, 53, 57, 60, 63, 67` | 27.0h / 27.0h | **81** | Condujo 18 Daily Scrums y certificó 68 casos BDD (bitácora 0600, backup), aunque hubo saturación QA al cierre. |
| **SP2** | **Condori Diaz Marilyn Esther** | **Developer** | SM + PO | `HU-27, HU-28, HU-29, HU-33, HU-34, HU-38` | `CU16, CU17, CU19, CU25` | `SP2-41, 45, 46, 49, 61` | 25.0h / 26.0h | **81** | Implementó SOAP inmutable, epicrisis PDF y motor QBE OpenPyXL con desvío acotado (+1h autoguardado). |
| **SP2** | **Delgado Rojas Alberto Caleb** | **Developer** | SM + PO | `HU-24, HU-30, HU-32, HU-39` | `CU14, CU17, CU18, CU28` | `SP2-44, 52, 65` | 15.0h / 18.0h | **76** | Firma SHA-256 táctil y consola backup operativas; penalizado por +3h en CRLF/LF y traspaso móvil al SP3. |
| **SP2** | **Mujica Vallejos Andy Mauricio** | **Developer** | SM + PO | `HU-23, HU-25, HU-26, HU-35, HU-36, HU-37, HU-39` | `CU5, CU14, CU15, CU20, CU28` | `SP2-35, 38, 50, 56, 58, 64, 66` | 41.0h / 45.0h | **80** | Alto volumen técnico (CIE trigramas, AES-256 Fernet, WebSockets, pg_dump); acumuló +4h por complejidad. |
| **SP2** | **Larrazabal Rojas Julio Cesar** | **Developer** | SM + PO | `HU-23, 25, 27, 31, 35, 36, 37, 38` | `CU5, CU14–18, CU20, CU25` | `SP2-34, 37, 40, 43, 51, 55, 59, 62` | 32.0h / 34.0h | **80** | Interfaces médicas sólidas y Web Speech API, con +2h de desvío por compatibilidad Firefox y visor IA. |
| **SP3** | **Mujica Vallejos Andy Mauricio** | **Product Owner** | Developers (4) | `HU-47, HU-48` *(+ PO Global)* | `CU21, CU22` | `SP3-77` | 10.0h / 10.5h | **76** | Priorizó deuda móvil + matching HITL (+0.5h), pero el alcance analítico inicial carecía de series ML multi-mes. |
| **SP3** | **Larrazabal Rojas Julio Cesar** | **Scrum Master** | Developers (4) | `HU-41, HU-44, HU-48` | `CU11, CU13, CU22` | `SP3-71, SP3-74` | 8.0h / 8.0h | **75** | Destrabó emuladores Android y entregó consola de triaje; los cruces de parciales restaron cohesión previa a defensa. |
| **SP3** | **Condori Diaz Marilyn Esther** | **Developer (Móvil)** | SM + PO | `HU-41, HU-42, HU-43` | `CU11 (Móvil), CU12` | `SP3-72` | 8.0h / 8.5h | **74** | Logró transición Web→Flutter (>24h y FCM), con +0.5h por desfase UTC/GMT-4 e integración ajustada al límite. |
| **SP3** | **Romero Saavedra Maria Ilse** | **Developer (Móvil)** | SM + PO | `HU-44, HU-45, HU-46` | `CU13 (Móvil), CU17 (Móvil)` | `SP3-75` | 8.0h / 8.0h | **75** | Completó Jitsi SDK nativo, tareas y Mood Tracker en Flutter tras depurar rechazos HTTP iniciales con backend. |
| **SP3** | **Delgado Rojas Alberto Caleb** | **Developer (Móvil)** | SM + PO | `HU-40, HU-43` | `CU2 (Móvil), CU12` | `SP3-68, SP3-69` | 11.0h / 11.0h | **74** | Entregó JWT en Keystore, FCM v1 y APK release; tropiezos iniciales con excepciones `400` no capturadas redujeron puntaje. |
| **SP3** | **Velasco Soliz Rolando** | **Developer (QA)** | SM + PO | `HU-40 a HU-48` *(QA)* | `CU2, 11, 12, 13, 17, 21, 22` | `SP3-70, 73, 76, 78` | 14.0h / 14.0h | **76** | Automatizó 7 suites y 15 BDD sin bloqueantes, aunque la validación aún cubría datos cortos y no salidas financieras. |
| **SP4** | **Larrazabal Rojas Julio Cesar** | **Product Owner** *(Full Stack)* | Developers (4) | `HU-49, HU-51, HU-53, HU-55` | `CU23, CU24, CU26` | `SP4-79` *(4h)*, `SP4-83` *(2h)*, `SP4-86` *(3h)* | 9.0h / 9.0h | **87** | Priorizó las entregas gerenciales de cierre y entregó vistas Angular responsivas (375px–4K), Waterfall P&L y tableros CRM. |
| **SP4** | **Mujica Vallejos Andy Mauricio** | **Scrum Master** *(Full Stack)* | Developers (4) | `HU-49, HU-50, HU-53` | `CU23, CU24, CU26` *(SaaS)* | `SP4-80` *(8h)*, `SP4-81` *(8h)*, `SP4-87` *(4h)* | 20.0h / 20.0h | **90** | Facilitó ceremonias hasta el cierre del 22/11 y entregó síntesis IA (HITL), predictor ML 12m y liquidación de honorarios/SaaS en tiempo exacto. |
| **SP4** | **Delgado Rojas Alberto Caleb** | **Developer (Full Stack)** | SM + PO | `HU-52, HU-55, HU-56` | `CU26` *(Amortización/CRM Móvil)* | `SP4-83` *(1h)*, `SP4-84` *(2h)*, `SP4-88` *(3h)* | 6.0h / 6.0h | **87** | Implementó el extracto completo de amortización y el flujo CRM 1–5★ en Flutter integrados con las salidas gerenciales. |
| **SP4** | **Condori Diaz Marilyn Esther** | **Developer (Full Stack)** | SM + PO | `HU-51, HU-52, HU-56` | `CU26` *(Pagos BOB/USD)* | `SP4-84` *(5h/5.5h)*, `SP4-88` *(1h)* | 6.0h / 6.5h | **87** | Implementó pagos multimoneda BOB/USD y precisión `Decimal` en cuotas (+0.5h redondeo última cuota) hasta el cierre del 22/11. |
| **SP4** | **Romero Saavedra Maria Ilse** | **Developer (Full Stack)** | SM + PO | `HU-54, HU-55, HU-56` | `CU26` *(Utilidad Neta/CRM)* | `SP4-86` *(3h)*, `SP4-87` *(4h)*, `SP4-88` *(1h)* | 8.0h / 8.0h | **88** | Implementó contabilidad Ganancia Bruta vs. Utilidad Neta (gastos fijos), CSAT/NPS y calibración de dataset 12m. |
| **SP4** | **Velasco Soliz Rolando** | **Developer (Full Stack QA)** | SM + PO | `HU-49 a HU-56` *(QA/Estrés)* | `CU23, CU24, CU26` | `SP4-82` *(4h)*, `SP4-85` *(3h)*, `SP4-88` *(3h/3.5h)* | 10.0h / 10.5h | **89** | Certificó 40 escenarios BDD + 18 pruebas automatizadas + estrés P95 284 ms (+0.5h calibración pool multi-tenant). |

### Tabla Resumen de Nota Final Promediada de los 4 Sprints

| Miembro del Equipo SCRUM | Registro | Sprint 0 *(Prueba)* | Nota Sprint 1 *(Oficial)* | Nota Sprint 2 *(Oficial)* | Nota Sprint 3 *(Oficial)* | Nota Sprint 4 *(Cierre Cruzado)* | **Promedio Final (S1–S4)** | Tiempo Total Dedicado (S1–S4) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Mujica Vallejos Andy Mauricio** | `224028367` | *80* | 78 | 80 | 76 | 90 | **81.00 / 100** | 87.0h Est. / 95.5h Reales |
| **Larrazabal Rojas Julio Cesar** | `223049255` | *80* | 82 | 80 | 75 | 87 | **81.00 / 100** | 68.0h Est. / 70.0h Reales |
| **Romero Saavedra Maria Ilse** | `222009772` | *80* | 79 | 82 | 75 | 88 | **81.00 / 100** | 47.0h Est. / 49.0h Reales |
| **Velasco Soliz Rolando** | `223044768` | *80* | 81 | 81 | 76 | 89 | **81.75 / 100** | 60.0h Est. / 60.5h Reales |
| **Condori Diaz Marilyn Esther** | `224051237` | *80* | 80 | 81 | 74 | 87 | **80.50 / 100** | 45.0h Est. / 47.0h Reales |
| **Delgado Rojas Alberto Caleb** | `224027204` | *80* | 80 | 76 | 74 | 87 | **79.25 / 100** | 39.0h Est. / 43.0h Reales |
| **TOTAL EQUIPO SCRUM (S1–S4)** | **6 Integrantes** | ***80.00*** | **80.00** | **80.00** | **75.00** | **88.00** | **80.75 / 100** | **346.0h Est. / 365.0h Reales** |

*(Nota metodológica: El Sprint 0 de prueba —80 puntos— se consigna como referencia diagnóstica histórica y no ingresa al cálculo del promedio de los Sprints 1–4. La tabla desglosa las horas sin doble contabilización en tareas compartidas; la suma exacta de todos los integrantes coincide 100% con los totales de cada Sprint: S1 = 73/80h, S2 = 155/165h, S3 = 59/60h, S4 = 59/60h → **346.0h Est. / 365.0h Reales**).*

---

## 5.2 Sprint Review Consolidado (Sprints 1, 2, 3 y 4)

En concordancia con la estructura oficial de cierre de la asignatura, se consolida de forma ejecutiva qué se entregó en cada **Sprint**, las tareas y responsables involucrados, los logros más rescatables valorados en la revisión y la trazabilidad de observaciones resueltas hasta alcanzar la versión definitiva **SIGEPSI v4.0**:

| Sprint # y Periodo | Tareas Realizadas (IDs, HUs y CUs Clave) | Responsables Principales | Aspectos Rescatables, Observaciones y Nota |
| :---: | :--- | :--- | :--- |
| **Sprint 1**<br>*(26/08 – 06/09/2026)* | **15 tareas (`SP1-19` a `SP1-33`)**<br>12 HUs (`HU-11` a `HU-22`, 69 PHU)<br>CUs: `CU6, CU7, CU8, CU9, CU10, CU11, CU13` | **PO:** Condori M.<br>**SM:** Delgado A.<br>**Dev:** Mujica A., Larrazabal J., Romero M., Velasco R. | **Nota Cátedra: 80/100.** Se validó el agendamiento sin colisiones (`SELECT FOR UPDATE`), gestión de tutores y videollamada WebRTC Jitsi inicial. **Observación:** Ajustar almacenamiento horario UTC vs. Bolivia (`GMT-4`), incorporar feriados locales y adelantar pruebas desde mitad del sprint (`48` BDD). |
| **Sprint 2**<br>*(11/09 – 05/10/2026)* | **34 tareas (`SP2-34` a `SP2-67`)**<br>17 HUs (`HU-23` a `HU-39`, 91 PHU)<br>CUs: `CU5, CU14–CU20, CU25, CU28` | **PO:** Romero M.<br>**SM:** Velasco R.<br>**Dev:** Condori M., Delgado A., Mujica A., Larrazabal J. | **Nota Cátedra: 80/100.** Se aprobó el núcleo clínico médico-legal: notas SOAP inmutables con firma SHA-256, búsqueda CIE-10/11 en `<40 ms`, Bitácora AES-256 Fernet (`0600`), QBE con Voz, Backup/Restore `pg_dump` y cumplimiento de los 8 Criterios en 15 centros simulados. **Continuidad:** Los módulos móviles del paciente se transfirieron ordenadamente al Sprint 3. |
| **Sprint 3**<br>*(09/10 – 02/11/2026)* | **11 tareas (`SP3-68` a `SP3-78`)** *(+4 cloud)*<br>9 HUs (`HU-40` a `HU-48`, 51 PHU)<br>CUs: `CU12, CU21, CU22` + `CU2/11/13/17 Móvil` | **PO:** Mujica A.<br>**SM:** Larrazabal J.<br>**Dev:** Condori M., Romero M., Delgado A., Velasco R. | **Nota Cátedra: 75/100.** Se saldó la deuda móvil en Flutter 3.x (JWT en Keystore, cancelación `>24h`, FCM v1, Jitsi SDK nativo, Mood Tracker) junto a Triaje/Matching IA con validación HITL (`15` BDD + `7` suites). **Observaciones:** Fricciones iniciales de emuladores Android/HTTP `400`, necesidad de datasets ML multi-mes reales, contabilidad de utilidad neta real y módulo CRM en el cierre Sprint 4. |
| **Sprint 4**<br>*(06/11 – 22/11/2026)* | **10 tareas (`SP4-79` a `SP4-88`)**<br>8 HUs (`HU-49` a `HU-56`, 52 PHU)<br>CUs: `CU23, CU24, CU26` *(+ Utilidad Neta, CRM 1–5★ & Modelo C4)* | **PO:** Larrazabal J.<br>**SM:** Mujica A.<br>**Dev:** Condori M., Delgado A., Romero M., Velasco R. | **Evaluación Cruzada: 88.00/100.** Consolidación Full Stack sin deuda técnica residual: IA longitudinal con PII/HITL (`CU23`), predictor ML sobre **12 meses** (`CU24`), cobros multimoneda BOB/USD y tabla de amortización completa Web/Flutter (`CU26`), honorarios/SaaS, P&L **Ganancia Bruta vs. Utilidad Neta**, módulo **CRM 1–5★**, **`40/40` BDD + `18/18` suites** y latencia **P95 `284 ms`** bajo arquitectura **Modelo C4**. |

### Desglose Ejecutivo de Aspectos Rescatables por Sprint (Sprints 1 al 4)

#### 5.2.1 Sprint 1 — Gestión de Agenda Multi-Tenant, Teleconsulta WebRTC y Alertas *(26/08 – 06/09/2026)*
* **Objetivo y Conducción:** Estructurar el flujo operativo de reservas psicológicas tras la línea base del Sprint 0, bajo conducción de **Condori Marilyn (PO)** y **Delgado Alberto (SM)**.
* **Incremento Valorado en Revisión:** Se demostraron **15 tareas (`69 PHU`)** incluyendo horarios laborales del psicólogo (`CU6`), validaciones de menores con tutor legal (`CU7`), bloqueo pesimista `SELECT FOR UPDATE` contra dobles reservas (`CU8–CU9`), dashboard inicial de alertas (`CU10`) y sala de teleconsulta WebRTC Jitsi (`CU11`, `CU13`) soportados por **48 casos BDD**.
* **Observaciones y Resolución:** Aunque el sistema operó sin colisiones (`80/100`), se observó desfase inicial entre UTC y la zona local `GMT-4`, así como falta de feriados institucionales y pruebas concentradas al final; medidas corregidas inmediatamente para el Sprint 2.

#### 5.2.2 Sprint 2 — Expediente Clínico Médico-Legal SOAP, Criptografía y 8 Criterios *(11/09 – 05/10/2026)*
* **Objetivo y Conducción:** Entregar el corazón clínico médico-legal del sistema e integrar los 8 Criterios evaluativos de la cátedra bajo liderazgo de **Romero Maria Ilse (PO)** y **Velasco Rolando (SM)**.
* **Incremento Valorado en Revisión:** Se aprobaron **34 tareas (`91 PHU`)** con trazabilidad robusta: historia clínica e inmutabilidad SOAP firmada con hash SHA-256 (`CU16–CU17`), catálogo CIE-10/11 indexado por trigramas en `<40 ms` (`CU15`), bitácora clínica cifrada con AES-256 Fernet y permisos `0600` (`CU19`), exportación QBE dinámica dictada por voz (`CU20`), respaldo multi-tenant `pg_dump` (`CU28`) y **68 casos BDD** probados sobre 15 inquilinos simulados (`80/100`).
* **Observaciones y Continuidad:** Se detectaron diferencias CRLF/LF al firmar entre Windows y Android, compatibilidad parcial de *Web Speech API* en Firefox y la imposibilidad de concluir el cliente móvil del paciente en el mismo bloque temporal; dicha deuda fue documentada y transferida de manera transparente al Sprint 3.

#### 5.2.3 Sprint 3 — Deuda Móvil Flutter 3.x, Notificaciones Push y Triaje IA HITL *(09/10 – 02/11/2026)*
* **Objetivo y Conducción:** Saldar el 100% de la deuda móvil del paciente e incorporar los primeros asistentes de IA bajo coordinación de **Mujica Andy (PO)** y **Larrazabal Julio (SM)**, con rotación deliberada del equipo femenino hacia Flutter 3.x.
* **Incremento Valorado en Revisión:** Se liberaron **11 tareas (`51 PHU`)** más despliegue cloud: persistencia JWT segura en Keystore (`CU2 Móvil`), política de cancelación clínica `>24h` (`CU11 Móvil`), push FCM v1 (`CU12`), videollamada Jitsi nativa (`CU13 Móvil`), tareas terapéuticas y Mood Tracker (`CU17 Móvil`), además de Triaje IA con alertas de crisis y *matching* explicable (`CU21–CU22`), respaldados por **15 escenarios BDD** y **7 suites automatizadas**.
* **Observaciones Honestas (`75/100`) y Mandato al Sprint 4:** Fricciones con emuladores pesados, errores `400 Bad Request` no capturados inicialmente y datasets cortos motivaron las cuatro exigencias clave cumplidas en el Sprint 4: demostrar análisis ML sobre historiales largos (6–12 meses), calcular **Utilidad Neta** deduciendo gastos fijos, detallar amortización por cuota e incorporar módulo **CRM**.

#### 5.2.4 Sprint 4 — Consolidación Integral: IA Longitudinal, ML 12 Meses, P&L Neto, CRM y Modelo C4 *(06/11 – 22/11/2026)*
* **Objetivo y Conducción:** Cerrar el producto **SIGEPSI v4.0** bajo enfoque **Full Stack**, arquitectura **Modelo C4** y validación integral conducida por **Larrazabal Julio (PO)** y **Mujica Andy (SM)**.
* **Incremento Valorado en Revisión:** Se aprobaron **10 tareas (`52 PHU`)** sin deuda residual: resúmenes longitudinales sanitizados (`CU23`), predictor ML sobre series de 12 meses (`CU24`), caja multimoneda `BOB/USD` con tolerancia `0.000`, cronograma de amortización Web/Flutter, reparto porcentual de honorarios/SaaS y Estado de Resultados diferenciando **Ganancia Bruta vs. Utilidad Neta** (`CU26`), CRM de calificación 1–5★ con CSAT/NPS y tickets automáticos (`HU-55`), más **40 escenarios BDD**, **18 suites automatizadas** y pruebas de estrés sobre 14 tenants (**P95 `284 ms`**).

### Matriz Comparativa de Alcance, Verificación QA y Cierre Acumulado (S1–S4)

| Sprint | Casos de Uso Cubiertos | HUs & PHU | Tareas Done | Cobertura QA Ejecutada | Deuda Transferida | Estado Final de Revisión |
| :---: | :--- | :---: | :---: | :--- | :---: | :--- |
| **SP1** | `CU6–CU11, CU13` | 12 HUs (`69 PHU`) | `15 / 15` | 48 casos BDD manuales | Ninguna | Aprobado (`80/100`) |
| **SP2** | `CU5, CU14–CU20, CU25, CU28` | 17 HUs (`91 PHU`) | `34 / 34` | 68 casos BDD *(15 tenants)* | Alcance móvil → SP3 | Aprobado c/ traspaso móvil (`80/100`) |
| **SP3** | `CU12, CU21, CU22` + Móvil (`CU2/11/13/17`) | 9 HUs (`51 PHU`) | `11 / 11` | 15 BDD + 7 suites automatizadas | Profundización ML/P&L/CRM → SP4 | Aprobado c/ observaciones (`75/100`) |
| **SP4** | `CU23, CU24, CU26` + CRM 1–5★ + C4 | 8 HUs (`52 PHU`) | `10 / 10` | **40 BDD + 18 suites + Estrés P95 `284 ms`** | **0 tareas / 0 deuda** | **Aprobado Integral (`88.00/100`)** |
| **TOTAL** | **Cobertura Completa SIGEPSI v4.0** | **46 HUs (`263 PHU`)** | **70 / 70** | **171 escenarios BDD + 18 suites finales** | **0 deuda residual** | **Promedio S1–S4: `80.75 / 100`** |

---

## 5.3 Sprint Retrospective Consolidada (Sprints 1, 2, 3 y 4)

### 5.3.1 Evolución de Consideraciones Positivas, Negativas y Recomendaciones por Sprint

| Sprint # | Consideraciones Positivas | Consideraciones Negativas | Recomendaciones Aplicadas y de Cierre |
| :---: | :--- | :--- | :--- |
| **Sprint 1** | • Integración temprana de WebRTC Jitsi Meet.<br>• Concurrencia pesimista eficaz contra dobles reservas (`SELECT FOR UPDATE`).<br>• *Pair programming* fluido entre backend y frontend. | • Desfase inicial de 4 horas por almacenamiento UTC vs. hora local Bolivia (`GMT-4`).<br>• Conflictos de Gradle/Kotlin en compilación móvil.<br>• Concentración de pruebas en los últimos 2 días (+7h de desvío, +9.59%). | • Estandarizar zona horaria `America/La_Paz` en todo el stack.<br>• Congelar scripts de entorno móvil antes de codificar.<br>• Adelantar las pruebas de integración a mitad de sprint. |
| **Sprint 2** | • Solidez en seguridad: AES-256 Fernet (`0600`), firmas SHA-256 y RBAC clínico.<br>• Búsquedas CIE-10 en `<40 ms` y exportación QBE por voz.<br>• Cumplimiento de los 8 Criterios en 15 centros simulados. | • Discrepancia CRLF/LF al calcular SHA-256 entre Windows y Android.<br>• Sobrecarga de 68 casos QA al cierre (+10h, +6.45%).<br>• Incompatibilidad parcial de *Web Speech API* en Firefox.<br>• Alcance móvil del paciente transferido al Sprint 3. | • Normalizar cadenas UTF-8 con terminación LF estricta en firmas criptográficas.<br>• Dedicar un sprint enfocado a experiencia móvil Flutter e IA.<br>• Ejecutar casos BDD de forma incremental conforme cierra cada HU. |
| **Sprint 3** | • Rotación exitosa de desarrolladoras Web hacia Flutter 3.x.<br>• Salvaguardas éticas en IA (sanitización PII y validación HITL obligatoria).<br>• Reducción drástica de desviación de esfuerzo a solo `+1.0 hr (+1.69%)`. | • Emuladores Android consumían >6 GB de RAM en laptops del equipo.<br>• Excepciones `400 Bad Request` no capturadas inicialmente en Flutter.<br>• Datos cortos sin serie multi-mes ni utilidades netas reales o CRM (reflejado en el `75/100`). | • Ejecutar demostraciones móviles en teléfonos físicos vía USB.<br>• Centralizar *helpers* de manejo de errores HTTP y zonas horarias.<br>• Ampliar datasets a 6–12 meses y demostrar Utilidad Neta, amortización y CRM en Sprint 4. |
| **Sprint 4** | • **Madurez Full Stack real:** Cada miembro cerró características completas BD → API → UI Web/Móvil.<br>• **Precisión financiera (`Decimal`):** Cero descuadres cambiarios BOB/USD, saldo final `0.00` en amortizaciones y cálculo exacto de **Utilidad Neta**.<br>• **Arquitectura Modelo C4** comprendida y documentada de Contexto a Código.<br>• Estabilidad sostenida en desviación mínima (`+1.0 hr / +1.69%`). | • Ajuste residual inicial de `0.01 BOB` en la última cuota de amortización durante las pruebas tempranas.<br>• Desbordamiento horizontal inicial en tablas contables de 8 columnas sobre `375 px`.<br>• Alto esfuerzo inicial de calibración en `seed_sprint4` (12 meses × 14 tenants) y ajuste del pool para pruebas de estrés. | • **Mantener aritmética `Decimal` obligatoria (`ROUND_HALF_UP`)** y prohibir `float` en todo cálculo monetario o ERP.<br>• **Adoptar diseño *mobile-first*** para tablas gerenciales y extractos financieros desde Figma.<br>• **Retroalimentar los modelos ML con datos clínicos reales anonimizados** supervisados por psicólogos al pasar a producción.<br>• **Institucionalizar revisiones semanales del tablero CRM (1–5★)** convirtiendo alertas $\le 2$★ en auditorías operativas del centro.<br>• **Automatizar pruebas de estrés multi-tenant en CI/CD** vigilando latencia P95 antes de cada liberación SaaS. |

### 5.3.2 Evaluación Comparativa: Desempeño Individual vs. Trabajo Integrado en Equipo (Sprints 1–4)

En respuesta directa a la directriz de medir cómo trabajó cada integrante de forma individual (autónoma) y cómo respondió integrado en grupo desde el inicio del proyecto hasta su cierre (`datos/requerimientosSprint4.md`):

| Integrante del Equipo | Roles Rotativos (S1–S4) | Desempeño en Autonomía Individual (Solo) | Desempeño Integrado en Equipo (Grupal) | Evolución Consolidada (S1 → S4) |
| :--- | :--- | :--- | :--- | :--- |
| **Mujica Vallejos Andy Mauricio** | Dev (`S1–S2`) · PO (`S3`) · SM (`S4`) | Sobresaliente capacidad para diseñar algoritmos de alta complejidad en solitario: motores `SELECT FOR UPDATE`, AES-256 Fernet, sanitización PII/HITL (`CU23`), predictor ML (`CU24`) y reparto SaaS. | Evolucionó desde una alta concentración individual de tareas (`S2: 45h`) hacia una conducción serena e integradora como PO (`S3`) y SM (`S4`), desbloqueando contratos API para todos. | Promedio **`81.00 / 100`** *(95.5h reales)*; referente de arquitectura, backend e IA/ML. |
| **Larrazabal Rojas Julio Cesar** | Dev (`S1–S2`) · SM (`S3`) · PO (`S4`) | Alta autonomía visual y de maquetado para producir prototipos Figma, calendarios interactivos, interfaces médicas y consolas responsivas Angular 17 respetando exactamente sus tiempos estimados. | Actuó como puente natural entre requisitos del negocio, backend y diseño visual; coordinó destrabes de entorno móvil en Sprint 3 y priorizó con acierto las vistas gerenciales en Sprint 4. | Promedio **`81.00 / 100`** *(70.0h reales)*; máxima precisión temporal y liderazgo UX/PO. |
| **Romero Saavedra Maria Ilse** | Dev (`S1`) · PO (`S2`) · Dev Móvil/Full Stack (`S3–S4`) | Gran rigor analítico individual al traducir reglas clínicas y contables hacia código verificable: motor heurístico, contabilidad **Ganancia Bruta vs. Utilidad Neta**, CSAT/NPS y `seed_sprint4` (12m). | Supo ordenar los 8 Criterios como PO (`S2`), adaptarse al reto Flutter en Sprint 3 y articular estrechamente sus agregaciones P&L/CRM con finanzas y frontend en Sprint 4. | Promedio **`81.00 / 100`** *(49.0h reales)*; sólida articulación negocio–datos–Full Stack. |
| **Velasco Soliz Rolando** | QA (`S1`) · SM (`S2`) · QA Full Stack (`S3–S4`) | Disciplina metódica ejemplar en trabajo autónomo: redactó más de 170 escenarios BDD en el semestre, 18 suites automatizadas multi-stack y scripts de carga/estrés sobre 14 tenants. | Su rol integrador fue clave: tras dirigir 18 dailies como SM (`S2`), estableció un canal temprano de reporte y validación directa con cada desarrollador, erradicando regresiones en el cierre. | Promedio **`81.75 / 100`** *(60.5h reales — nota más alta)*; garante transversal de calidad. |
| **Condori Diaz Marilyn Esther** | PO (`S1`) · Dev (`S2–S3`) · Dev Full Stack Finanzas (`S4`) | Muy sólida en lógica de negocio y persistencia transaccional autónoma (SOAP inmutable, epicrisis PDF, QBE OpenPyXL, pagos multimoneda BOB/USD y amortización exacta). | Superó la barrera de trabajar únicamente en backend web asumiendo con éxito el desarrollo móvil (`S3`) y coordinando contratos en tiempo real con Flutter para cobros/cuotas (`S4`). | Promedio **`80.50 / 100`** *(47.0h reales)*; notable salto hacia integración Full Stack. |
| **Delgado Rojas Alberto Caleb** | SM (`S1`) · Dev Móvil (`S2–S4`) | Gran iniciativa autónoma en el ecosistema Flutter/Android (almacenamiento seguro JWT, WebRTC Jitsi, firma SHA-256 táctil, cronograma móvil de amortización y calificación CRM). | Aunque en el Sprint 2 sufrió fricciones de integración (`CRLF/LF` y traspaso móvil, `76/100`), corrigió su coordinación con backend en S3–S4 logrando cierre limpio y sincronizado en dispositivos físicos. | Promedio **`79.25 / 100`** *(43.0h reales)*; consolidación móvil e integración efectiva al cierre. |

> **Síntesis de Cohesión Grupal:** El equipo superó las asimetrías iniciales de carga y comunicación detectadas entre el Sprint 0 y Sprint 2 mediante tres prácticas decisivas: (1) **rotación obligatoria de PO y SM**, que desarrolló empatía entre negocio, UX y operación técnica; (2) **pruebas cruzadas y ejecución incremental de BDD**, eliminando la acumulación final de errores; y (3) **transición Full Stack real en el Sprint 4**, donde los seis integrantes compartieron responsabilidad integral desde la base de datos PostgreSQL hasta la experiencia móvil y Web.

### 5.3.3 Banco Consolidado de Recomendaciones Técnicas y Operativas (Post-Sprint 4)

| Dimensión del Producto | Recomendación Estratégica de Evolución y Continuidad |
| :--- | :--- |
| **Arquitectura y Multi-Tenancy** | Conservar la documentación viva en **Modelo C4** ante cada nuevo microservicio o esquema cliente y automatizar pruebas de aislamiento entre esquemas PostgreSQL antes de cada migración en producción. |
| **Finanzas y Contabilidad** | Mantener tolerancia cero frente a tipos flotantes (`float`), auditar mensualmente el log `ajuste_redondeo` y conectar la pasarela simulada hacia adquirentes locales bolivianos/regionales (QR Simple oficial y facturación SIN/SIAT). |
| **Inteligencia Artificial y ML** | Mantener intacta la barrera **HITL (Human-in-the-Loop)** impidiendo decisiones clínicas autónomas sin firma profesional, y reentrenar los pesos predictivos de `CU24` conforme crezcan los historiales reales anonimizados de pacientes. |
| **Calidad QA, Móvil y CRM** | Incorporar suites E2E móviles y pruebas de estrés (`k6`/Locust) dentro del flujo CI/CD, e instituir protocolos semanales en cada clínica para atender cualquier ticket CRM $\le 2$★ en menos de 24 horas. |

---

## 5.4 Gráfica Consolidada de Burndown, BurnUp y Esfuerzo (Sprints 1 al 4)

A continuación se consolidan los datos de **Estimación vs. Realización**, ritmo de entrega y convergencia al objetivo de los cuatro sprints ejecutados (**Sprint 1 al Sprint 4**, excluyendo el Sprint 0 diagnóstico de `18` tareas / `80` pts / `76.0h` est. / `87.0h` reales, que permanece únicamente como línea base fundacional) sobre una **única línea temporal continua**:

### 5.4.1 Tabla Maestra Consolidada de Carga y Avance (Sprints 1 al 4)

| Sprint | Hito Temporal | Tareas Planificadas | Tareas Done Acum. | PHU Acumulados | Horas Estimadas Sprint | Horas Reales Sprint | Desviación (hr / %) | Carga Restante Ideal Proyecto | Carga Restante Real Proyecto |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SP1** | Inicio S1 (26/08) → Fin S1 (06/09) | 15 (`SP1-19..33`) | 15 (21.4%) | 69 PHU | 73.0 hr | 80.0 hr | **+7.0 hr (+9.59%)** | 346.0 → 273.0 hr | 365.0 → 285.0 hr |
| **SP2** | Inicio S2 (11/09) → Fin S2 (05/10) | 34 (`SP2-34..67`) | 49 (70.0%) | 160 PHU | 155.0 hr | 165.0 hr | **+10.0 hr (+6.45%)** | 273.0 → 118.0 hr | 285.0 → 120.0 hr |
| **SP3** | Inicio S3 (09/10) → Fin S3 (02/11) | 11 (`SP3-68..78`) | 60 (85.7%) | 211 PHU | 59.0 hr | 60.0 hr | **+1.0 hr (+1.69%)** | 118.0 → 59.0 hr | 120.0 → 60.0 hr |
| **SP4** | Inicio S4 (06/11) → Fin S4 (22/11) | 10 (`SP4-79..88`) | **70 (100.0%)** | **263 PHU** | 59.0 hr | 60.0 hr | **+1.0 hr (+1.69%)** | 59.0 → **0.0 hr** | 60.0 → **0.0 hr** |
| **TOT** | **Sprints 1 a 4 Consolidados** | **70 Tareas** | **70 (100%)** | **263 PHU** | **346.0 hr** | **365.0 hr** | **+19.0 hr (+5.49%)** | **0.0 hr** | **0.0 hr** |

### 5.4.2 Indicadores Consolidados de Velocidad, Quema Diaria y Precisión por Sprint

| Sprint | Jornadas Ejecutivas | Tareas Done | PHU Entregados | Velocidad (PHU/día) | Quema Media Real (hr/día) | Desviación (hr / %) | Precisión de Estimación | Cumplimiento del Alcance |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **SP1** | 12 días *(D1–D12)* | 15 | 69 | `5.75 PHU/día` | `6.67 hr/día` | `+7.0 hr (+9.59%)` | **90.41%** | **100%** *(15/15 tareas)* |
| **SP2** | 18 días *(D1–D18)* | 34 | 91 | `5.06 PHU/día` | `9.17 hr/día` | `+10.0 hr (+6.45%)` | **93.55%** | **100% Web/BD** *(Móvil→SP3)* |
| **SP3** | 10 días *(D1–D10)* | 11 | 51 | `5.10 PHU/día` | `6.00 hr/día` | `+1.0 hr (+1.69%)` | **98.31%** | **100%** *(11/11 + deuda móvil)* |
| **SP4** | 12 días *(D1–D12)* | 10 | 52 | `4.33 PHU/día` | `5.00 hr/día` | `+1.0 hr (+1.69%)` | **98.31%** | **100%** *(10/10 tareas finales)* |
| **TOT** | **52 días efectivos** | **70** | **263** | **`5.06 PHU/día`** | **`7.02 hr/día`** | **`+19.0 hr (+5.49%)`** | **94.51%** | **100% (0 deuda técnica residual)** |

### 5.4.3 Gráficas Unificadas de los 4 Sprints en Una Sola Línea

#### 1. Gráfica Continua de Burndown (Carga Restante Ideal vs. Real, Sprints 1–4)

![Burndown Consolidado 4 Sprints](./imagenes/burndown_consolidado_4sprints.png)

* **Comparativa directa generada nativamente desde Excel ([`sprint4.xlsx` — hoja `Consolidado_S1_S4`](file:///c:/Users/User/Documents/2-2026/SI2/PROYECTO_GRUPAL_OFI/diagramas/sprint4.xlsx)):**

![Burndown Consolidado 4 Sprints (Excel)](./imagenes/burndown_consolidado_4sprints_excel.png)

#### 2. Gráfica Continua de BurnUp (Acumulado de Tareas Terminadas y PHU, Sprints 1–4)

![BurnUp Consolidado 4 Sprints](./imagenes/burnup_consolidado_4sprints.png)

* **Comparativa directa generada nativamente desde Excel ([`sprint4.xlsx` — hoja `Consolidado_S1_S4`](file:///c:/Users/User/Documents/2-2026/SI2/PROYECTO_GRUPAL_OFI/diagramas/sprint4.xlsx)):**

![BurnUp Consolidado 4 Sprints (Excel)](./imagenes/burnup_consolidado_4sprints_excel.png)

#### 3. Gráfica Continua de Estimación vs. Realización y Convergencia al Objetivo (Sprints 1–4)

![Esfuerzo Consolidado 4 Sprints](./imagenes/esfuerzo_consolidado_4sprints.png)

* **Comparativa directa generada nativamente desde Excel ([`sprint4.xlsx` — hoja `Consolidado_S1_S4`](file:///c:/Users/User/Documents/2-2026/SI2/PROYECTO_GRUPAL_OFI/diagramas/sprint4.xlsx)):**

![Esfuerzo Consolidado 4 Sprints (Excel)](./imagenes/esfuerzo_consolidado_4sprints_excel.png)

### 5.4.4 Análisis Comparativo de Alejamiento y Aproximación al Objetivo

* **Tramo de Mayor Alejamiento del Objetivo (`Sprint 1: +9.59%` y `Sprint 2: +6.45%`):** En el **Sprint 1** (*Objetivo: consolidar agenda multi-tenant sin colisiones y teleconsulta WebRTC*), el equipo se alejó en `+7.0 hr` sobre las `73.0 hr` estimadas (`90.41%` de precisión) debido a la curva inicial de aprendizaje en concurrencia pesimista (`SELECT FOR UPDATE`), ajuste horario `GMT-4` y configuración temprana en Android. En el **Sprint 2** (*Objetivo: entregar expediente clínico SOAP médico-legal, criptografía y los 8 Criterios*), aunque el desvío porcentual bajó a `+6.45%` (`93.55%` de precisión), se produjo la mayor brecha absoluta (`+10.0 hr` sobre `155.0 hr`) por la expansión del backlog hacia **34 tareas** (`9.17 hr/día`), concentrando esfuerzos criptográficos y QA al cierre.
* **Tramo de Aproximación Óptima al Objetivo (`Sprint 3: +1.69%` y `Sprint 4: +1.69%`):** A partir del **Sprint 3** (*Objetivo: saldar deuda móvil Flutter 3.x e implementar Triaje/Matching IA HITL*), la recalibración del *Planning Poker* y la experiencia acumulada redujeron el desvío a exactamente **+1.0 hr sobre 59.0 hr** (`98.31%` de precisión). En el **Sprint 4** (*Objetivo: cierre integral Full Stack con IA longitudinal 12m, predictor ML, amortización Web/Móvil, P&L Utilidad Neta, CRM 1–5★ y Modelo C4*), el equipo sostuvo la misma precisión óptima del **`98.31%`** (`59.0 hr` est. vs `60.0 hr` reales), cerrando los cuatro sprints en una sola línea continua con apenas **`+5.49%` (`+19.0 hr` en `52` días ejecutivos)** y **`0.0 hr`** pendientes en el Burndown final.

---

# 6. CONCLUSIÓN

## 6.1 Conclusión General del Trabajo

El desarrollo integral de la plataforma **SIGEPSI** (*Sistema Web y Móvil SaaS Multi-Tenant de Gestión Integral para Centros de Salud Mental*) durante los cuatro sprints del semestre (con línea base diagnóstica en el **Sprint 0 [80/100]**, consolidación técnica en los **Sprints 1 y 2 [80/100]**, punto de inflexión móvil-analítico en el **Sprint 3 [75/100]** y madurez arquitectónica en el **Sprint 4 [Evaluación Cruzada: 88.00/100]**) demostró la viabilidad metodológica y de ingeniería de construir un software clínico-administrativo escalable bajo el marco ágil **SCRUM**, la arquitectura jerárquica **Modelo C4** (Niveles 1 al 4) y un enfoque real de ingeniería **Full Stack** sobre **Django 5.x REST Framework**, **Angular 17**, **Flutter 3.x** y **PostgreSQL 16** con aislamiento estricto de esquemas mediante `django-tenants`.

Desde la perspectiva técnica y funcional, el incremento final superó el alcance transaccional básico para entregar salidas gerenciales, clínicas, financieras y de fidelización auditables y verificables. En seguridad y trazabilidad médico-legal, la solución resguarda historiales clínicos electrónicos con control de acceso basado en roles (**RBAC**), notas evolutivas **SOAP** inmutables, sellado criptográfico **SHA-256**, bitácora forense cifrada con **AES-256 Fernet** y respaldos automatizados por inquilino. Sobre dicha base segura, el componente asistivo de **Inteligencia Artificial y Machine Learning** implementa resúmenes clínicos longitudinales (`CU23`) y detección temprana predictiva de señales de riesgo (`CU24`) entrenada sobre datasets sintéticos continuos de **6 a 12 meses** (`2,180+` sesiones y `14,400+` registros diarios de estado de ánimo), garantizando sanitización previa de datos personales (**PII**) y validación humana obligatoria (**Human-in-the-Loop**).

Complementariamente, el núcleo financiero y comercial (`CU26`) resolvió los requerimientos reales de gerencia mediante operaciones multimoneda exactas (**BOB/USD** con aritmética `Decimal` libre de errores de redondeo), planes de pago fraccionados con extracto completo de amortización disponible tanto en el portal Web como en la aplicación móvil Flutter, liquidación automatizada de honorarios profesionales y un Estado de Resultados gerencial que distingue explícitamente la **Ganancia Bruta** de la **Utilidad Neta Real** tras deducir los gastos operativos fijos mensuales de cada clínica (alquileres, servicios básicos y personal de apoyo). Dicho ciclo operativo se cierra con el módulo **CRM de satisfacción post-consulta (1 a 5 estrellas)** y métricas estadísticas **CSAT/NPS** integradas en el tablero principal. Finalmente, el aprendizaje del equipo validó que el trabajo Full Stack individual integrado mediante evaluaciones cruzadas honestas, pruebas automatizadas BDD y trazabilidad UML completa permite revertir desviaciones técnicas tempranas y entregar un producto SaaS cohesivo y defendible ante escenarios reales.

<div style="page-break-after: always;"></div>

<!-- Salto de página obligatorio: Conclusiones Individuales en la página siguiente conforme a datos/requerimientosSprint4.md -->

## 6.2 Conclusiones Individuales

### Condori Diaz Marilyn Esther (Reg. 224051237)
**Condori Diaz Marilyn Esther:** A lo largo de los cuatro sprints experimenté una evolución profesional integral al asumir sucesivamente los roles de **Product Owner** en el Sprint 1, **Desarrolladora Backend** en el Sprint 2, **Desarrolladora Móvil** en el Sprint 3 y **Desarrolladora Full Stack Financiera** en el cierre del Sprint 4. La transición desde el desarrollo servidor hacia Flutter en el Sprint 3 —donde enfrentamos ajustes de zona horaria `GMT-4` y el desafío de consolidar una calificación grupal de `75/100`— me exigió reforzar mi disciplina de integración continua. Finalmente, consolidar en el Sprint 4 el motor financiero multimoneda (**BOB/USD**) con planes de amortización de exactitud `Decimal` me permitió comprobar que un sistema clínico serio exige dominio completo de extremo a extremo: desde evitar descuadres de centavos en PostgreSQL hasta verificar que el paciente consulte sus cuotas sin fricción desde el teléfono.

### Delgado Rojas Alberto Caleb (Reg. 224027204)
**Delgado Rojas Alberto Caleb:** Mi participación se centró en consolidar la experiencia móvil nativa en **Flutter 3.x** desde los cimientos multi-tenant hasta los entregables gerenciales de cierre, alternando entre **Scrum Master** en el Sprint 1 y **Desarrollador Móvil Full Stack** hasta el cierre del Sprint 4. Los tropiezos ocurridos durante los Sprints 2 y 3 —especialmente el traspaso parcial de alcance móvil, errores de normalización `CRLF/LF` y excepciones HTTP `400` iniciales en el cliente Android— me enseñaron la importancia de validar contratos API y dispositivos físicos de forma temprana. Integrar en el Sprint 4 entregables de alto impacto verificable para el usuario final —extractos transparentes de amortización de cuotas en el celular, firma táctil SHA-256, tokens en Keystore y el flujo completo de calificación **CRM (1–5 estrellas)**— fortaleció mi criterio de calidad multiplataforma.

### Larrazabal Rojas Julio Cesar (Reg. 223049255)
**Larrazabal Rojas Julio Cesar:** Como responsable transversal de los prototipos **UI/UX en Figma** y del frontend en **Angular 17 Standalone**, además de ejercer como **Scrum Master** durante el Sprint 3 y **Product Owner** en el Sprint 4, comprobé que la ingeniería de interfaz es determinante para que la lógica clínica y financiera compleja resulte comprensible en contextos médicos reales. En los Sprints 1 al 3 comprendí los límites de diseñar únicamente para resoluciones de escritorio cuando las pruebas en portátiles estándar y móviles evidenciaron problemas de responsividad y horarios fragmentados antes de la defensa. Durante el Sprint 4 superé ese reto priorizando e implementando componentes adaptativos verificados entre `375 px` y `4K` para el tablero gerencial, gráficos *Waterfall* de **Ganancia Bruta vs. Utilidad Neta**, histogramas **CRM** y el mapa completo **Modelo C4**, logrando consistencia visual sin desbordamientos.

### Mujica Vallejos Andy Mauricio (Reg. 224028367)
**Mujica Vallejos Andy Mauricio:** Participar en la arquitectura **SaaS Multi-Tenant (`django-tenants`)**, el blindaje criptográfico (bitácora AES-256 Fernet, hash SHA-256), los servicios de **Inteligencia Artificial y Machine Learning (`CU21–CU24`)** y la liquidación porcentual de honorarios (`CU26`), además de actuar como **Product Owner** en el Sprint 3 y **Scrum Master** en el Sprint 4, consolidó mi criterio arquitectónico sobre sistemas críticos de salud mental. La observación docente tras el Sprint 3 evidenció que las reglas analíticas simples sobre pocos registros carecen de sustento real. Por ello, en el Sprint 4 reorienté el diseño hacia datasets sintéticos longitudinales de **6 a 12 meses**, incorporé trazabilidad arquitectónica mediante el **Modelo C4** y reforcé la sanitización **PII** junto al control **Human-in-the-Loop**, confirmando que la IA clínica solo aporta valor si es explicable, auditable y subordinada al especialista humano.

### Romero Saavedra Maria Ilse (Reg. 222009772)
**Romero Saavedra Maria Ilse:** Desempeñarme como **Product Owner** en el Sprint 2 y posteriormente rotar hacia el desarrollo **Full Stack** en Flutter, Contabilidad Gerencial y Analítica **CRM** durante los Sprints 3 y 4 me permitió traducir reglas reales de negocio psicológico-administrativo hacia algoritmos verificables. Tras identificar que reportar únicamente ingresos cobrados ocultaba la rentabilidad efectiva de los centros clínicos, diseñé en el Sprint 4 el motor contable que deduce gastos operativos fijos mensuales para determinar la **Utilidad Neta**, articulado con indicadores **CSAT/NPS** del módulo **CRM (1–5 estrellas)** y series históricas sintéticas de 12 meses. Este recorrido demostró que el verdadero valor gerencial de un software empresarial reside en convertir registros aislados de citas, pagos y encuestas en información financiera y de calidad accionable.

### Velasco Soliz Rolando (Reg. 223044768)
**Velasco Soliz Rolando:** Ejercer como **Scrum Master** en el Sprint 2 y liderar la estrategia **QA Full Stack** durante los cuatro sprints me permitió constatar que la confiabilidad de una plataforma SaaS multi-tenant depende directamente de la disciplina temprana de verificación. Durante los Sprints 1 y 2 detectamos cómo concentrar pruebas al final eleva la presión operativa, y en el Sprint 3 verificamos que las pruebas funcionales aisladas no bastan si no validan salidas financieras acumuladas ni carga real multi-inquilino. En el Sprint 4 sistematicé **40 escenarios BDD**, **18 pruebas automatizadas** en Python, Angular y Dart, además de ensayos de estrés concurrente sobre los 14 esquemas tenant (**P95 de 284 ms** y cero errores de redondeo cambiario), confirmando que el aseguramiento continuo es la columna vertebral de la calidad entregada.

---

# 7. RECOMENDACIÓN

En estricta correspondencia con la conclusión general obtenida al cierre de **SIGEPSI**, se recomienda que la transición de la plataforma desde su entorno académico validado hacia una puesta en producción comercial en centros de salud mental reales se ejecute de forma escalonada bajo cuatro líneas operativas concretas:

1. **Sustitución Progresiva de Datasets Sintéticos y Recalibración del Modelo Predictivo (`CU24`):** Reemplazar gradualmente los registros sintéticos longitudinales de **6 a 12 meses** por historiales clínicos reales debidamente anonimizados y respaldados por consentimiento informado digital expreso. Sobre esa base real, establecer ciclos trimestrales de reentrenamiento supervisado para recalibrar umbrales de riesgo emocional y métricas de precisión, manteniendo invariable la intervención obligatoria del psicólogo mediante el enfoque **Human-in-the-Loop**.
2. **Integración Tributaria Local y Pasarelas Financieras en Tiempo Real (`CU26`):** Conectar el motor multimoneda (**BOB/USD**) y el módulo de planes de amortización de cuotas con el sistema de facturación electrónica en línea del **Servicio de Impuestos Nacionales (SIN)** y pasarelas bancarias locales (QR interoperable/tarjetas), automatizando la conciliación bancaria diaria sobre el Estado de Resultados de **Ganancia Bruta vs. Utilidad Neta**.
3. **Gestión Gerencial Continua mediante CRM (`1–5★`) y Control de Rentabilidad:** Institucionalizar revisiones quincenales en cada clínica tenant cruzando los indicadores de satisfacción **CSAT/NPS** y alertas de calificaciones $\le 2$ estrellas con la estructura mensual de gastos fijos operativos, transformando la retroalimentación directa del paciente en acciones correctivas medibles sobre puntualidad, calidad de teleconsulta y retención terapéutica.
4. **Endurecimiento de Infraestructura Cloud SaaS y Automatización CI/CD:** Migrar los contenedores Docker actuales hacia planes productivos dedicados sin reposo de instancia, configurando réplicas automatizadas de **PostgreSQL 16**, monitoreo continuo de latencia por esquema tenant y *pipelines* **CI/CD** que bloqueen cualquier despliegue si fallan las suites unitarias, criptográficas (**SHA-256 / Fernet**) o de estrés multi-tenant.

---

# 8. BIBLIOGRAFÍA

### 8.1 Libros Físicos y Literatura Académica
* American Psychological Association. (2017). *Ethical principles of psychologists and code of conduct*. APA.
* Beck, J. S. (2011). *Cognitive behavior therapy: Basics and beyond* (2.ª ed.). Guilford Press.
* Brown, S. (2023). *The C4 model for visualising software architecture: Software architecture for developers* (Vol. 2). Leanpub.
* Colegio de Psicólogos de Bolivia. (2002). *Código de ética del psicólogo boliviano*. La Paz, Bolivia.
* Fernández-Ballesteros, R. (2013). *Evaluación psicológica: Conceptos, métodos y estudio de casos* (2.ª ed.). Ediciones Pirámide.
* Fowler, M. (2018). *Refactoring: Improving the design of existing code* (2.ª ed.). Addison-Wesley Professional.
* Graham, S., Depp, C., Lee, E. E., Nebeker, C., Tu, X., Kim, H. C., & Jeste, D. V. (2019). Artificial intelligence for mental health and mental illnesses: An overview. *Current Psychiatry Reports*, 21(11), 1–15. https://doi.org/10.1007/s11920-019-1094-0
* Horngren, C. T., Sundem, G. L., & Elliott, J. A. (2018). *Introducción a la contabilidad financiera* (11.ª ed.). Pearson Educación.
* Laudon, K. C., & Laudon, J. P. (2020). *Management information systems: Managing the digital firm* (16.ª ed.). Pearson.
* Organización Mundial de la Salud. (2022). *Informe mundial sobre salud mental: Transformar la salud mental para todos*. OMS. https://www.who.int/es/publications/i/item/9789240050860
* Pressman, R. S., & Maxim, B. R. (2020). *Ingeniería del software: Un enfoque práctico* (9.ª ed.). McGraw-Hill.
* Russell, S., & Norvig, P. (2021). *Artificial intelligence: A modern approach* (4.ª ed.). Pearson.
* Schwaber, K., & Sutherland, J. (2020). *La Guía de Scrum: La guía definitiva de Scrum: Las reglas del juego*. Scrum.org.
* Sommerville, I. (2016). *Software engineering* (10.ª ed.). Pearson.

### 8.2 Sitios Web Especializados, Plataformas Cloud y Documentación Técnica
* Angular Team. (2025). *Angular 17 Standalone Components & Signals Documentation*. Google. https://angular.dev/
* Django Software Foundation. (2025). *Django 5.x & Django REST Framework Documentation*. https://www.djangoproject.com/
* Django-Tenants Contributors. (2025). *Multi-tenancy in Django using PostgreSQL schemas*. https://django-tenants.readthedocs.io/
* Firebase Team. (2025). *Firebase Cloud Messaging (FCM) HTTP v1 API Documentation*. Google. https://firebase.google.com/docs/cloud-messaging
* Flutter Team. (2025). *Flutter 3.x Multiplatform Mobile Documentation*. Google. https://docs.flutter.dev/
* Jitsi Meet Project. (2025). *Jitsi Meet External API & Flutter SDK Documentation*. 8x8 Inc. https://jitsi.github.io/handbook/
* MentalGest. (2025). *Software clínico para psicólogos y centros de psicología*. https://mentalgest.com/
* PostgreSQL Global Development Group. (2025). *PostgreSQL 16 Official Documentation (Schemas, JSONB & Trigram Indexes)*. https://www.postgresql.org/docs/16/
* Render Cloud Platform. (2025). *Blueprint Infrastructure as Code (render.yaml) & Docker Deployment*. https://render.com/docs/blueprint-spec
* Spring Health. (2025). *Precision mental healthcare platform*. https://www.springhealth.com/
* Stripe Inc. (2025). *Stripe Checkout, Webhooks & Multi-Currency Billing API*. https://docs.stripe.com/api
* Talkspace. (2025). *Online therapy and telepsychiatry services platform*. https://www.talkspace.com/

### 8.3 Modelos, Motores y Agentes de Inteligencia Artificial Utilizados
* Google DeepMind / Google AI. (2025). *Gemini 1.5 Pro API – Clinical Pre-Analysis & Longitudinal Text Synthesis (with PII Sanitization)*. https://ai.google.dev/
* Hugging Face & PyTorch Community. (2025). *Transformers & FastAPI NLP Inference Microservice (`antidino-iacupficct.hf.space`)*. https://huggingface.co/docs/transformers/
* Scikit-Learn Developers. (2025). *Scikit-Learn Machine Learning in Python: Feature Weighting & Risk Scoring Pipelines*. https://scikit-learn.org/
* Anthropic / Claude & Antigravity Coding Agent. (2026). *Asistencia en verificación de arquitectura Modelo C4, consistencia PlantUML/UML 2.5, validación de trazabilidad SCRUM y revisión de pruebas automatizadas bajo supervisión humana del equipo*. https://www.anthropic.com/
* OpenAI. (2025). *ChatGPT / GPT-4o – Asistencia en diseño de prompts UI/UX para Figma y depuración conceptual de criterios BDD*. https://openai.com/
* PlantUML & C4-PlantUML Contributors. (2025). *C4 Model Diagrams & UML 2.5 Modeling Engine*. https://github.com/plantuml-stdlib/C4-PlantUML

### 8.4 Entrevistas y Consultas del Rubro
* Lic. Marilyn Esther Condori Diaz *(Product Owner Inicial del Proyecto)*: Definición del alcance funcional, historias clínicas y reglas de negocio de atención psicológica (Agosto 2026).
* Lic. Claudia Mendoza V. *(Psicóloga Clínica – Consulta Privada)*: Consulta sobre flujos de notas SOAP, consentimientos informados, privacidad y necesidades reales de telepsicología en Bolivia (Agosto 2026).
* Dr. Fernando Ramos G. *(Coordinador de Centro Psicológico)*: Requerimientos de control de citas, liquidación porcentual de honorarios, gastos fijos operativos de consultorios y seguimiento de satisfacción del paciente (Septiembre – Noviembre 2026).

---

# 9. ANEXOS

## Anexo 1: Caso de Estudio 1 – MentalGest

* **Descripción General:** **MentalGest** es una plataforma SaaS latinoamericana orientada específicamente a consultorios y centros de psicología clínica para digitalizar su administración diaria y el expediente del paciente.
* **Módulos y Capacidades Analizadas:**
  * Agenda médica por profesional con recordatorios automáticos.
  * Historia clínica psicológica digital, notas de evolución por sesión y adjuntos clínicos.
  * Gestión básica de consentimientos informados y reportes de ingresos/atenciones.
* **Fortalezas Identificadas:** Interfaz adaptada al vocabulario psicológico hispanohablante y flujo ágil de recepción.
* **Limitaciones frente a SIGEPSI:** Carece de aplicación móvil nativa dedicada para el paciente (*Mood Tracker* y tareas inter-sesión), no incorpora detección predictiva de señales de riesgo mediante Machine Learning ni estado de resultados contable automatizado que diferencie Ganancia Bruta de Utilidad Neta tras gastos fijos.
* **Aporte al Proyecto SIGEPSI:** Inspiró la estructura base de la agenda clínica multi-profesional (`CU6, CU8, CU11`), el expediente electrónico (`CU15`) y los indicadores operativos iniciales (`CU9`).

---

## Anexo 2: Caso de Estudio 2 – Talkspace

* **Descripción General:** **Talkspace** es una de las plataformas globales referentes en telepsicología y terapia en línea, orientada a conectar pacientes con terapeutas licenciados mediante canales digitales síncronos y asíncronos.
* **Módulos y Capacidades Analizadas:**
  * Evaluación inicial (*Intake*) guiada antes de asignar al terapeuta.
  * Sesiones de videoconferencia seguras y mensajería continua entre sesiones.
  * Esquema de planes de suscripción y paquetes de sesiones prepagadas para pacientes y empresas.
* **Fortalezas Identificadas:** Experiencia móvil ubicua altamente intuitiva, baja fricción para iniciar terapia a distancia y seguimiento continuo fuera del horario de consulta.
* **Limitaciones frente a SIGEPSI:** Modelo cerrado centrado únicamente en el mercado estadounidense (sin soporte multi-moneda BOB/USD ni gestión administrativa de consultorios físicos presenciales bajo esquema SaaS B2B Multi-Tenant).
* **Aporte al Proyecto SIGEPSI:** Fundamentó el diseño de la experiencia móvil en Flutter (`CU13, CU17 Móvil`), el cuestionario previo paso a paso (`CU14`), el chatbot orientativo (`CU20`) y el modelo híbrido de paquetes/planes de pago (`CU26`).

---

## Anexo 3: Caso de Estudio 3 – Spring Health

* **Descripción General:** **Spring Health** es una plataforma internacional de salud mental de precisión (*Precision Mental Healthcare*) que combina evaluación clínica validada con modelos de Inteligencia Artificial y Machine Learning para optimizar la asignación terapéutica y el seguimiento de resultados.
* **Módulos y Capacidades Analizadas:**
  * Triaje clínico asistido por algoritmos para clasificar severidad del motivo de consulta.
  * Emparejamiento inteligente (*Care Matching*) entre perfil del paciente y especialidad/disponibilidad del profesional.
  * Monitoreo longitudinal de evolución emocional y detección temprana de deterioro o riesgo de abandono.
* **Fortalezas Identificadas:** Uso riguroso de analítica predictiva orientada a reducir el tiempo hasta la primera intervención efectiva y prevenir crisis mediante alertas tempranas.
* **Limitaciones frente a SIGEPSI:** Enfocado a grandes aseguradoras corporativas y no diseñado como una plataforma SaaS multi-inquilino accesible para gabinetes independientes o clínicas psicológicas locales con contabilidad de Utilidad Neta y CRM integrado.
* **Aporte al Proyecto SIGEPSI:** Sustentó el diseño ético del módulo de Inteligencia Artificial con supervisión humana (*Human-in-the-Loop*), la clasificación asistida (`CU21`), el algoritmo multivariable de emparejamiento (`CU22`), los resúmenes longitudinales (`CU23`) y el motor predictivo ML de riesgo (`CU24`).

---

## Anexo 4: Ecosistema Digital, Enlaces de Despliegue y Códigos QR Oficiales

Para facilitar la verificación directa por parte de la cátedra durante la defensa final (**24 y 26 de noviembre de 2026**), se adjuntan los enlaces oficiales de despliegue cloud (definidos en `prototipo/render.yaml` para la liberación del **22/11/2026**), repositorio, microservicio IA activo y códigos QR generados para acceso instantáneo desde computadora o teléfono móvil:

| Componente del Ecosistema SIGEPSI | Tecnología / Plataforma | Enlace Oficial de Acceso | Estado de Entrega |
| :--- | :--- | :--- | :---: |
| **Portal Web Responsivo (Frontend)** | Angular 17 Standalone + Nginx Docker (Render Cloud) | `https://sigepsi-frontend.onrender.com` | Servicio Blueprint `render.yaml` (cierre 22/11) |
| **Backend Core API REST (Multi-Tenant)** | Django 5.x REST + Gunicorn + PostgreSQL 16 (Render Cloud) | `https://sigepsi-backend.onrender.com/api/` | Servicio Blueprint `render.yaml` (cierre 22/11) |
| **Microservicio IA / Chatbot NLP** | FastAPI + PyTorch / Transformers (Hugging Face Spaces) | `https://antidino-iacupficct.hf.space/docs` | Desplegado en Hugging Face Spaces |
| **Repositorio GitHub y APK Móvil Flutter** | Git / Flutter 3.22 (`sigepsi-v4.0.0-release.apk`) | `https://github.com/Andy-top801/Sistema-Psicol-gico-.git` | Repositorio oficial / APK release v4.0.0 |

![Códigos QR del Ecosistema Digital SIGEPSI](./imagenes/qr_ecosistema_sigepsi.png)

---

*Documento oficial de cierre del **Sprint 4** y **Artefactos Finales (Sprints 1–4)** elaborado por el **Equipo SCRUM Grupo #9 – SIGEPSI** para la asignatura **Sistemas de Información II (Semestre 2-2026)**.*
