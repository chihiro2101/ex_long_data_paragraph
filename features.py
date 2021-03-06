import preprocess
import math
import nltk
import numpy as np


class METRIC(object):
    def __init__(self, title, sentences, agent, simWithTitle, simWithDoc, sim2sents, number_of_nouns, simWithAbs, rougeforsentences,  order_params):
        self.title = title
        self.sentences = sentences
        self.n = len(sentences)
        self.values = agent
        self.simWithTitle = simWithTitle
        self.simWithDoc = simWithDoc
        self.sim2sents = sim2sents
        self.number_of_nouns = number_of_nouns
        # self.sum_nouns = sum(number_of_nouns)
        self.order_params = order_params
        self.simWithAbs = simWithAbs
        self.rougeforsentences = rougeforsentences

    # number of sentences in summary
    def O(self):
        return np.sum(self.values)

    def position(self):
        p = 0
        for i in range(self.n):
            if self.values[i] == 1:
                p = p + math.sqrt(1 / (i + 1))
        return p

    # def scale_noun(self):
    #     scale = 0
    #     for i in range(self.n):
    #         if self.values[i] == 1:
    #             scale += self.number_of_nouns[i]
    #     return scale / self.sum_nouns

    def relationT(self):
        rt = 0
        for i in range(self.n):
            if self.values[i] == 1:
                rt += self.simWithTitle[i]/(self.O())
        return rt

    def cohesion(self):
        Ns = (self.O())*(self.O() - 1)/2.0
        simcos_sents_in_summary = []
        for i in range(self.n - 1):
            if self.values[i] == 1:
                for j in range(i+1, self.n):
                    if self.values[j] == 1:
                        simcos_sents_in_summary.append(self.sim2sents[i][j])

        Cs = np.sum(simcos_sents_in_summary)/Ns
        try:
            M = max(simcos_sents_in_summary)
        except:
            M = 0
        if M == 0:
            CoH = 0
        else:
            CoH = (math.log(Cs*9.0+1.0))/(math.log(M*9.0+1.0))
        return CoH

    def Cov(self):
        cov = 0
        for i in range(self.n):
            if self.values[i] == 1:
                cov += self.simWithDoc[i]
        return cov

    def CoverABS(self):
        covABS = 0
        for i in range(self.n):
            if self.values[i] == 1:
                covABS += self.simWithAbs[i]
        return covABS


    def rouge_scores(self):
        rouge1f = 0
        for i in range(self.n):
            if self.values[i] == 1:
                rouge1f += self.rougeforsentences[i]
        return rouge1f/self.O()


    def leng(self):
        length = {}
        for i in range(self.n):
            if self.values[i] == 1:
                length[i] = self.words_count(self.sentences[i])

        length_value = list(length.values())
        std = np.std(length_value)
        avgl = np.mean(length_value)

        le = 0
        for i in range(len(length_value)):
            if std == 0:
                sigmoid = 0.98
            else:
                sigmoid = np.exp((-length_value[i] - avgl) / std)
            le += (1 - sigmoid) / (1 + sigmoid)
        return le

    def words_count(self, sentences):
        words = nltk.word_tokenize(sentences)
        return len(words)

    def fitness(self):
        if self.order_params == 0:
            rel = 0.35
            cover = 0.3
            le  = 0.35
            fit = rel*self.relationT() + cover*self.Cov() + le*self.leng()
        elif self.order_params == 1:
            rel = 0.35
            covABS = 0.3
            le  = 0.35
            fit = rel*self.relationT() + covABS*self.CoverABS() + le*self.leng()
        elif self.order_params == 2:
            rel = 0.35
            coh = 0.15
            covABS = 0.15
            le  = 0.35
            fit = rel*self.relationT() + coh*self.cohesion() + le*self.leng() + covABS*self.CoverABS()  
        elif self.order_params == 3:
            rel = 0.3
            covABS = 0.2
            cover = 0.2
            le  = 0.3   
            fit = rel*self.relationT() + covABS*self.CoverABS() + le*self.leng() + cover*self.Cov() 
        elif self.order_params == 4:
            rel = 0.25
            covABS = 0.15
            cover = 0.15
            le  = 0.25   
            rouge = 0.2
            fit = rel*self.relationT() + covABS*self.CoverABS() + le*self.leng() + cover*self.Cov()  + rouge*self.rouge_scores()
        elif self.order_params == 5:
            rel = 0.3
            covABS = 0.15
            cover = 0.1
            le  = 0.3   
            rouge = 0.15
            fit = rel*self.relationT() + covABS*self.CoverABS() + le*self.leng() + cover*self.Cov()  + rouge*self.rouge_scores()
        return fit

    # def GLS(self):
    #     sim_sent = []
    #     sim_sent = self.simWithTitle
    #     c = []
    #     d = []
    #     p = [0]*self.n
    #     max_sim = max(sim_sent)
    #     for i in range(self.n):
    #         c.append(math.sqrt(1 / (i + 1)) + sim_sent[i]/max_sim)
    #         d.append(c[i]/(1+p[i]))

    #     gls = 0
    #     for i in range(self.n):
    #         if d[i] == min(d):
    #             p[i] += 1
    #         gls += 0.5*p[i]*self.values[i]
    #     return self.fitness() - gls


def compute_fitness(title, sentences, agent, simWithTitle, simWithDoc, sim2sents, number_of_nouns, simWithAbs, rougeforsentences, order_params):
    metric = METRIC(title, sentences, agent, simWithTitle,
                    simWithDoc, sim2sents, number_of_nouns,simWithAbs, rougeforsentences, order_params)
    # return metric.GLS()
    return metric.fitness()
