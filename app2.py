"""
Este script calcula el nivel de riesgo en cuatro componentes de la vida académica universitaria en la Universidad Tecnológica de Pereira:
    
    - Vida Académica
    - Familiar
    - Económico
    - Psicosocial 

El cálculo de los riesgos se basa en las respuestas a un formulario diseñado para capturar aspectos integrales de la persona (ver Anexo 1). 
Usando modelos de clasificación previamente entrenados con una población de referencia, el script clasifica el riesgo en cada componente 
en tres niveles: BAJO, MEDIO y ALTO.

Entradas:
    - Formulario: contiene las respuestas recopiladas de los estudiantes.

Salidas:
    - Tablas que muestran la clasificación de riesgo para cada componente en los niveles BAJO, MEDIO y ALTO.

Requisitos:
    - Modelos de clasificación previamente entrenados.
    - Formulario con el formato especificado en Anexo 1.

Uso:
    Una vez diligenciado el formulario, presionar el boton "Cargar datos" y posteriormente "Calcular puntaje"
"""

#----------------------------------------------------------------  LIBRERIAS    ------------------------------------------------------------------------------------------------------------
import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import OneHotEncoder
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.ensemble import RandomForestClassifier

import joblib
from io import StringIO
import time
#----------------------------------------------------------------  TITULO    ------------------------------------------------------------------------------------------------------------


st.title("CUESTIONARIO DE ALERTAS TEMPRANAS, INNTERVENCIÓN Y SEGUIMIENTO")
st.markdown("El cuestionario de alertas tempranas, intervención y Seguimiento, tiene como propósito identificar el nivel de riesgo de los estudiantes de pregrado en cuatro aspectos: académico, familar, económico y psicosocial; que puedan dificultar la permanencia del estudiante durante su proceso de formación en la Universidad Tecnológica de Pereira.")

# Variable de estado
if "cargar_datos_presionado" not in st.session_state:
    st.session_state.cargar_datos_presionado = False

if "calcular_puntaje_presionado" not in st.session_state:
    st.session_state.calcular_puntaje_presionado = False
#----------------------------------------------------------------  CASILLAS DE IDENTIFICACIÓN    ------------------------------------------------------------------------------------------------------------


Autorizacion_Datos = st.checkbox("¿Autoriza de manera libre, previa, expresa y voluntaria el tratamiento de datos personales a la Universidad Tecnológica de Pereira en concordancia con lo dispuesto en la Ley 1581 y el Decreto 1377 de 2013?")

nombre_completo = st.text_input("**Nombre y apellidos completos**",key="Nombre Completo")
#numero_documento = st.number_input("**Número de documento de identidad**", step=1, min_value=1)
numero_documento = st.text_input("**Número de documento de identidad**")

#----------------------------------------------------------------  PERFIL VOCACIONAL    ------------------------------------------------------------------------------------------------------------

st.subheader("PERFIL VOCACIONAL",divider=True)

# Selección de Preguntas perfil vocacional
vocacional = [
    st.radio("**¿Cuál de las siguientes opciones define mejor la razón por la que usted eligió el actual programa de estudios?**",
                        ["Conozco el programa, se ajusta con mis intereses, personalidad y habilidades.", "Conozco el programa, presenta una buena oferta laboral y puede representar estabilidad económica.",
                         "Es una alternativa de lo que realmente desearía estudiar.","Sin ser la carrera que quisiera estudiar es la única en la que mi familia me apoya.",
                         "Por sugerencia de amigos, familia y medios de comunicación sin tener claridad de qué es lo que realmente quiero estudiar."]),
    
    st.radio("**¿Qué tan bien conoce el plan de estudios del programa al cual ingresó?**",["Lo conozco detalladamente",
                                                                                                  "Lo conozco de manera superficial","No lo conozco"]),
    st.radio("**¿Con cuál de las siguientes afirmaciones está de acuerdo?**",
                        ["Me identifico con el perfil profesional de mi carrera y mi desempeño académico es bueno.","Me identifico con el perfil profesional de mi carrera y mi desempeño académico es regular.",
                         "No me identifico con el perfil profesional de mi carrera."]),
    st.radio("**¿Cuánto tiempo usualmente invierte por día para estudiar fuera del aula de clase?**",["4 o más horas",
                                                                                     "Entre 3 y 4 horas","Entre 2 y 3 horas","Entre 1 y 2 horas","Menos de 1 hora"]),

    st.radio("**En general, ¿cómo calificaría su desempeño durante su trayectoria académica?**",
                        ["Sobresaliente","Bueno","Regular","Deficiente","Muy deficiente"]),
    
    st.radio("**Antes de iniciar este semestre, ¿cuánto tiempo estuvo desvinculado como estudiante de una Institución Educativa?**",
                        ["Menos de 6 meses","6 meses a 1 año","1 año a 3 años","3 años o más"]),

]

#----------------------------------------------------------------  RAZONAMIENTO    ------------------------------------------------------------------------------------------------------------

st.subheader("TEXTO PARA LA SECCIÓN DE LECTOESCRITURA",divider=True)
st.markdown(
    """
    <p style="font-size:18x;font-weight:bold;">Lea el siguiente texto con mucha atención, más adelante se le harán algunas preguntas alrededor del mismo.</p>
    """, 
    unsafe_allow_html=True
)

# Texto para la selección de preguntas lecto escritura (Comprensión lectora)
texto = """
El jueves la señora Aura Ríos, estaba en el aeropuerto con su esposo Luis García, 
pues iban de viaje a celebrar su aniversario de bodas. Ellos habían comprado un vuelo 
desde Argentina hacia Puerto Rico. Al llegar al mostrador y pasar sus tiquetes se 
dieron cuenta que había un error y en realidad tenían como destino Perú. Aura al ver 
esto llamó de inmediato a Andrés, el agente de viajes que había realizado la reserva. 
Andrés le mencionó que había entendido que ellos iban a viajar a Perú y que se 
disculpaba por la equivocación. Debido al error de Andrés, la empresa de viajes 
decidió compensar a Aura y Luis obsequiando la estadía en uno de sus hoteles en Perú, 
puesto que el destino del viaje no se había podido modificar.
"""
st.write(texto)

# Selección preguntas razonamiento logico
texto = ''' **A continuación, se presenta una prueba de razonamiento lógico. En cada serie de figuras, falta una figura específica, 
la cual se encuentra entre las 5 opciones presentadas en la parte inferior.
Por favor, seleccione la opción que considere correcta.**
'''
st.write(texto)

st.subheader("**1.**",divider="rainbow")
st.image("imagenes/razonamiento1.png",use_column_width=True)
razonamiento = [st.radio("Seleccione la respuesta correcta 1:", ["1","2","3","4","5"])]

st.subheader("**2.**",divider="rainbow")
st.image("imagenes/razonamiento2.png",use_column_width=True)
razonamiento += [st.radio("Seleccione la respuesta correcta 2:", ["1","2","3","4","5"])]

st.subheader("**3.**",divider="rainbow")
st.image("imagenes/razonamiento3.png",use_column_width=True)
razonamiento += [st.radio("Seleccione la respuesta correcta 3:", ["1","2","3","4","5"])]


st.subheader("**4.**",divider="rainbow")
st.image("imagenes/razonamiento4.png",use_column_width=True)

razonamiento += [st.radio("Seleccione la respuesta correcta 4:", ["1","2","3","4","5"])]

st.subheader("**5.**",divider="rainbow")
st.image("imagenes/razonamiento5.png",use_column_width=True)
razonamiento += [st.radio("Seleccione la respuesta correcta 5:", ["1","2","3","4","5"])]

st.subheader("6.",divider="rainbow")
st.image("imagenes/razonamiento6.png",use_column_width=True)
razonamiento += [st.radio("Seleccione la respuesta correcta 6:", ["1","2","3","4","5"])]

#----------------------------------------------------------------  LECTOESCRITURA    ------------------------------------------------------------------------------------------------------------


st.subheader("COMPRESIÓN LECTORA",divider=True)
st.markdown(
    """
    <p style="font-size:18px;font-weight:bold;">Teniendo en cuenta la lectura presentada anteriormente, responda las siguientes preguntas:</p>
    """, 
    unsafe_allow_html=True
)
# selección preguntas comprensión lectora
lectora = [
    st.radio("**¿Qué día iban a viajar los personajes de la historia?**",
                     ["Lunes.","Jueves.","Martes.","Domingo."]),
    st.radio("**¿Con motivo de qué celebración iba a viajar esta pareja?**",["Luna de miel.","Aniversario de bodas.","Cumpleaños de ambos.","Vacaciones."]),
    st.radio("**¿Cuál era el nombre de la mujer que protagoniza la historia?**",["Andrea.","Alma.","Ana","Aura"]),
    st.radio("**¿Cuál era el nombre del hombre que protagoniza la historia?**",["Leonardo.","Lucas.","Luis.","Lorenzo."]),
    st.radio("**Inicialmente, ¿A qué país iban a viajar?**",["México.","Costa Rica.","Puerto Rico.","Guatemala."]),
    st.radio("**¿Cuál era el nombre del agente de viajes?**",["Andrés.","Armando.","Alberto.","Ninguno de los anteriores."]),
    st.radio("**Finalmente, ¿A qué país terminaron viajando?**",["Puerto Rico.","París.","Perú.","Ninguno de los anteriores."])
]


# Opciones de respuesta generales en el formulario
opciones1 = ["Sí","No"]
opciones2 = ["Sí","A veces","No"]
opciones3 = ["Buena","Regular","Mala"]
opciones4 = ["Frecuentemente","Algunas veces","Nunca"]
opciones5 = ["Nunca","Pocas veces","Algunas veces","A menudo","Siempre"]

st.markdown(
    """
    <p style="font-size:18px;font-weight:bold;">Con relación a sus técnicas de estudio responda las siguientes preguntas:</p>
    """, 
    unsafe_allow_html=True
)

lectora += [
    st.radio("**¿El lugar donde estudia cuenta con las condiciones adecuadas para estudiar? (iluminación, libre de ruido, suficiente espacio)**",opciones2),
    st.radio("**¿Encuentra motivación en las diferentes actividades que realiza a nivel académico?**",opciones2),
    st.radio("**¿Considera que las técnicas de estudio que utiliza son efectivas?**",opciones2),
    st.radio("**¿Le han diagnosticado alguna  dificultad de aprendizaje como dificultad para concentrarse, falta de atención, impulsividad, hiperactividad, dislexia o discalculia?**",opciones1)
]


#----------------------------------------------------------------  DIAGNOSTICO FAMILIAR    ------------------------------------------------------------------------------------------------------------

st.subheader("DIAGNÓSTICO FAMILIAR",divider=True)

#Selección preguntas dianóstico familiar
diagnostico = [
    st.radio("**¿Cuenta con una red de apoyo  (familiares, amigos o adultos cercanos) que le brinden ayuda a nivel emocional, social, económica o de salud?**",opciones1),
    st.radio("**¿Cómo definiría la relación con las personas que conviven con usted?**",
                         ["Tenemos muy buena relación.","Discutimos pocas veces y cuando lo hacemos solucionamos los problemas hablando y llegando a un acuerdo.",
                          "Apenas hablamos entre nosotros.","Discutimos algunas veces y no  llegamos a acuerdos.","Discutimos muchas veces sin llegar a acuerdos."]),
    st.radio("Comunicación",opciones3),
    st.radio("Expresión de afecto entre los miembros de la familia",opciones3),
    st.radio("Afrontamiento de problemas familiares",opciones3),
    st.radio("Establecimiento de normas en el contexto familiar",opciones3),
    st.radio("Cercanía de los miembros de su familia",opciones3),st.radio("**Elija la opción que mejor refleje su entorno familiar:**",
                         ["En mi hogar las normas se establecen a través de la negociación","Las normas del hogar ya están establecidas y todos las cumplimos",
                          "Hay normas establecidas, pero no las cumplo porque no estoy de acuerdo","No me quedan muy claras cuáles son las normas de convivencia que hay en el hogar",
                          "En mi hogar no hay establecidas normas de convivencia"])
]
st.markdown(
    """
    <p style="font-size:18px;font-weight:bold;">¿Con qué frecuencia su familia realiza las siguientes acciones?</p>
    """, 
    unsafe_allow_html=True
)

diagnostico += [ 
                st.radio("**Cuando algo le preocupa, ¿puede pedir ayuda a su familia?**",opciones4),
                st.radio("**Disfruta el tiempo que comparte con su familia.**",opciones4),
                st.radio("**Su familia lo acompaña en su vida universitaria.**",opciones4)
                ]

st.markdown(
    """
    <p style="font-size:18px;font-weight:bold;">¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive? </p>
    """, 
    unsafe_allow_html=True
)

diagnostico += [
    st.radio("**Interrumpo constantemente a mis padres porque no estoy de acuerdo con lo que dicen**",opciones5),
    st.radio("**Intento cambiar de tema y evitar hablar de lo que ha pasado**",opciones5),
    st.radio("**Discuto con mis padres o tutores y me enfrento a ellos**",opciones5),
    st.radio("**Aporto soluciones para resolver el problema**",opciones5),
    st.radio("**Cuando nos enfadamos, incluso llegamos a la violencia física**",opciones5),
    st.radio("**Intento tratar el conflicto dialogando y escuchando a mis padres.**",opciones5),
    st.multiselect("**¿Actualmente en su familia se presentan algunas de las siguientes situaciones? (Selección múltiple)**",
                                ["Malas relaciones intrafamiliares","Fallecimiento de algún pariente","Violencia intrafamiliar",
                                 "Abuso o violencia sexual","Enfermedad crónica de algún pariente","Separación de los padres","Alcoholismo o adicción a sustancias",
                                "Desplazamiento forzado","Dificultades económicas de la familia","Ninguna"],
                                default="Ninguna"),
    st.radio("**¿Cuántos hijos tiene usted?**",["Ninguno",
                                                              "Uno","Dos","Más de dos"])
]


#----------------------------------------------------------------  HABILIDADES SOCIALES    ------------------------------------------------------------------------------------------------------------


st.header("HABILIDADES SOCIALES",divider=True)
st.markdown("<p style='font-size:18px;font-weight:bold;'>Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones:</p>", unsafe_allow_html=True)
opciones6 = ["Nunca","Pocas veces","Algunas veces","Siempre"]

# Preguntas de habilidades sociales
sociales = [
    st.radio("**En una conversación. Presta atención a la persona que le está hablando**", opciones6),
    st.radio("**Toma la iniciativa de darse a conocer a otras personas**", opciones6),
    st.radio("**Ayuda a que los demás se conozcan entre sí**", opciones6),
    st.radio("**Pide ayuda cuando tiene alguna dificultad**", opciones6),
    st.radio("**Se integra con facilidad a un grupo o participa en actividades grupales**", opciones6),
    st.radio("**Pide disculpas a los demás por haber hecho algo mal**", opciones6),
    st.radio("**Reconoce cuando es necesario pedir permiso para hacer algo y lo solicita a la persona indicada**", opciones6),
    st.radio("**Presta ayuda a quien lo necesita**", opciones6),
    st.radio("**En una situación que le genera enojo, logra controlar esta emoción**", opciones6),
    st.radio("**Se mantiene al margen de situaciones que le pueden ocasionar problemas**", opciones6),
    st.radio("**Se cohibe de participar en actividades sociales por miedo a la critica o por vergüenza**", opciones6),
    st.radio("**Antes de una conversación problemática, planifica la forma de exponer su punto de vista**", opciones6),
    st.radio("**En un contexto social, si no tiene claro el tema de conversación o surgen inquietudes alrededor del mismo, solicita explicación**", opciones6)
]

#----------------------------------------------------------------  COMPONENTE ECONOMICO    ------------------------------------------------------------------------------------------------------------


st.subheader("COMPONENTE ECONÓMICO",divider=True)
st.markdown("<p style='font-size:18px;font-weight:bold;'>¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda?</p>", unsafe_allow_html=True)
# Preguntas económicas
econo = [
    st.radio("**Energía eléctrica**", opciones1),
    st.radio("**Alcantarillado**", opciones1),
    st.radio("**Gas natural o propano**", opciones1),
    st.radio("**Recolección de basuras**", opciones1),
    st.radio("**Acueducto**", opciones1),
    st.radio("**Internet hogar**", opciones1),
    st.radio("**Plan de datos (celular)**", opciones1),
    st.radio("**La vivienda ocupada es:**", 
             ["Propia, totalmente pagada", "Propia, la están pagando", "Con permiso del propietario o de familia", "En arriendo o subarriendo", "Posesión sin título, ocupante de hecho (invasión)"]),
    st.radio("**El agua para el consumo o preparación de alimentos la obtienen principalmente de:**", 
             ["Acueducto", "Pozo con bomba", "Pozo sin bomba, jagüey", "Agua lluvia", "Río, quebrada, manantial, escorrentía, nacimiento", "Pila pública", "Carrotanque", "Aguatero", "Agua embotellada o en bolsa"]),
    st.radio("**¿Qué tipo de sanitario utiliza en su hogar?**", 
             ["Con conexión a alcantarillado", "Con conexión a pozo séptico", "Sin conexión a alcantarillado ni a pozo séptico", "Letrina, bajamar", "No tiene"])
]

st.markdown("<p style='font-size:18px;font-weight:bold;'>¿Cuáles de los siguientes bienes posee este hogar?</p>", 
            unsafe_allow_html=True)
# Más preguntas económicas
econo += [
    st.radio("**Nevera o refrigerador**", opciones1),
    st.radio("**Máquina lavadora de ropa**", opciones1),
    st.radio("**Computador**", opciones1),
    st.radio("**Celular, tablet**", opciones1),
    st.radio("**Fogón o estufa**", opciones1),
    st.radio("**Televisión o equipo de sonido**", opciones1),
    st.radio("**Consola de videojuegos**", opciones1)
]
st.markdown("<p style='font-size:18px;font-weight:bold;'>Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos?</p>", unsafe_allow_html=True)

# Preguntas sobre eventos
econo += [
    st.radio("**Inundaciones, crecientes, arroyos**", opciones1),
    st.radio("**Avalanchas, derrumbes o deslizamientos**", opciones1),
    st.radio("**Terremotos**", opciones1),
    st.radio("**Incendios**", opciones1),
    st.radio("**Hundimientos de terreno**", opciones1),
    st.radio("**Desalojos**", opciones1),
    st.radio("**Conflicto armado**", opciones1),
    st.radio("**Las vías de acceso vehicular a su vivienda son principalmente:**", ["Vía pavimentada", "Destapada, trocha, herradura", "No hay vía"])
]

st.markdown("<p style='font-size:18px;font-weight:bold;'>Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para?</p>", unsafe_allow_html=True)

econo += [
    "Sí" if st.checkbox("Ver") else "No",
    "Sí" if st.checkbox("Oír") else "No",
    "Sí" if st.checkbox("Hablar") else "No",
    "Sí" if st.checkbox("Moverse o caminar por sí mismo") else "No",
    "Sí" if st.checkbox("Bañarse, vestirse o alimentarse por sí mismo") else "No",
    "Sí" if st.checkbox("Dificultad para salir a la calle sin ayuda o compañía") else "No",
    "Sí" if st.checkbox("Entender o aprender") else "No"
]

econo.append(st.radio("**¿Usted es el responsable del cuidado de una persona que presenta una condición especial o adulto mayor?**", opciones1))

econo.append(st.radio("**Ingreso mensual de la familia**", ["Menos de 1 salario mínimo mensual legal vigente.", "Entre 1 y 2 salarios mínimos mensuales legales vigentes.", "Más de 2 y menos de 3 salarios mensuales mínimos legales vigentes.", "Más de 3 y menos de 4 salarios mensuales mínimos legales vigentes.", "Más de 4 salarios mínimos mensuales legales vigentes."]))

econo.append(st.number_input("**¿Cuántas personas dependen del ingreso familiar?**", min_value=1, max_value=5))

#----------------------------------------------------------------  ESTRATEGIAS DE AFRONTAMIENTO    ------------------------------------------------------------------------------------------------------------


st.subheader("ESTRATEGIAS DE AFRONTAMIENTO",divider=True)

# Selección preguntas de afrontamiento
afront_1 = st.slider("**Indique el grado de intensidad de estrés que le ha generado esa situación, donde 1 es nada estresante y 5 muy estresante**", min_value=1, max_value=5)
afront_2 = st.slider("**Indique el grado en que creía controlar este problema. Donde 1 es nada y 5 es mucho**", min_value=1, max_value=5)

st.write("**Cuando ocurrió este problema:**")

# Convierto checkbox a "Sí" o "No"
afront_3 = "Sí" if st.checkbox("¿Pensó en él como una amenaza?") else "No"
afront_4 = "Sí" if st.checkbox("¿Pensó en él como un reto?") else "No"
afront_5 = "Sí" if st.checkbox("¿Pensó en diferentes maneras de resolver el problema?") else "No"
afront_6 = "Sí" if st.checkbox("¿Decidió una forma de resolver el problema y la aplicó?") else "No"

st.markdown("<p style='font-size:18px;font-weight:bold;'>Lea atentamente cada una de las siguientes preguntas y señale con qué frecuencia actúa </p>", unsafe_allow_html=True)

opciones7 = ["Nunca", "Pocas veces", "Algunas veces", "Muchas veces"]
afront_radio_respuestas = [
    st.radio("¿Se decía a sí mismo algo para sentirse mejor?", opciones7),
    st.radio("¿Habló con algún familiar sobre el problema?", opciones7),
    st.radio("¿Intentó olvidarlo todo?", opciones7),
    st.radio("¿Intentó ayudar a otros a resolver un problema similar?", opciones7),
    st.radio("¿Descargó su enfado sobre otras personas cuando se sentía triste o enfadado?", opciones7),
    st.radio("¿Intentó distanciarse del problema y ser más objetivo?", opciones7),
    st.radio("¿Se recordó a sí mismo que las cosas podían ser mucho peores?", opciones7),
    st.radio("¿Habló con algún amigo sobre el problema?", opciones7),
    st.radio("¿Se esforzó por resolver el problema?", opciones7),
    st.radio("¿Intentó no pensar en el problema?", opciones7),
    st.radio("¿Se dio cuenta de que no controlaba el problema?", opciones7),
    st.radio("¿Empezó a hacer nuevas actividades?", opciones7),
    st.radio("¿Se aventuró e hizo algo arriesgado?", opciones7),
    st.radio("¿Pensó acerca de lo que tenía que hacer o decir en torno al problema?", opciones7),
    st.radio("¿Intentver el lado positivo de la situación?**", opciones7),
    st.radio("¿Habló con algún profesional (por ejemplo, psicólogo, médico, abogado, sacerdote...)?", opciones7),
    st.radio("¿Fantaseó o imaginó mejores tiempos y situaciones que las que estaba viviendo?", opciones7),
    st.radio("¿Creyó que el resultado sería decidido por el destino?", opciones7),
    st.radio("¿Intentó hacer nuevos amigos?", opciones7),
    st.radio("¿Se mantuvo apartado de la gente?", opciones7),
    st.radio("¿Intentó prever cómo podrían cambiar las cosas?", opciones7),
    st.radio("¿Pensó que estaba mejor que otras personas con el mismo problema que el suyo?", opciones7),
    st.radio("¿Buscó la ayuda de otras personas o grupos con el mismo tipo de problema?", opciones7),
    st.radio("¿Intentó resolver el problema al menos de dos formas diferentes?", opciones7),
    st.radio("¿Intentó no pensar en su situación, aún sabiendo que tendría que hacerlo en otro momento?", opciones7),
    st.radio("¿Aceptó el problema porque no se podía hacer algo para cambiarlo?", opciones7),
    st.radio("¿Leyó con más frecuencia como forma de distracción?", opciones7),
    st.radio("¿Gritó o lloró para desahogarse?", opciones7),
    st.radio("¿Trató de dar algún sentido personal a la situación?", opciones7),
    st.radio("¿Intentó decirse a sí mismo que las cosas mejorarían?", opciones7),
    st.radio("¿Procuró informarse más sobre la situación?", opciones7),
    st.radio("¿Intentó aprender a hacer más cosas por su cuenta?", opciones7),
    st.radio("¿Deseó que el problema desapareciera o deseó acabar con él de algún modo?", opciones7),
    st.radio("¿Esperó que se resolviera de la peor manera posible?", opciones7),
    st.radio("¿Empleó mucho tiempo en actividades de recreo?", opciones7),
    st.radio("¿Intentó anticipar las nuevas demandas que le podían pedir?", opciones7),
    st.radio("¿Pensó en cómo esta situación podía cambiar su vida para mejor?", opciones7),
    st.radio("¿Rezó para guiarse o fortalecerse?", opciones7),
]

#----------------------------------------------------------------  VERIFICACION    ------------------------------------------------------------------------------------------------------------

# Concateno preguntas de afrontamiento
afront = [afront_1, afront_2, afront_3, afront_4, afront_5, afront_6] + afront_radio_respuestas

conn = st.connection("gsheets", type=GSheetsConnection)
datos_SAT = conn.read(worksheet="Datos", ttl=5).dropna(how="all")

def validar_entrada(numero_documento, nombre_completo, Autorizacion_Datos, vocacional, razonamiento, lectora, diagnostico, sociales, econo, afront):
    # Verificar autorización
    if not Autorizacion_Datos:
        return False, "No has aceptado el tratamiento de datos personales. Por favor, acepta para continuar."

    # Verificar número de documento
    if not numero_documento:
        return False, "Por favor, ingrese su número de documento de identidad."
    try:
        numero_documento = int(numero_documento)
        if numero_documento <= 0:
            return False, "Número de documento de identidad inválido."
    except ValueError:
        return False, "Por favor, ingrese solo números para el documento de identidad."

    # Verificar documento duplicado en Google Sheets
    if numero_documento in datos_SAT['Número de documento de identidad.'].values:
        return False, "Este número de documento ya está registrado. No se puede volver a cargar."

    # Verificar campo de nombre completo
    if not nombre_completo:
        return False, "Por favor, ingrese su nombre completo."

    # Verificar que todas las preguntas estén contestadas
    all_respuestas = vocacional + razonamiento + lectora + diagnostico + sociales + econo + afront
    if not all(all_respuestas):
        return False, "Por favor, responda todas las preguntas."

    return True, None  # Todas las validaciones pasaron



if st.button("Cargar Datos", disabled=st.session_state.get('cargar_datos_presionado', False)):
    # Realizar validación
    valido, mensaje_error = validar_entrada(
        numero_documento, nombre_completo, Autorizacion_Datos,
        vocacional, razonamiento, lectora, diagnostico, sociales, econo, afront
    )

    if not valido:
        st.error(mensaje_error)
    else:
        # Crear el DataFrame `df` solo después de pasar las validaciones
        basico = [nombre_completo, numero_documento]
        data = {
            "Datos básicos": basico,
            "Vocacional": vocacional,
            "Razonamiento": razonamiento,
            "Lectora": lectora,
            "Diagnóstico": diagnostico,
            "Habilidades Sociales": sociales,
            "Componente Económico": econo,
            "Estrategias de Afrontamiento": afront
        }

        # Aplanar respuestas y crear DataFrame
        respuestas = {f"{key} {i + 1}": [value] for key, values in data.items() for i, value in enumerate(values)}
        df = pd.DataFrame(respuestas)

        # Verificar tamaño y concatenar con datos_SAT
        if df.shape[1] == datos_SAT.shape[1] == 136:
            df.columns = [f"col_{i}" for i in range(136)]
            datos_copy_SAT = datos_SAT.copy()
            datos_copy_SAT.columns = [f"col_{i}" for i in range(136)]
            
            # Concatenar y actualizar Google Sheets
            datos_SAT_concatenado = pd.concat([datos_copy_SAT, df], ignore_index=True).fillna("")
            datos_SAT_concatenado.columns = list(datos_SAT.columns)  # Restaurar nombres de columnas
            conn.update(worksheet="Datos", data=datos_SAT_concatenado)

            st.success("Respuestas guardadas exitosamente.")
        else:
            st.error("Los DataFrames no tienen el mismo número de columnas.")
        
        st.session_state.cargar_datos_presionado = True  # Evitar que el botón se presione de nuevo
#----------------------------------------------------------------  CALCULO PUNTAJE    ------------------------------------------------------------------------------------------------------------

df_Total = conn.read(worksheet="Datos",ttl=5) # Leer los datos de la hoja "Datos" conectada a 'conn' con un tiempo de vida en caché de 5 segundos

df_SAT = df_Total.tail(1).copy() # Crear una copia del último registro en df_Total para su análisis en df_SAT


# Activa una opción para que Pandas emita advertencias sobre cambios de tipo de datos
pd.set_option('future.no_silent_downcasting', True)

# construcción función Asignacion_SAT que asigna puntuaciones de riesgo a cada categoría

def Asignacion_SAT(X):
   
    # Cargar los modelos de clasificación previamente entrenados para cada componente de riesgo 
    model_proyecto = joblib.load("modelo_proyecto.pkl")
    model_familiar = joblib.load("modelo_familiar.pkl")
    model_economica = joblib.load("modelo_economica.pkl")
    model_psico = joblib.load("modelo_psico.pkl")
    def df_numeric(X):

        # Cargar datos CSV en un DataFrame desde una cadena usando StringIO, para mapeo de ponderaciones y respuestas
        # Cadena de texto que representa el contenido de ponderación de preguntas
        datos_csv = """
PREGUNTA;RESPUESTA;PUNTUACION;CARACTERISTICA
¿Cuál de las siguientes opciones define mejor la razón por la que usted eligió el actual programa de estudios? ;Conozco el programa, se ajusta con mis intereses, personalidad y habilidades.;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál de las siguientes opciones define mejor la razón por la que usted eligió el actual programa de estudios? ;Conozco el programa, presenta una buena oferta laboral y puede representar estabilidad económica.;2;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál de las siguientes opciones define mejor la razón por la que usted eligió el actual programa de estudios? ;Es una alternativa de lo que realmente desearía estudiar.;3;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál de las siguientes opciones define mejor la razón por la que usted eligió el actual programa de estudios? ;Sin ser la carrera que quisiera estudiar es la única en la que mi familia me apoya.;4;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál de las siguientes opciones define mejor la razón por la que usted eligió el actual programa de estudios? ;Por sugerencia de amigos, familia y medios de comunicación sin tener claridad de qué es lo que realmente quiero estudiar.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Qué tan bien conoce el plan de estudios del programa al cual ingresó?;Lo conozco detalladamente;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Qué tan bien conoce el plan de estudios del programa al cual ingresó?;Lo conozco de manera superficial;3;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Qué tan bien conoce el plan de estudios del programa al cual ingresó?;No lo conozco;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Con cuál de las siguientes afirmaciones está de acuerdo?;Me identifico con el perfil profesional de mi carrera y mi desempeño académico es bueno.;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Con cuál de las siguientes afirmaciones está de acuerdo?;Me identifico con el perfil profesional de mi carrera y mi desempeño académico es regular.;3;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Con cuál de las siguientes afirmaciones está de acuerdo?;No me identifico con el perfil profesional de mi carrera.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuánto tiempo usualmente invierte por día para estudiar fuera del aula de clase? ;4 o más horas;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuánto tiempo usualmente invierte por día para estudiar fuera del aula de clase? ;Entre 3 y 4 horas;2;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuánto tiempo usualmente invierte por día para estudiar fuera del aula de clase? ;Entre 2 y 3 horas;3;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuánto tiempo usualmente invierte por día para estudiar fuera del aula de clase? ;Entre 1 y 2 horas;4;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuánto tiempo usualmente invierte por día para estudiar fuera del aula de clase? ;Menos de 1 hora;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
En general, ¿cómo calificaría su desempeño durante su trayectoria académica?;Sobresaliente;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
En general, ¿cómo calificaría su desempeño durante su trayectoria académica?;Bueno;2;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
En general, ¿cómo calificaría su desempeño durante su trayectoria académica?;Regular;3;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
En general, ¿cómo calificaría su desempeño durante su trayectoria académica?;Deficiente;4;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
En general, ¿cómo calificaría su desempeño durante su trayectoria académica?;Muy deficiente;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Antes de iniciar este semestre, ¿cuánto tiempo estuvo desvinculado como estudiante de una Institución Educativa?;Menos de 6 meses;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Antes de iniciar este semestre, ¿cuánto tiempo estuvo desvinculado como estudiante de una Institución Educativa?;6 meses a 1 año;2;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Antes de iniciar este semestre, ¿cuánto tiempo estuvo desvinculado como estudiante de una Institución Educativa?;1 año a 3 años;3;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Antes de iniciar este semestre, ¿cuánto tiempo estuvo desvinculado como estudiante de una Institución Educativa?;3 años o más;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Qué día iban a viajar los personajes de la historia?;Lunes.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Qué día iban a viajar los personajes de la historia?;Jueves.;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Qué día iban a viajar los personajes de la historia?;Martes.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Qué día iban a viajar los personajes de la historia?;Domingo.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Con motivo de qué celebración iba a viajar esta pareja?;Luna de miel.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Con motivo de qué celebración iba a viajar esta pareja?;Aniversario de bodas.;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Con motivo de qué celebración iba a viajar esta pareja?;Cumpleaños de ambos.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Con motivo de qué celebración iba a viajar esta pareja?;Vacaciones.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre de la mujer que protagoniza la historia?;Andrea.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre de la mujer que protagoniza la historia?;Alma.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre de la mujer que protagoniza la historia?;Ana;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre de la mujer que protagoniza la historia?;Aura.;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre del hombre que protagoniza la historia?;Leonardo.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre del hombre que protagoniza la historia?;Lucas.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre del hombre que protagoniza la historia?;Luis.;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre del hombre que protagoniza la historia?;Lorenzo.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Inicialmente, ¿A qué país iban a viajar?;México.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Inicialmente, ¿A qué país iban a viajar?;Costa Rica.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Inicialmente, ¿A qué país iban a viajar?;Puerto Rico.;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Inicialmente, ¿A qué país iban a viajar?;Guatemala.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre del agente de viajes?;Andrés.;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre del agente de viajes?;Armando.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre del agente de viajes?;Alberto.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuál era el nombre del agente de viajes?;Ninguno de los anteriores.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Finalmente, ¿A qué país terminaron viajando?;Puerto Rico.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Finalmente, ¿A qué país terminaron viajando?;París.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Finalmente, ¿A qué país terminaron viajando?;Perú.;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Finalmente, ¿A qué país terminaron viajando?;Ninguno de los anteriores.;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Con relación a sus técnicas de estudio responda las siguientes preguntas:  [¿El lugar donde estudia cuenta con las condiciones adecuadas para estudiar? (iluminación, libre de ruido, suficiente espacio)];Sí;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Con relación a sus técnicas de estudio responda las siguientes preguntas:  [¿El lugar donde estudia cuenta con las condiciones adecuadas para estudiar? (iluminación, libre de ruido, suficiente espacio)];A veces;3;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Con relación a sus técnicas de estudio responda las siguientes preguntas:  [¿El lugar donde estudia cuenta con las condiciones adecuadas para estudiar? (iluminación, libre de ruido, suficiente espacio)];No;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Con relación a sus técnicas de estudio responda las siguientes preguntas:  [¿Encuentra motivación en las diferentes actividades que realiza a nivel académico?];Sí;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Con relación a sus técnicas de estudio responda las siguientes preguntas:  [¿Encuentra motivación en las diferentes actividades que realiza a nivel académico?];A veces;3;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Con relación a sus técnicas de estudio responda las siguientes preguntas:  [¿Encuentra motivación en las diferentes actividades que realiza a nivel académico?];No;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Con relación a sus técnicas de estudio responda las siguientes preguntas:  [¿Considera que las técnicas de estudio que utiliza son efectivas?];Sí;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Con relación a sus técnicas de estudio responda las siguientes preguntas:  [¿Considera que las técnicas de estudio que utiliza son efectivas?];A veces;3;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
Con relación a sus técnicas de estudio responda las siguientes preguntas:  [¿Considera que las técnicas de estudio que utiliza son efectivas?];No;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Le han diagnosticado alguna  dificultad de aprendizaje como dificultad para concentrarse, falta de atención, impulsividad, hiperactividad, dislexia o discalculia?;Sí;5;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Le han diagnosticado alguna  dificultad de aprendizaje como dificultad para concentrarse, falta de atención, impulsividad, hiperactividad, dislexia o discalculia?;No;1;PROYECTO DE VIDA ACADEMICA-PROFESIONAL
¿Cuenta con una red de apoyo  (familiares, amigos o adultos cercanos) que le brinden ayuda a nivel emocional, social, económica o de salud? ;Sí;1;FAMILIAR
¿Cuenta con una red de apoyo  (familiares, amigos o adultos cercanos) que le brinden ayuda a nivel emocional, social, económica o de salud? ;No;5;FAMILIAR
¿Cómo definiría la relación con las personas que conviven con usted?;Tenemos muy buena relación.;1;FAMILIAR
¿Cómo definiría la relación con las personas que conviven con usted?;Discutimos pocas veces y cuando lo hacemos solucionamos los problemas hablando y llegando a un acuerdo.;2;FAMILIAR
¿Cómo definiría la relación con las personas que conviven con usted?;Apenas hablamos entre nosotros.;3;FAMILIAR
¿Cómo definiría la relación con las personas que conviven con usted?;Discutimos algunas veces y no  llegamos a acuerdos.;4;FAMILIAR
¿Cómo definiría la relación con las personas que conviven con usted?;Discutimos muchas veces sin llegar a acuerdos.;5;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Comunicación];Buena;1;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Comunicación];Regular;3;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Comunicación];Mala;5;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Expresión de afecto entre los miembros de la familia];Buena;1;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Expresión de afecto entre los miembros de la familia];Regular;3;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Expresión de afecto entre los miembros de la familia];Mala;5;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Afrontamiento de problemas familiares];Buena;1;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Afrontamiento de problemas familiares];Regular;3;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Afrontamiento de problemas familiares];Mala;5;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Establecimiento de normas en el contexto familiar];Buena;1;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Establecimiento de normas en el contexto familiar];Regular;3;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Establecimiento de normas en el contexto familiar];Mala;5;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Cercanía de los miembros de su familia];Buena;1;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Cercanía de los miembros de su familia];Regular;3;FAMILIAR
De acuerdo a la relación que tiene con su familia, califique los siguientes aspectos: [Cercanía de los miembros de su familia];Mala;5;FAMILIAR
Elija la opción que mejor refleje su entorno familiar:;En casa, mis padres (o acudientes) establecen las normas a través de la negociación.;1;FAMILIAR
Elija la opción que mejor refleje su entorno familiar:;Mis padres establecen las normas del hogar y todos las cumplimos.;2;FAMILIAR
Elija la opción que mejor refleje su entorno familiar:;Hay normas establecidas por mis padres (o acudientes), pero no las cumplo porque no estoy de acuerdo.;3;FAMILIAR
Elija la opción que mejor refleje su entorno familiar:;No me quedan muy claras cuáles son las normas de convivencia que hay en casa;4;FAMILIAR
Elija la opción que mejor refleje su entorno familiar:;En mi casa no hay establecidas normas de convivencia;5;FAMILIAR
¿Con qué frecuencia su familia realiza las siguientes acciones? [Cuando algo le preocupa, ¿puede pedir ayuda a su familia?];Frecuentemente;1;FAMILIAR
¿Con qué frecuencia su familia realiza las siguientes acciones? [Cuando algo le preocupa, ¿puede pedir ayuda a su familia?];Algunas veces;3;FAMILIAR
¿Con qué frecuencia su familia realiza las siguientes acciones? [Cuando algo le preocupa, ¿puede pedir ayuda a su familia?];Nunca;5;FAMILIAR
¿Con qué frecuencia su familia realiza las siguientes acciones? [Disfrutra el tiempo que comparte con su familia.];Frecuentemente;1;FAMILIAR
¿Con qué frecuencia su familia realiza las siguientes acciones? [Disfrutra el tiempo que comparte con su familia.];Algunas veces;3;FAMILIAR
¿Con qué frecuencia su familia realiza las siguientes acciones? [Disfrutra el tiempo que comparte con su familia.];Nunca;5;FAMILIAR
¿Con qué frecuencia su familia realiza las siguientes acciones? [Su familia lo acompaña en su vida universitaria.];Frecuentemente;1;FAMILIAR
¿Con qué frecuencia su familia realiza las siguientes acciones? [Su familia lo acompaña en su vida universitaria.];Algunas veces;3;FAMILIAR
¿Con qué frecuencia su familia realiza las siguientes acciones? [Su familia lo acompaña en su vida universitaria.];Nunca;5;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Interrumpo constantemente a mis padres porque no estoy de acuerdo con lo que dicen];Nunca;1;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Interrumpo constantemente a mis padres porque no estoy de acuerdo con lo que dicen];Pocas veces;2;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Interrumpo constantemente a mis padres porque no estoy de acuerdo con lo que dicen];Algunas veces;3;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Interrumpo constantemente a mis padres porque no estoy de acuerdo con lo que dicen];A menudo;4;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Interrumpo constantemente a mis padres porque no estoy de acuerdo con lo que dicen];Siempre;5;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Intento cambiar de tema y evitar hablar de lo que ha pasado];Nunca;1;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Intento cambiar de tema y evitar hablar de lo que ha pasado];Pocas veces;2;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Intento cambiar de tema y evitar hablar de lo que ha pasado];Algunas veces;3;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Intento cambiar de tema y evitar hablar de lo que ha pasado];A menudo;4;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Intento cambiar de tema y evitar hablar de lo que ha pasado];Siempre;5;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Discuto con mis padres o tutores y me enfrento a ellos];Nunca;1;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Discuto con mis padres o tutores y me enfrento a ellos];Pocas veces;2;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Discuto con mis padres o tutores y me enfrento a ellos];Algunas veces;3;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Discuto con mis padres o tutores y me enfrento a ellos];A menudo;4;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Discuto con mis padres o tutores y me enfrento a ellos];Siempre;5;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Aporto soluciones para resolver el problema];Nunca;5;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Aporto soluciones para resolver el problema];Pocas veces;4;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Aporto soluciones para resolver el problema];Algunas veces;3;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Aporto soluciones para resolver el problema];A menudo;2;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Aporto soluciones para resolver el problema];Siempre;1;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Cuando nos enfadamos, incluso llegamos a la violencia física];Nunca;1;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Cuando nos enfadamos, incluso llegamos a la violencia física];Pocas veces;2;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Cuando nos enfadamos, incluso llegamos a la violencia física];Algunas veces;3;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Cuando nos enfadamos, incluso llegamos a la violencia física];A menudo;4;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Cuando nos enfadamos, incluso llegamos a la violencia física];Siempre;5;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Intento tratar el conflicto dialogando y escuchando a mis padres.];Nunca;5;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Intento tratar el conflicto dialogando y escuchando a mis padres.];Pocas veces;4;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Intento tratar el conflicto dialogando y escuchando a mis padres.];Algunas veces;3;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Intento tratar el conflicto dialogando y escuchando a mis padres.];A menudo;2;FAMILIAR
¿Cómo gestiona los conflictos familiares con sus padres o personas con las que convive?  [Intento tratar el conflicto dialogando y escuchando a mis padres.];Siempre;1;FAMILIAR
¿Actualmente en su familia se presentan algunas de las siguientes situaciones?;Malas relaciones intrafamiliares;5;FAMILIAR
¿Actualmente en su familia se presentan algunas de las siguientes situaciones?;Fallecimiento de algún pariente;5;FAMILIAR
¿Actualmente en su familia se presentan algunas de las siguientes situaciones?;Violencia intrafamiliar;5;FAMILIAR
¿Actualmente en su familia se presentan algunas de las siguientes situaciones?;Abuso o violencia sexual;5;FAMILIAR
¿Actualmente en su familia se presentan algunas de las siguientes situaciones?;Enfermedad crónica de algún pariente;5;FAMILIAR
¿Actualmente en su familia se presentan algunas de las siguientes situaciones?;Separación de los padres;5;FAMILIAR
¿Actualmente en su familia se presentan algunas de las siguientes situaciones?;Alcoholismo o adicción a sustancias;5;FAMILIAR
¿Actualmente en su familia se presentan algunas de las siguientes situaciones?;Desplazamiento forzado;5;FAMILIAR
¿Actualmente en su familia se presentan algunas de las siguientes situaciones?;Dificultades económicas de la familia;5;FAMILIAR
¿Actualmente en su familia se presentan algunas de las siguientes situaciones?;Ninguno;1;FAMILIAR
¿Cuántos hijos tiene usted?;Ninguno;1;FAMILIAR
¿Cuántos hijos tiene usted?;Uno;2;FAMILIAR
¿Cuántos hijos tiene usted?;Dos;3;FAMILIAR
¿Cuántos hijos tiene usted?;Más de dos;5;FAMILIAR
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Energía eléctrica];Sí;1;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Energía eléctrica];No;5;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Alcantarillado];Sí;1;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Alcantarillado];No;5;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Gas natural o propano];Sí;1;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Gas natural o propano];No;5;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Recolección de basuras];Sí;1;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Recolección de basuras];No;5;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Acueducto];Sí;1;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Acueducto];No;5;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Internet hogar];Sí;1;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Internet hogar];No;5;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Plan de datos (celular)];Sí;1;ECONOMICA
¿Con cuáles de los siguientes servicios públicos, privados o comunales cuenta la vivienda? [Plan de datos (celular)];No;5;ECONOMICA
La vivienda ocupada es:;Propia, totalmente pagada;1;ECONOMICA
La vivienda ocupada es:;Propia, la están pagando;2;ECONOMICA
La vivienda ocupada es:;Con permiso del propietario o de familia;3;ECONOMICA
La vivienda ocupada es:;En arriendo o subarriendo;4;ECONOMICA
La vivienda ocupada es:;Posesión sin título, ocupante de hecho (invasión);5;ECONOMICA
El agua para el consumo o preparación de alimentos la obtienen principalmente de:;Acueducto;1;ECONOMICA
El agua para el consumo o preparación de alimentos la obtienen principalmente de:;Pozo con bomba;3;ECONOMICA
El agua para el consumo o preparación de alimentos la obtienen principalmente de:;Pozo sin bomba, jagüey;5;ECONOMICA
El agua para el consumo o preparación de alimentos la obtienen principalmente de:;Agua lluvia;5;ECONOMICA
El agua para el consumo o preparación de alimentos la obtienen principalmente de:;Río, quebrada, manantial, escorrentía, nacimiento;5;ECONOMICA
El agua para el consumo o preparación de alimentos la obtienen principalmente de:;Pila pública;3;ECONOMICA
El agua para el consumo o preparación de alimentos la obtienen principalmente de:;Carrotanque;3;ECONOMICA
El agua para el consumo o preparación de alimentos la obtienen principalmente de:;Aguatero;3;ECONOMICA
El agua para el consumo o preparación de alimentos la obtienen principalmente de:;Agua embotellada o en bolsa;3;ECONOMICA
¿Qué tipo de sanitario utiliza en su hogar?;Con conexión a alcantarillado;1;ECONOMICA
¿Qué tipo de sanitario utiliza en su hogar?;Con conexión a pozo séptico;2;ECONOMICA
¿Qué tipo de sanitario utiliza en su hogar?;Sin conexión a alcantarillado ni a pozo séptico;4;ECONOMICA
¿Qué tipo de sanitario utiliza en su hogar?;Letrina, bajamar;4;ECONOMICA
¿Qué tipo de sanitario utiliza en su hogar?;No tiene;5;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Nevera o refrigerador];Sí;1;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Nevera o refrigerador];No;5;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Máquina lavadora de ropa];Sí;1;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Máquina lavadora de ropa];No;3;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Computador];Sí;1;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Computador];No;3;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Celular, tablet];Sí;1;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Celular, tablet];No;3;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Fogón o estufa];Sí;1;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Fogón o estufa];No;5;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Televisión o equipo de sonido];Sí;1;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Televisión o equipo de sonido];No;3;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Consola de videojuegos];Sí;1;ECONOMICA
¿Cuáles de los siguientes bienes posee este hogar? [Consola de videojuegos];No;1;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Inundaciones, crecientes, arroyos];Sí;5;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Inundaciones, crecientes, arroyos];No;1;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Avalanchas, derrumbes o deslizamientos];Sí;5;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Avalanchas, derrumbes o deslizamientos];No;1;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Terremotos];Sí;5;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Terremotos];No;1;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Incendios];Sí;5;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Incendios];No;1;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Hundimientos de terreno];Sí;5;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Hundimientos de terreno];No;1;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Desalojos];Sí;5;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Desalojos];No;1;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Conflicto armado];Sí;5;ECONOMICA
Durante el tiempo que lleva habitando su vivienda, ¿ésta ha sido afectada por alguno de los siguientes eventos? [Conflicto armado];No;1;ECONOMICA
Las vías de acceso vehicular a su vivienda son principalmente:;Vía pavimentada;1;ECONOMICA
Las vías de acceso vehicular a su vivienda son principalmente:;Destapada, trocha, herradura;3;ECONOMICA
Las vías de acceso vehicular a su vivienda son principalmente:;No hay vía;5;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Ver];Sí;5;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Ver];No;1;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Oír];Sí;5;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Oír];No;1;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Hablar];Sí;5;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Hablar];No;1;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Moverse o caminar por sí mismo];Sí;5;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Moverse o caminar por sí mismo];No;1;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Bañarse, vestirse o alimentarse por sí mismo];Sí;5;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Bañarse, vestirse o alimentarse por sí mismo];No;1;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Dificultad para salir a la calle sin ayuda o compañía];Sí;5;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Dificultad para salir a la calle sin ayuda o compañía];No;1;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Entender o aprender];Sí;5;ECONOMICA
Por enfermedad, accidente o nacimiento ¿tiene usted limitaciones permanentes para? [Entender o aprender];No;1;ECONOMICA
¿Usted es el responsable del cuidado de una persona que presenta una condición especial o adulto mayor?;Sí;5;ECONOMICA
¿Usted es el responsable del cuidado de una persona que presenta una condición especial o adulto mayor?;No;1;ECONOMICA
¿En qué rango se encuentra el ingreso mensual de la familia?;Menos de 1 salario mínimo mensual legal vigente.;5;ECONOMICA
¿En qué rango se encuentra el ingreso mensual de la familia?;Entre 1 y 2 salarios mínimos mensuales legales vigentes.;4;ECONOMICA
¿En qué rango se encuentra el ingreso mensual de la familia?;Más de 2 y menos de 3 salarios mensuales  mínimos legales vigentes.;3;ECONOMICA
¿En qué rango se encuentra el ingreso mensual de la familia?;Más de 3 y menos de 4 salarios mensuales mínimos legales vigentes.;2;ECONOMICA
¿En qué rango se encuentra el ingreso mensual de la familia?;Más de 4 salarios mínimos mensuales legales vigentes.;1;ECONOMICA
¿Cuántas personas dependen del ingreso familiar?;1;1;ECONOMICA
¿Cuántas personas dependen del ingreso familiar?;2;2;ECONOMICA
¿Cuántas personas dependen del ingreso familiar?;3;3;ECONOMICA
¿Cuántas personas dependen del ingreso familiar?;4;4;ECONOMICA
¿Cuántas personas dependen del ingreso familiar?;5;5;ECONOMICA
¿Cuántas personas dependen del ingreso familiar?;>5;5;ECONOMICA
Indique el grado de intensidad de estrés que le ha generado esa situación;1;1;PSICOSOCIAL
Indique el grado de intensidad de estrés que le ha generado esa situación;2;2;PSICOSOCIAL
Indique el grado de intensidad de estrés que le ha generado esa situación;3;3;PSICOSOCIAL
Indique el grado de intensidad de estrés que le ha generado esa situación;4;4;PSICOSOCIAL
Indique el grado de intensidad de estrés que le ha generado esa situación;5;5;PSICOSOCIAL
Indique el grado en que creía controlar este problema.;1;5;PSICOSOCIAL
Indique el grado en que creía controlar este problema.;2;4;PSICOSOCIAL
Indique el grado en que creía controlar este problema.;3;3;PSICOSOCIAL
Indique el grado en que creía controlar este problema.;4;2;PSICOSOCIAL
Indique el grado en que creía controlar este problema.;5;1;PSICOSOCIAL
Cuando ocurrió este problema: [¿Pensó en él como una amenaza?];Sí;5;PSICOSOCIAL
Cuando ocurrió este problema: [¿Pensó en él como una amenaza?];No;1;PSICOSOCIAL
Cuando ocurrió este problema: [¿Pensó en el como un reto?];Sí;1;PSICOSOCIAL
Cuando ocurrió este problema: [¿Pensó en el como un reto?];No;5;PSICOSOCIAL
Cuando ocurrió este problema: [¿Pensó en diferentes maneras de resolver el problema?];Sí;1;PSICOSOCIAL
Cuando ocurrió este problema: [¿Pensó en diferentes maneras de resolver el problema?];No;5;PSICOSOCIAL
Cuando ocurrió este problema: [¿Decidió una forma de resolver el problema y la aplicó?];Sí;1;PSICOSOCIAL
Cuando ocurrió este problema: [¿Decidió una forma de resolver el problema y la aplicó?];No;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se decía a si mismo algo para sentirse mejor?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se decía a si mismo algo para sentirse mejor?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se decía a si mismo algo para sentirse mejor?];Algunas veces;2;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se decía a si mismo algo para sentirse mejor?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún familiar sobre el problema?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún familiar sobre el problema?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún familiar sobre el problema?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún familiar sobre el problema?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó olvidarlo todo?];Nunca;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó olvidarlo todo?];Pocas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó olvidarlo todo?];Algunas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó olvidarlo todo?];Muchas veces;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó ayudar a otros a resolver un problema similar?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó ayudar a otros a resolver un problema similar?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó ayudar a otros a resolver un problema similar?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó ayudar a otros a resolver un problema similar?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Descargó su enfado sobre otras personas cuando se sentía triste o enfadado?];Nunca;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Descargó su enfado sobre otras personas cuando se sentía triste o enfadado?];Pocas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Descargó su enfado sobre otras personas cuando se sentía triste o enfadado?];Algunas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Descargó su enfado sobre otras personas cuando se sentía triste o enfadado?];Muchas veces;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó distanciarse del problema y ser más objetivo?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó distanciarse del problema y ser más objetivo?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó distanciarse del problema y ser más objetivo?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó distanciarse del problema y ser más objetivo?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se recordó a sí mismo que las cosas podían ser mucho peores?];Nunca;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se recordó a sí mismo que las cosas podían ser mucho peores?];Pocas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se recordó a sí mismo que las cosas podían ser mucho peores?];Algunas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se recordó a sí mismo que las cosas podían ser mucho peores?];Muchas veces;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún amigo sobre el problema?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún amigo sobre el problema?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún amigo sobre el problema?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún amigo sobre el problema?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se esforzó por resolver el problema?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se esforzó por resolver el problema?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se esforzó por resolver el problema?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se esforzó por resolver el problema?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó no pensar en el problema?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó no pensar en el problema?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó no pensar en el problema?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó no pensar en el problema?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se dio cuenta de que no controlaba el problema?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se dio cuenta de que no controlaba el problema?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se dio cuenta de que no controlaba el problema?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se dio cuenta de que no controlaba el problema?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Empezó a hacer nuevas actividades?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Empezó a hacer nuevas actividades?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Empezó a hacer nuevas actividades?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Empezó a hacer nuevas actividades?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se aventuro e hizo algo arriesgado?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se aventuro e hizo algo arriesgado?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se aventuro e hizo algo arriesgado?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se aventuro e hizo algo arriesgado?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó acerca de lo que tenía que hacer o decir en torno al problema?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó acerca de lo que tenía que hacer o decir en torno al problema?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó acerca de lo que tenía que hacer o decir en torno al problema?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó acerca de lo que tenía que hacer o decir en torno al problema?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó ver el lado positivo de la situación?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó ver el lado positivo de la situación?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó ver el lado positivo de la situación?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó ver el lado positivo de la situación?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún profesional (por ejemplo, psicólogo, médico, abogado, sacerdote...)?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún profesional (por ejemplo, psicólogo, médico, abogado, sacerdote...)?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún profesional (por ejemplo, psicólogo, médico, abogado, sacerdote...)?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Habló con algún profesional (por ejemplo, psicólogo, médico, abogado, sacerdote...)?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Fantaseó o imagino mejores tiempos y situaciones que las que estaba viviendo?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Fantaseó o imagino mejores tiempos y situaciones que las que estaba viviendo?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Fantaseó o imagino mejores tiempos y situaciones que las que estaba viviendo?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Fantaseó o imagino mejores tiempos y situaciones que las que estaba viviendo?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Creyó que el resultado sería decidido por el destino?];Nunca;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Creyó que el resultado sería decidido por el destino?];Pocas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Creyó que el resultado sería decidido por el destino?];Algunas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Creyó que el resultado sería decidido por el destino?];Muchas veces;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó hacer nuevos amigos?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó hacer nuevos amigos?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó hacer nuevos amigos?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó hacer nuevos amigos?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se mantuvo apartado de la gente?];Nunca;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se mantuvo apartado de la gente?];Pocas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se mantuvo apartado de la gente?];Algunas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Se mantuvo apartado de la gente?];Muchas veces;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó prever cómo podrían cambiar las cosas?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó prever cómo podrían cambiar las cosas?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó prever cómo podrían cambiar las cosas?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó prever cómo podrían cambiar las cosas?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó que estaba mejor que otras personas con el mismo problema que el suyo?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó que estaba mejor que otras personas con el mismo problema que el suyo?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó que estaba mejor que otras personas con el mismo problema que el suyo?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó que estaba mejor que otras personas con el mismo problema que el suyo?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Buscó la ayuda de otras personas o grupos con el mismo tipo de problema?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Buscó la ayuda de otras personas o grupos con el mismo tipo de problema?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Buscó la ayuda de otras personas o grupos con el mismo tipo de problema?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Buscó la ayuda de otras personas o grupos con el mismo tipo de problema?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó resolver el problema al menos de dos formas diferentes?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó resolver el problema al menos de dos formas diferentes?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó resolver el problema al menos de dos formas diferentes?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó resolver el problema al menos de dos formas diferentes?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó no pensar en su situación, aún sabiendo que tendría que hacerlo en otro momento?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó no pensar en su situación, aún sabiendo que tendría que hacerlo en otro momento?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó no pensar en su situación, aún sabiendo que tendría que hacerlo en otro momento?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó no pensar en su situación, aún sabiendo que tendría que hacerlo en otro momento?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Aceptó el problema por que no se podía hacer algo para cambiarlo?];Nunca;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Aceptó el problema por que no se podía hacer algo para cambiarlo?];Pocas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Aceptó el problema por que no se podía hacer algo para cambiarlo?];Algunas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Aceptó el problema por que no se podía hacer algo para cambiarlo?];Muchas veces;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Leyó con más frecuencia como forma de distracción?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Leyó con más frecuencia como forma de distracción?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Leyó con más frecuencia como forma de distracción?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Leyó con más frecuencia como forma de distracción?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Gritó o lloró para desahogarse?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Gritó o lloró para desahogarse?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Gritó o lloró para desahogarse?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Gritó o lloró para desahogarse?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Trató de dar algún sentido personal a la situación?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Trató de dar algún sentido personal a la situación?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Trató de dar algún sentido personal a la situación?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Trató de dar algún sentido personal a la situación?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó decirse a sí mismo que las cosas mejorarían?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó decirse a sí mismo que las cosas mejorarían?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó decirse a sí mismo que las cosas mejorarían?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó decirse a sí mismo que las cosas mejorarían?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Procuró informarse más sobre la situación?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Procuró informarse más sobre la situación?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Procuró informarse más sobre la situación?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Procuró informarse más sobre la situación?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó aprender a hacer más cosas por su cuenta?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó aprender a hacer más cosas por su cuenta?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó aprender a hacer más cosas por su cuenta?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó aprender a hacer más cosas por su cuenta?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Deseó que el problema desapareciera o deseó acabar con él de algún modo?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Deseó que el problema desapareciera o deseó acabar con él de algún modo?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Deseó que el problema desapareciera o deseó acabar con él de algún modo?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Deseó que el problema desapareciera o deseó acabar con él de algún modo?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Esperó que se resolviera de la peor manera posible?];Nunca;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Esperó que se resolviera de la peor manera posible?];Pocas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Esperó que se resolviera de la peor manera posible?];Algunas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Esperó que se resolviera de la peor manera posible?];Muchas veces;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Empleó mucho tiempo en actividades de recreo?];Nunca;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Empleó mucho tiempo en actividades de recreo?];Pocas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Empleó mucho tiempo en actividades de recreo?];Algunas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Empleó mucho tiempo en actividades de recreo?];Muchas veces;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó anticipar las nuevas demandas que le podían pedir?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó anticipar las nuevas demandas que le podían pedir?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó anticipar las nuevas demandas que le podían pedir?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Intentó anticipar las nuevas demandas que le podían pedir?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó en cómo está situación podía cambiar su vida para mejor?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó en cómo está situación podía cambiar su vida para mejor?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó en cómo está situación podía cambiar su vida para mejor?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Pensó en cómo está situación podía cambiar su vida para mejor?];Muchas veces;1;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Rezó para guiarse o fortalecerse?];Nunca;5;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Rezó para guiarse o fortalecerse?];Pocas veces;4;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Rezó para guiarse o fortalecerse?];Algunas veces;3;PSICOSOCIAL
Lea atentamente cada una de las siguientes preguntas  y señale con qué frecuencia actúa  [¿Rezó para guiarse o fortalecerse?];Muchas veces;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En una conversación. Presta atención a la persona que le está hablando];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En una conversación. Presta atención a la persona que le está hablando];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En una conversación. Presta atención a la persona que le está hablando];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En una conversación. Presta atención a la persona que le está hablando];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Toma la iniciativa de darse a conocer a otras personas];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Toma la iniciativa de darse a conocer a otras personas];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Toma la iniciativa de darse a conocer a otras personas];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Toma la iniciativa de darse a conocer a otras personas];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Ayuda a que los demás se conozcan entre sí];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Ayuda a que los demás se conozcan entre sí];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Ayuda a que los demás se conozcan entre sí];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Ayuda a que los demás se conozcan entre sí];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Pide ayuda cuando tiene alguna dificultad];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Pide ayuda cuando tiene alguna dificultad];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Pide ayuda cuando tiene alguna dificultad];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Pide ayuda cuando tiene alguna dificultad];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se integra con facilidad a un grupo o  participa en actividades grupales];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se integra con facilidad a un grupo o  participa en actividades grupales];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se integra con facilidad a un grupo o  participa en actividades grupales];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se integra con facilidad a un grupo o  participa en actividades grupales];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Pide disculpas a los demás por haber hecho algo mal];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Pide disculpas a los demás por haber hecho algo mal];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Pide disculpas a los demás por haber hecho algo mal];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Pide disculpas a los demás por haber hecho algo mal];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Reconoce cuando es necesario pedir permiso para hacer algo y lo solicita a la persona indicada];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Reconoce cuando es necesario pedir permiso para hacer algo y lo solicita a la persona indicada];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Reconoce cuando es necesario pedir permiso para hacer algo y lo solicita a la persona indicada];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Reconoce cuando es necesario pedir permiso para hacer algo y lo solicita a la persona indicada];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Presta ayuda a quien lo necesita];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Presta ayuda a quien lo necesita];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Presta ayuda a quien lo necesita];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Presta ayuda a quien lo necesita];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En una situación que le genera enojo, logra controlar esta emoción];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En una situación que le genera enojo, logra controlar esta emoción];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En una situación que le genera enojo, logra controlar esta emoción];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En una situación que le genera enojo, logra controlar esta emoción];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se mantiene al margen de situaciones que le pueden ocasionar problemas];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se mantiene al margen de situaciones que le pueden ocasionar problemas];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se mantiene al margen de situaciones que le pueden ocasionar problemas];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se mantiene al margen de situaciones que le pueden ocasionar problemas];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se cohibe de participar en actividades sociales por miedo a la critica o por verguenza];Nunca;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se cohibe de participar en actividades sociales por miedo a la critica o por verguenza];Pocas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se cohibe de participar en actividades sociales por miedo a la critica o por verguenza];Algunas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Se cohibe de participar en actividades sociales por miedo a la critica o por verguenza];Siempre;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Antes de una conversación problemática, planifica la forma de exponer su punto de vista];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Antes de una conversación problemática, planifica la forma de exponer su punto de vista];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Antes de una conversación problemática, planifica la forma de exponer su punto de vista];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [Antes de una conversación problemática, planifica la forma de exponer su punto de vista];Siempre;1;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En un contexto social, sino tiene claro el tema de conversación o surgen inquietudes alrededor del mismo, solicita explicación];Nunca;5;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En un contexto social, sino tiene claro el tema de conversación o surgen inquietudes alrededor del mismo, solicita explicación];Pocas veces;4;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En un contexto social, sino tiene claro el tema de conversación o surgen inquietudes alrededor del mismo, solicita explicación];Algunas veces;3;PSICOSOCIAL
Señale la frecuencia con la que le ocurre lo indicado en cada una de las siguientes afirmaciones: [En un contexto social, sino tiene claro el tema de conversación o surgen inquietudes alrededor del mismo, solicita explicación];Siempre;1;PSICOSOCIAL
"""
        ponderaciones = pd.read_csv(StringIO(datos_csv), sep=';',engine="python") # Cargo un data frame con los datos de ponderaciones y puntuaciones
        
        # Selección y procesamiento de preguntas para el componente de "Proyecto de Vida Académica-Profesional"
        preguntas_proyecto = ponderaciones.loc[ponderaciones["CARACTERISTICA"]=="PROYECTO DE VIDA ACADEMICA-PROFESIONAL","PREGUNTA"].unique()
        df_proyecto = X[preguntas_proyecto].copy()
        
        # Reemplazo de respuestas por puntuaciones nuúmericas usando las ponderaciones
        for pregunta in preguntas_proyecto:
            reemplazos = ponderaciones.loc[ponderaciones["PREGUNTA"]==pregunta,"RESPUESTA"].values.tolist()
            puntuaciones = ponderaciones.loc[ponderaciones["PREGUNTA"]==pregunta,"PUNTUACION"].values.tolist()
            df_proyecto.loc[:,pregunta] = df_proyecto.loc[:,pregunta].replace(reemplazos,puntuaciones).infer_objects(copy=False)
            
        # Renombrar las columnas de df_proyecto para mantener un formato estándar
        new_column_names_proyecto = {old_name: f'Pregunta{i+1}' for i, old_name in enumerate(df_proyecto.columns)}
        df_proyecto.rename(columns=new_column_names_proyecto, inplace=True)
        # Seleccionar preguntas específicas de "Proyecto de Vida" para la clasificación final
        selected_questions_proyecto = ["Pregunta1","Pregunta7","Pregunta17","Pregunta9"]
        df_proyecto_selected = df_proyecto[selected_questions_proyecto]
        
        # Repetir el proceso anterior para el componente "Económico"
        preguntas_economica = ponderaciones.loc[ponderaciones["CARACTERISTICA"]=="ECONOMICA","PREGUNTA"].unique()
        df_economica = X[preguntas_economica].copy()
        
        # Mapeo de respuestas a puntuaciones en el componente económico
        for pregunta in preguntas_economica:
            reemplazos = ponderaciones.loc[ponderaciones["PREGUNTA"]==pregunta,"RESPUESTA"].values.tolist()
            puntuaciones = ponderaciones.loc[ponderaciones["PREGUNTA"]==pregunta,"PUNTUACION"].values.tolist()
            df_economica.loc[:,pregunta] = df_economica.loc[:,pregunta].replace(reemplazos,puntuaciones).infer_objects(copy=False)
        # Renombrar y seleccionar preguntas de "Económico"
        selected_questions_economico =  ['Pregunta6', 'Pregunta7', 'Pregunta5', 'Pregunta1']
        new_column_names_economico = {old_name: f'Pregunta{i+1}' for i, old_name in enumerate(df_economica.columns)}
        df_economica.rename(columns=new_column_names_economico, inplace=True)
        df_economica_selected = df_economica[selected_questions_economico]

        # Repetir proceso para el componente "Psicosocial"
        preguntas_psico = ponderaciones.loc[ponderaciones["CARACTERISTICA"]=="PSICOSOCIAL","PREGUNTA"].unique()
        df_psico = X[preguntas_psico].copy()

        for pregunta in preguntas_psico:
            reemplazos = ponderaciones.loc[ponderaciones["PREGUNTA"]==pregunta,"RESPUESTA"].values.tolist()
            puntuaciones = ponderaciones.loc[ponderaciones["PREGUNTA"]==pregunta,"PUNTUACION"].values.tolist()
            df_psico.loc[:,pregunta] = df_psico.loc[:,pregunta].replace(reemplazos,puntuaciones).infer_objects(copy=False)
        selected_questions_psico = ['Pregunta38', 'Pregunta21', 'Pregunta25', 'Pregunta15', 'Pregunta43', 'Pregunta50', 'Pregunta26',
                                    'Pregunta35', 'Pregunta6', 'Pregunta52', 'Pregunta7', 'Pregunta3', 'Pregunta8', 'Pregunta4']
        new_column_names_psico = {old_name: f'Pregunta{i+1}' for i, old_name in enumerate(df_psico.columns)}
        df_psico.rename(columns=new_column_names_psico, inplace=True)
        df_psico_selected = df_psico[selected_questions_psico]
        
        # Procesamiento el componente "Familiar"

         # Función auxiliar para dividir texto en columnas separadas, manejando faltantes
        def split_text_to_columns(text, max_splits=9):
            phrases = text.split(',')
            phrases = [phrase.strip() for phrase in phrases]
            # Si hay menos de max_splits frases, rellenamos con None o con un string vacío
            while len(phrases) < max_splits:
                phrases.append(None)
            return phrases[:max_splits]

        # Función para asignar valores según condiciones específicas
        def assign_values(value):
            if pd.isna(value) or value == '':
                return 0
            elif value == 'Ninguna':
                return 1
            else:
                return 5
            
        preguntas_familiar = ponderaciones.loc[ponderaciones["CARACTERISTICA"]=="FAMILIAR","PREGUNTA"].unique()
        df_familiar = X[preguntas_familiar].astype(str).copy()
        
        for pregunta in preguntas_familiar:
            # Expandir preguntas con múltiples opciones a columnas separadas
            if pregunta =="¿Actualmente en su familia se presentan algunas de las siguientes situaciones?":
                columns = [f'col_{i+1}' for i in range(9)]
                df_familiar.loc[:,"¿Actualmente en su familia se presentan algunas de las siguientes situaciones?"] = df_familiar["¿Actualmente en su familia se presentan algunas de las siguientes situaciones?"].astype(str)
                df_expanded = df_familiar["¿Actualmente en su familia se presentan algunas de las siguientes situaciones?"].apply(split_text_to_columns).apply(pd.Series)
                df_expanded.columns = [f'col_{i+1}' for i in range(df_expanded.shape[1])]

                df_expanded2 = df_expanded.apply(lambda col: col.map(assign_values))

                df_familiar = pd.concat([df_familiar, df_expanded2], axis=1)
                df_familiar = df_familiar.drop(columns=["¿Actualmente en su familia se presentan algunas de las siguientes situaciones?"])

            else:
                reemplazos = ponderaciones.loc[ponderaciones["PREGUNTA"]==pregunta,"RESPUESTA"].values.tolist()
                puntuaciones = ponderaciones.loc[ponderaciones["PREGUNTA"]==pregunta,"PUNTUACION"].values.tolist()
                df_familiar.loc[:,pregunta] = df_familiar.loc[:,pregunta].replace(reemplazos,puntuaciones).infer_objects(copy=False)
        
        # Renombrar y seleccionar preguntas para "Familiar"
        selected_questions_familiar = ['Pregunta20', 'Pregunta4', 'Pregunta3', 'Pregunta11', 'Pregunta19', 'Pregunta5', 'Pregunta9']
        new_column_names_familiar = {old_name: f'Pregunta{i+1}' for i, old_name in enumerate(df_familiar.columns)}
        df_familiar.rename(columns=new_column_names_familiar, inplace=True) 
        df_familiar_selected =  df_familiar[selected_questions_familiar]      
    
    
        # Retornar los DataFrames seleccionados de cada componente
        return df_proyecto_selected, df_familiar_selected,df_economica_selected,df_psico_selected
    
    # Mapear predicciones numéricas a etiquetas de riesgo
    mapa_etiquetas = {0: 'BAJO', 1: 'MEDIO', 2: 'ALTO'}
    
     # Predecir y etiquetar los niveles de riesgo
    df_proyecto,df_familiar,df_economico,df_psico = df_numeric(X)
    y_pred_proyecto = model_proyecto.predict(df_proyecto)
    y_pred_proyecto = np.vectorize(mapa_etiquetas.get)(y_pred_proyecto)
    
    y_pred_familiar = model_familiar.predict(df_familiar)
    y_pred_familiar = np.vectorize(mapa_etiquetas.get)(y_pred_familiar)
    y_pred_economico = model_economica.predict(df_economico)
    y_pred_economico = np.vectorize(mapa_etiquetas.get)(y_pred_economico)
    
    y_pred_psico = model_psico.predict(df_psico)
    y_pred_psico = np.vectorize(mapa_etiquetas.get)(y_pred_psico)
    
    # Retornar predicciones para cada componente
    return y_pred_proyecto,y_pred_familiar,y_pred_economico,y_pred_psico


if st.session_state.get('cargar_datos_presionado', False):
    # Si el botón de cargar datos ha sido presionado, muestra el botón para calcular puntaje.
    if st.button("Calcular Puntaje", disabled=st.session_state.get('calcular_puntaje_presionado', False)):
        st.write("**Espere un momento...**") # Mensaje de espera mientras se calcula el puntaje.
        time.sleep(3) # Pausa de 3 segundos antes de mostrar resultados.
        st.session_state.calcular_puntaje_presionado = True
        
        # Llama a la función Asignacion_SAT para obtener los riesgos de los componentes 
        # y selecciona el primer valor de cada resultado (proyecto, familiar, economico, psico).
        proyecto,familiar,economico,psico =[v[0]for v in Asignacion_SAT(df_SAT)]

        # Crear un contenedor HTML para los resultados
        html_content = f"""
        <div style="text-align: center;">
            <div style="border: 2px solid #4CAF50; border-radius: 5px; padding: 10px; margin-bottom: 20px;">
                <h4 style="margin: 0;">Riesgo Académico</h4>
                <p style="font-size: 36px; font-weight: bold; margin: 10px 0;">{proyecto}</p>
            </div>
            <div style="border: 2px solid #2196F3; border-radius: 5px; padding: 10px; margin-bottom: 20px;">
                <h4 style="margin: 0;">Riesgo Familiar</h4>
                <p style="font-size: 36px; font-weight: bold; margin: 10px 0;">{familiar}</p>
            </div>
            <div style="border: 2px solid #FF9800; border-radius: 5px; padding: 10px; margin-bottom: 20px;">
                <h4 style="margin: 0;">Riesgo Economico</h4>
                <p style="font-size: 36px; font-weight: bold; margin: 10px 0;">{economico}</p>
            </div>
            <div style="border: 2px solid #F44336; border-radius: 5px; padding: 10px; margin-bottom: 20px;">
                <h4 style="margin: 0;">Riesgo Psicosocial</h4>
                <p style="font-size: 36px; font-weight: bold; margin: 10px 0;">{psico}</p>
            </div>
        </div>
        """

        # Mostrar el contenido HTML
        st.markdown(html_content, unsafe_allow_html=True)
            # Botón para volver a calcular y reiniciar
        
        #desactivar botones 
        if st.session_state.cargar_datos_presionado and st.session_state.calcular_puntaje_presionado:
            st.info("Proceso completado. Reinicie para volver a calcular")
#        if st.button("Reiniciar"):
            #st.experimental_rerun()  # Reinicia la aplicación



