# Ventilación mecánica

- Bases
    
    **PRINCIPIOS DE VENTILACIÓN MECÁNICA**
    
    Ventilación mecánica a cualquier método de respiración que emplee un aparato mecánico para satisfacer parcialmente o por completo los requerimientos de flujo de la respiración de un paciente. No es terapéutica, solo soporte y transitoria.
    
    Indicaciones y objetivos
    
    - Inestabilidad y colapso alveolar en insuficiencia respiratoria aguda
    - Pérdida de control de la vía aérea
    - Alta demanda metabólica
    
    Objetivos de la asistencia respiratoria
    
    - Mantener intercambio de gases
    - Disminuir trabajo respiratorio
    - Minimizar el riesgo de complicaciones por VM
    
    **Fisiología de la Ventilación mecánica**
    
    - El ventilador produce presión positiva en la vía aérea
    - A la presión positiva se le opone otra presión de diferente magnitud
        - **La resistencia ofrecida por el árbol traqueobronquial (normal menor o igual a 5 cmH2O)**
        - **Fuerza de retracción elástica** del parénquima pulmonar y pared torácica
            - Impedancia: resistencia y elastancia
    - Ecuación del movimiento: presión para insuflar pulmonar (Pt) depende de las propiedades resistivas (Pr) y elásticas del sistema respiratorio (Pe) **Pt= Pr+Pe**
        - Propiedades **resistivas**: Presión de resistencia/flujo
            - Presión trans vía aérea
        - Distensibilidad: Volumen/presión de **elastancia o conformidad pulmonar** (facilidad con la que se estiran y expanden para dar lugar a un cambio en el volumen o la presión)
            - **Presión transtorácica: gradiente de presión entre espacio alveolar y superficie corporal, requerida para vencer retroceso elástico**
    
    [](https://lh7-us.googleusercontent.com/Ci_5vZFQ9tk16NJDa0UWu7-lko05Nc4c4cULSHxEt4ByDE9-hCDGi3uWjl6sJUQGts4BTDrW6VaZOhTSUbo6GIeVg-y9G1nEZEkHNy4mNJ6oQFcGyi_j9JoWj4jrruw7pMdkJH47zxbxcqA9hR4Azw)
    
    [](https://lh7-us.googleusercontent.com/pEe3R14HjbRHpWjqbC3Lkd9JiIsAd-JEhiBlF4ot5RHDvZDs39ClRgVGCND1LHnjaSgQdWIT7v8qT8gh4iMcBUAJ3MIkIOMV6scn-e0Wf3wetPLG3QRNjryZP92L3L7WJJIkVugw7834BjXxEKyf7g)
    
    **Efectos adversos de la ventilación mecánica**
    
    - Respiratorios
        - Ventilación a presión positiva en zonas inferiores es peor que zonas superiores, por lo tanto hay menos correlación de la ventilación con la perfusión.
    - Corazón - pulmón
        - Aumento de presión intratorácica se transmite a través de la AD e **impide el retorno venoso,** por lo tanto, disminuye precarga de VD y por consecuencia la precarga de VI, disminuye VTDVI y baja el gasto cardiaco
        - Un PEEP demasiado alto puede producir sobredistensión alveolar y compresión de capilares adyacentes lo que aumenta la resistencia al flujo sanguíneo pulmonar, es decir aumenta la postcarga del VD.
    - Renal
        - **Reduce excreción de sodio y agua por disminución del gasto cardiaco y PAM**, lo que aumenta actividad simpática y aumento de ADH, con un SRAA aumentado
        - Como la AD no está distendida, se reduce la cantidad de péptido natriurético
    - Hígado
        - Baja gasto cardiaco y baja el flujo hepático
        - Congestión venosa hepática por aumento de presión en AD
    - Cerebrales
        - Aumento de presión de AD impide buen retorno venoso con incremento en la presión intracraneal por aumento de la presión venosa yugular y reducción del retorno venoso.
    - Digestivo
        - Riesgo de úlcera y hemorragia digestiva al aumentar la resistencia esplácnica
    
    **Modos de ventilación**
    
    - Es la forma como se programa un ventilador para funcionar
    - Se clasifican según
        - Patrón respiratorio (variable de control principal de la frecuencia respiratoria)
            - Controlado por volumen (Vc y flujo están prefijados)
            - Controlado por presión (onda de presión prefijada)
    
    Estos pueden clasificarse según hay respiraciones espontáneas o mandatorias.
    
    Ventilación mandatoria continua
    
    Ventilación espontánea continua
    
    Ventilación mandatoria intermitente
    
    - Tipo de control (punto de ajuste, servo o control administrativo), habitualmente en un circuito cerrado
    - Estrategia de control específica (variables de fase y lógica de funcionamiento)
    
    ***Variables de control***
    
    *Son solo 3, un ventilador solo puede controlar una de estas a la vez, siendo la variable independiente (de control), mientras que el resto son dependientes de esta (condicionales).*
    
    - *Presión*
    - *Volumen*
    - *Flujo*
    
    ***Fases de la ventilación mecánica***
    
    *Una respiración o ciclo ventilatorio consta de 4 fases:*
    
    - *Inicio de la inspiración (trigger)*
    - *Inspiración*
    - *Final de la inspiración*
    - *Espiración*
    
    ***Variable de trigger (activación):** la que causa el comienzo de la inspiración, por la máquina o por el paciente. Si es por la máquina, la variable trigger será el tiempo, si es por el paciente, la variable puede ser la presión, el volumen o el flujo.*
    
    - *Trigger de tiempo*
    - *Trigger del paciente*
    
    ***Variables de límite***
    
    *La presión, volumen y flujo que se alcanza en forma prefijada antes de que finalice la inspiración, pero no hacen que termine.*
    
    ***Variables de ciclado***
    
    *La inspiración pasa a espiración cuando se alcanza el nivel prefijado de presión, volumen o flujo.*
    
    - *Ciclado por presión: ventilador entrega flujo hasta alcanzar presión preseleccionada.*
    - *Ciclado por volumen: entrega flujo hasta el volumen seleccionado.*
    - *Ciclado por flujo: entrega flujo hasta que se alcanza el seleccionado.*
    - *Ciclado de tiempo: “tiempo de flujo inspiratorio”*
    - *Ciclado por paciente: Para que el ciclado sea por el paciente este tiene que ser capaz de cambiar el tiempo inspiratorio, ya sea por esfuerzo inspiratorio o espiratorio.*
    
    ***Variable de referencia (basal)***
    
    *Variable controlada durante espiración, si se fija a una presión mayor a la atmosférica se denomina presión positiva al final de la espiración (PEEP). Eleva la capacidad residual funcional para mejorar oxigenación y prevenir colapso alveolar.*
    
    ***Variables condicionales***
    
    *Son aquellos que el circuito de control de ventilador emplea para tomar decisiones.*
    
    Tipos
    
    - **Ventilación asistida-controlada (A/C)**
        - Controlada: todas las ventilaciones dirigidas por el ventilador
            - Se debe establecer una frecuencia respiratoria
        - Asistidas: asiste las ventilaciones iniciadas por el paciente
        - Puede ser controlada por volumen o presión
    
    [](https://lh7-us.googleusercontent.com/5WbQpszfrxCP9c_NDXtsi7pkdU40Q_RrR0ux1jcnBIczw43bUTnHD9Z133ozh6Vv449dWgqhva1P2URcIEcK5BtBSYyz5EW4VsEhA3H8kiA96iLwaxJvA6Ax3lhxZtyh1L8iwZB7v38BBM48-PUs6w)
    
    *A. Ventilación por control de volumen. B. Ventilación por control de presión*
    
    - **Ventilación mecánica intermitentemente sincronizada (SIMV)**
        - Combina la ventilación asistida-controlada con la ventilación espontánea, el ventilador proporciona ciclos ventilatorios asistidos (mandatorios) controlados por volumen o presión, a una frecuencia predeteminada, pero permite que se intercalen ciclos espontáneos entre los mandatorios sincronizándolos donde solo aporta presión de soporte o CPAP.
        - Tiene la ventaja de tener menos efectos cardiovasculares adversos, mantiene una ventilación minuto mínima.
    - Ventilación con presión de soporte (PSV)
        - Cada esfuerzo ventilatorio es asistido por el ventilador hasta un límite programado de presión inspiratoria
        - Recibe PEEP
        - Flujo inspirado, FR y volumen tidal son dependientes del paciente
    - Presión positiva continua en la vía aérea (CPAP)
        - Depende del paciente
        - Mantiene presión base
    
    [](https://lh7-us.googleusercontent.com/B9NkzoHqInkxoqOcANG1jtzNo5LZCA2tDHZHox_5IcqzFrVlcV0wCBckeyjvofvHnIU2eLWpR4zQb2-ksDKFSsiv7PZWgnqDjuT528sAtca2TH8Q3a-7OeX9_JIt_upmLxONvN-ouEiQ064KI3kAYw)
    
    [](https://lh7-us.googleusercontent.com/OYOfrCrLsnKNgIpsgAK2Y0ftbpbuG0EYQZtgzdVVeK02lmlaIuHY5Z2lkYrJpmsBexLx066zoZ8A5hbV15GAMKVXDAL99URUTWOHEfAsadB5Fr4Wv60LeFRUAsNyYrotZg8tNdB2tisYCUfuryEflQ)
    
    **Programación básica del ventilador mecánico**
    
    - Elección de modalidad ventilatoria
    - Frecuencia respiratoria
        - 10 a 12
            - Iniciar con 20 a 25 por minuto para evitar autoPEEP
        - Relación inspiración:espiración 1:2
            - Mínima 1:1,5
            - Inspiracuión al menos 0,75 a 1 seg
            - Aumentar en obstrucciones 1:3 - 1:4
    - Sensibilidad o trigger
        - Valor umbral para detectar esfuerzo inspiratorio (gatillado)
        - Presión -0,5 a 2 cms H2O
        - Flujo 1 a 5 L/min
    - Presión positiva al final de la espiración (PEEP)
        - Mínimo 5 cmH2O
        - Podría hacerse una maniobra de reclutamiento unos 10 a 15 antes evitando presión peak >40
    - Volumen tidal o volumen corriente
        - **6 a 8 ml/kg de peso ideal**
    - Flujo inspiratorio
        - 50 a 60 L/min
    - FiO2
        - Objetivo 88-95%
    
    **Bibliografía**
    
    - HarvardX - Ventilación mecánica en COVID19 - 2020
    - Kilickaya O, Gajic O. Initial ventilator settings for critically ill patients. Critical Care 2013;17: 123
- Ventilación mecánica no invasiva
    
    Efectos sobre la función respiratoria y cardiaca
    
    - Aporte de soporte ventilatorio inspiratorio hace que se descarguen los músculos respiratorios, mejora el patrón respiratorio, disminuye la FR, aumenta el volumen circulante, mejora actividad diafragmática y trabajo respiratorio
    - Mejora intercambio gaseoso
    - Aumenta la capacidad residual funcional, reduce el shunt intrapulmonar, mejora la distensibilidad y oxigenación
    - Evita el “desreclutamiento” y recluta nuevas antes colapsadas con PEEP
    
    Indicaciones
    
    - EPOC (pH <7,35 con PaCO2 >45), pero más acidótico, más falla
    - EPA cardiogénico
    - IRA con Pa/FiO2 250-200 o pH 7,25 - 7,35
        - FR 25 a 30 resp/min
        - Uso de musculatura accesoria
        - Estabilidad hemodinámica
        - Tos eficaz, sin secreciones bronquiales
        - Necesidad no prolongada de soporte ventilatorio
        - Criterios clínicos y gasométricos en a 1 a 2 horas
        - Tiene buen valor para reducir la intubación, pero no tan claro para impedir la progresión de insuficiencia respiratoria
    - Se ha utilizado en weaning, beneficio sería en relación a prevenir IRA
    - Candidatos controvertidos
        - SDRA, neumonía
        - IRA grave con PaFi < 200 o PH < 7,25 (idealmente no)
        - Graves, con APACHE 29 o más o SAPSII >34
        - Inestabilidad hemodinámica
        - Agitación o disminución del nivel de alerta
        - Tos ineficaz
    
    Contraindicaciones
    
    - Paro o inestabilidad hemodinámica
    - Isquemia miocárdica aguda
    - Arritmia grave
    - Apnea o depresión respiratoria grave
    - Obstrucción de VAS
    - Broncorrea excesiva o alto riesgo de aspiración
    - Traumatismo o cirugía facial reciente
    - Agitación psicomotriz grave
    - Encefalopatía grave no hipercárbica
    - HDA
    - Cirugía digestiva alta reciente
    - Obstrucción intestinal
    - Neumotórax no drenado
    
    Aplicación de la VMNI
    
    - Ventilador
        - Idealmente de turbina para humidificar el gas, con adecuada compensación de fugas >60 L/min, que permite monitorizar sincronía paciente/ventilador con curvas gráficas de presión, flujo y volumen.
        - Que evite reinhalación
        - Que permite ajuste de FiO2
        - Posibilidad de ajustar trigger inspiratorio y ciclado
    - Interfase
        - Nasal
            - Mejor tolerada, permite hablar, comer, expectorar, menor espacio muerto, fácil de fijar, menos riesgo de aspiración
            - Riesgo de fugas bucales, más resistencia al flujo, presión dorso, sequedad de boca
            - Se prefiere en IRA más leve
        - Oronasal
            - IRA moderada, grave. Para mayores niveles de presión y compensación de fugas
            - Riesgo de aspiración
            - Imposibilidad de comer
        - Mascarilla facial completa
            - Menor riesgo de úlcera
            - Mayor espacio muerto, sequedad ocular
        - Helmet
            - Para algunos más cómoda, menos riesgo de úlceras faciales
            - Reinhalación CO2, peor sincronía, riesgo de asfixia si falla ventilador
    
    [](https://lh7-us.googleusercontent.com/aQoi83G3qyXFuBDXDBKtIX55fiy1gHO2A8UtNyeOvWqL9ZPd3ruLZGmUGNI0n1B6ds1VSm544_qH-IHTVUvny-t5WK66woZ8EMknEZwHuV7unzVoEXRqGcHuobUYyu83a4ilA4shNNex9KvEzcWEJPw)
    
    - Modo ventilatorio
        - Controlada por presión es la más extendida y mejor tolerada en procesos agudos
            - El **modo independiente es la presión**, volumen depende de la presión programada
            - BIPAP (presión positiva en la vía aérea de doble nivel) el paciente respira espontáneo con una presión en 2 niveles
                - IPAP y EPAP
                    - La diferencia entre estos es presión soporte efectivo
                - Se divide en 3 modos
                    - ***S (espontáneo):*** la unidad cicla entre IPAP y EPAP siguiendo el ritmo respiratorio del paciente. Envía presión positiva solo si el paciente es capaz de hacer el trigger. El paciente siempre marca frecuencia respiratoria.
                    - **ST (espontáneo/timed):** si el paciente es incapaz de iniciar respiración en un tiempo predeterminado, la unidad ciclará a IPAP e iniciará respiración. La frecuencia será la del paciente o ventilador. el modo más usado.
                    - T (timed): unidad cilca entre IPAP y EPAP en base a frecuencia respiratoria programada en el respirador y la proporción de tiempo inspiratorio seleccionado
                    - PAV (presión asistida proporcional): ventilador genera volumen y presión en proporción al esfuerzo del paciente, facilitando un patrón ventilatorio adecuado a las demandas metabólicas.
            - CPAP no se considera un modo de VMNI propiamente dicho, ya que no aporta presión de soporte, solo presión positiva continua en la vía aérea a un único nivel, manteniendo presión estable durante el ciclo respiratorio.
                - Reduce shunt intrapulmonar mediante reclutamiento alveolar, mejora capacidad residual y la distensibilidad pulmonar, puede contrarrestar el autoPEEP
    
    [](https://lh7-us.googleusercontent.com/5XaVVw8LMnQ8vvL0_zG8NTlqHb2XqhHkmBJab0ykTAyZN3sCzIEWk0-1r76GBeRgfWysWYcxNADHevDYtpCAeCZLzjQ7wvvtlHMUvx4XR-RdqssyeSBvONi8zDPF8tNNDPCAK9QQ3l8sp5SsQ9T9rAc)
    
    - Inicio
        - **Controlado por presión BiPAP**
            - Se inicia con niveles de IPAP y EPAP (PEEP) bajos, aumentando progresivamente hasta el objetivo
            - **IPAP 6-8 cmH2O**
            - **EPAP 3 cmH2O**
            - **Rampa 50%**
            - **Trigger 3 L/seg**
            - **Sensibilidad espiratoria 25% del FIM**
            - **4 a 8 resp/min de seguridad (mandatorias)**
    
    [](https://lh7-us.googleusercontent.com/5BDzdzCEsyWdIIxbnLOv8GUPzYqDZNMGbf7YTgsnglCCGYdvgYyaJCwtNiS7q_CXUy7osZ28K3O6Gp2duYNN2Puy5sHS3TTo7vB4vc7a3_3glWoD3E42oFIY8okKgugtXtUBmlUf8R_yhZmqpoiTzEM)
    
    - Ajustes posteriores
        - Incrementos de **IPAP 2 a 4 cmH2O hasta VC 6-10 ml/kg y FR <25/min** (suele conseguirse con 10 a 20 cmH2O, pero a mayor presión hay más fugas e incomodidad, debe evitarse pasar de 25 o 30 por apertura del esfínter esofágico inferior y distensión gástrica)
        - EPAP regular de 2 a 2 hasta 5-10 cmH2O para **SatO2 >90%** con la menor FiO2 posible
        - Evaluando auto PEEP
        - Ajustar trigger
        - Ajustar rampa
        - Ajustar sensibilidad respiratoria
    - Ajustes intermedios
        - Hipoxemia, aumentar EPAP (máximo 12) hasta SatO2 >90%
        - Hipercapnia: aumentar IPAP para pH normal (máximo 20)
        - Desadaptación
            - Contracción esternocleido: subir IPAP
            - Contracción abdomen: Bajar IPAP
            - Inspiraciones fallidas: Subir EPAP (para compensar auto-PEEP) máximo 8
            - Si VC bajo: ajustar mascarilla, evitar presión pico >30
    - **Evaluación en 1 hora**
        - Evaluación clínica
        - Control de fugas
        - Sincronía paciente/ventilador
        - Gasométrica
        - Complicaciones de VMNI
            - Eritema facial
            - Ulceraciones
            - Conjuntivitis
            - Distensión gástrica
            - claustrofobia
            - Sequedad de mucosas
    
    **Soporte ventilatorio a largo plazo**
    
    - Síntomas de hipoventilación nocturna (cefalea matutina, dificultad para conciliar el sueño, despertares con disnea, somnolencia diurna)
    - Criterios fisiológicos
        - CO2 > 55
        - CO2 50 - 54 y desaturaciones nocturnas (<88% por más de 5 minutos)
        - CO2 50 - 54 e ingresos repetidos (>2 al año) por insuficiencia respiratoria hipercápnica
    
    Tipos de ventilador
    
    - Dependientes del VM como neuromusculares o de UCI que no se pueden desconectar. Se debe emplear volumétricos, con alarmas y bateria interna.
        - Volumétricos introducen un volumen prefijado en la tubuladura y vía aérea, con mecanismos de seguridad. No aportan presión espiratoria.
    - No dependientes, durante el sueño, con soporte de presión
    
    Bibliografía
    
    Bourke S, et al. Lancet Resp Med 2018; 6: 935-47
    
    Del Castillo Otero D. SEPAR.
    
- Monitorización
    
    **MONITORIZACIÓN DE LA VENTILACIÓN MECÁNICA E**
    
    **INTERACCIÓN PACIENTE - VENTILADOR**
    
    Mediciones
    
    - Presión plateau
    - Distensibilidad estática
    - Resistencia de vía aérea
    - Auto PEEP
    
    Pausas
    
    - Inspiratoria
        - Tiempo en que las válvulas se cierran al final de la inspiración
        - Permite medir **presión plateau o meseta:** presión necesaria para mantener insuflación pulmonar en ausencia de flujo aéreo (Pplat). **Equivalente clínico de la presión alveolar. Se espera que sea bajo 25 cmH2O.**
    - Espiratoria
        - válvulas cerradas al final de la espiración
        - Permite medir autoPEEP o PEEPi, es decir presión positiva alveolar al final de la espiración
    
    Variables
    
    - **Presión inspiratoria Pico (PIP o Ppeak)**
        - Máxima presión en las vías aéreas al final de la fase inspiratoria.
        - Determinada por la resistencia de vía aérea como elastancia
        - ideal es presión **pico bajo 35 cm H2O**
    - **Presión plateau o meseta (PPlat)**
        - Presión que se mantiene el alveolo durante fase plateau, donde hay cese del flujo de aire
        - Debe mantenerse bajo **25 cm H20**
    - **Presión positiva al final de la espiración (PEEP)**
        - Ayuda a prevenir la atelectasia, al no permitir el colapso alveolar
    - **Driving pressure o presión de distensión**
        - Plateau - PEEP
        - Indicador de **presión de distensión alveolar**
            - Medida objetiva: presión transpulmonar a partir de medida de presión esofágica (diferencia entre presión alveolar y pleural)
        - **Objetivo bajo 15 cmH2O**.
    
    [](https://lh7-us.googleusercontent.com/AJEGULfSNuuRs0Oc3BTHHMP5FE41Y_PsQdCndjiD_oG4-T4Syef3q2Vawbm8OsiBVrVca3tBJBT-_OdB9xWO6SyoB4_Q5X72PS5T0GLFBUi44yrLZ81ulPk6PYjChKP2vVLoVpGslYKsRdEGRIGukw)
    
    - **Distensibilidad o compliance**
        - Relación entre **cambio de volumen y el incremento de presión** necesario para producirlo.
        - Compliance estática= Vt / driving pressure
            - Inversa matemática es la elastancia
        - Distensibilidad de pulmonares y pared torácica
        - El paciente no debe gatillar para medirla porque interviene contracción muscular.
        - Valor normal **50 a 80 ml/cmH2O**
            - Aumenta en enfisema
            - Baja den SDRA donde puede llegar a ser menor a 25 ml/cmH20
        - Medición ideal con catéter esofágico
    - **Auto PEEP o PEEP intrínseco**
        - **Estimación de la presión alveolar al final de la espiración** en flujo cero de pausa espiratoria
        - Si hay flujo cero y existe flujo espiratorio quiere decir que la presión alveolar es positiva o al nivel de la PEEP extrínseca
        - Puede ser por tiempo espiratorio corto o cierre precoz de vía aérea por colapso u obstrucción. Otras causas puede ser VC alto, FR alto sin tiempo de espiración suficiente, relación inspiración/espiración elevada (más inspiración)
        - autoPEEP aumenta trabajo respiratorio, hipotensión, barotrauma
    
    **INTERACCIÓN PACIENTE-VENTILADOR**
    
    - Cuando se inicia VM se crea un nuevo sistema: paciente, interfase (TOT - circuito) - Ventilador
    - Componentes unidos en serie
    - Buen ajuste depende de consecución de objetivos de la ventilación, tolerancia, comodidad y la ausencia de complicaciones
    
    Factores determinantes de la interacción paciente-ventilador
    
    - Para que exista un buen acoplamiento se necesita
        - Reconocimiento de la inspiración: Inicio de actividad inspiratoria del paciente debe provocar de inmediato el suministro de gas por el VM
        - Presurización adecuada: la provisión de flujo debe ser adecuada para las necesidades de la ventilación del enfermo, valorando pH y PaCO2
        - Reconocimiento de la espiración: el ceso de la inspiración o ciclado debe coincidir con el corte de la insuflación, sin retrasos, por el aparato
    - Factores relacionados con el ventilador
        - Calidad del **generador de flujo** (capacidad de presurización)
            - Pico de flujo debe superar al del paciente
            - En presión soporte, debe prooporcionar un flujo desacelerante y elevado, al menos 60 L/min a 20 cmH2O
            - Que aumente linealmente cuando aumente la presión de soporte
            - Con velocidad de presurización (rampa, pendiente o rise time) graduable
            - Importante que presión sea constante durante inspiración, sin oscilaciones en la meseta, con ascenso y descenso sin improntas ni “rebotes”
    
    [](https://lh7-us.googleusercontent.com/j9_LX7s8j-UZ1s_dAmE4q6Eb_6B-oKCwZnngM6yZKLO9wcsdJ9GoyUvU9K2FXpbvzLkZNn8qH8G6kkMipPwGu0fXQXGUp96ZskUhKjIMyEBLulwej8ZVknXcHrSH65S1SweTmp_yy3Ak8IQ_9O9PeQ)
    
    - Respuesta de variables de fase (**trigger** y ciclado)
        - Debe ser rápido y sensible
        - Siempre debe ser inferior a 100 ms (ideal bajo 50 ms)
    - Ciclado
        - Es controlado por el operador en los controlados, pero con soporte parcial debe coincidir con el cese de la actividad diafragmática del paciente
        - En PS el VM supone que finaliza ventilación cuando cesa el flujo o baja de 5 a 15 L/min o 12 a 25% del flujo máximo, se puede regular con trigger espiratorio
    
    [](https://lh7-us.googleusercontent.com/FK3fSfMC-x6nAo-ifx2Hvgi0Z8vYPmSlVsIsFndxXTMsGJRUtc1uNxjssUOsjPh7MGc-Wv3nZHJ2P_8eAfynnYfz2NRX5Ny9u0ln2Vg7R7gSA7Ku5dDaPoQYZwqWLqhXK1xtLp6GrRxOMY6B-nr-dg)
    
    - Interfase
    - Factores relacionados con el paciente
        - Demanda ventilatoria
            - Flujo debe ser mayor al del paciente, pero puede generar intolerancia si es demasiado alto
        - Patrón respiratorio
            - Los pacientes con IRA tienen patrón de Vc bajo y FR rápida
            - El impulso neuromuscular central, medido por la presión de oclusión de vía aérea en los primeros 100 ms o **P0,1 puede superar los 10 cmH20 cuando su valor normal es bajo 2**.
                - Produce vaciado pulmonar incompleto, hiperinsuflación dinámica y auto-PEEP (PEEPi)
                - Hace más dificil para el paciente el disparo del ventilador
        - Función muscular
            - Si no funcionan bien músculos no puede generar el trigger
    
    Concepto y consecuencias de la desadaptación de la ventilación mecánica
    
    - Desadaptación: concepto que describe falta de sincronía entre el paciente y el ventilador
    - Complicaciones que determinar la intolerancia y fracaso de VM
        - Taquipnea, acorta el tiempo espiratorio y produce autoPEEP
        - Hiperinsuflación dinámica, estira el diafragma y no se contrae adecuadamente y se fatiga
        - AutoPEEP disminuye precarga
        - Fatiga de músculos respiratorios
    
    [](https://lh7-us.googleusercontent.com/4MdrM3MpF5AFFHKTifwLD41Jf8wXP3q9I94hrvnxt7tn1iYf8hePI2_Hne8_PThO43Y4PfmaaD4036gpN-LgOYZ9fkiams7byEoK_bR0j8RhbOkAATyUZztsQ_KIxGV60cnsw3uqvI5PpnlBlhv5TQ)
    
    Manejo clínico de la desadaptación
    
    - Necesita una triple sincronía
        - **Trigger**
            - Causas
                - Baja sensibilidad
                    - Mal ajuste del trigger
                    - Insuficiencia impulso central o debilidad muscular
                    - AutoPEEP
                        - TTO:
                            - Aumentar sensibilidad
                            - Cambiar trigger de flujo
                            - Bajar PS o Vt para reducir hiperinsuflación
                            - Broncodilatadores para autoPEEP
                            - Añadir PEEP externa
                - Excesiva sensibilidad
                    - Autodisparo
                        - TTO:
                            - Bajar sensibilidad
                            - Revisar circuitos
                            - Comprobar fugas
        - Flujo
            - Causas
                - Flujo insuficiente (taquipnea, fascie disneica)
                    - TTO
                        - Aumentar PS o Vm
                        - Rampa más rápida
                        - Disminuir fiebre, ansiedad, analgesia, sedar
                - Flujo excesivo (FR baja, Vt excesivo)
                    - TTO
                        - Bajar PS o Vt
                        - Evitar hiperinsuflación
        - Ciclado
            - Ciclado precoz (inspiraciones muy largas)
                - TTO:
                    - Subir PS
                    - Incrementar tiempo inspiratorio?
            - Ciclo tardío
                - TTO
                    - Variar el umbral de ciclado
                    - Evitar fugas
                    - Disminuir resistencia de flujo aéreo
                    - Limitar tiempo inspiratorio
    - Debe descartarse
        - Falla de la vía aérea
        - Complicación respiratoria
        - Ineficacia de VMI
    
    **ANÁLISIS DE FORMA DE ONDA - ASINCRONÍA**
    
    - Volumen, presión y flujo v/s tiempo
    - Modo A/C por volumen
        - Flujo constante, recto o lineal
        - Cuando el volumen es alcanzado, la inspiración debiese terminar
    
    [](https://lh7-us.googleusercontent.com/UzWAV4GOGgV7kmmJwD40SAdA-VHHZi_RM-R0nDZEwW-6j6Q0XqT_xW0ogVMsSmOc0nQHJuJkTIzsB7FYObZ9vWxAJ2JxaomXssWZO4UaZbVAsLVL2Jas_A9pHiKHacejr6w3-MX8AUHOu6HUc4ILmQ)
    
    - Modo A/C por presión
        - Presión es constante, tiempo de elevación o de rampa de presurización es el tiempo que toma alcanzar la presión provista durante la inspiración
        - El flujo sube rápido hasta alcanzar la presión y luego se disminuye lentamente para mantener la presión
    
    [](https://lh7-us.googleusercontent.com/GTu1m2Zh-tz5Ik-qL253gq1PijIASPI08hTkihHX-84yXpq1_NJ-5gwDigeTsmjPXlP-9ngWypOB98MDtJAv9UgyDZnfMcK3VrYzbvXKX5Ybuw0A_uA8TwzqNtDyna134aOXNbbZS0GbjVA0w6hhbQ)
    
    Cuando el pacientes hace esfuerzo
    
    - Hay cambios en los patrones
    - Altera el parámetro no controlado
        - En **volumen** control, cambia la **presión**
            - Cuando hay un esfuerzo excesivo, se puede provocar una forma de cuchara porque el paciente está haciendo presión negativa
                - Se puede medir en la presión de oclusión, que estará alta
    
    [](https://lh7-us.googleusercontent.com/NOEuZ3ldNmPM_cgiCB2pLoiiflvtKY6X2qSe5ZfYsDD-7FucanBjvIYjgw41DH-O8rGBz7Lo3exHUzZrIyvfqtUU5QR0bxykuUcqKpuCI8h2JqLsOsfzyaZyRQrMjkE6iZ92Lt-fbaTeXhN1Ftnn-w)
    
    - En **presión** control, cambia el **flujo**
        - Cuando hay un esfuerzo excesivo se cambia la onda de flujo, se hace más redonda que lo normal (habitualmente hace un pico)
            - También cambia la caída de la onda
            - También aumenta P0.1
    
    [](https://lh7-us.googleusercontent.com/oivb2DNam09U-KpvQkELhYlUSyDl98COU_Nhq7uG4HCjBfasWvrC_IPnPoaMQN798FHB8Mwe3tBukdx8iQvukaI3lCufO7veOlrvQE_K-DnqkDYOifyGK91krqdSlmw8uA__ZLxgqqFEWtxuiaR9mQ)
    
    - 
    
    **Asincronía**
    
    - ***Tiempo neurológico y del ventilador están desincronizados***
    - Inanición de flujo ***(el ventilador no satisface la demanda del paciente)***
    - El paciente ***no puede cumplir con el criterio de activación***
    - En A/C volumen se verá el esfuerzo del paciente en muescas negativas de la onda de presión
        - Es importante monitorear la presión de oclusión o p0.1 para asegurarse que no sea demasiado alta
    - El A/C presión, el esfuerzo del paciente debe cambiar la onda de flujo
        - Verificar si el flujo llega a 0, cuando la presión llega a 0 durante la inspiración o si hay una atenuación del flujo espiratorio pico durante la exhalación para revisar que el paciente no esté experimentando asincronía
    
    **DAÑO INDUCIDO POR VENTILACIÓN MECÁNICA**
    
    **EVALUACIÓN DIARIA DEL PACIENTE EN VENTILACIÓN MECÁNICA**
    
    - Sistema neurológico
        - Examen neurológico
        - Sedación - RASS
        - Analgesia - Medicamentos
        - Delirio - CAM
        - Modo ventilatorio
        - Sincronía
        - Habilidad de liberar
    - Cardiovascular
        - Hipotensión, Meta PAM 65 (HTA crónica podría ser 75)
        - Monitoreo ECG
        - Tipo de shock
        - Estado de volumen
    - Pulmonar
        - Modo de ventilación
            - A/C V: verificar peak y plateau
            - A/C P y PS: verificar volumen tidal pico y ventilación/minuto
        - Volumen tidal
        - Presión
        - Presión plateau (<27 o <30 en SDRA)
        - Presión de distensión
        - PEEP
        - Tasa respiratoria
        - FiO2
        - PaO2/FiO2
        - Tipo de falla respiratoria
    - Gases arteriales
        - Evaluar pH
        - Verificar acides o alcalinidad
        - Respiratorio o metabólico
        - Tiene factor de corrección
        - Anión gap
    - Renal
        - Buscar balance negativo
        - Medir creatinina y diuresis
    - Gastrointestinal/nutrición
        - Hígado
    - Hematológico
        - Hemoglobina, plaquetas, coagulación
        - Evaluar sangrados
    - Infeccioso
        - GB
        - Temperatura
        - Cultivos
        - Procalcitonina si es necesaria
        - Imágenes de ser necesario
    - Endocrino
        - Glicemia
        - Control de tiroides
    - Profilaxis de NAVM
        - Lávese las manos
        - Elevar cabecera
        - Técnica aséptica al succionar y hacerlo lo menos posible con baja presión
        - Hiperoxigenar antes y despúes de succionar
        - Haga interrupciones en sedación
        - Evalue extubnación
        - Profilaxis de TVP
    - Alarmas del ventilador
        - Ventilación/minuto
        - Presión pico
        - Presión plateau
        - PEEP
    
    *Guía del pase de visita de terapia intensiva*
    
    - ¿Está empeorando, mejor o igual?
    - Enfocarse en 1 a 4 problemas principales
    
    *“El Señor P. está en el día #7 de terapia intensiva, y la verdad, no está mejorando. Su principal problema es el SDRA relacionado con el COVID-19, tiene una neumonía superpuesta, así como lesión aguda de los riñones*
    
    - Datos - evaluación - plan
    
    Bibliografía
    
    HarvardX - Ventilación mecánica en COVID19 - 2020
    
- Ventilación de patologías obstructivas
    
    **VENTILACIÓN MECÁNICA - Patologías obstructivas**
    
    ***Asma***
    
    - Constricción de músculo liso bronquial por broncoespasmo
    - Atrapamiento aéreo
    - Evitar autoPEEP e instabilidad hemodinámica
    - Luego de intubados deben seguir usando broncodilatadores, corticoides, magnesia, sedación profunda y quizás bloqueo neuromuscular al principio para relajar la musculatura de la pared torácica y ganar el control de la situación.
        - Bloqueo neuromuscular solo sirve en músculos esqueléticos
    - **Broncoconstricción**
        - puede provocar aumento de presión pico pese a Vt bajo
        - Cuando aumenta la resistencia de vía aérea, sube mucho presión pico en relación al plateau (hay un gran delta)
    - **Maniobras para aumentar el tiempo espiratorio**
        - **Disminuir la frecuencia respiratoria**
            - Más efectivo
            - <20. Idealmente cercana a 10
        - Disminuir la relación inspiración: espiración
            - 1:3 o menor
        - Disminuir el tiempo inspiratorio
            
            [](https://lh7-us.googleusercontent.com/p21LY3dPW_Sr8tzm6olXpL_ZNxtjmsZq85mbm3jlGvyStozJEh2IiDsqDJnFnGdFGQ6rJ4xzD76-JNjk9NxYpt50pFSTdEVkDWinLj8vJvr_MIaZVVMlyoLpRzZJVBVavLzHUdcd4KceToi_mjJOfQ)
            
        - Aumentar flujo inspiratoria
    - Deben ventilarse con bajos volúmenes tidales 6-8 ml/Kg
    - Agregar PEPP de 5 cmH2O
    - Monitorización
        - En la curva de flujo, no regresa a la linea de base, el paciente está aun espirando cuando inicia el ciclo inspiratorio
        - Monitorear auto PEEP
        - Hipercapnia permisiva
            - Tolerar PaCO2 <30 y pH > 7,2 o 7,25
    
    ***EPOC***
    
    - Bronquitis crónica
        - Hipertrofia muscular
        - Aumento de mucosidad
        - Broncoconstricción
    - Enfisema
        - Destrucción parenquimatosa en alveolos
            - Disminuye superficie de intercambio gaseoso
        - Pequeñas vías aéreas pueden colapsar con la exhalación, atrapando aire
    - Manejo
        - Bipap puede ser mejor que la intubación
        - Ventilación mecánica con prioridad de que exhale (similar a Asma)
        - Aplicar PEEP para prevenir autoPEEP y que no colapse la vía aérea
        - 
            
            [](https://lh7-us.googleusercontent.com/T54AJCNwm6-c6DheIufb8y7Io1ef1bPLPOnyi_DeztBUBTCOdJanNQww3JmtWx1tFNlw7fwLn3E9Pd7wnj-LSU4FUKNKRatjGgWdmI48BroDZiIlnr1G67QIL0PEPu64p3zYTKVncKyugDFtGqObBw)
            
        - Saturación de oxígeno debe estar entre 88 a 92%
        - En casos extremos, con PEEP intrínseca muy aumentada y que no está exhalando casi nada, se podría sacar del ventilador unos segundos, comprimir el pecho y dejar que exhale
    
    Bibliografía
    
    - HarvardX
- Weaning
    - Proceso de liberar completamente al paciente crítico del soporte ventilatorio mecánico y del tubo. No se incluye la extubación postoperatoria.
    - 6 etapas del proceso de cuidado del paciente ventilado
        - Tratamiento de la insuficiencia respiratoria
        - Sospecha de que el destete puede ser posible
        - Evaluación de la preparación del destete
        - Prueba de respiración espontánea
        - Extubación
        - Posible reintubación
    - El proceso de destete es 40 a 50% de la VM
    - Éxito del destete: extubación y ausencia de apoyo ventilatorio por 48 horas posterior.
        - Si está con VMNI es “destete en curso”
    - Destete ha fracasado si:
        - Falla de la prueba de respiración espontánea
            - Taquipnea, taquicardia, hipertensión, hipotensión, hipoxemia, acidosis o arritmia
            - Agitación, inquietud, estado mental deprimido, diaforesis, evidencia de aumento de trabajo respiratorio
        - Reintubación y/o reanudación de la asistencia ventilatoria
        - Muerte dentro de 48 horas posteriores a extubación
    - Predictores de fracaso
        - Exceso de secreciones
        - PaCO2 >45 mmHg
        - Duración de ventilación mecánica >72 horas
        - Trastornos de las vías aéreas superiores
        - Intento fallido previo de destete
    - Clasificación según gravedad y duración del proceso:
        - Destete simple: pasan prueba de respiración espontánea y son extubados en el primer intento (69%, buen pronóstico, mortalidad uci 5%, hospitalaria 12%)
        - **Destete difícil:** hasta tres pruebas de respiración espontánea o un tiempo de **hasta 7 días** a partir de la primera prueba para lograr el éxito. (16%, 25% mortalidad UCI)
        - **Destete prolongado:** requieren más de 3 prueba de respiración espontánea o **más de 7 días** de destete después de primera prueba. (15%, mortalidad uci 25%).
    
    **Proceso de discontinuación**
    
    1. Tratamiento de la causa
    2. Sospecha clínica de la capacidad de desconexión
    3. Potencial de desconexión
        1. Debe haber una evaluación diaria del estado clínico, cardiovascular, respiratorio y mental. Se busca la condición cercana a la ideal para poder liberar al paciente del ventilador:
        2. Las condiciones ideales son (no siempre están presente todas, no están basadas en la evidencia):
            1. Clínicas: paciente **puede toser**, tiene escasas secreciones, no tiene fiebre (< 37,5° C), se ha resuelto la enfermedad causal o está en vía de hacerlo
            2. Respiratorias: ventilación espontánea (gatilla), **SatO2> 90% con FiO2< 40%, PaO2/FiO2> 150, PEEP bajo 8 cmH2O, Índice de oxigenación bajo 5. pH <7,3 PaCO2 cercano al basal**
            3. Estado mental: vigil, obedece órdenes simples, sin delirium o con delirium controlado
            4. Estado cardiovascular: Frecuencia cardiaca dentro de rango 50-120 lpm, presión sistólica entre 90 y 160 mmHg, **sin uso de vasopresores o en dosis bajas**
    4. **Prueba de Ventilación Espontánea (PVE**)
        1. Simula condiciones del paciente cuando esté ventilando sin tubo.
        2. Estima clínicamente si será capaz de tolerar los cambios que induce la pérdida de presión positiva en la función cardiopulmonar.
        3. Utilidad es disminuir los fracasos de desconexión.
        4. Métodos para realizar PVE: tubo T o presión de soporte
            1. ambos son similares en efectividad entre sí.
            2. El paciente se debe mantener **30 a 120 minutos** en la modalidad elegida para evaluar su tolerancia
            3. Tubo T: el sujeto queda expuesto a la presión ambiental, el problema de este sistema es que puede sobrecargar al paciente, pero se ha demostrado que los pacientes al extubar tienen mayor trabajo respiratorio que con tubo T. Se recomienda verificar que el tubo endotraqueal o el tubo T no estén obstruidos o acodados.
            4. Ventilación con presión de soporte (CPAP/PSV): este sistema puede sobre asistir al paciente sobretodo en pacientes con escasa reserva cardiopulmonar, en estos casos se preferiría el tubo T.
            5. No se incluye la ventilación en SIMV porque ha demostrado ser inferior en rendimiento.
        5. Predictores a realizar antes de la PVE para determinar la probabilidad de éxito, el rendimiento de cada uno de los índices es mala y algunos estudios han mostrado que no existirían diferencias significativas entre usarlos o no. En la práctica, los parámetros a evaluar que mejor predicen el éxito del retiro de ventilación mecánica son el **f/Vt** y **P0,1**.
            1. **f/Vt:** para medirlo se usa el **ventilómetro** (mide el volumen minuto directamente desde el tubo) y un reloj, se calcula la frecuencia respiratoria (ventilaciones/minuto) y se divide por el volumen corriente en litros. El **f/Vt debe ser menor a 105**, este tiene un OR 10,3 para extubación exitosa.
            2. **P0.1:** es un indicador sensible pero poco específico de la intensidad del estímulo neurológico hacia la musculatura periférica, refleja el “hambre de aire” que aún tiene el paciente. Se mide en la p**endiente de presión negativa que se genera durante los primeros 100 milisegundos de inspiración voluntaria en contra de una válvula inspiratoria cerrada.** En estos primeros milisegundos no existe conciencia voluntaria de estar inspirando contra un sistema cerrado, de tal modo, que entre mayor sea la pendiente, más negativos serán los valores de P 0.1 y más hambre de aire tendrá el paciente. Algunos estudios sugieren que valores **mayores a -6 cms de H2O son un buen predictor de éxito, al contrario de tener valores menores a -30 cms de H2O.**
    5. Potencial para extubación
        1. Si tiene potencial de extubación según la prueba de ventilación espontánea, se realiza la extubación.
        2. Succionar tubo y cavidad oral
        3. Los esteroides administrados antes de la extubación planeada (metilprednisolona o Dexametasona) comparados con placebo han demostrado una reducción significativa de edema laríngeo y reintubación, este efecto es más significativo cuando se usan 4 horas antes de extubar19.
    6. Reintubación
        1. Se considera fracaso de extubación (fracaso de desconexión) cuando debe insertarse nuevamente el tubo orotraqueal después de 48 horas de una prueba de ventilación espontánea exitosa.
        2. Normalmente se acepta que un 10 a 15% de los pacientes extubados se vuelva a reintubar a pesar de tener una prueba de ventilación espontánea satisfactoria, considerando que el 20% de los pacientes de los pacientes falla en su primera PVE, si esta no se realizara, un 30 a 35% de los pacientes extubados deberían reintubarse.
        3. Tradicionalmente se asume que la reintubación se asocia a mayor morbimortalidad de los pacientes, sin embargo, esta solo aumenta en aquellos que deben ser reintubados por falla respiratoria o insuficiencia cardiaca descompensada. Los que tienen obstrucción de la vía aérea superior o exceso de secreciones no cambian su pronóstico.
    
    Traqueostomía
    
    - La intubación translaríngea prolongada puede generar complicaciones como úlceras, estenosis, parálisis o traqueomalacia, adicionalmente, la mantención del tubo orotraqueal determina la necesidad de mayor sedación, incomodidad y mayores dificultades para movilizar al paciente19.
    - La traqueostomía permite prevenir las complicaciones laríngeas, resulta más cómoda para los pacientes, facilita el drenaje de secreciones y frecuentemente presenta una menor resistencia de vía aérea que los tubos endotraqueales.
    - Sin embargo, como procedimiento invasivo no está exenta de riesgos como infecciones, hemorragia del estoma, pneumomediastino o pneumotórax y riesgo vital por pérdida de vía aérea, pero estas complicaciones son infrecuentes y es un procedimiento relativamente seguro19.
    - Se indica en aquellos pacientes que van a necesitar **más de 2 semanas tubo orotraqueal** (esto es discutible y no hay evidencia suficiente para recomendar un punto de corte, otros autores hablan de 3 semanas), aunque realizarla antes en pacientes en los que se espera no pueda retirarse la ventilación mecánica antes de 2 semanas es aceptado, sobretodo en pacientes neuroquirúrgicos.