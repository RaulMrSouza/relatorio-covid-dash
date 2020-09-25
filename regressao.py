# -*- coding: utf-8 -*-
"""
Created on Mon Mar 30 21:18:33 2020

@author: Pichau
"""

import pandas as pd
import numpy as np
import scipy as sp
# import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.preprocessing import FunctionTransformer, OneHotEncoder, MultiLabelBinarizer
from sklearn.base import BaseEstimator, TransformerMixin
from nltk.corpus import stopwords
import nltk 
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import AdaBoostRegressor
from sklearn import ensemble
import xgboost
from sklearn import preprocessing
from sklearn import utils

nltk.download()


def UnidadePorTexto(quantidade):
    i=0
    for i,c in enumerate(quantidade):
        if not c.isdigit() and c != ',' and c != '.' and c != ' ':
            break
    qtd= -1
    try:
        qtd = float(quantidade[:i])
    except ValueError:
        print("")
    unidade=quantidade[i:]
    return (qtd, unidade)

def score(a, b):
    score = 0
    e = np.array([])
    for i in range(len(a)):
        if b[i] != 0:
            score += np.abs(a[i] - b[i]) / b[i]
            e = np.append(e, np.abs(a[i] - b[i]) / b[i]*100)

    return (score / len(a), e)

data = pd.read_csv("resultado4.csv")
data = pd.concat([data, pd.read_csv("resultado5.csv"),pd.read_csv("resultado6.csv")], ignore_index=True)

#data = pd.read_csv("resultadoRhamos4.csv")
data = data.sort_values(by=['criado'], ascending=False)
#data['criado'] =  data.criado.date() - data.criado.min().date()
#print(data.farma.count())

data = data[(data['farma'].str.strip() ==  '2CF4EC23-F78C-4318-98BE-7FBD17318958')]
print("Total:",data.farma.count())
data = data[(data['volumeTipo'].str.strip() ==  'CAP')]
print("Caps:",data.farma.count())
data = data[(data['incerteza'] ==  0)]
(scoreIni, eIni) = score(data['calculado'].tolist(), data['correto'].tolist())
data['erro'] = eIni

print("Sem incerteza:",data.farma.count())
data = data.drop_duplicates("descricao")
print("Sem duplicados:",data.farma.count())
qtd = []
for index, row in data.iterrows():
    formula = row['descricao']
        
    formulaVolume = str(formula).split('|')[0]
        
    (formulaQtd, formulaUnidade) = UnidadePorTexto(formulaVolume)
    
    qtd.append(formulaQtd)
    
data['qtd'] = data['ajuste']
data['qtd'] = qtd

#data['descricao'] = data['qtd'].astype(str)
data.qtd = data.qtd.astype(int)
data.qtdInsumos = data.qtdInsumos.astype(int)
data.calculado = data.calculado.astype(int)
data.ajuste = data.ajuste.astype(int)
data.incerteza = data.incerteza.astype(int)

volumeTipo_encoder = OneHotEncoder()
volumeTipo_encoder.fit(np.array(data.volumeTipo).reshape(-1, 1))

#X_train = data.tail(300)
#X_test = data.head(198)



X_train = data.tail(data.criado.count() - 200)
X_test = data.head(200)
y_train = X_train.correto.tolist()
y_test = X_test.correto.tolist()
descricoes = X_test.descricao.tolist()

titulo_encoder = MultiLabelBinarizer()

x_train_titulo = []
for i in data.volumeTipo:
    x_train_titulo.append(i.lower().split())

titulo_encoder.fit(x_train_titulo)

class ItemSelector(BaseEstimator, TransformerMixin):

    def __init__(self, key):
        self.key = key

    def fit(self, x, y=None):
        return self

    def transform(self, data_dict):
        if self.key == "farma":
            x = []
            for i in data_dict[self.key]:
                x.append(i.lower().split())

            fitted = province_encoder.transform(x)
            return fitted
        elif self.key == 'calculado':
            return sp.sparse.bsr_matrix(np.transpose(np.matrix(data_dict[self.key]))).todense()
        elif self.key == 'qtd':
            return sp.sparse.bsr_matrix(np.transpose(np.matrix(data_dict[self.key]))).todense()
        elif self.key == 'qtdInsumos':
            return sp.sparse.bsr_matrix(np.transpose(np.matrix(data_dict[self.key]))).todense()
        elif self.key == 'criado':
            return sp.sparse.bsr_matrix(np.transpose(np.matrix(data_dict[self.key]))).todense()
        elif self.key == 'volumeTipo':
            fitted = volumeTipo_encoder.transform(np.array(data_dict[self.key]).reshape(-1, 1))
            return fitted.toarray()
        else:
            #print(data_dict[self.key])
            return data_dict[self.key]




def regression(regressor_model):

    regressor = Pipeline([
        ('features', FeatureUnion([
            ('descricao', Pipeline([
                ('selector', ItemSelector(key='descricao')),
                ('vectorizer', TfidfVectorizer(stop_words=stopwords.words('portuguese')))
            ])),
            ('calculado', Pipeline([
                ('selector', ItemSelector(key='calculado'))
            ])),
            ('qtdInsumos', Pipeline([
                ('selector', ItemSelector(key='qtdInsumos'))
            ])),
            ('qtd', Pipeline([
                ('selector', ItemSelector(key='qtd'))
            ])),
            ('volumeTipo', Pipeline([
                ('selector', ItemSelector(key='volumeTipo'))
            ]))
            #('criado', Pipeline([
            #    ('selector', ItemSelector(key='criado'))
            #]))
        ])),
        ('regressor', regressor_model)
    ])

    
    regressor = regressor.fit(X_train, y_train)
    print("Treinado")
    
    predictions = regressor.predict(X_test)
    print("Calculado")
    
    return (predictions, y_test, regressor, regressor_model)


(predictions, y_test, r1, m1) = regression(KNeighborsRegressor(n_neighbors=15))
(score1, e1) = score(predictions, y_test)
calculado = (X_test.calculado+30).tolist()
calculado = calculado
(score2, e2) = score(calculado, y_test)

# Fit regression model
regr_1 = DecisionTreeRegressor(max_depth=62)

regr_2 = AdaBoostRegressor(DecisionTreeRegressor(max_depth=62),
                          n_estimators=100)

(predictions3, y_test3, r3, m3) = regression(regr_1)
(score3, e3) = score(predictions3, y_test3)
(predictions4, y_test4, r4, m4)  = regression(regr_2)
(score4, e4) = score(predictions4, y_test4)

#print(utils.multiclass.type_of_target(X_train))

original_params = {'n_estimators': 1000, 'max_leaf_nodes': 4, 'max_depth': None, 'random_state': 2,
                   'min_samples_split': 5}

model = xgboost.XGBRegressor(colsample_bytree=0.4,
                 gamma=0,                 
                 learning_rate=0.03,
                 max_depth=8,
                 min_child_weight=1.5,
                 n_estimators=20000,                                                                    
                 reg_alpha=0.75,
                 reg_lambda=0.45,
                 subsample=0.6,
                 seed=42) 
#(predictions5, y_test5) = regression(model)
#clf = BayesianRidge(compute_score=True)
#(predictions5, y_test5) = regression(clf)
#(score5, e5) = score(predictions5, y_test5)

erro = np.array([])
for i in range(0,200):
    if np.array([e1[i], e4[i]]).var() < 25:
        erro = np.append(erro, e3[i])
for i in range(0,20):
    print("")
    print(np.array([e1[i], e3[i], e4[i]]).var())
    
    print("erro "+ str(e1[i]))
    print("formula "+ str(descricoes[i]))
    print("original "+ str(calculado[i]))
    print("predição1 : "+str(predictions[i]) + " correto: "+ str(y_test[i]))
    print("predição2 : "+str(predictions3[i]))
    print("predição3 : "+str(predictions4[i]))
print("")   
print("Original: " + str(score2),'precisão:',str(abs(100 - score2*100)))
print(" erro < 5% ", np.sum(e2 < 5)," erro < 10% ", np.sum(e2 < 10)," erro < 20% ", np.sum(e2 < 20),"erro > 50", np.sum(e2 > 50))
print("Erro KNN: " + str(score1),'precisão:',str(100 - score1*100))
print(" erro < 5% ", np.sum(e1 < 5)," erro < 10% ", np.sum(e1 < 10)," erro < 20% ", np.sum(e1 < 20),"erro > 50", np.sum(e1 > 50))
print("Erro Arvore: " + str(score3),'precisão:',str(100 - score3*100))
print(" erro < 5% ", np.sum(e3 < 5)," erro < 10% ", np.sum(e3 < 10)," erro < 20% ", np.sum(e3 < 20),"erro > 50", np.sum(e3 > 50))
print("Erro Boost: " + str(score4),'precisão:',str(100 - score4*100))
print(" erro < 5% ", np.sum(e4 < 5)," erro < 10% ", np.sum(e4 < 10)," erro < 20% ", np.sum(e4 < 20),"erro > 50", np.sum(e4 > 50))
#print("Erro Boost: " + str(score5),'precisão:',str(100 - score5*100))