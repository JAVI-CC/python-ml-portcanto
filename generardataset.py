"""
@ IOC - CE IABD
"""
import os
import logging
import numpy as np

def generar_dataset(num, ind, dicc):
	"""
	Genera els temps dels ciclistes, de forma aleatòria, però en base a la informació del diccionari
	"""
	# Variable per guardar les dades de cada ciclista en una llista
	list_ciclistes = []

	# Variable per obtenir en una llista tots els dorsals de cada un dels ciclistes.
	dorsal = list(range((num*ind), (num*(ind+1))))

	# Bucle for per obtenir de forma aleatòria tots els temps de cada un dels ciclistes
	for i in range(num):
		# Per obtenir el temps de pujada
		tp = int(np.random.normal(dicc['mu_p'], dicc['sigma']))

		# Per obtenir el temps de baixada
		tb = int(np.random.normal(dicc['mu_b'], dicc['sigma']))

		# Per obtenir el temps total
		tt = tp + tb

		# Per guardar les dades de cada ciclista en la llista que havia definit abans.
		list_ciclistes.append({"id": dorsal[i]+1, "tp": tp, "tb": tb, "tt": tt, "tipus": dicc['name']})

	# Per retornar la llista amb totes les dades de tots els ciclistes
	return list_ciclistes

if __name__ == "__main__":

	# Per veure la informació dels resultats des de la consola.
	logging.basicConfig(format='%(message)s', level=logging.DEBUG)

	# Per no mostrar els missatges de la llibreria Matplotlib.
	logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

	STR_CICLISTES = 'data/ciclistes.csv'

	try:
		os.makedirs(os.path.dirname(STR_CICLISTES))
	except FileExistsError:
		pass

	# BEBB: bons escaladors, bons baixadors
	# BEMB: bons escaladors, mal baixadors
	# MEBB: mal escaladors, bons baixadors
	# MEMB: mal escaladors, mal baixadors

	# Port del Cantó (18 Km de pujada, 18 Km de baixada)
	# pujar a 20 Km/h són 54 min = 3240 seg
	# pujar a 14 Km/h són 77 min = 4268 seg
	# baixar a 45 Km/h són 24 min = 1440 seg
	# baixar a 30 Km/h són 36 min = 2160 seg
	MU_P_BE = 3240 # mitjana temps pujada bons escaladors
	MU_P_ME = 4268 # mitjana temps pujada mals escaladors
	MU_B_BB = 1440 # mitjana temps baixada bons baixadors
	MU_B_MB = 2160 # mitjana temps baixada mals baixadors
	SIGMA = 240 # 240 s = 4 min

	dicc_ciclistes = [
		{"name":"BEBB", "mu_p": MU_P_BE, "mu_b": MU_B_BB, "sigma": SIGMA},
		{"name":"BEMB", "mu_p": MU_P_BE, "mu_b": MU_B_MB, "sigma": SIGMA},
		{"name":"MEBB", "mu_p": MU_P_ME, "mu_b": MU_B_BB, "sigma": SIGMA},
		{"name":"MEMB", "mu_p": MU_P_ME, "mu_b": MU_B_MB, "sigma": SIGMA}
	]

	# Variable per guardar el número de files a generar de cada tipus de ciclista.
	NUM_FILES_GENERAR = 600

	# Per crear i obrir el fitxer data/ciclistes.csv
	with open(STR_CICLISTES, "w", encoding="UTF-8") as foutput:

  	# Per escriure en la primera linía els noms de les columnes
		# id: Dorsal del ciclista
		# tp: Temps de pujada
		# tb: Temps de baixada
		# tt: Temps total (tp + tb)
		# tipus: El tipus de ciclista ('BEBB' | 'BEMB' | 'MEBB' | 'MEMB')
		foutput.write("id;tp;tb;tt;tipus\n")

		# Bucle for per generar una llista per a cada un dels tipus de ciclistes
		for x in list(range(len(dicc_ciclistes))):
			dataset_ciclistes = generar_dataset(NUM_FILES_GENERAR, x, dicc_ciclistes[x])

			# Bucle for per guardar cada element de la llista en l'arxiu ciclistes.csv
			for y in list(range(len(dataset_ciclistes))):
				ciclista = dataset_ciclistes[y]
				foutput.write(
					f"{ciclista['id']};{ciclista['tp']};{ciclista['tb']};{ciclista['tt']};{ciclista['tipus']}\n")

	logging.info("s'ha generat data/ciclistes.csv")
