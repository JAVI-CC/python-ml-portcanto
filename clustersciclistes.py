"""
@ IOC - CE IABD
"""
import os
import logging
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import pickle

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.metrics.cluster import homogeneity_score, completeness_score, v_measure_score

# Per veure només els logs en mode info dels resultats des de la consola.
# logging.getLogger().setLevel(logging.INFO)

# Per veure els resultats tant del mode debug como del mode info des de la consola.
logging.basicConfig(level=logging.DEBUG)

@contextmanager
def suppress_stdout_stderr():
	""" A context manager that redirects stdout and stderr to devnull """
	with open(os.devnull, 'w', encoding="UTF-8") as fnull:
		with redirect_stderr(fnull) as err, redirect_stdout(fnull) as out:
			yield (err, out)

def load_dataset(path):
	"""
	Carrega el dataset de registres dels ciclistes

	arguments:
		path -- dataset

	Returns: dataframe
	"""

	return pd.read_csv(path, delimiter=';')

def exploratory_data_analysis(df):
	"""
	Exploratory Data Analysis del dataframe

	arguments:
		df -- dataframe

	Returns: None
	"""

	logging.debug('\n%s\n', df.shape)
	logging.debug('\n%s\n', df.head())
	logging.debug('\n%s\n', df.columns)
	logging.debug('\n%s\n', df.info())

def clean(df):
	"""
	Elimina les columnes que no són necessàries per a l'anàlisi dels clústers

	arguments:
		df -- dataframe

	Returns: dataframe
	"""

	df = df.drop('id', axis=1)
	df = df.drop('tt', axis=1)

	logging.debug('\nDataframe:\n%s\n', df.head())

	return df

def extract_true_labels(df):
	"""
	Guardem les etiquetes dels ciclistes (BEBB, ...)

	arguments:
		df -- dataframe

	Returns: numpy ndarray (true labels)
	"""

	tipus_true_labels = df["tipus"].to_numpy()
	logging.debug('\nTipus de cada ciclista:\n%s\n', df.groupby(['tipus'])['tipus'].count())

	return tipus_true_labels

def visualitzar_pairplot(df):
	"""
	Genera una imatge combinant entre sí tots els parells d'atributs.
	Serveix per apreciar si es podran trobar clústers.

	arguments:
		df -- dataframe

	Returns: None
	"""

	df = df.rename(columns={'tp': 'Temps pujada', 'tb': 'Temps baixada'})
	sns.pairplot(df)

	try:
		os.makedirs(os.path.dirname('img/'))
	except FileExistsError:
		pass

	plt.savefig("img/pairplot.png")

def clustering_kmeans(data, n_clusters=4):
	"""
	Crea el model KMeans de sk-learn, amb 4 clusters (estem cercant 4 agrupacions)
	Entrena el model

	arguments:
		data -- les dades: tp i tb

	Returns: model (objecte KMeans)
	"""

	model = KMeans(n_clusters=n_clusters, random_state=42)

	with suppress_stdout_stderr():
		model.fit(data)

	return model

def visualitzar_clusters(data, labels):
	"""
	Visualitza els clusters en diferents colors. Provem diferents combinacions de parells d'atributs

	arguments:
		data -- el dataset sobre el qual hem entrenat
		labels -- l'array d'etiquetes a què pertanyen les dades 
		(hem assignat les dades a un dels 4 clústers)

	Returns: None
	"""

	try:
		os.makedirs(os.path.dirname('img/'))
	except FileExistsError:
		pass

	fig = plt.figure()
	plt.xlabel("Temps de pujada")
	plt.ylabel("Temps de baixada")
	sns.scatterplot(x='tp', y='tb', data=data, hue=labels, palette="rainbow")
	plt.savefig("img/grafica1.png")
	fig.clf()
	#plt.show()

def associar_clusters_patrons(tipus, model):
	"""
	Associa els clústers (labels 0, 1, 2, 3) als patrons de comportament (BEBB, BEMB, MEBB, MEMB).
	S'han trobat 4 clústers però aquesta associació encara no s'ha fet.

	arguments:
	tipus -- un array de tipus de patrons que volem actualitzar associant els labels
	model -- model KMeans entrenat

	Returns: array de diccionaris amb l'assignació dels tipus als labels
	"""
	# proposta de solució
	dicc = {'tp': 0, 'tb': 1}

	logging.info('Centres:')
	for j in range(len(tipus)):
		model_cluster_tp = f"{model.cluster_centers_[j][dicc['tp']]:.1f}"
		model_cluster_tb = f"{model.cluster_centers_[j][dicc['tb']]:.1f}"
		logging.info('%s:\t(tp: %s\ttb: %s)', j, model_cluster_tp, model_cluster_tb)
	logging.info('Centres finalitzat\n')


	# Procés d'assignació
	ind_label_0 = -1
	ind_label_1 = -1
	ind_label_2 = -1
	ind_label_3 = -1

	suma_max = 0
	suma_min = 50000

	for j, center in enumerate(model.cluster_centers_):
		suma = round(center[dicc['tp']], 1) + round(center[dicc['tb']], 1)
		if suma_max < suma:
			suma_max = suma
			ind_label_3 = j
		if suma_min > suma:
			suma_min = suma
			ind_label_0 = j

	tipus[0].update({'label': ind_label_0})
	tipus[3].update({'label': ind_label_3})

	lst = [0, 1, 2, 3]
	lst.remove(ind_label_0)
	lst.remove(ind_label_3)

	if model.cluster_centers_[lst[0]][0] < model.cluster_centers_[lst[1]][0]:
		ind_label_1 = lst[0]
		ind_label_2 = lst[1]
	else:
		ind_label_1 = lst[1]
		ind_label_2 = lst[0]

	tipus[1].update({'label': ind_label_1})
	tipus[2].update({'label': ind_label_2})

	logging.info('\nHem fet l\'associació')
	logging.info('\nTipus i labels:\n%s\n', tipus)

	return tipus

def generar_informes(df, tipus):
	"""
	Generació dels informes a la carpeta informes/. 
	Tenim un dataset de ciclistes i 4 clústers, i generem
	4 fitxers de ciclistes per cadascun dels clústers

	arguments:
		df -- dataframe
		tipus -- objecte que associa els patrons de comportament amb els labels dels clústers

	Returns: None
	"""

	ciclistes_label = [
		df[df['label'] == 0],
		df[df['label'] == 1],
		df[df['label'] == 2],
		df[df['label'] == 3]
	]

	try:
		os.makedirs(os.path.dirname('informes/'))
	except FileExistsError:
		pass

	for tip in tipus:
		fitxer = tip['name'].replace(' ', '_') + '.txt'
		with open("informes/" + fitxer, "w", encoding="UTF-8") as foutput:
			ti = [ti for ti in tipus if ti['name'] == tip['name']]
			ciclistes = ciclistes_label[ti[0]['label']]
			ciclistes = ciclistes[['tp', 'tb']].values.tolist()

			for ciclista in ciclistes:
				foutput.write(f"{str(ciclista[0])}-{str(ciclista[1])}\n")

	logging.info('\nS\'han generat els informes en la carpeta informes/\n')

def nova_prediccio(dades, model):
	"""
	Passem nous valors de ciclistes, per tal d'assignar aquests valors a un dels 4 clústers

	arguments:
		dades -- llista de llistes, que segueix l'estructura 'id', 'tp', 'tb', 'tt'
		model -- clustering model
	Returns: (dades agrupades, prediccions del model)
	"""

	df_nous_dades_ciclistes = pd.DataFrame(columns=['id', 'tp', 'tb', 'tt'], data=dades)

	df_nous_dades_ciclistes = df_nous_dades_ciclistes.drop(['id', 'tt'], axis=1)

	logging.info('\nNous valors agrupats:\n%s\n', df_nous_dades_ciclistes.head())

	return df_nous_dades_ciclistes, model.predict(df_nous_dades_ciclistes)

# ----------------------------------------------

if __name__ == "__main__":

	# Per veure la informació dels resultats des de la consola.
	logging.basicConfig(format='%(message)s', level=logging.DEBUG)

	# Per no mostrar els missatges de la llibreria Matplotlib.
	logging.getLogger('matplotlib.font_manager').setLevel(logging.ERROR)

	PATH_DATASET = './data/ciclistes.csv'

	# load_dataset
	df_ciclistes = load_dataset(PATH_DATASET)

	# Exploratory Data Analysis (EDA)
	exploratory_data_analysis(df_ciclistes)

	# clean
	df_ciclistes = clean(df_ciclistes)

	# extract_true_labels
	true_labels = extract_true_labels(df_ciclistes)

	# eliminem el tipus, ja no interessa .drop('tipus', axis=1)
	df_ciclistes = df_ciclistes.drop('tipus', axis=1)

	# visualitzar_pairplot
	visualitzar_pairplot(df_ciclistes)

	# clustering_kmeans
	clustering_model = clustering_kmeans(df_ciclistes)
	data_labels = clustering_model.labels_

  # pickle.dump() per guardar el model
	with open('model/clustering_model.pkl', 'wb') as f:
		pickle.dump(clustering_model, f)

	# mostrar scores i guardar scores
	logging.info('\n\nHomogeneity: %.3f', homogeneity_score(true_labels, data_labels))
	logging.info('Completeness: %.3f', completeness_score(true_labels, data_labels))
	logging.info('V-measure: %.3f\n', v_measure_score(true_labels, data_labels))

	with open('model/scores.pkl', 'wb') as f:
		pickle.dump({
		"h": homogeneity_score(true_labels, data_labels),
		"c": completeness_score(true_labels, data_labels),
		"v": v_measure_score(true_labels, data_labels)
		}, f)

	# visualitzar_clusters
	visualitzar_clusters(df_ciclistes, data_labels)

	# array de diccionaris que assignarà els tipus als labels
	tipus_labels = [{'name': 'BEBB'}, {'name': 'BEMB'}, {'name': 'MEBB'}, {'name': 'MEMB'}]

	"""
	afegim la columna label al dataframe
	associar_clusters_patrons(tipus, clustering_model)
	guardem la variable tipus a model/tipus_dict.pkl
	generar_informes
	"""

	# Per afegir la columna label al dataframe
	df_ciclistes['label'] = clustering_model.labels_.tolist()
	logging.debug('\nColumna label:\n%s\n', df_ciclistes[:5])

	# associar_clusters_patrons(tipus, clustering_model)
	tipus_clusters = associar_clusters_patrons(tipus_labels, clustering_model)

	# Per guardar la variable tipus a model/tipus_dict.pkl
	with open('model/tipus_dict.pkl', 'wb') as f:
		pickle.dump(tipus_clusters, f)

	# generar_informes
	generar_informes(df_ciclistes, tipus_labels)

	# Classificació de nous valors
	nous_ciclistes = [
		[500, 3230, 1430, 4660], # BEBB
		[501, 3300, 2120, 5420], # BEMB
		[502, 4010, 1510, 5520], # MEBB
		[503, 4350, 2200, 6550] # MEMB
	]

	# nova_prediccio
	logging.debug('\nNous valors:\n%s\n', nous_ciclistes)

	df_nous_ciclistes, pred = nova_prediccio(nous_ciclistes, clustering_model)

	logging.info('\nPredicció dels valors:\n%s', pred)

	# Assignació dels nous valors als tipus
	for i, p in enumerate(pred):
		t = [t for t in tipus_labels if t['label'] == p]
		logging.info('tipus %s (%s) - classe %s', df_nous_ciclistes.index[i], t[0]['name'], p)
