# -*- coding: utf-8 -*-
import re

prompts = {
    'HU-11': 'Pantalla Directorio y Perfil Psicólogo (Figma)<br>**Prompt para IA (Generación UI):** *"UI/UX web design of a professional psychologist directory and profile management screen for a mental health platform named SIGEPSI, Angular 17 style. Clean light mode with teal and indigo tones. Main view includes search bar with specialty filters (Terapia Cognitivo-Conductual, Infanto-Juvenil, Pareja) and a grid of therapist profile cards showing avatar photo, full name, professional license number (Colegiatura), active specialties badges, consultation fee (Bs. 180), modalities accepted (Presencial / Virtual), and action buttons \'Editar Perfil\' and \'Ver Horarios\'. Modern SaaS medical typography Inter, high fidelity Figma UI, crisp layout, 4k."*',
    
    'HU-12': 'Pantalla Matriz de Disponibilidad Semanal (Figma)<br>**Prompt para IA (Generación UI):** *"UI/UX web application screen of a weekly schedule and shift availability matrix for psychologists in mental health clinic SIGEPSI, Angular style. Clean modern design with soft neutral background and purple/teal accents. Left panel with therapist summary and consultation duration selector (30 min, 45 min, 60 min). Center view displays an interactive weekly schedule matrix (Monday to Saturday) with toggle switches for active days and configurable time blocks (e.g. 08:00 - 12:00, 14:00 - 18:00) with visual time chip tags and \'Agregar Franja\' button. Clear warning notice for active appointments conflict. High fidelity Figma mockup, clean UI kit, 4k."*',
    
    'HU-13': 'Pantalla Gestión y Ficha de Paciente (Figma - Larrazabal Julio Cesar)<br>**Prompt para IA (Generación UI):** *"UI/UX desktop web design for clinical patient registration and electronic health record intake form for SIGEPSI mental health system, Angular 17. Clean clinical light theme. Form organized in modern card sections: Personal Identification (Full Name, CI/DNI, Date of Birth, Gender), Emergency Contact with legal guardian toggle for minors under 18 showing guardian full name and phone number. Top header with patient code badge \'EXP-2026-084\'. Tabbed navigation for Personal Info, Consultation History, and Active Alerts. Modern clean form inputs, floating labels, validation states, Figma design system, 4k."*',
    
    'HU-14': 'Pantalla Perfil y Datos Personales Móvil (Figma)<br>**Prompt para IA (Generación UI):** *"Mobile app UI design for patient personal profile screen in Flutter 3 style on an iPhone 15 Pro mockup for SIGEPSI mental health app. Modern soothing pastel blue and mint green palette. Top app bar with back arrow and center title \'Mi Perfil\'. User avatar circle with camera edit badge, patient full name \'Sofía Beltrán\', and tenant clinic badge \'Centro San Rafael\'. Card list displaying editable fields: phone number, residential address, emergency contact person and phone, and security options. Primary button \'Guardar Cambios\' with smooth corner radius. Clean mobile UX, high fidelity Figma mockup, 4k."*',
    
    'HU-15': 'Pantalla Calendario y Reserva de Citas Web (Figma)<br>**Prompt para IA (Generación UI):** *"UI/UX web modal and page for booking psychological appointments in SIGEPSI, Angular 17. Clean SaaS modal dialog overlaid on a blurred clinic dashboard. Left section has doctor selection with avatar, specialty, and modality selector pills: \'Presencial (Consultorio 3)\' or \'Teleconsulta (Jitsi Meet)\'. Center shows an interactive mini calendar and available time slots (chips: 09:00, 10:00, 11:00, 15:00) with real-time collision detection badge \'Horario Disponible\'. Bottom input for reason of consultation and primary confirm button \'Confirmar Reserva\'. High fidelity Figma mockup, modern healthcare UI, 4k."*',
    
    'HU-16': 'Pantalla Mis Citas y Reservar Cita Móvil (Figma)<br>**Prompt para IA (Generación UI):** *"Mobile application UI screen for patient appointment management \'Mis Citas\' in Flutter 3 for SIGEPSI on iOS/Android device. Soothing mental wellness colors, teal and lavender accents. Segmented control with tabs \'Próximas\' and \'Historial\'. Cards for upcoming sessions showing psychologist photo, name, date badge \'Jueves 3 Sept - 10:00 AM\', session type \'Teleconsulta Virtual\', and color badge \'Confirmada\' in emerald green. Card has an active prominent button \'Ingresar a Teleconsulta\' with a video icon. Floating action button \'+\' to book a new appointment. High fidelity Figma UI, 4k."*',
    
    'HU-17': 'Modal Reprogramar / Cancelar Cita (Figma)<br>**Prompt para IA (Generación UI):** *"UI/UX modal pop-up design for rescheduling or canceling a clinical appointment in psychological platform SIGEPSI, Angular 17. Centered clean dialog with backdrop blur. Top alert notice in amber: \'Cancelación sin recargo permitida hasta 24 horas antes\'. Two distinct action tabs: \'Reprogramar Cita\' with date picker and available time slots chips, and \'Cancelar Cita\' with dropdown for cancellation reason (Motivo personal, Salud, Cruce de horarios) and optional text feedback. Actions: secondary ghost button \'Volver\' and danger button \'Confirmar Cancelación\'. Clean medical SaaS UX, Figma mockup, 4k."*',
    
    'HU-18': 'Pantalla Videoconsulta WebRTC (Figma - Larrazabal Julio Cesar)<br>**Prompt para IA (Generación UI):** *"UI/UX desktop web screen for encrypted telehealth psychological video consultation using embedded Jitsi Meet in SIGEPSI, Angular 17. Dark elegant teletherapy room layout. Main central video area showing the patient in high definition, with picture-in-picture floating window of the psychologist in the bottom right corner. Bottom floating glassmorphic control dock with mute audio, toggle video, end call (red button), secure chat panel toggle, and digital session timer showing \'34:12 / 50:00 min\'. Top bar with patient name, encrypted lock icon, and quick clinical notes sidebar toggle. High fidelity Figma UI, professional telepsychology SaaS, 4k."*',
    
    'HU-19': 'Pantalla Sala de Teleconsulta Móvil (Figma)<br>**Prompt para IA (Generación UI):** *"Mobile app UI design for telehealth video session in Flutter 3 on a smartphone for mental health patient in SIGEPSI. Fullscreen immersive video layout showing the psychologist speaking on full display with soft lighting and professional office background, patient self-view in a small top-right rounded corner thumbnail. Bottom semi-transparent floating action bar with rounded touch buttons: microphone mute, camera flip, chat overlay toggle, and red end-session button. Top overlay shows connection status indicator \'HD Seguro\' and call duration timer \'18:45\'. Modern mobile UX, Figma style, 4k."*',
    
    'HU-20': 'Pantalla Dashboard Indicadores y Métricas (Figma)<br>**Prompt para IA (Generación UI):** *"UI/UX analytics dashboard design for clinical mental health clinic management SIGEPSI, Angular 17 desktop view. Modern clean layout with soft neutral grey background. Top metrics row with four key KPI metric cards: \'Citas Hoy\' (28 citas), \'Pacientes Activos del Mes\' (142 pacientes), \'Tasa de Inasistencia\' (6.4% in green down trend), and \'Ocupación Profesional\' (84%). Middle section with two interactive charts: monthly appointment volume bar chart and consultation modality distribution donut chart (Presencial vs Teleconsulta). Filter bar by therapist and date range. Figma UI kit, clean typography, 4k."*',
    
    'HU-21': 'Panel de Notificaciones y Alertas Clínicas (Figma)<br>**Prompt para IA (Generación UI):** *"UI/UX notification center and clinical alert panel for psychologists in SIGEPSI, Angular 17. Slide-over drawer and table view displaying prioritized patient risk and attendance alerts. Alert cards categorized by severity badges: Red badge \'Riesgo de Abandono\' (Paciente >21 días sin cita), Orange badge \'Inasistencias Reiteradas\' (2 faltas consecutivas), and Blue badge \'Confirmación Pendiente\'. Each card shows patient avatar, days elapsed, quick notes input, and action button \'Contactar Paciente\' / \'Marcar Resuelta\'. Clean clinical healthcare UX, Figma mockup, 4k."*',
    
    'HU-22': 'Vista Calendario Semanal / Diario por Profesional (Figma)<br>**Prompt para IA (Generación UI):** *"UI/UX dashboard design of an interactive clinical appointment calendar for a mental health platform named SIGEPSI. Desktop web interface in Angular style, clean light mode, modern SaaS healthcare design. Top bar with clinic name, date navigation \'Lunes 1 de Septiembre\', view switcher pills (Mes, Semana, Día) with \'Semana\' selected, and psychologist filter dropdown \'Lic. Andy Mujica - Psicología Clínica\'. Main weekly calendar time grid (08:00 to 18:00, Monday to Saturday) populated with color-coded appointment cards: blue for \'Programada\', emerald green for \'Confirmada\', vibrant orange with video icon for \'En Teleconsulta\', grey for \'Realizada\'. An interactive floating popover card is highlighted over a 10:00 AM slot displaying patient \'Carlos Mendoza\', service \'Teleconsulta Jitsi Meet\', time \'10:00 - 10:50 AM\', and quick action buttons \'Ingresar a Sala\' in teal and \'Reprogramar\'. Clean typography, 8px grid, Figma UI design, premium medical software, high fidelity, 4k."*'
}

def update_document(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    for hu_id, p_text in prompts.items():
        # Look for the HU header, then find **Prototipo:** up to |
        # pattern finds the exact line: | **Desarrollador a cargo:** | ... **Prototipo:** ... |
        escaped_hu = re.escape(hu_id)
        # Search for HU block
        hu_match = re.search(rf'#### Historia de Usuario {escaped_hu}\b.*?(?=(?:#### Historia de Usuario|### 4\.1\.3|$))', content, flags=re.DOTALL)
        if not hu_match:
            print(f'HU {hu_id} not found in {path}')
            continue
            
        block = hu_match.group(0)
        # In this block, replace from **Prototipo:** to the end of that table cell |
        new_block = re.sub(r'(\*\*Prototipo:\*\*\s*)([^|]+?)(\s*\|)', rf'\g<1>{p_text} \3', block)
        content = content[:hu_match.start()] + new_block + content[hu_match.end():]

    # In HU-22, ensure the image is attached right below the table
    if 'prototipo_calendario_hu22.png' not in content:
        content = re.sub(
            r'(#### Historia de Usuario HU-22\b.*?\|\s*\*\*Desarrollador a cargo:\*\*.*?\|\n)',
            r'\1\n<br>\n\n**Visualización del Prototipo Generado:**\n\n![Prototipo UI Generado por IA - Calendario Interactivo de Agenda (HU-22)](./imagenes/prototipo_calendario_hu22.png)\n',
            content,
            flags=re.DOTALL
        )

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Document {path} updated successfully.')

if __name__ == '__main__':
    update_document('documentacion/intento.md')
    update_document('documentacion/sprint1.md')
